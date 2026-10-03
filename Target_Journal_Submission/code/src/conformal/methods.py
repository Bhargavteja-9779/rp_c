"""Prediction-interval methods compared in the study.

A :class:`FoldContext` holds one outer train/test split (one deployment scenario) and lazily
computes the expensive shared quantities (group-wise and random cross-fits, final model, random
split model). Every method returns ``(lower, upper)`` for the test spectra.

Naming of the cross-fitted conformal family (factorial ablation):
    {R,G}-{U,W}-{A,D}
    R / G : calibration scores from random (unit-grouped) folds / out-of-group folds
    U / W : uniform weights / group-balanced weights (each calibration group has equal mass)
    A / D : absolute residual score / diagnostic-normalised score |r|/σ(T², Q)
The proposed method is G-W-D (``GC-D``): ŷ(x) ± q̂·σ(x), with q̂ the group-balanced quantile of
out-of-group normalised residuals.
"""
from __future__ import annotations

import os
import time

import numpy as np
from scipy import stats

from ..models.pls import PLS1
from ..training.crossfit import CrossFit, group_balanced_weights, make_folds
from .core import (DiagnosticScale, KNNScale, diag_features, jackknife_plus_interval,
                   split_conformal_quantile, weighted_quantile)


class FoldContext:
    def __init__(self, Xtr, ytr, gtr, utr, Xte, yte, gte, ute, cfg, seed=0, A_fixed=None):
        self.Xtr, self.ytr, self.gtr, self.utr = Xtr, ytr, np.asarray(gtr).astype(str), np.asarray(utr).astype(str)
        self.Xte, self.yte, self.gte, self.ute = Xte, yte, np.asarray(gte).astype(str), np.asarray(ute).astype(str)
        self.cfg, self.seed = cfg, seed
        self.A_max = cfg.get("A_max", 20)
        self.timing = {}
        t0 = time.time()
        # ---- group-wise cross-fit (calibration groups = deployment-level groups in training)
        gmode = cfg.get("group_mode", "group")
        self.gfolds = make_folds(self.gtr, self.utr, gmode, n_folds=cfg.get("group_folds"),
                                 n_unit_folds=cfg.get("n_unit_folds", 5), seed=seed)
        self.gcf = CrossFit(Xtr, ytr, self.gfolds, self.A_max)
        self.gw = group_balanced_weights(self.gtr)
        A, self.rmsecv_curve_g = self.gcf.choose_A(weights=self.gw)
        self.A = A if A_fixed is None else A_fixed
        if cfg.get('A_offset'):
            self.A = int(np.clip(self.A + cfg['A_offset'], 1, self.A_max))
        self.timing["group_cv"] = time.time() - t0
        # ---- final model on all training data
        t0 = time.time()
        self.model = PLS1(self.A_max).fit(Xtr, ytr).set_n_lv(self.A)
        self.yhat = self.model.predict(Xte)
        dte = self.model.diagnostics(Xte)
        self.T2te, self.Qte, self.Ste = dte["T2"], dte["Q"], dte["scores"]
        dtr = self.model.diagnostics(Xtr)
        self.Qref = np.median(dtr["Q"])
        self.htr = dtr["h"]
        self.hte = dte["h"]
        self.timing["final_fit"] = time.time() - t0
        self._rcf = None
        self._split = None

    # ------------------------------------------------------------------ lazily computed pieces
    @property
    def rcf(self):
        if self._rcf is None:
            t0 = time.time()
            self.rfolds = make_folds(self.gtr, self.utr, "random", n_folds=self.cfg.get("random_folds", 5), seed=self.seed)
            self._rcf = CrossFit(self.Xtr, self.ytr, self.rfolds, self.A_max)
            self.timing["random_cv"] = time.time() - t0
        return self._rcf

    @property
    def split(self):
        """Random unit-wise split (75 % proper training / 25 % calibration) for split-CP methods."""
        if self._split is None:
            rng = np.random.default_rng(self.seed + 1000)
            uu = np.unique(self.utr)
            cal_units = rng.choice(uu, size=max(1, int(round(0.25 * len(uu)))), replace=False)
            cal = np.isin(self.utr, cal_units)
            m = PLS1(self.A_max).fit(self.Xtr[~cal], self.ytr[~cal]).set_n_lv(self.A)
            dcal = m.diagnostics(self.Xtr[cal]); dte = m.diagnostics(self.Xte); dpr = m.diagnostics(self.Xtr[~cal])
            self._split = dict(cal=cal, model=m, cal_pred=m.predict(self.Xtr[cal]), te_pred=m.predict(self.Xte),
                               dcal=dcal, dte=dte, dpr=dpr, Qref=np.median(dpr["Q"]))
        return self._split

    # ------------------------------------------------------------------ helpers
    def _oof(self, cf):
        r = self.ytr - cf.oof_at(self.A)
        T2, Q = cf.oof_diagnostics(self.A)
        return r, T2, Q

    def _scale_model(self, cf):
        r, T2, Q = self._oof(cf)
        ok = cf.covered
        Z = diag_features(T2[ok], Q[ok], self.Qref, self.cfg.get('diag_mode', 'both'))
        sm = DiagnosticScale(self.cfg.get('floor_frac', 0.1)).fit(Z, np.abs(r[ok]))
        return sm, r, T2, Q


