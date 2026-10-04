"""Deployment-shift tasks. Each task yields outer folds: (name, train_idx, test_idx, group arrays).

``calib_group``  : grouping of TRAINING spectra used for out-of-group calibration (deployment level).
``test_group``   : grouping of TEST spectra used to report per-group results.
All outer splits are unit-disjoint: no physical sample appears in both training and test.
"""
from __future__ import annotations

import numpy as np

from ..data import loaders as L
from ..preprocessing.spectral import preprocess

RECIPES = {
    # fixed a priori, not tuned on test data
    "mango": [("savgol", {"window": 13, "poly": 2, "deriv": 2})],
    "ossl": [("savgol", {"window": 11, "poly": 2, "deriv": 1})],
    "corn": [("snv", {}), ("savgol", {"window": 15, "poly": 2, "deriv": 1})],
    "tablets": [("snv", {}), ("savgol", {"window": 15, "poly": 2, "deriv": 1})],
}


def _ud(train_mask, units, test_mask):
    """Remove from training every unit that appears in the test set."""
    return train_mask & ~np.isin(units, np.unique(units[test_mask]))


def get_task(name, quick=False, seed=0):
    """Returns dict(ds, X (preprocessed), folds=[dict(name, train, test, calib_group, test_group)], cfg)."""
    rng = np.random.default_rng(seed)
    if name.startswith("mango"):
        ds = L.load_mango()
        X = preprocess(ds.X, RECIPES["mango"]).astype(np.float32)
        m = ds.meta
        units = m["unit"].to_numpy()
        folds = []
        if name == "mango_season_loso":
            for s in sorted(m.season.unique()):
                te = (m.season == s).to_numpy()
                folds.append(dict(name=f"season{s}", train=np.where(_ud(~te, units, te))[0], test=np.where(te)[0],
                                  calib_group=m.season.astype(str).to_numpy(), test_group=m.season.astype(str).to_numpy()))
            cfg = dict(A_max=20, group_mode="group")
        elif name == "mango_season_forward":
            for s in sorted(m.season.unique())[2:]:
                te = (m.season == s).to_numpy(); tr = (m.season < s).to_numpy()
                folds.append(dict(name=f"season{s}", train=np.where(tr)[0], test=np.where(te)[0],
                                  calib_group=m.season.astype(str).to_numpy(), test_group=m.season.astype(str).to_numpy()))
            cfg = dict(A_max=20, group_mode="group")
        elif name == "mango_instrument":
            fr = m.groupby("instrument").unit.nunique()
            insts = sorted(fr[fr >= 300].index)
            for ins in insts:
                te = (m.instrument == ins).to_numpy()
                folds.append(dict(name=f"inst{ins}", train=np.where(_ud(~te, units, te))[0], test=np.where(te)[0],
                                  calib_group=m.instrument.to_numpy(), test_group=m.instrument.to_numpy()))
            cfg = dict(A_max=20, group_mode="group")
        elif name == "mango_population":
            pops = m.population.unique()
            perm = rng.permutation(len(pops))
            for j in range(10):
                tp = pops[perm[j::10]]
                te = m.population.isin(tp).to_numpy()
                folds.append(dict(name=f"popfold{j}", train=np.where(_ud(~te, units, te))[0], test=np.where(te)[0],
                                  calib_group=m.population.to_numpy(), test_group=m.population.to_numpy()))
            cfg = dict(A_max=20, group_mode="group", group_folds=10)
        elif name == "mango_cultivar":
            # reviewer-requested external-validity test: an unseen cultivar (10 cultivars, leave-one-out)
            for cv in sorted(m.cultivar.unique()):
                te = (m.cultivar == cv).to_numpy()
                folds.append(dict(name=f"cultivar_{cv}", train=np.where(_ud(~te, units, te))[0], test=np.where(te)[0],
                                  calib_group=m.cultivar.to_numpy(), test_group=m.cultivar.to_numpy()))
            cfg = dict(A_max=20, group_mode="group")
        else:
            raise ValueError(name)
        recipe = RECIPES["mango"]
    elif name.startswith("ossl"):
        if name == "ossl_lucas_block":
            ds = L.load_ossl("LUCAS.SSL")
            m = ds.meta
            ok = (m.block != "-1").to_numpy()
            units = m["unit"].to_numpy()
            folds = []
            for b in sorted(m.block[ok].unique(), key=int):
                te = (m.block == b).to_numpy()
                tr = ok & ~te
                folds.append(dict(name=f"block{b}", train=np.where(_ud(tr, units, te))[0], test=np.where(te)[0],
                                  calib_group=m.block.to_numpy(), test_group=m.block.to_numpy()))
            cfg = dict(A_max=25, group_mode="group", log_target=True)
        elif name == "ossl_lucas_campaign":
            ds = L.load_ossl("LUCAS.SSL")
            m = ds.meta
            ok = (m.block != "-1").to_numpy()
            units = m["unit"].to_numpy()
            camps = sorted(m.campaign.unique())
            folds = []
            for c in camps:
                te = (m.campaign == c).to_numpy() & ok
                tr = ok & ~te
                folds.append(dict(name=f"campaign{c}", train=np.where(_ud(tr, units, te))[0], test=np.where(te)[0],
                                  calib_group=m.block.to_numpy(), test_group=(m.campaign + "_b" + m.block).to_numpy()))
            cfg = dict(A_max=25, group_mode="group", log_target=True)
        elif name == "ossl_kssl_to_lucas":
            # cross-library / cross-instrument / cross-continent stress test: train KSSL, test LUCAS
            k = L.load_ossl("KSSL.SSL"); lu = L.load_ossl("LUCAS.SSL")
            import pandas as pd
            mk = k.meta.assign(lib="KSSL"); ml = lu.meta.assign(lib="LUCAS")
            ds = L.SpectralDataset("ossl_kssl_lucas", np.vstack([k.X, lu.X]), np.r_[k.y, lu.y], k.wl,
                                   pd.concat([mk, ml], ignore_index=True), "organic carbon", "% w/w")
            m = ds.meta
            tr = (m.lib == "KSSL").to_numpy()   # KSSL calibration groups = survey projects (84)
            te = ((m.lib == "LUCAS") & (m.block != "-1")).to_numpy()
            cg = np.where(m.lib == "KSSL", "K_" + m.project, "L_" + m.block)
            folds = [dict(name="KSSL_to_LUCAS", train=np.where(tr)[0], test=np.where(te)[0],
                          calib_group=cg, test_group=("L" + m.block).to_numpy())]
            cfg = dict(A_max=25, group_mode="group", log_target=True)
        else:
            raise ValueError(name)
        X = preprocess(ds.X, RECIPES["ossl"]).astype(np.float32)
        recipe = RECIPES["ossl"]
    elif name.startswith("corn"):
        prop = name.split("_")[1]
        ds = L.load_corn(prop)
        X = preprocess(ds.X, RECIPES["corn"]).astype(np.float32)
        m = ds.meta
        units = m["unit"].to_numpy()
        folds = []
        n_rep = 2 if quick else 10
        for ins in ["m5", "mp5", "mp6"]:
            for r in range(n_rep):
                uu = np.unique(units)
                test_units = np.random.default_rng(1000 * r + 7).choice(uu, size=20, replace=False)
                te = (m.instrument == ins).to_numpy() & np.isin(units, test_units)
                tr = (m.instrument != ins).to_numpy() & ~np.isin(units, test_units)
                folds.append(dict(name=f"{ins}_rep{r}", train=np.where(tr)[0], test=np.where(te)[0],
                                  calib_group=m.instrument.to_numpy(), test_group=np.array([f"{ins}_rep{r}"] * len(m))))
        cfg = dict(A_max=15, group_mode="group_unitfold", n_unit_folds=5, random_folds=5)
        recipe = RECIPES["corn"]
    elif name.startswith("tablets"):
        ds = L.load_tablets("assay")
        X = preprocess(ds.X, RECIPES["tablets"]).astype(np.float32)
        m = ds.meta
        tr = m.partition.isin(["calibrate", "validate"]).to_numpy() & (m.instrument == "1").to_numpy()
        folds = []
        for ins in ["1", "2"]:
            te = (m.partition == "test").to_numpy() & (m.instrument == ins).to_numpy()
            folds.append(dict(name=f"cal1_test{ins}", train=np.where(tr)[0], test=np.where(te)[0],
                              calib_group=m.unit.to_numpy(), test_group=np.array([f"inst{ins}"] * len(m))))
        cfg = dict(A_max=15, group_mode="group", group_folds=5, random_folds=5)
        recipe = RECIPES["tablets"]
    else:
        raise ValueError(name)
    return dict(ds=ds, X=X, folds=folds, cfg=cfg, recipe=recipe)
