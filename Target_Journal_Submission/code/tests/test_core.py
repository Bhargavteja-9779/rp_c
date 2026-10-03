import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pytest
from src.conformal.core import weighted_quantile, split_conformal_quantile, jackknife_plus_interval
from src.training.crossfit import make_folds, group_balanced_weights
from src.models.pls import PLS1


def test_weighted_quantile_uniform_matches_split():
    rng = np.random.default_rng(0)
    s = rng.normal(size=99)
    w = np.ones(99)
    q1 = weighted_quantile(s, w, 0.9, inf_mass=1.0)
    q2 = split_conformal_quantile(s, 0.1)
    assert q1 == q2


def test_weighted_quantile_inf():
    assert np.isinf(weighted_quantile(np.arange(5.0), np.ones(5), 0.9, inf_mass=1.0))


def _brute_jplus(mu, sig, scores, fid, w, alpha, inf_mass):
    vals_up, vals_lo, ww = [], [], []
    for i in range(len(scores)):
        k = fid[i]
        vals_up.append(mu[k] + sig[k] * scores[i]); vals_lo.append(mu[k] - sig[k] * scores[i]); ww.append(w[i])
    vals_up = np.array(vals_up); vals_lo = np.array(vals_lo); ww = np.array(ww)
    out_lo, out_hi = [], []
    for j in range(mu.shape[1]):
        out_hi.append(weighted_quantile(vals_up[:, j], ww, 1 - alpha, inf_mass))
        out_lo.append(-weighted_quantile(-vals_lo[:, j], ww, 1 - alpha, inf_mass))
    return np.array(out_lo), np.array(out_hi)


def test_jackknife_plus_matches_bruteforce():
    rng = np.random.default_rng(1)
    K, m, n = 4, 7, 60
    mu = rng.normal(size=(K, m)); sig = rng.uniform(0.5, 2, size=(K, m))
    scores = np.abs(rng.normal(size=n)); fid = np.arange(n) % K; w = rng.uniform(0.5, 1.5, n)
    lo, hi = jackknife_plus_interval(mu, sig, scores, fid, w, 0.1, inf_mass=0.3)
    blo, bhi = _brute_jplus(mu, sig, scores, fid, w, 0.1, 0.3)
    np.testing.assert_allclose(hi, bhi, atol=1e-6)
    np.testing.assert_allclose(lo, blo, atol=1e-6)


def test_folds_are_unit_disjoint():
    groups = np.array(["a", "a", "b", "b", "c", "c"])
    units = np.array(["u1", "u2", "u1", "u3", "u4", "u2"])  # u1, u2 shared across groups
    for tr, te in make_folds(groups, units, "group"):
        assert not set(units[tr]) & set(units[te])
    for tr, te in make_folds(groups, units, "group_unitfold", n_unit_folds=2, seed=0):
        assert not set(units[tr]) & set(units[te])
        assert len(set(groups[te])) == 1 and not set(groups[tr]) & set(groups[te])


def test_group_weights_sum():
    w = group_balanced_weights(np.array(list("aaabbc")))
    assert abs(w.sum() - 1) < 1e-12
    assert abs(w[:3].sum() - 1 / 3) < 1e-12


def test_split_conformal_coverage_exchangeable():
    rng = np.random.default_rng(2)
    covs = []
    for r in range(300):
        s = np.abs(rng.normal(size=50)); t = np.abs(rng.normal())
        covs.append(t <= split_conformal_quantile(s, 0.1))
    assert 0.86 <= np.mean(covs) <= 0.96


def test_hierarchical_split_coverage_new_group():
    """Group-balanced quantile with +inf mass covers a new group's point at >= 1-alpha on a
    random-effects model (scores = |b_g + e|), while pooling with uniform weights over large,
    unequal groups is not guaranteed."""
    rng = np.random.default_rng(3)
    hits = []
    for r in range(400):
        K = 15
        sizes = rng.integers(5, 200, K)
        b = rng.normal(scale=2.0, size=K + 1)
        s = np.concatenate([np.abs(b[k] + rng.normal(size=sizes[k])) for k in range(K)])
        g = np.repeat(np.arange(K), sizes)
        w = np.array([1.0 / ((K + 1) * sizes[k]) for k in g])
        q = weighted_quantile(s, w, 0.9, inf_mass=1.0 / (K + 1))
        hits.append(np.abs(b[K] + rng.normal()) <= q)
    assert np.mean(hits) >= 0.87


def test_pls_diagnostics_shapes():
    rng = np.random.default_rng(4)
    X = rng.normal(size=(50, 10)); y = X[:, 0] + 0.1 * rng.normal(size=50)
    m = PLS1(5).fit(X, y).set_n_lv(3)
    d = m.diagnostics(X)
    assert d["T2"].shape == (50,) and (d["Q"] >= 0).all() and (d["h"] > 0).all()