def _memo(ctx, key, fn):
    """Cache alpha-independent computations on the context (same result for every alpha)."""
    if key not in ctx.__dict__:
        ctx.__dict__[key] = fn()
    return ctx.__dict__[key]


# ======================================================================================
# Baselines
# ======================================================================================
def m_astm(ctx: FoldContext, alpha, source="random"):
    """Classical PLS interval: ŷ ± t_{1−α/2, n−A−1} · RMSECV · √(1 + h(x)) (ASTM E1655-type)."""
    cf = ctx.rcf if source == "random" else ctx.gcf
    w = None if source == "random" else ctx.gw
    r = ctx.ytr - cf.oof_at(ctx.A)
    ok = cf.covered
    rmsecv = np.sqrt(np.average(r[ok] ** 2, weights=None if w is None else w[ok]))
    tq = stats.t.ppf(1 - alpha / 2, df=max(1, len(ctx.ytr) - ctx.A - 1))
    half = tq * rmsecv * np.sqrt(1 + ctx.hte)
    return ctx.yhat - half, ctx.yhat + half


def m_scp(ctx, alpha):
    """Split conformal prediction with absolute residuals (random unit-wise split)."""
    sp = ctx.split
    s = np.abs(ctx.ytr[sp["cal"]] - sp["cal_pred"])
    q = split_conformal_quantile(s, alpha)
    return sp["te_pred"] - q, sp["te_pred"] + q


def m_ncp_knn(ctx, alpha):
    """Normalised split CP with kNN difficulty in PLS-score space (Papadopoulos et al.)."""
    sp = ctx.split

    def _fit():
        pr = ~sp["cal"]
        # out-of-fold residuals of the proper training set (internal 5-fold, unit-grouped)
        folds = make_folds(ctx.gtr[pr], ctx.utr[pr], "random", n_folds=5, seed=ctx.seed)
        cf = CrossFit(ctx.Xtr[pr], ctx.ytr[pr], folds, ctx.A)
        rpr = np.abs(ctx.ytr[pr] - cf.oof_at(ctx.A))
        ks = KNNScale().fit(sp["dpr"]["scores"], rpr)
        return ks.predict(sp["dcal"]["scores"]), ks.predict(sp["dte"]["scores"])
    sig_cal, sig_te = _memo(ctx, "ncp_knn", _fit)
    s = np.abs(ctx.ytr[sp["cal"]] - sp["cal_pred"]) / sig_cal
    q = split_conformal_quantile(s, alpha)
    return sp["te_pred"] - q * sig_te, sp["te_pred"] + q * sig_te


def m_cvplus(ctx, alpha):
    """CV+ (Barber et al. 2021) with random unit-grouped folds (jackknife+ family; cf. Lin et al. 2022)."""
    cf = ctx.rcf
    r = np.abs(ctx.ytr - cf.oof_at(ctx.A))
    mu, _, _ = _memo(ctx, "rcf_fold_predict", lambda: cf.fold_predict(ctx.Xte, ctx.A))
    w = np.ones(len(r))
    return jackknife_plus_interval(mu, np.ones_like(mu), r, cf.fold_id, w, alpha, inf_mass=1.0)


