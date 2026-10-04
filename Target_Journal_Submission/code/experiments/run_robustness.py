"""E4 robustness and E7 sensitivity experiments.

  --exp groups     number of calibration groups K ∈ {3,5,10,20} (mango_instrument, ossl_lucas_block)
  --exp size       fraction of training units ∈ {0.1,0.25,0.5} (mango_season_loso)
  --exp perturb    test-time spectral perturbations simulating instrument drift (mango_season_loso)
  --exp sensitivity  nLV offset, difficulty features, floor, preprocessing, number of group folds
"""
import argparse, copy, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from scipy.interpolate import interp1d
from src.evaluation.engine import run_task
from src.evaluation.tasks import get_task
from src.preprocessing.spectral import preprocess
from src.utils import RESULTS, get_logger, set_seed

p = argparse.ArgumentParser()
p.add_argument("--exp", required=True)
p.add_argument("--task", default=None)
p.add_argument("--quick", action="store_true")
a = p.parse_args()
out = os.path.join(RESULTS, "robustness"); os.makedirs(out, exist_ok=True)
log = get_logger(f"robust_{a.exp}_{a.task}")
A01 = [0.1]


def subset_task(task, keep_idx_fn, tag):
    t = dict(task); t["folds"] = []
    for f in task["folds"]:
        g = dict(f); g["train"] = keep_idx_fn(f); g["name"] = f["name"]
        t["folds"].append(g)
    return t


if a.exp == "groups":
    methods = ["SCP", "CV+", "G-W-A", "GC-D", "HJ+", "HCP-D", "ORACLE"]
    for tname in ([a.task] if a.task else ["mango_instrument", "ossl_lucas_block"]):
        task = get_task(tname)
        folds = task["folds"][:3] if a.quick else task["folds"]
        for K in [3, 5, 10, 20]:
            for rep in ([0] if a.quick else [0, 1, 2]):
                rng = np.random.default_rng(100 * K + rep)
                t = dict(task); t["folds"] = []
                for f in folds:
                    tr = f["train"]; g = f["calib_group"][tr]
                    ug = np.unique(g)
                    if K > len(ug):
                        continue
                    keep = rng.choice(ug, size=K, replace=False)
                    h = dict(f); h["train"] = tr[np.isin(g, keep)]
                    t["folds"].append(h)
                df = run_task(t, tname, methods, A01, rep, os.path.join(out, "tmp"), log=log.info, store_points=False, resume=False)
                df["K"] = K; df["rep"] = rep
                df.to_csv(os.path.join(out, f"groups_{tname}_K{K}_rep{rep}.csv"), index=False)

elif a.exp == "size":
    methods = ["SCP", "CV+", "ASTM-R", "G-W-A", "GC-D", "ORACLE"]
    task = get_task("mango_season_loso")
    units = task["ds"].meta.unit.to_numpy()
    for frac in [0.1, 0.25, 0.5]:
        for rep in ([0] if a.quick else [0, 1, 2]):
            rng = np.random.default_rng(int(frac * 1000) + rep)
            t = dict(task); t["folds"] = []
            for f in (task["folds"][:2] if a.quick else task["folds"]):
                tr = f["train"]; uu = np.unique(units[tr])
                ku = rng.choice(uu, size=max(10, int(frac * len(uu))), replace=False)
                h = dict(f); h["train"] = tr[np.isin(units[tr], ku)]; t["folds"].append(h)
            df = run_task(t, "mango_season_loso", methods, A01, rep, os.path.join(out, "tmp"), log=log.info, store_points=False, resume=False)
            df["frac"] = frac; df["rep"] = rep
            df.to_csv(os.path.join(out, f"size_frac{frac}_rep{rep}.csv"), index=False)

