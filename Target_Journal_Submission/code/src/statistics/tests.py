"""Statistical procedures used in the paper.

Unit of analysis for method comparisons: the held-out deployment group (season, instrument,
population fold, spatial block, …). Per-group values are first averaged over seeds.
"""
from __future__ import annotations

import numpy as np
from scipy import stats

BIG = 1e9  # finite stand-in for an infinite interval score / width when ranking


def finite(x):
    x = np.asarray(x, float)
    return np.where(np.isfinite(x), x, BIG)


def wilcoxon_paired(a, b):
    """Two-sided Wilcoxon signed-rank test of a vs b (paired), with the matched-pairs
    rank-biserial correlation r = (W⁺ − W⁻)/(W⁺ + W⁻) (positive: a > b) and the median
    difference. Zero differences are dropped (Wilcoxon 'wilcox' zero method)."""
    a, b = finite(a), finite(b)
    d = a - b
    nz = d[d != 0]
    out = {"n_pairs": int(len(d)), "n_nonzero": int(len(nz)), "median_diff": float(np.median(d))}
    if len(nz) < 1:
        out.update(p=1.0, W=np.nan, r_rb=0.0)
        return out
    ranks = stats.rankdata(np.abs(nz))
    wp, wm = ranks[nz > 0].sum(), ranks[nz < 0].sum()
    out["r_rb"] = float((wp - wm) / (wp + wm))
    if len(nz) < 2:
        out.update(p=1.0, W=float(min(wp, wm)))
        return out
    res = stats.wilcoxon(nz, zero_method="wilcox", alternative="two-sided",
                         method="exact" if len(nz) <= 25 else "approx")
    out.update(p=float(res.pvalue), W=float(res.statistic))
    return out


def holm(pvals):
    """Holm–Bonferroni adjusted p-values (same order as input)."""
    p = np.asarray(pvals, float)
    m = len(p)
    o = np.argsort(p)
    adj = np.empty(m)
    run = 0.0
    for i, j in enumerate(o):
        run = max(run, (m - i) * p[j])
        adj[j] = min(1.0, run)
    return adj


def bootstrap_ci(x, stat=np.mean, n_boot=5000, level=0.95, seed=0):
    """Percentile bootstrap CI over units (e.g. held-out groups)."""
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    if len(x) < 2:
        return (float(stat(x)), float(stat(x)))
    bs = np.array([stat(x[rng.integers(0, len(x), len(x))]) for _ in range(n_boot)])
    a = (1 - level) / 2
    return float(np.quantile(bs, a)), float(np.quantile(bs, 1 - a))


def cluster_bootstrap_coverage(covered, clusters, n_boot=2000, level=0.95, seed=0):
    """CI for a coverage proportion when several spectra share one physical sample: resample
    clusters (fruit / soil sample) with replacement."""
    covered = np.asarray(covered, float)
    cl, inv = np.unique(np.asarray(clusters), return_inverse=True)
    s = np.bincount(inv, weights=covered)
    n = np.bincount(inv)
    rng = np.random.default_rng(seed)
    bs = np.empty(n_boot)
    for b in range(n_boot):
        k = rng.integers(0, len(cl), len(cl))
        bs[b] = s[k].sum() / n[k].sum()
    a = (1 - level) / 2
    return float(np.quantile(bs, a)), float(np.quantile(bs, 1 - a))