def m_wcp(ctx, alpha, max_n=20000):
    """Weighted split CP under covariate shift (Tibshirani et al. 2019). The density ratio
    p_test(x)/p_cal(x) is estimated with a logistic classifier (calibration vs. unlabelled test
    spectra of the deployment group) on [standardised PLS scores, log Q]. Uses unlabelled test
    spectra (transductive)."""
    from sklearn.linear_model import LogisticRegression
    sp = ctx.split
    lo = np.empty(len(ctx.yte)); hi = np.empty(len(ctx.yte))
    s_cal = np.abs(ctx.ytr[sp["cal"]] - sp["cal_pred"])
    Fc = np.c_[sp["dcal"]["scores"], np.log(sp["dcal"]["Q"] / sp["Qref"])]
    Ft = np.c_[sp["dte"]["scores"], np.log(sp["dte"]["Q"] / sp["Qref"])]
    mu, sd = Fc.mean(0), Fc.std(0) + 1e-12
    Fc, Ft = (Fc - mu) / sd, (Ft - mu) / sd
    def _weights():
        rng = np.random.default_rng(ctx.seed)
        out = {}
        for g in np.unique(ctx.gte):
            te = np.where(ctx.gte == g)[0]
            ic = rng.choice(len(Fc), size=min(len(Fc), max_n), replace=False)
            it = rng.choice(te, size=min(len(te), max_n), replace=False)
            Xc = np.r_[Fc[ic], Ft[it]]; yc = np.r_[np.zeros(len(ic)), np.ones(len(it))]
            clf = LogisticRegression(C=1.0, max_iter=1000).fit(Xc, yc)
            prior = len(ic) / len(it)
            out[g] = (te, np.exp(clf.decision_function(Fc)) * prior, np.exp(clf.decision_function(Ft[te])) * prior)
        return out
    for g, (te, w_cal, w_te) in _memo(ctx, "wcp_weights", _weights).items():
        o = np.argsort(s_cal); s_sorted = s_cal[o]; cw = np.cumsum(w_cal[o])
        tot = cw[-1] + w_te
        k = np.searchsorted(cw, (1 - alpha) * tot - 1e-12, side="left")
        q = np.where(k >= len(s_sorted), np.inf, s_sorted[np.minimum(k, len(s_sorted) - 1)])
        lo[te] = sp["te_pred"][te] - q; hi[te] = sp["te_pred"][te] + q
    return lo, hi


def m_gpr(ctx, alpha, n_sub=1000):
    """Gaussian-process regression on standardised PLS scores (RBF + white noise kernel)."""
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel

    def _fit():
        S = ctx.model.diagnostics(ctx.Xtr)["scores"]
        mu, sd = S.mean(0), S.std(0) + 1e-12
        rng = np.random.default_rng(ctx.seed)
        idx = rng.choice(len(S), size=min(n_sub, len(S)), replace=False)
        k = ConstantKernel(1.0) * RBF(length_scale=np.ones(S.shape[1]) * 3.0) + WhiteKernel(0.1)
        gp = GaussianProcessRegressor(kernel=k, normalize_y=True, random_state=ctx.seed, n_restarts_optimizer=0)
        gp.fit((S[idx] - mu) / sd, ctx.ytr[idx])
        return gp.predict((ctx.Ste - mu) / sd, return_std=True)
    m, s = _memo(ctx, "gpr", _fit)
    z = stats.norm.ppf(1 - alpha / 2)
    return m - z * s, m + z * s


def m_bagging(ctx, alpha, B=25):
    """Bagged PLS (unit-level bootstrap). σ²(x) = var_bag(x) + mean OOB squared residual."""
    c, sd = _memo(ctx, "bagging", lambda: _bag_fit(ctx, B))
    z = stats.norm.ppf(1 - alpha / 2)
    return c - z * sd, c + z * sd


