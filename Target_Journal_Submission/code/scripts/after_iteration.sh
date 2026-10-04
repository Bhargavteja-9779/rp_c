#!/usr/bin/env bash
cd "$(dirname "$0")/.."
while pgrep -f "experiments/run_iteration.py" > /dev/null; do sleep 30; done
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NJOBS=1 python experiments/run_timing.py > results/experiment_logs/stdout_timing.txt 2>&1
echo "finished rc=$? :: timing (idle machine)" >> results/experiment_logs/followup_progress2.txt