elif a.exp == "perturb":
    methods = ["SCP", "CV+", "ASTM-R", "WCP", "G-W-A", "GC-D", "ORACLE"]
    task = get_task("mango_season_loso")
    ds = task["ds"]; raw = ds.X.astype(float); wl = ds.wl
    sd_ref = np.median(raw.std(0))
    def pert(Xr, kind, lev, rng):
        if kind == "noise":
            return Xr + rng.normal(scale=lev * sd_ref, size=Xr.shape)
        if kind == "gain":
            return Xr * (1 + lev)
        if kind == "offset_slope":   # additive linear baseline tilt across the window
            return Xr + lev * sd_ref * (wl - wl.min()) / (wl.max() - wl.min())
        if kind == "wl_shift":       # wavelength-axis shift by lev nm (linear interpolation)
            return interp1d(wl, Xr, axis=1, bounds_error=False, fill_value="extrapolate")(wl - lev)
        raise ValueError(kind)
    grid = [("none", 0.0), ("noise", 0.01), ("noise", 0.03), ("noise", 0.1), ("gain", 0.02), ("gain", 0.05),
            ("offset_slope", 0.5), ("offset_slope", 2.0), ("wl_shift", 0.5), ("wl_shift", 1.0), ("wl_shift", 2.0)]
    if a.quick:
        grid = grid[:2]
    for kind, lev in grid:
        rng = np.random.default_rng(0)
        dfs = []
        for f in (task["folds"][:2] if a.quick else task["folds"]):
            # perturb ONLY the test spectra of this fold; the training spectra stay untouched
            te = f["test"]
            Xp = task["X"].copy()
            Xp[te] = preprocess(pert(raw[te], kind, lev, rng) if kind != "none" else raw[te], task["recipe"])
            assert np.array_equal(Xp[f["train"]], task["X"][f["train"]])
            dfs.append(run_task(task, "mango_season_loso", methods, A01, 0, os.path.join(out, "tmp"), log=log.info,
                                store_points=False, resume=False, X_override=Xp, fold_filter=[f["name"]]))
        df = pd.concat(dfs, ignore_index=True)
        df["perturbation"] = kind; df["level"] = lev
        df.to_csv(os.path.join(out, f"perturb_{kind}_{lev}.csv"), index=False)

elif a.exp == "sensitivity":
    methods = ["SCP", "R-U-D", "G-W-A", "GC-D"]
    variants = [("A_offset", -4), ("A_offset", 4), ("diag_mode", "T2"), ("diag_mode", "Q"),
                ("floor_frac", 0.02), ("floor_frac", 0.3)]
    for tname in ([a.task] if a.task else ["mango_season_loso", "ossl_lucas_block"]):
        task = get_task(tname)
        if a.quick:
            task["folds"] = task["folds"][:2]
        for key, val in variants:
            t = dict(task); t["cfg"] = dict(task["cfg"]); t["cfg"][key] = val
            df = run_task(t, tname, methods, A01, 0, os.path.join(out, "tmp"), log=log.info, store_points=False, resume=False)
            df["variant"] = f"{key}={val}"
            df.to_csv(os.path.join(out, f"sens_{tname}_{key}_{val}.csv"), index=False)
        if tname.startswith("mango"):
            alt = [("snv", {}), ("savgol", {"window": 13, "poly": 2, "deriv": 1})]
            Xa = preprocess(task["ds"].X, alt).astype(np.float32)
            df = run_task(task, tname, methods, A01, 0, os.path.join(out, "tmp"), log=log.info, store_points=False, resume=False, X_override=Xa)
            df["variant"] = "preprocessing=SNV+SG1"
            df.to_csv(os.path.join(out, f"sens_{tname}_preproc_snvsg1.csv"), index=False)
elif a.exp == "sens_popfolds":
    methods = ["SCP", "R-U-D", "G-W-A", "GC-D"]
    if True:
        task = get_task("mango_population")
        if a.quick:
            task["folds"] = task["folds"][:1]
        for gf in [5, 20]:
            t = dict(task); t["cfg"] = dict(task["cfg"]); t["cfg"]["group_folds"] = gf
            df = run_task(t, "mango_population", methods, A01, 0, os.path.join(out, "tmp"), log=log.info, store_points=False, resume=False)
            df["variant"] = f"group_folds={gf}"
            df.to_csv(os.path.join(out, f"sens_mango_population_groupfolds_{gf}.csv"), index=False)
else:
    raise ValueError(a.exp)
log.info("done")