def _bag_fit(ctx, B):
    rng = np.random.default_rng(ctx.seed)
    uu, inv = np.unique(ctx.utr, return_inverse=True)
    preds = np.empty((B, len(ctx.yte)))
    oob_sum = np.zeros(len(ctx.ytr)); oob_cnt = np.zeros(len(ctx.ytr))
    for b in range(B):
        bu = rng.integers(0, len(uu), len(uu))
        mult = np.bincount(bu, minlength=len(uu))
        rows = np.repeat(np.arange(len(ctx.ytr)), mult[inv])
        m = PLS1(ctx.A).fit(ctx.Xtr[rows], ctx.ytr[rows])
        preds[b] = m.predict(ctx.Xte, ctx.A)
        oob = mult[inv] == 0
        oob_sum[oob] += m.predict(ctx.Xtr[oob], ctx.A); oob_cnt[oob] += 1
    ok = oob_cnt > 0
    s2 = np.mean((ctx.ytr[ok] - oob_sum[ok] / oob_cnt[ok]) ** 2)
    return preds.mean(0), np.sqrt(preds.var(0, ddof=1) + s2)


def _qgb_models(ctx, alpha):
    import lightgbm as lgb
    sp = ctx.split
    pr = ~sp["cal"]
    F = lambda d, Qr: np.c_[d["scores"], np.log1p(d["T2"]), np.log(d["Q"] / Qr)]
    Fpr, Fcal, Fte = F(sp["dpr"], sp["Qref"]), F(sp["dcal"], sp["Qref"]), F(sp["dte"], sp["Qref"])
    out = {}
    for name, a in (("lo", alpha / 2), ("hi", 1 - alpha / 2)):
        m = lgb.LGBMRegressor(objective="quantile", alpha=a, n_estimators=300, learning_rate=0.05,
                              num_leaves=31, min_child_samples=20, subsample=0.8, subsample_freq=1,
                              colsample_bytree=0.9, random_state=ctx.seed, n_jobs=int(os.environ.get("NJOBS", "1")), verbose=-1)
        m.fit(Fpr, ctx.ytr[pr])
        out[name] = (m.predict(Fcal), m.predict(Fte))
    return out


def m_qgb(ctx, alpha):
    """Raw quantile gradient boosting on PLS scores + diagnostics (no conformal correction)."""
    key = ("qgb", alpha)
    if key not in ctx.__dict__:
        ctx.__dict__[key] = _qgb_models(ctx, alpha)
    o = ctx.__dict__[key]
    return o["lo"][1], o["hi"][1]


def m_cqr(ctx, alpha):
    """Conformalised quantile regression (Romano et al. 2019) on the same quantile models."""
    key = ("qgb", alpha)
    if key not in ctx.__dict__:
        ctx.__dict__[key] = _qgb_models(ctx, alpha)
    o = ctx.__dict__[key]
    ycal = ctx.ytr[ctx.split["cal"]]
    E = np.maximum(o["lo"][0] - ycal, ycal - o["hi"][0])
    q = split_conformal_quantile(E, alpha)
    return o["lo"][1] - q, o["hi"][1] + q


