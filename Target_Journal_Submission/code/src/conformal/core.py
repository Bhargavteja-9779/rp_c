"""Conformal building blocks: weighted quantiles, difficulty (scale) models, jackknife+-type intervals."""
from __future__ import annotations

import numpy as np
from sklearn.linear_model import PoissonRegressor
from sklearn.neighbors import NearestNeighbors


def weighted_quantile(scores, weights, level, inf_mass=0.0):
    """Smallest t such that  Σ_i w_i 1{s_i ≤ t} ≥ level · (Σ_i w_i + inf_mass).

    ``inf_mass`` is a point mass placed at +∞ (finite-sample correction). Returns +inf if the level
    cannot be reached with finite scores."""
    s = np.asarray(scores, float)
    w = np.asarray(weights, float)
    o = np.argsort(s)
    s, w = s[o], w[o]
    tot = w.sum() + inf_mass
    cw = np.cumsum(w) / tot
    k = np.searchsorted(cw, level - 1e-12, side="left")
    return np.inf if k >= len(s) else s[k]


def split_conformal_quantile(scores, alpha):
    """Standard split-conformal quantile: the ⌈(n+1)(1−α)⌉-th smallest score."""
    s = np.sort(np.asarray(scores, float))
    n = len(s)
    k = int(np.ceil((n + 1) * (1 - alpha)))
    return np.inf if k > n else s[k - 1]


# ---------------------------------------------------------------------------------------------
# Difficulty (scale) models σ(x)
# ---------------------------------------------------------------------------------------------
def diag_features(T2, Q, q_ref, mode="both"):
    """z = [log(1 + T²), log(Q / Q_ref)] — Q_ref is the median training Q of the same model.
    ``mode`` ∈ {"both", "T2", "Q"} (sensitivity analysis)."""
    z1 = np.log1p(np.maximum(T2, 0))
    z2 = np.log(np.maximum(Q, 1e-300) / q_ref)
    if mode == "T2":
        return z1[:, None]
    if mode == "Q":
        return z2[:, None]
    return np.c_[z1, z2]


class DiagnosticScale:
    """σ(x) = exp(β₀ + β₁ log(1+T²) + β₂ log(Q/Q_ref)), fitted as a log-link GLM (Poisson
    quasi-likelihood) of |residual| on the PLS diagnostics of out-of-sample predictions.
    A floor of ``floor_frac`` × median fitted σ prevents division by near-zero scales."""

    def __init__(self, floor_frac=0.1):
        self.floor_frac = floor_frac

    def fit(self, Z, abs_res, sample_weight=None):
        ok = np.isfinite(Z).all(1) & np.isfinite(abs_res)
        self.scale_ = np.mean(abs_res[ok])
        self.glm = PoissonRegressor(alpha=0.0, max_iter=300)
        self.glm.fit(Z[ok], abs_res[ok] / self.scale_, sample_weight=None if sample_weight is None else sample_weight[ok])
        self.floor_ = self.floor_frac * np.median(self._raw(Z[ok]))
        return self

    def _raw(self, Z):
        return self.glm.predict(Z) * self.scale_

    def predict(self, Z):
        return np.maximum(self._raw(Z), self.floor_)


class KNNScale:
    """Papadopoulos-type normalisation: σ(x) = β + mean |r| of the k nearest calibration-model
    training points in standardised PLS-score space (|r| = out-of-fold residuals)."""

    def __init__(self, k=20, beta_frac=0.1):
        self.k, self.beta_frac = k, beta_frac

    def fit(self, S, abs_res):
        self.mu, self.sd = S.mean(0), S.std(0) + 1e-12
        self.nn = NearestNeighbors(n_neighbors=self.k).fit((S - self.mu) / self.sd)
        self.r = abs_res
        self.beta = self.beta_frac * np.median(abs_res)
        return self

    def predict(self, S):
        idx = self.nn.kneighbors((S - self.mu) / self.sd, return_distance=False)
        return self.r[idx].mean(1) + self.beta


# ---------------------------------------------------------------------------------------------
# Jackknife+ / CV+ type intervals (mixture quantiles), with optional group weights and scaling
# ---------------------------------------------------------------------------------------------
def _mixture_quantile(mu, sig, fold_scores, fold_weights, level, inf_mass, upper=True, iters=60):
    """For each test point solve  Σ_k Σ_{i∈k} w_i 1{μ_k ± σ_k S_i ≤ t} ≥ level·(Σw + inf_mass).

    mu, sig: (K, m) fold-specific centres and scales at the test points.
    fold_scores[k]: sorted scores S_i of fold k; fold_weights[k]: matching cumulative weights."""
    K, m = mu.shape
    tot = sum(fw[-1] for fw in fold_weights if len(fw)) + inf_mass
    smax = max(fs[-1] for fs in fold_scores if len(fs))
    lo = (mu - sig * smax).min(0) - 1.0
    hi = (mu + sig * smax).max(0) + 1.0
    target = level * tot

    def F(t):  # weighted count of {values ≤ t}
        c = np.zeros(m)
        for k in range(K):
            fs, fw = fold_scores[k], fold_weights[k]
            if len(fs) == 0:
                continue
            if upper:   # values μ_k + σ_k S ≤ t  ⇔  S ≤ (t − μ_k)/σ_k
                thr = (t - mu[k]) / sig[k]
                j = np.searchsorted(fs, thr, side="right")
            else:       # values μ_k − σ_k S ≤ t  ⇔  S ≥ (μ_k − t)/σ_k
                thr = (mu[k] - t) / sig[k]
                j0 = np.searchsorted(fs, thr, side="left")
                c += fw[-1] - np.where(j0 > 0, fw[np.maximum(j0 - 1, 0)], 0.0)
                continue
            c += np.where(j > 0, fw[np.maximum(j - 1, 0)], 0.0)
        return c

    if upper and (sum(fw[-1] for fw in fold_weights if len(fw)) < target - 1e-12):
        return np.full(m, np.inf)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        ok = F(mid) >= target - 1e-12
        hi = np.where(ok, mid, hi)
        lo = np.where(ok, lo, mid)
    return hi


def jackknife_plus_interval(mu_folds, sig_folds, scores, fold_id, weights, alpha, inf_mass=0.0):
    """Generalised (hierarchical, scaled) jackknife+ interval.

    lower = Q'_α { μ_{-k(i)}(x) − σ_{-k(i)}(x) S_i },  upper = Q_{1−α} { μ_{-k(i)}(x) + σ_{-k(i)}(x) S_i }
    with weights w_i and a point mass ``inf_mass`` at ±∞ (Lee, Barber & Willett, eq. 20, when σ ≡ 1)."""
    K = mu_folds.shape[0]
    fs, fw = [], []
    for k in range(K):
        sel = fold_id == k
        s = scores[sel]; w = weights[sel]
        o = np.argsort(s)
        fs.append(s[o]); fw.append(np.cumsum(w[o]))
    up = _mixture_quantile(mu_folds, sig_folds, fs, fw, 1 - alpha, inf_mass, upper=True)
    # lower bound: −Q_{1−α}{ −(μ − σS) }  computed on the negated problem
    lo = -_mixture_quantile(-mu_folds, sig_folds, fs, fw, 1 - alpha, inf_mass, upper=True)
    return lo, up
