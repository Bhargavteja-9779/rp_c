"""Synthetic study of finite-K behaviour (reviewer request R4.1 / R1.19).

Hierarchical model:  y_ij = x_ij'β + b_g + ε_ij,  x_ij ~ N(μ_g, I_p),  μ_g ~ N(0, s_x² I_p),  b_g ~ N(0, τ²),
ε_ij ~ N(0, σ²(1 + ||x_ij − μ̄||² / p)) (heteroscedastic), σ = 1. A least-squares model is fitted on K calibration groups
and deployed on a new group drawn from the same hierarchy. Calibration of the 1−α interval ŷ ± q:
  SCP      random 75/25 split of the calibration observations (absolute residuals),
  GC-A     leave-one-group-out residuals of the cross-fitted model, group-balanced weights (centre: full model),
  GC-A+    GC-A with the finite-sample point mass 1/(K+1) at +∞ (unbounded when K + 1 ≤ 1/α).
The point predictor is deliberately simple: the study isolates the calibration step. For every setting, R deployments
give the distribution of the coverage attained in a single new group.
Output: results/revision/simulation_finiteK.csv (one row per setting) and simulation_finiteK_raw.parquet.
"""
import os, sys, itertools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from src.conformal.core import weighted_quantile
from src.utils import RESULTS

OUT = os.path.join(RESULTS, "revision"); os.makedirs(OUT, exist_ok=True)
P, N_NEW, SX = 10, 200, 1.0
R = int(os.environ.get("SIM_R", 1000))


def draw_group(rng, n, beta, tau):
    mu = rng.normal(0, SX, P)
    X = mu + rng.normal(size=(n, P))
    sd = np.sqrt(1 + np.sum(X ** 2, 1) / P)
    return X, X @ beta + rng.normal(0, tau) + rng.normal(size=n) * sd


def one(rng, K, alpha, tau, balance):
    beta = rng.normal(size=P)
    sizes = np.full(K, 50) if balance == "balanced" else np.maximum(5, np.round(50 * rng.lognormal(0, 1.0, K) / np.exp(0.5))).astype(int)
    G = [draw_group(rng, n, beta, tau) for n in sizes]
    X = np.vstack([g[0] for g in G]); y = np.concatenate([g[1] for g in G]); gid = np.repeat(np.arange(K), sizes)
    X1 = np.c_[np.ones(len(y)), X]
    XtX, Xty = X1.T @ X1, X1.T @ y
    b_full = np.linalg.solve(XtX, Xty)
    Xn, yn = draw_group(rng, N_NEW, beta, tau)
    yhat_n = np.c_[np.ones(N_NEW), Xn] @ b_full
    out = {}
    # SCP: random split of observations
    cal = rng.random(len(y)) < 0.25
    b_sp = np.linalg.lstsq(X1[~cal], y[~cal], rcond=None)[0]
    s = np.sort(np.abs(y[cal] - X1[cal] @ b_sp)); k = int(np.ceil((len(s) + 1) * (1 - alpha)))
    q = s[min(k, len(s)) - 1] if k <= len(s) else np.inf
    out["SCP"] = np.mean(np.abs(yn - np.c_[np.ones(N_NEW), Xn] @ b_sp) <= q)
    # GC-A: leave-one-group-out residuals (rank-one block downdates of the normal equations)
    r = np.empty(len(y))
    for g in range(K):
        m = gid == g
        Xg = X1[m]
        bg = np.linalg.lstsq(XtX - Xg.T @ Xg, Xty - Xg.T @ y[m], rcond=None)[0]
        r[m] = y[m] - Xg @ bg
    w = 1.0 / (K * sizes[gid])
    q = weighted_quantile(np.abs(r), w, 1 - alpha)
    out["GC-A"] = np.mean(np.abs(yn - yhat_n) <= q)
    inf_mass = (1.0 / (K + 1)) / (1 - 1.0 / (K + 1)) * w.sum()
    q = weighted_quantile(np.abs(r), w, 1 - alpha, inf_mass=inf_mass)
    out["GC-A+"] = np.mean(np.abs(yn - yhat_n) <= q); out["GC-A+_finite"] = float(np.isfinite(q))
    return out


rows, raw = [], []
grid = list(itertools.product([3, 5, 10, 20, 50], [0.05, 0.10, 0.20], [0.5, 1.0], ["balanced", "unbalanced"]))
for i, (K, alpha, tau, bal) in enumerate(grid):
    rng = np.random.default_rng(20261031 + i)   # deterministic per setting
    res = pd.DataFrame([one(rng, K, alpha, tau, bal) for _ in range(R)])
    for m in ["SCP", "GC-A", "GC-A+"]:
        c = res[m].to_numpy()
        # within-group (sampling) variance of a coverage proportion over N_NEW points, at the mean coverage
        within = np.mean(c * (1 - c)) / N_NEW
        rows.append(dict(K=K, alpha=alpha, tau=tau, balance=bal, method=m, mean_coverage=c.mean(), sd_coverage=c.std(),
                         p10_coverage=np.quantile(c, 0.10), share_below_nominal_minus_005=np.mean(c < 1 - alpha - 0.05),
                         between_group_var_share=max(0.0, 1 - within / max(c.var(), 1e-12)),
                         finite_frac=res["GC-A+_finite"].mean() if m == "GC-A+" else 1.0))
    res["K"], res["alpha"], res["tau"], res["balance"] = K, alpha, tau, bal
    raw.append(res)
    print(K, alpha, tau, bal, res[["SCP", "GC-A", "GC-A+"]].mean().round(3).to_dict(), flush=True)
pd.DataFrame(rows).to_csv(os.path.join(OUT, "simulation_finiteK.csv"), index=False)
pd.concat(raw).to_parquet(os.path.join(OUT, "simulation_finiteK_raw.parquet"), index=False)
