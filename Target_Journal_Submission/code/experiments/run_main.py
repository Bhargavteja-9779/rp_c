"""E1/E2/E3 (main comparison, baselines, factorial ablation) for one task and one seed.

Usage: python experiments/run_main.py --task mango_season_loso --seed 0 [--quick]
"""
import argparse, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.conformal.methods import METHODS
from src.evaluation.engine import run_task
from src.evaluation.tasks import get_task
from src.utils import set_seed, get_logger, RESULTS

p = argparse.ArgumentParser()
p.add_argument("--task", required=True)
p.add_argument("--seed", type=int, default=0)
p.add_argument("--alphas", default="0.05,0.1,0.2")
POSTHOC = {"GC-D2", "GC-CQR"}  # evaluated separately in run_iteration.py
p.add_argument("--methods", default=",".join(m for m in METHODS if m not in POSTHOC))
p.add_argument("--quick", action="store_true")
p.add_argument("--out", default=os.path.join(RESULTS, "main"))
a = p.parse_args()
set_seed(a.seed)
if not a.quick and os.path.exists(os.path.join(a.out, f"groups_{a.task}_seed{a.seed}.csv")):
    print(f"{a.task} seed {a.seed} already complete; skipping"); sys.exit(0)
log = get_logger(f"main_{a.task}_seed{a.seed}")
task = get_task(a.task, quick=a.quick, seed=a.seed)
if a.quick:
    task["folds"] = task["folds"][:2]
t0 = time.time()
run_task(task, a.task, a.methods.split(","), [float(x) for x in a.alphas.split(",")], a.seed, a.out,
         log=log.info, store_points=(a.seed == 0))
log.info(f"done {a.task} seed {a.seed} in {time.time()-t0:.1f}s")
