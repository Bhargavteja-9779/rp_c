#!/usr/bin/env bash
cd "$(dirname "$0")/.."
while pgrep -f "followup_queue2.txt" > /dev/null; do sleep 60; done
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NJOBS=1 python experiments/run_timing.py > results/experiment_logs/stdout_timing.txt 2>&1
echo "finished rc=$? :: timing" >> results/experiment_logs/followup_progress2.txt
