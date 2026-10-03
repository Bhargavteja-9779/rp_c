#!/usr/bin/env bash
# Runs "task seed" lines from a queue file with N parallel single-threaded workers.
# usage: bash scripts/run_queue.sh QUEUE_FILE N_WORKERS
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NJOBS=1
cat "$1" | xargs -P "${2:-4}" -L 1 bash -c 'python experiments/run_main.py --task "$0" --seed "$1" > results/experiment_logs/stdout_$0_seed$1.txt 2>&1; echo "finished $0 $1 rc=$?"'
