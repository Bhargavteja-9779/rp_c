"""Experiment engine: runs interval methods on every outer fold of a task and stores
per-group summaries (CSV) and per-spectrum intervals (Parquet)."""
from __future__ import annotations

import json
import os
import time
import traceback

import numpy as np
import pandas as pd

from ..conformal.methods import METHODS, FoldContext
from .metrics import summarize_group


def run_task(task, task_name, methods, alphas, seed, out_dir, A_fixed=None, log=print,
             store_points=True, fold_filter=None, X_override=None, resume=True):
    os.makedirs(out_dir, exist_ok=True)
    ds, X, cfg = task["ds"], task["X"] if X_override is None else X_override, task["cfg"]
    y_all = ds.y.astype(float)
    log_t = cfg.get("log_target", False)
    fwd = (lambda v: np.log1p(v)) if log_t else (lambda v: v)
    inv = (lambda v: np.expm1(v)) if log_t else (lambda v: v)
    units = ds.meta["unit"].to_numpy()
    rows, points, fold_info = [], [], []
    tag = f"{task_name}_seed{seed}"
    part_dir = os.path.join(out_dir, "partial", tag)
    os.makedirs(part_dir, exist_ok=True)
    for fold in task["folds"]:
        if fold_filter and fold["name"] not in fold_filter:
            continue
        tr, te = fold["train"], fold["test"]
        if len(tr) == 0 or len(te) == 0:
            continue
        pf = os.path.join(part_dir, f"{fold['name']}")
        if resume and os.path.exists(pf + "_groups.csv"):  # fold already completed (resumable runs)
            rows.extend(pd.read_csv(pf + "_groups.csv").to_dict("records"))
            fold_info.extend(pd.read_csv(pf + "_fold.csv").to_dict("records"))
            if store_points and os.path.exists(pf + "_points.parquet"):
                points.append(pd.read_parquet(pf + "_points.parquet"))
            log(f"  [{task_name}] fold {fold['name']}: loaded from partial results")
            continue
        n_rows0, n_pts0 = len(rows), len(points)
        assert not np.intersect1d(units[tr], units[te]).size, "unit leakage between train and test"
        t0 = time.time()
        ctx = FoldContext(X[tr], fwd(y_all[tr]), fold["calib_group"][tr], units[tr],
                          X[te], fwd(y_all[te]), fold["test_group"][te], units[te], cfg, seed=seed, A_fixed=A_fixed)
        yhat = inv(ctx.yhat)
        fold_info.append(dict(fold=fold["name"], n_train=len(tr), n_test=len(te), A=ctx.A,
                              n_calib_groups=int(len(np.unique(fold["calib_group"][tr]))),
                              setup_s=round(time.time() - t0, 2), **{f"t_{k}": round(v, 3) for k, v in ctx.timing.items()}))
        log(f"  [{task_name}] fold {fold['name']}: n_tr={len(tr)} n_te={len(te)} A={ctx.A} "
            f"K={fold_info[-1]['n_calib_groups']} setup={time.time()-t0:.1f}s")
        tg = fold["test_group"][te]
        for meth in methods:
            for a in alphas:
                t1 = time.time()
                try:
                    lo, hi = METHODS[meth](ctx, a)
                except Exception as e:  # failures are recorded, never silently dropped
                    log(f"    !! {meth} alpha={a} failed: {e}")
                    traceback.print_exc()
                    rows.append(dict(task=task_name, fold=fold["name"], group="ALL", method=meth, alpha=a,
                                     seed=seed, error=str(e)))
                    continue
                el = time.time() - t1
                lo, hi = inv(lo), inv(hi)
                yt = y_all[te]
                for g in np.unique(tg):
                    s = tg == g
                    r = summarize_group(yt[s], yhat[s], lo[s], hi[s], a)
                    rows.append(dict(task=task_name, fold=fold["name"], group=g, method=meth, alpha=a, seed=seed,
                                     A=ctx.A, time_s=el, **r))
                if store_points:
                    points.append(pd.DataFrame(dict(task=task_name, fold=fold["name"], method=meth, alpha=a, seed=seed,
                                                    idx=te.astype(np.int32), group=tg, y=yt.astype(np.float32),
                                                    yhat=yhat.astype(np.float32), lo=lo.astype(np.float32),
                                                    hi=hi.astype(np.float32), T2=ctx.T2te.astype(np.float32),
                                                    Qr=(ctx.Qte / ctx.Qref).astype(np.float32))))
        if resume:  # the _groups.csv file is the completion marker, so it is written last (atomically)
            pd.DataFrame(fold_info[-1:]).to_csv(pf + "_fold.csv", index=False)
            if store_points and len(points) > n_pts0:
                pd.concat(points[n_pts0:], ignore_index=True).to_parquet(pf + "_points.parquet", index=False)
            pd.DataFrame(rows[n_rows0:]).to_csv(pf + "_groups.csv.tmp", index=False)
            os.replace(pf + "_groups.csv.tmp", pf + "_groups.csv")
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(out_dir, f"groups_{tag}.csv"), index=False)
    pd.DataFrame(fold_info).to_csv(os.path.join(out_dir, f"folds_{tag}.csv"), index=False)
    if store_points and points:
        pd.concat(points, ignore_index=True).to_parquet(os.path.join(out_dir, f"points_{tag}.parquet"), index=False)
    return df