def m_oracle(ctx, alpha):
    """Reference only: split CP calibrated on labelled spectra of the test group itself
    (2-fold over test units, absolute residuals of the final model). Not available in practice."""
    lo = np.empty(len(ctx.yte)); hi = np.empty(len(ctx.yte))
    rng = np.random.default_rng(ctx.seed + 7)
    for g in np.unique(ctx.gte):
        te = np.where(ctx.gte == g)[0]
        uu = np.unique(ctx.ute[te])
        half = set(rng.choice(uu, size=len(uu) // 2, replace=False))
        a = np.array([u in half for u in ctx.ute[te]])
        for cal, ev in ((a, ~a), (~a, a)):
            s = np.abs(ctx.yte[te][cal] - ctx.yhat[te][cal])
            q = split_conformal_quantile(s, alpha) if cal.sum() else np.inf
            lo[te[ev]] = ctx.yhat[te[ev]] - q; hi[te[ev]] = ctx.yhat[te[ev]] + q
    return lo, hi


# ======================================================================================
# Cross-fitted conformal family (ablation cells) and the proposed method
# ======================================================================================
def m_crossfit_family(ctx, alpha, folds="G", weights="W", score="D", finite_correction=False):
    cf = ctx.gcf if folds == "G" else ctx.rcf
    r = ctx.ytr - cf.oof_at(ctx.A)
    ok = cf.covered
    if weights == "W":
        w = group_balanced_weights(ctx.gtr[ok])
        K = len(np.unique(ctx.gtr[ok]))
    else:
        w = np.ones(ok.sum()) / ok.sum()
        K = ok.sum()
    if score == "D":
        key = ("scale", folds)
        if key not in ctx.__dict__:
            ctx.__dict__[key] = ctx._scale_model(cf)
        sm, _, T2, Q = ctx.__dict__[key]
        sig_cal = sm.predict(diag_features(T2[ok], Q[ok], ctx.Qref, ctx.cfg.get('diag_mode', 'both')))
        sig_te = sm.predict(diag_features(ctx.T2te, ctx.Qte, ctx.Qref, ctx.cfg.get('diag_mode', 'both')))
    else:
        sig_cal = np.ones(ok.sum()); sig_te = np.ones(len(ctx.yte))
    s = np.abs(r[ok]) / sig_cal
    inf_mass = (1.0 / (K + 1)) / (1 - 1.0 / (K + 1)) * w.sum() if finite_correction else 0.0
    q = weighted_quantile(s, w, 1 - alpha, inf_mass=inf_mass)
    return ctx.yhat - q * sig_te, ctx.yhat + q * sig_te


def m_gc_jplus(ctx, alpha, score="A"):
    """Hierarchical jackknife+ (Lee, Barber & Willett; leave-one-group-out folds, group-balanced
    weights, +∞ mass 1/(K+1)). Guarantee ≥ 1−2α under hierarchical exchangeability for score="A"."""
    cf = ctx.gcf
    ok = cf.covered
    r = np.abs(ctx.ytr - cf.oof_at(ctx.A))
    K = len(np.unique(ctx.gtr[ok]))
    _, counts = np.unique(ctx.gtr, return_counts=True)
    gi = {g: c for g, c in zip(*np.unique(ctx.gtr, return_counts=True))}
    w = np.array([1.0 / ((K + 1) * gi[g]) for g in ctx.gtr])
    mu, T2f, Qf = _memo(ctx, "gcf_fold_predict", lambda: cf.fold_predict(ctx.Xte, ctx.A))
    if score == "D":
        key = ("scale", "G")
        if key not in ctx.__dict__:
            ctx.__dict__[key] = ctx._scale_model(cf)
        sm, _, T2, Q = ctx.__dict__[key]
        sig_cal = sm.predict(diag_features(T2, Q, ctx.Qref, ctx.cfg.get('diag_mode', 'both')))
        sig = np.stack([sm.predict(diag_features(T2f[k], Qf[k], ctx.Qref, ctx.cfg.get('diag_mode', 'both'))) for k in range(len(cf.models))])
    else:
        sig_cal = np.ones(len(r)); sig = np.ones_like(mu)
    sc = np.where(ok, r / sig_cal, np.nan)
    fid = np.where(ok, cf.fold_id, -1)
    return jackknife_plus_interval(mu, sig, np.nan_to_num(sc, nan=0.0), fid, np.where(ok, w, 0.0), alpha,
                                   inf_mass=1.0 / (K + 1))


def m_hcp_split(ctx, alpha, score="D"):
    """Hierarchical split CP (Lee, Barber & Willett, eq. 6): half of the training groups fit the
    PLS model and σ(·); the other half calibrate with weights 1/((K₁+1)N_k) and +∞ mass 1/(K₁+1).
    Exact marginal coverage ≥ 1−α for a test point from a new exchangeable group."""
    rng = np.random.default_rng(ctx.seed + 99)
    ug = np.unique(ctx.gtr)
    calg = rng.choice(ug, size=len(ug) // 2, replace=False)
    cal = np.isin(ctx.gtr, calg)
    cal_units = np.unique(ctx.utr[cal])
    prop = ~cal & ~np.isin(ctx.utr, cal_units)
    if prop.sum() < 2 * ctx.A_max or len(calg) < 1:
        # not applicable (e.g. every unit measured in every group): report an uninformative interval
        return np.full(len(ctx.yte), -np.inf), np.full(len(ctx.yte), np.inf)
    sub_groups = ctx.gtr[prop]
    folds = make_folds(sub_groups, ctx.utr[prop], ctx.cfg.get("group_mode", "group"),
                       n_folds=ctx.cfg.get("group_folds"), n_unit_folds=ctx.cfg.get("n_unit_folds", 5), seed=ctx.seed)
    m = PLS1(ctx.A_max).fit(ctx.Xtr[prop], ctx.ytr[prop]).set_n_lv(ctx.A)
    Qref = np.median(m.diagnostics(ctx.Xtr[prop])["Q"])
    dcal = m.diagnostics(ctx.Xtr[cal]); dte = m.diagnostics(ctx.Xte)
    if score == "D" and len(np.unique(sub_groups)) >= 2:
        cf = CrossFit(ctx.Xtr[prop], ctx.ytr[prop], folds, ctx.A)
        r = ctx.ytr[prop] - cf.oof_at(ctx.A)
        T2, Q = cf.oof_diagnostics(ctx.A)
        okk = cf.covered
        sm = DiagnosticScale(ctx.cfg.get('floor_frac', 0.1)).fit(diag_features(T2[okk], Q[okk], Qref, ctx.cfg.get('diag_mode', 'both')), np.abs(r[okk]))
        sig_cal = sm.predict(diag_features(dcal["T2"], dcal["Q"], Qref, ctx.cfg.get('diag_mode', 'both')))
        sig_te = sm.predict(diag_features(dte["T2"], dte["Q"], Qref, ctx.cfg.get('diag_mode', 'both')))
    else:
        sig_cal = np.ones(cal.sum()); sig_te = np.ones(len(ctx.yte))
    s = np.abs(ctx.ytr[cal] - m.predict(ctx.Xtr[cal])) / sig_cal
    K1 = len(calg)
    gi = {g: c for g, c in zip(*np.unique(ctx.gtr[cal], return_counts=True))}
    w = np.array([1.0 / ((K1 + 1) * gi[g]) for g in ctx.gtr[cal]])
    q = weighted_quantile(s, w, 1 - alpha, inf_mass=1.0 / (K1 + 1))
    yh = m.predict(ctx.Xte)
    return yh - q * sig_te, yh + q * sig_te


METHODS = {
    # classical / model-based baselines
    "ASTM-R": lambda c, a: m_astm(c, a, "random"),
    "ASTM-G": lambda c, a: m_astm(c, a, "group"),
    "GPR": m_gpr,
    "BAG": m_bagging,
    "QGB": m_qgb,
    # conformal baselines
    "SCP": m_scp,
    "NCP-kNN": m_ncp_knn,
    "CV+": m_cvplus,
    "CQR": m_cqr,
    "WCP": m_wcp,
    # factorial ablation of the proposed method (cross-fitted, centre = full-data model)
    "R-U-A": lambda c, a: m_crossfit_family(c, a, "R", "U", "A"),
    "R-U-D": lambda c, a: m_crossfit_family(c, a, "R", "U", "D"),
    "G-U-A": lambda c, a: m_crossfit_family(c, a, "G", "U", "A"),
    "G-W-A": lambda c, a: m_crossfit_family(c, a, "G", "W", "A"),
    "G-U-D": lambda c, a: m_crossfit_family(c, a, "G", "U", "D"),
    "GC-D": lambda c, a: m_crossfit_family(c, a, "G", "W", "D"),          # proposed
    "GC-D+": lambda c, a: m_crossfit_family(c, a, "G", "W", "D", True),   # + finite-sample correction
    # variants with formal guarantees
    "HJ+": lambda c, a: m_gc_jplus(c, a, "A"),
    "HJ+-D": lambda c, a: m_gc_jplus(c, a, "D"),
    "HCP-D": lambda c, a: m_hcp_split(c, a, "D"),
    "HCP-A": lambda c, a: m_hcp_split(c, a, "A"),
    # reference
    "ORACLE": m_oracle,
}


# ======================================================================================
# Post-hoc iteration 1 (see supplementary/research_process/04_iteration_log.md)
# ======================================================================================
def m_gc_d2(ctx, alpha):
    """GC-D with the predicted value added to the scale model: σ(log(1+T²), log(Q/Q_ref), ŷ)."""
    def _fit():
        cf = ctx.gcf
        r, T2, Q = ctx._oof(cf)
        ok = cf.covered
        yo = cf.oof_at(ctx.A)
        Zc = np.c_[diag_features(T2[ok], Q[ok], ctx.Qref), yo[ok]]
        sm = DiagnosticScale(ctx.cfg.get("floor_frac", 0.1)).fit(Zc, np.abs(r[ok]))
        sig_cal = sm.predict(Zc)
        sig_te = sm.predict(np.c_[diag_features(ctx.T2te, ctx.Qte, ctx.Qref), ctx.yhat])
        w = group_balanced_weights(ctx.gtr[ok])
        return np.abs(r[ok]) / sig_cal, w, sig_te
    s, w, sig_te = _memo(ctx, "gc_d2", _fit)
    q = weighted_quantile(s, w, 1 - alpha)
    return ctx.yhat - q * sig_te, ctx.yhat + q * sig_te


def _qfeat(m, X, Qref):
    d = m.diagnostics(X)
    return np.c_[d["scores"], np.log1p(d["T2"]), np.log(d["Q"] / Qref)]


def _lgb_q(a, seed):
    import lightgbm as lgb
    return lgb.LGBMRegressor(objective="quantile", alpha=a, n_estimators=300, learning_rate=0.05, num_leaves=31,
                             min_child_samples=20, subsample=0.8, subsample_freq=1, colsample_bytree=0.9,
                             random_state=seed, n_jobs=int(os.environ.get("NJOBS", "1")), verbose=-1)


def m_gc_cqr(ctx, alpha):
    """Group-calibrated CQR: quantile GBMs (on PLS scores + diagnostics) are cross-fitted over the
    out-of-group folds; CQR conformity scores E_i = max(q̂_lo − y, y − q̂_hi) are computed out-of-group
    and their group-balanced (1−α) quantile widens the full-data quantile band."""
    key = ("gc_cqr", alpha)
    if key not in ctx.__dict__:
        cf = ctx.gcf
        E = np.full(len(ctx.ytr), np.nan)
        for k, (tr, te) in enumerate(ctx.gfolds):
            m = cf.models[k]
            Qr = np.median(m.diagnostics(ctx.Xtr[tr], ctx.A)["Q"])
            m.set_n_lv(ctx.A)
            Ftr, Fte = _qfeat(m, ctx.Xtr[tr], Qr), _qfeat(m, ctx.Xtr[te], Qr)
            lo = _lgb_q(alpha / 2, ctx.seed).fit(Ftr, ctx.ytr[tr]).predict(Fte)
            hi = _lgb_q(1 - alpha / 2, ctx.seed).fit(Ftr, ctx.ytr[tr]).predict(Fte)
            E[te] = np.maximum(lo - ctx.ytr[te], ctx.ytr[te] - hi)
        ok = np.isfinite(E)
        Ftr = _qfeat(ctx.model, ctx.Xtr, ctx.Qref); Fte = _qfeat(ctx.model, ctx.Xte, ctx.Qref)
        lo = _lgb_q(alpha / 2, ctx.seed).fit(Ftr, ctx.ytr).predict(Fte)
        hi = _lgb_q(1 - alpha / 2, ctx.seed).fit(Ftr, ctx.ytr).predict(Fte)
        q = weighted_quantile(E[ok], group_balanced_weights(ctx.gtr[ok]), 1 - alpha)
        ctx.__dict__[key] = (lo - q, hi + q)
    return ctx.__dict__[key]


METHODS.update({"GC-D2": m_gc_d2, "GC-CQR": m_gc_cqr})
