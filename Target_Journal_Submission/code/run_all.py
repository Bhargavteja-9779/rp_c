"""Reproduce the complete study.

    python run_all.py --mode quick     # pipeline check: 2 folds per task, seed 0, few methods (~15 min, 4 CPU cores)
    python run_all.py --mode full      # complete study as reported (several hours on 4 CPU cores)

Steps: download data -> unit tests -> main experiments (E1-E3, E5) -> post-hoc iteration ->
robustness/sensitivity (E4, E7) -> CNN model-agnosticism check -> aggregation & statistics ->
error/decision analysis (E8, E9) -> figures -> tables.
Quick-mode outputs go to results_quick/ so they never overwrite the full results.
Full mode is resumable: completed folds are skipped on re-run.
"""
import argparse, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN_TASKS = ["mango_season_loso", "mango_season_forward", "mango_instrument", "mango_population", "ossl_lucas_block",
              "corn_moisture", "corn_oil", "corn_protein", "corn_starch", "ossl_lucas_campaign", "ossl_kssl_to_lucas", "tablets"]
ITER_TASKS = MAIN_TASKS[:9]


def sh(cmd, env):
    print(">>", cmd, flush=True)
    r = subprocess.run(cmd, shell=True, cwd=HERE, env=env)
    if r.returncode != 0:
        raise SystemExit(f"command failed ({r.returncode}): {cmd}")


def parallel(cmds, env, workers):
    qf = os.path.join(env["RESULTS_DIR"], "experiment_logs", "queue_run_all.txt")
    os.makedirs(os.path.dirname(qf), exist_ok=True)
    open(qf, "w").write("\n".join(cmds) + "\n")
    sh(f"bash scripts/run_cmds.sh {qf} {workers}", env)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["quick", "full"], default="quick")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 0))
    ap.add_argument("--skip-download", action="store_true")
    a = ap.parse_args()
    env = dict(os.environ)
    env["RESULTS_DIR"] = os.path.join(HERE, "results" if a.mode == "full" else "results_quick")
    if a.mode == "quick":
        env["FIG_DIR"] = os.path.join(HERE, "figures_quick"); env["TABLE_DIR"] = os.path.join(HERE, "tables_quick")
    env.update(OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NJOBS="1")
    py = sys.executable
    if not a.skip_download:
        sh(f"{py} scripts/download_data.py", env)
    sh(f"{py} -m pytest -q tests", env)
    quick = " --quick" if a.mode == "quick" else ""
    seeds = [0] if a.mode == "quick" else [0, 1, 2, 3, 4]
    tasks = ["mango_season_loso", "ossl_lucas_block", "corn_protein", "tablets"] if a.mode == "quick" else MAIN_TASKS
    lg = os.path.join(env["RESULTS_DIR"], "experiment_logs")
    os.makedirs(lg, exist_ok=True)
    cmds = [f"{py} experiments/run_main.py --task {t} --seed {s}{quick} > {lg}/stdout_{t}_seed{s}.txt 2>&1"
            for s in seeds for t in tasks]
    parallel(cmds, env, a.workers)
    it_tasks = ["mango_season_loso"] if a.mode == "quick" else ITER_TASKS
    cmds = [f"{py} experiments/run_iteration.py --task {t} --seed {s}{quick} > {lg}/stdout_iter1_{t}_seed{s}.txt 2>&1"
            for s in seeds for t in it_tasks]
    if a.mode == "full":
        cmds += [f"{py} experiments/run_robustness.py --exp groups --task mango_instrument",
                 f"{py} experiments/run_robustness.py --exp groups --task ossl_lucas_block",
                 f"{py} experiments/run_robustness.py --exp size",
                 f"{py} experiments/run_robustness.py --exp perturb",
                 f"{py} experiments/run_robustness.py --exp sensitivity --task mango_season_loso",
                 f"{py} experiments/run_robustness.py --exp sensitivity --task ossl_lucas_block",
                 f"{py} experiments/run_robustness.py --exp sens_popfolds"]
        cmds += [f"{py} experiments/run_cnn.py --seed {s}" for s in (0, 1, 2)]
    else:
        cmds += [f"{py} experiments/run_robustness.py --exp perturb --quick",
                 f"{py} experiments/run_cnn.py --seed 0 --quick"]
    parallel(cmds, env, a.workers)
    sh(f"{py} experiments/aggregate.py", env)
    sh(f"{py} experiments/aggregate_extra.py", env)
    sh(f"{py} experiments/analysis_points.py", env)
    sh(f"{py} experiments/make_figures.py", env)
    sh(f"{py} experiments/make_tables.py", env)
    print("done; outputs in", env["RESULTS_DIR"], "figures/ and tables/")


if __name__ == "__main__":
    main()
