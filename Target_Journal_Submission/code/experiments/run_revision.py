"""Experiments added in response to the reviewers (revision 1). All at alpha = 0.10.

  --exp ctxpass  --task T   one fold context per outer fold of task T (seed 0), on which are computed
                            (i)  scale-model form variants of GC-D (R1.9, R4.3): GLM family, T² transform,
                                 Q normalisation, T²×Q interaction, group-weighted fit;
                            (ii) diagnostic limits for a rejection rule (95/99 % quantiles of the out-of-group
                                 Q ratio and T² of the calibration spectra) (R1.15, R1.18, R4.2);
                            (iii) bias correction with k labelled units of the new group (R1.13, R1.17).
  --exp reject              Q-based rejection rule on the test-time perturbations of mango new seasons (R1.18).
  --exp unbalanced --task T semi-synthetic, highly unequal calibration-group sizes (R1.8).
  --exp wcp      --task T   weighted CP: density-ratio caps and estimator variants, weight diagnostics (R1.4, R4.4).
Outputs: results/revision/*.csv
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from scipy.interpolate import interp1d
from src.conformal.core import DiagnosticScale, diag_features, weighted_quantile
from src.conformal.methods import METHODS, FoldContext
from src.evaluation.engine import run_task
from src.evaluation.metrics import interval_score
from src.evaluation.tasks import get_task
from src.preprocessing.spectral import preprocess
from src.training.crossfit import group_balanced_weights
from src.utils import RESULTS, get_logger

p = argparse.ArgumentParser()
p.add_argument("--exp", required=True)
p.add_argument("--task", default=None)
p.add_argument("--quick", action="store_true")
a = p.parse_args()
OUT = os.path.join(RESULTS, "revision"); os.makedirs(OUT, exist_ok=True)
log = get_logger(f"revision_{a.exp}_{a.task}")
ALPHA = 0.1


def contexts(task, cfg=None, X_override=None, seed=0):
    """Yield (fold, ctx, y_test_original_scale, inv, units_test, test_groups) for every outer fold."""
    ds, cfg = task["ds"], dict(task["cfg"], **(cfg or {}))
    X = task["X"] if X_override is None else X_override
    y_all = ds.y.astype(float)
    log_t = cfg.get("log_target", False)
    fwd = (lambda v: np.log1p(v)) if log_t else (lambda v: v)
    inv = (lambda v: np.expm1(v)) if log_t else (lambda v: v)
    units = ds.meta["unit"].to_numpy()
    folds = task["folds"][:2] if a.quick else task["folds"]
    for f in folds:
        tr, te = f["train"], f["test"]
        if len(tr) == 0 or len(te) == 0:
            continue
        assert not np.intersect1d(units[tr], units[te]).size
        ctx = FoldContext(X[tr], fwd(y_all[tr]), f["calib_group"][tr], units[tr], X[te], fwd(y_all[te]),
                          f["test_group"][te], units[te], cfg, seed=seed)
        yield f, ctx, y_all[te], inv, units[te], f["test_group"][te]


def summarize(y, lo, hi):
    cov = (y >= lo) & (y <= hi)
    return dict(coverage=float(cov.mean()), width=float(np.mean(hi - lo)),
                interval_score=float(np.mean(interval_score(y, lo, hi, ALPHA))), n=int(len(y)))


SCALE_VARIANTS = [("default (Poisson, log(1+T²), Q/Q̃)", {}),
                  ("Gamma GLM", {"scale_family": "gamma"}),
                  ("Gaussian GLM, log link", {"scale_family": "gaussian"}),
                  ("log-normal (LS on log|r|)", {"scale_family": "lognormal"}),
                  ("log T² instead of log(1+T²)", {"t2_transform": "log"}),
                  ("Q not normalised by Q̃", {"q_norm": "none"}),
                  ("with T²×Q interaction", {"diag_interaction": True}),
                  ("group-weighted GLM fit", {"scale_weights": "group"}),
                  ("Q only", {"diag_mode": "Q"}),
                  ("T² only", {"diag_mode": "T2"})]
K_BIAS = [1, 2, 3, 5, 10]
R_BIAS = 20


def gcd_from_residuals(ctx, r, T2, Q, groups, sel):
    """GC-D quantile and scale model from (possibly bias-corrected) out-of-group residuals r[sel]."""
    Z = diag_features(T2[sel], Q[sel], ctx.Qref, ctx.cfg)
    sm = DiagnosticScale(ctx.cfg.get("floor_frac", 0.1)).fit(Z, np.abs(r[sel]))
    s = np.abs(r[sel]) / sm.predict(Z)
    q = weighted_quantile(s, group_balanced_weights(groups[sel]), 1 - ALPHA)
    return q, sm


if a.exp == "ctxpass":
    task = get_task(a.task, seed=0)
    rows_scale, rows_lim, rows_bias = [], [], []
    do_bias = a.task in ("mango_instrument", "mango_season_loso", "mango_population")
    do_scale = a.task in ("mango_season_loso", "mango_season_forward", "mango_instrument", "ossl_lucas_block")
    for f, ctx, yte, inv, ute, gte in contexts(task):
        log.info(f"[{a.task}] fold {f['name']} A={ctx.A}")
        base_cfg = dict(ctx.cfg)
        # (i) scale-model form ------------------------------------------------------------------
        if do_scale:
            for name, over in SCALE_VARIANTS:
                ctx.cfg = dict(base_cfg, **over)
                ctx.__dict__.pop(("scale", "G"), None)
                lo, hi = METHODS["GC-D"](ctx, ALPHA)
                lo, hi = inv(lo), inv(hi)
                for g in np.unique(gte):
                    s = gte == g
                    rows_scale.append(dict(task=a.task, fold=f["name"], group=g, variant=name, **summarize(yte[s], lo[s], hi[s])))
            ctx.cfg = base_cfg; ctx.__dict__.pop(("scale", "G"), None)
        # (ii) diagnostic limits from the out-of-group calibration spectra -----------------------
        cf = ctx.gcf; ok = cf.covered
        T2o, Qo = cf.oof_diagnostics(ctx.A)
        qr = Qo[ok] / ctx.Qref
        rows_lim.append(dict(task=a.task, fold=f["name"], Qr95=float(np.quantile(qr, 0.95)), Qr99=float(np.quantile(qr, 0.99)),
                             T2_95=float(np.quantile(T2o[ok], 0.95)), T2_99=float(np.quantile(T2o[ok], 0.99)),
                             y_lo=float(np.quantile(inv(ctx.ytr), ALPHA / 2)), y_hi=float(np.quantile(inv(ctx.ytr), 1 - ALPHA / 2))))
        # (iii) bias correction with k labelled units of the new group ----------------------------
        if do_bias:
            r = ctx.ytr - cf.oof_at(ctx.A)
            lo0, hi0 = METHODS["GC-D"](ctx, ALPHA)
            q0, sm0 = gcd_from_residuals(ctx, r, T2o, Qo, ctx.gtr, ok)
            sig_te = sm0.predict(diag_features(ctx.T2te, ctx.Qte, ctx.Qref, ctx.cfg))
            gtr, utr = ctx.gtr, ctx.utr
            for k in K_BIAS:
                for rep in range(R_BIAS):
                    rng = np.random.default_rng(1000 * k + rep)
                    # recalibration: in every calibration group, k units play the role of the labelled reference samples
                    rb = r.copy(); keep = ok.copy()
                    for g in np.unique(gtr[ok]):
                        ig = np.where(ok & (gtr == g))[0]
                        uu = np.unique(utr[ig])
                        if len(uu) <= k:
                            keep[ig] = False; continue
                        ref = rng.choice(uu, size=k, replace=False)
                        isref = np.isin(utr[ig], ref)
                        rb[ig[~isref]] -= r[ig[isref]].mean()
                        keep[ig[isref]] = False
                    qb, smb = gcd_from_residuals(ctx, rb, T2o, Qo, gtr, keep)
                    sig_b = smb.predict(diag_features(ctx.T2te, ctx.Qte, ctx.Qref, ctx.cfg))
                    for g in np.unique(gte):
                        ig = np.where(gte == g)[0]
                        uu = np.unique(ute[ig])
                        if len(uu) <= k:
                            continue
                        ref = rng.choice(uu, size=k, replace=False)
                        isref = np.isin(ute[ig], ref)
                        ev = ig[~isref]
                        bias = float(np.mean(ctx.yte[ig[isref]] - ctx.yhat[ig[isref]]))
                        base = dict(task=a.task, fold=f["name"], group=g, k=k, rep=rep, bias_hat=bias,
                                    bias_true=float(np.mean(ctx.yte[ig] - ctx.yhat[ig])))
                        rows_bias.append(dict(base, variant="GC-D (no correction)", **summarize(yte[ev], inv(lo0[ev]), inv(hi0[ev]))))
                        rows_bias.append(dict(base, variant="GC-D, centre shifted", **summarize(yte[ev], inv(lo0[ev] + bias), inv(hi0[ev] + bias))))
                        c = ctx.yhat[ev] + bias
                        rows_bias.append(dict(base, variant="GC-D-BC (shifted and recalibrated)",
                                              **summarize(yte[ev], inv(c - qb * sig_b[ev]), inv(c + qb * sig_b[ev]))))
    if rows_scale:
        pd.DataFrame(rows_scale).to_csv(os.path.join(OUT, f"scale_form_{a.task}.csv"), index=False)
    pd.DataFrame(rows_lim).to_csv(os.path.join(OUT, f"diag_limits_{a.task}.csv"), index=False)
    if rows_bias:
        pd.DataFrame(rows_bias).to_csv(os.path.join(OUT, f"bias_correction_{a.task}.csv"), index=False)

elif a.exp == "reject":
    task = get_task("mango_season_loso", seed=0)
    ds = task["ds"]; raw = ds.X.astype(float); wl = ds.wl
    sd_ref = np.median(raw.std(0))
    def pert(Xr, kind, lev, rng):
        if kind == "noise":
            return Xr + rng.normal(scale=lev * sd_ref, size=Xr.shape)
        if kind == "gain":
            return Xr * (1 + lev)
        if kind == "offset_slope":
            return Xr + lev * sd_ref * (wl - wl.min()) / (wl.max() - wl.min())
        if kind == "wl_shift":
            return interp1d(wl, Xr, axis=1, bounds_error=False, fill_value="extrapolate")(wl - lev)
        raise ValueError(kind)
    grid = [("none", 0.0), ("noise", 0.003), ("noise", 0.01), ("noise", 0.03), ("gain", 0.05),
            ("offset_slope", 2.0), ("wl_shift", 0.5), ("wl_shift", 1.0), ("wl_shift", 2.0)]
    rows = []
    for f, ctx, yte, inv, ute, gte in contexts(task):
        te = f["test"]
        cf = ctx.gcf; ok = cf.covered
        T2o, Qo = cf.oof_diagnostics(ctx.A)
        lim = dict(Q95=np.quantile(Qo[ok] / ctx.Qref, 0.95), Q99=np.quantile(Qo[ok] / ctx.Qref, 0.99),
                   T2_99=np.quantile(T2o[ok], 0.99))
        for kind, lev in grid:
            rng = np.random.default_rng(0)
            Xp = preprocess(pert(raw[te], kind, lev, rng) if kind != "none" else raw[te], task["recipe"]).astype(np.float32)
            # swap the test set of the context (training parts, scale model and quantile are unchanged)
            ctx.Xte = Xp; ctx.yhat = ctx.model.predict(Xp)
            d = ctx.model.diagnostics(Xp); ctx.T2te, ctx.Qte, ctx.Ste, ctx.hte = d["T2"], d["Q"], d["scores"], d["h"]
            ctx._split = None; ctx.__dict__.pop("wcp_weights", None)
            lo, hi = METHODS["GC-D"](ctx, ALPHA); slo, shi = METHODS["SCP"](ctx, ALPHA)
            Qr = ctx.Qte / ctx.Qref
            rows.append(pd.DataFrame(dict(fold=f["name"], perturbation=kind, level=lev, Qr=Qr, T2=ctx.T2te,
                                          rej_Q95=Qr > lim["Q95"], rej_Q99=Qr > lim["Q99"],
                                          rej_Q99_T2=(Qr > lim["Q99"]) | (ctx.T2te > lim["T2_99"]),
                                          abs_err=np.abs(yte - ctx.yhat), cov_gcd=(yte >= lo) & (yte <= hi),
                                          cov_scp=(yte >= slo) & (yte <= shi), width_gcd=hi - lo)))
        log.info(f"reject: fold {f['name']} done")
    pd.concat(rows).to_parquet(os.path.join(OUT, "reject_points.parquet"), index=False)

elif a.exp == "unbalanced":
    methods = ["SCP", "G-U-A", "G-W-A", "G-U-D", "GC-D", "ORACLE"]
    task = get_task(a.task, seed=0)
    units = task["ds"].meta.unit.to_numpy()
    for rep in ([0] if a.quick else [0, 1, 2]):
        rng = np.random.default_rng(500 + rep)
        t = dict(task); t["folds"] = []; imb = []
        for f in (task["folds"][:2] if a.quick else task["folds"]):
            tr = f["train"]; g = f["calib_group"][tr]
            ug = rng.permutation(np.unique(g))
            frac = (np.arange(1, len(ug) + 1) ** -1.5)          # Zipf-like target fractions: 1, 0.35, 0.19, ...
            keep = []
            for gg, fr in zip(ug, frac):
                ig = tr[g == gg]; uu = np.unique(units[ig])
                ku = rng.choice(uu, size=min(len(uu), max(5, int(round(fr * len(uu))))), replace=False)
                keep.append(ig[np.isin(units[ig], ku)])
            h = dict(f); h["train"] = np.sort(np.concatenate(keep)); t["folds"].append(h)
            sizes = pd.Series(f["calib_group"][h["train"]]).value_counts()
            imb.append(dict(fold=f["name"], rep=rep, largest_share=float(sizes.iloc[0] / sizes.sum()),
                            max_min_ratio=float(sizes.iloc[0] / sizes.iloc[-1]), n_train=int(sizes.sum())))
        df = run_task(t, a.task, methods, [ALPHA], rep, os.path.join(OUT, "tmp"), log=log.info, store_points=False, resume=False)
        df["rep"] = rep
        df.to_csv(os.path.join(OUT, f"unbalanced_{a.task}_rep{rep}.csv"), index=False)
        pd.DataFrame(imb).to_csv(os.path.join(OUT, f"unbalanced_sizes_{a.task}_rep{rep}.csv"), index=False)

elif a.exp == "wcp":
    from sklearn.linear_model import LogisticRegression
    task = get_task(a.task, seed=0)
    fi = pd.read_csv(os.path.join(RESULTS, "main", f"folds_{a.task}_seed0.csv")).set_index("fold")
    ests = [("logistic, C = 1, all scores + log Q (as in main runs)", 1.0, None),
            ("logistic, C = 0.01 (strong regularisation)", 0.01, None),
            ("logistic, C = 1, first 3 scores only", 1.0, 3)]
    caps = [None, 100.0, 50.0, 20.0, 10.0, 5.0]
    rows = []
    ds = task["ds"]; units = ds.meta["unit"].to_numpy(); y_all = ds.y.astype(float)
    log_t = task["cfg"].get("log_target", False)
    fwd = (lambda v: np.log1p(v)) if log_t else (lambda v: v); inv = (lambda v: np.expm1(v)) if log_t else (lambda v: v)
    for f in (task["folds"][:2] if a.quick else task["folds"]):
        tr, te = f["train"], f["test"]
        ctx = FoldContext(task["X"][tr], fwd(y_all[tr]), f["calib_group"][tr], units[tr], task["X"][te], fwd(y_all[te]),
                          f["test_group"][te], units[te], dict(task["cfg"], skip_gcv=True), seed=0, A_fixed=int(fi.loc[f["name"], "A"]))
        sp = ctx.split
        s_cal = np.abs(ctx.ytr[sp["cal"]] - sp["cal_pred"])
        Fc0 = np.c_[sp["dcal"]["scores"], np.log(sp["dcal"]["Q"] / sp["Qref"])]
        Ft0 = np.c_[sp["dte"]["scores"], np.log(sp["dte"]["Q"] / sp["Qref"])]
        gte = f["test_group"][te]; yte = y_all[te]
        for ename, C, nf in ests:
            cols = list(range(nf)) if nf else list(range(Fc0.shape[1]))
            Fc, Ft = Fc0[:, cols], Ft0[:, cols]
            mu, sd = Fc.mean(0), Fc.std(0) + 1e-12; Fc, Ft = (Fc - mu) / sd, (Ft - mu) / sd
            rng = np.random.default_rng(0)
            for g in np.unique(gte):
                it_all = np.where(gte == g)[0]
                ic = rng.choice(len(Fc), size=min(len(Fc), 20000), replace=False)
                it = rng.choice(it_all, size=min(len(it_all), 20000), replace=False)
                clf = LogisticRegression(C=C, max_iter=2000).fit(np.r_[Fc[ic], Ft[it]], np.r_[np.zeros(len(ic)), np.ones(len(it))])
                prior = len(ic) / len(it)
                wc0 = np.exp(clf.decision_function(Fc)) * prior; wt0 = np.exp(clf.decision_function(Ft[it_all])) * prior
                for cap in caps:
                    wc, wt = wc0.copy(), wt0.copy()
                    if cap is not None:
                        scl = wc.mean(); wc = np.minimum(wc / scl, cap); wt = np.minimum(wt / scl, cap)
                    o = np.argsort(s_cal); ss = s_cal[o]; cw = np.cumsum(wc[o]); tot = cw[-1] + wt
                    kq = np.searchsorted(cw, (1 - ALPHA) * tot - 1e-12, side="left")
                    q = np.where(kq >= len(ss), np.inf, ss[np.minimum(kq, len(ss) - 1)])
                    lo, hi = inv(sp["te_pred"][it_all] - q), inv(sp["te_pred"][it_all] + q)
                    fin = np.isfinite(q)
                    cov = (yte[it_all] >= lo) & (yte[it_all] <= hi)
                    ess = wc.sum() ** 2 / np.sum(wc ** 2)
                    rows.append(dict(task=a.task, fold=f["name"], group=g, estimator=ename, cap="none" if cap is None else cap,
                                     coverage=float(cov.mean()), finite_frac=float(fin.mean()),
                                     interval_score=float(np.mean(interval_score(yte[it_all], lo, hi, ALPHA))),
                                     width_finite=float(np.mean((hi - lo)[fin])) if fin.any() else np.inf,
                                     ess_frac=float(ess / len(wc)), test_mass_median=float(np.median(wt / (wc.sum() + wt))),
                                     test_mass_gt_alpha=float(np.mean(wt / (wc.sum() + wt) > ALPHA)),
                                     clf_auc=float(__import__("sklearn.metrics", fromlist=["roc_auc_score"]).roc_auc_score(
                                         np.r_[np.zeros(len(ic)), np.ones(len(it))], clf.decision_function(np.r_[Fc[ic], Ft[it]])))))
        log.info(f"wcp {a.task} fold {f['name']} done")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, f"wcp_variants_{a.task}.csv"), index=False)
else:
    raise ValueError(a.exp)
log.info("done")
