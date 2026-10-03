"""Cross-fitting utilities: fold construction (group-wise, unit-disjoint) and out-of-fold PLS fits.

Leakage rule enforced everywhere: a physical sample (``unit``: fruit, soil sample, tablet, corn
sample) never contributes to the training set of a model that is evaluated on any spectrum of
that same unit.
"""
from __future__ import annotations

import numpy as np

from ..models.pls import PLS1


def _unit_disjoint_train(train_mask, units, test_idx):
    test_units = np.unique(units[test_idx])
    return train_mask & ~np.isin(units, test_units)


def make_folds(groups, units, mode="group", n_folds=None, n_unit_folds=5, seed=0):
    """Return a list of (train_idx, test_idx).

    mode = "group"          each group (or each set of groups when ``n_folds`` < #groups) is held
                            out; training excludes every unit that appears in the held-out set.
    mode = "group_unitfold" for groups that share units (e.g. the same corn samples measured on
                            every instrument): held-out = (group g) ∩ (unit fold v),
                            training = (groups ≠ g) ∩ (units ∉ fold v).
    mode = "random"         unit-grouped random K-fold (K = ``n_folds`` or 5), ignoring groups.
    """
    groups = np.asarray(groups).astype(str)
    units = np.asarray(units).astype(str)
    n = len(groups)
    rng = np.random.default_rng(seed)
    folds = []
    if mode == "random":
        k = n_folds or 5
        uu = np.unique(units)
        perm = rng.permutation(len(uu))
        fold_of_unit = dict(zip(uu[perm], np.arange(len(uu)) % k))
        f = np.array([fold_of_unit[u] for u in units])
        for j in range(k):
            te = np.where(f == j)[0]
            tr = np.where(f != j)[0]
            folds.append((tr, te))
        return folds
    ug = np.unique(groups)
    if mode == "group":
        if n_folds is None or n_folds >= len(ug):
            gsets = [[g] for g in ug]
        else:
            perm = rng.permutation(len(ug))
            gsets = [list(ug[perm[j::n_folds]]) for j in range(n_folds)]
        for gs in gsets:
            te_mask = np.isin(groups, gs)
            te = np.where(te_mask)[0]
            tr = np.where(_unit_disjoint_train(~te_mask, units, te))[0]
            folds.append((tr, te))
        return folds
    if mode == "group_unitfold":
        uu = np.unique(units)
        perm = rng.permutation(len(uu))
        fold_of_unit = dict(zip(uu[perm], np.arange(len(uu)) % n_unit_folds))
        uf = np.array([fold_of_unit[u] for u in units])
        for g in ug:
            for v in range(n_unit_folds):
                te = np.where((groups == g) & (uf == v))[0]
                if len(te) == 0:
                    continue
                tr = np.where((groups != g) & (uf != v))[0]
                folds.append((tr, te))
        return folds
    raise ValueError(mode)


class CrossFit:
    """Out-of-fold PLS predictions for 1..A_max latent variables, plus per-fold models."""

    def __init__(self, X, y, folds, A_max=20):
        self.X, self.y, self.folds, self.A_max = X, y, folds, A_max
        n = len(y)
        self.oof = np.full((n, A_max), np.nan)
        self.fold_id = np.full(n, -1)
        self.models = []
        for j, (tr, te) in enumerate(folds):
            m = PLS1(A_max).fit(X[tr], y[tr])
            P = m.predict_all(X[te])
            if P.shape[1] < A_max:  # pad if fewer LVs were extractable
                P = np.c_[P, np.repeat(P[:, -1:], A_max - P.shape[1], 1)]
            self.oof[te] = P
            self.fold_id[te] = j
            self.models.append(m)
        self.covered = self.fold_id >= 0

    def rmse_curve(self, weights=None):
        c = self.covered
        r2 = (self.oof[c] - self.y[c, None]) ** 2
        w = np.ones(c.sum()) if weights is None else weights[c]
        return np.sqrt((r2 * w[:, None]).sum(0) / w.sum())

    def choose_A(self, weights=None, one_se=False):
        curve = self.rmse_curve(weights)
        return int(np.argmin(curve)) + 1, curve

    def oof_at(self, A):
        return self.oof[:, A - 1]

    def oof_diagnostics(self, A):
        n = len(self.y)
        T2 = np.full(n, np.nan); Q = np.full(n, np.nan)
        for j, (tr, te) in enumerate(self.folds):
            d = self.models[j].diagnostics(self.X[te], A)
            T2[te], Q[te] = d["T2"], d["Q"]
        return T2, Q

    def fold_predict(self, Xnew, A):
        """μ_{-k}(x) and diagnostics for every fold model k; arrays of shape (K, m)."""
        mu = np.stack([m.predict(Xnew, A) for m in self.models])
        T2 = []; Q = []
        for m in self.models:
            d = m.diagnostics(Xnew, A)
            T2.append(d["T2"]); Q.append(d["Q"])
        return mu, np.stack(T2), np.stack(Q)


def group_balanced_weights(groups):
    """w_i = 1 / (K · N_g(i)) so that every group carries the same total mass 1/K."""
    groups = np.asarray(groups).astype(str)
    ug, inv, cnt = np.unique(groups, return_inverse=True, return_counts=True)
    return 1.0 / (len(ug) * cnt[inv])
