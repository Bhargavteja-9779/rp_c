"""E6 computational cost: wall time and peak Python memory of each interval method, measured in isolation.

For each of three held-out seasons (mango LOSO, ~70k training spectra) a FRESH FoldContext is built for every
method, so lazily computed shared components (random split model, random CV, quantile models, …) are charged to
the method that needs them. The group-wise cross-validation + final PLS fit done in the context constructor is
timed separately ("shared setup"); it is the same work as standard group-wise CV for choosing the number of LVs.
Run on an otherwise idle machine, single-threaded BLAS.
"""
import os, sys, time, tracemalloc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np, pandas as pd
from src.conformal.methods import METHODS, FoldContext
from src.evaluation.tasks import get_task
from src.utils import RESULTS

task = get_task("mango_season_loso")
X, y, units = task["X"], task["ds"].y.astype(float), task["ds"].meta.unit.to_numpy()
rows = []
methods = [m for m in METHODS if m not in ("GC-D2", "GC-CQR")] + ["GC-D2", "GC-CQR"]
for f in [f for f in task["folds"] if f["name"] in ("season2016", "season2018", "season2020")]:
    tr, te = f["train"], f["test"]
    args = (X[tr], y[tr], f["calib_group"][tr], units[tr], X[te], y[te], f["test_group"][te], units[te], task["cfg"])
    for m in methods:
        t0 = time.perf_counter()
        ctx = FoldContext(*args, seed=0)
        setup = time.perf_counter() - t0
        tracemalloc.start()
        t1 = time.perf_counter()
        lo, hi = METHODS[m](ctx, 0.1)
        el = time.perf_counter() - t1
        peak = tracemalloc.get_traced_memory()[1] / 2 ** 20
        tracemalloc.stop()
        per_spec_ms = 1000 * el / len(te)
        rows.append(dict(fold=f["name"], method=m, n_train=len(tr), n_test=len(te), shared_setup_s=setup,
                         method_s=el, method_peak_MiB=peak, method_ms_per_test_spectrum=per_spec_ms))
        print(f["name"], m, f"setup {setup:.1f}s method {el:.2f}s peak {peak:.0f}MiB", flush=True)
df = pd.DataFrame(rows)
df.to_csv(os.path.join(RESULTS, "timing_raw.csv"), index=False)
s = df.groupby("method").agg(method_s=("method_s", "mean"), method_s_sd=("method_s", "std"),
                             peak_MiB=("method_peak_MiB", "mean"), ms_per_test_spectrum=("method_ms_per_test_spectrum", "mean"),
                             shared_setup_s=("shared_setup_s", "mean")).reset_index().sort_values("method_s")
s.to_csv(os.path.join(RESULTS, "timing_summary.csv"), index=False)
print(s.round(3).to_string())
