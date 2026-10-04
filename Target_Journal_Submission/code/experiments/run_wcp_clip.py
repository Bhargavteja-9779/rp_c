"""Reviewer-requested baseline: weighted CP with clipped density ratios (WCP-clip, cap 20 after normalising the
calibration weights to mean 1). Uses the same random split, PLS model and number of LVs (taken from the main run's
fold files) as WCP, so it differs from WCP only in the weight clipping. Seeds 0-4, alpha = 0.1."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from src.evaluation.engine import run_task
from src.evaluation.tasks import get_task
from src.utils import RESULTS, get_logger

task_name, seed = sys.argv[1], int(sys.argv[2])
log = get_logger(f"wcpclip_{task_name}_seed{seed}")
task = get_task(task_name, seed=seed)
fi = pd.read_csv(os.path.join(RESULTS, "main", f"folds_{task_name}_seed{seed}.csv")).set_index("fold")
out = os.path.join(RESULTS, "wcp_clip"); dfs = []
for f in task["folds"]:
    t = dict(task); t["folds"] = [f]; t["cfg"] = dict(task["cfg"], skip_gcv=True)
    dfs.append(run_task(t, task_name, ["WCP", "WCP-clip"], [0.1], seed, out, A_fixed=int(fi.loc[f["name"], "A"]),
                        log=log.info, store_points=False, resume=False))
pd.concat(dfs).to_csv(os.path.join(out, f"groups_{task_name}_seed{seed}.csv"), index=False)
