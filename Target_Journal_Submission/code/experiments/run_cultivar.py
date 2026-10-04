"""Reviewer-requested external-validity test (Review round 5): leave-one-cultivar-out on the mango data.
Methods: classical (random / group CV), SCP, CV+, CQR, group CP (abs), GC-D, HJ+, oracle; alpha = 0.1; seeds 0-2."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.evaluation.engine import run_task
from src.evaluation.tasks import get_task
from src.utils import RESULTS, get_logger
seed = int(sys.argv[1])
log = get_logger(f"cultivar_seed{seed}")
task = get_task("mango_cultivar", seed=seed)
run_task(task, "mango_cultivar", ["ASTM-R", "ASTM-G", "SCP", "CV+", "CQR", "G-W-A", "GC-D", "HJ+", "ORACLE"], [0.1], seed,
         os.path.join(RESULTS, "cultivar"), log=log.info, store_points=False)
