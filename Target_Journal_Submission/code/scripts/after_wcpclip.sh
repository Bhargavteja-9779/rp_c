#!/usr/bin/env bash
cd "$(dirname "$0")/.."
while pgrep -f "wcpclip_queue.txt" > /dev/null; do sleep 60; done
for s in 0 1 2; do echo "python experiments/run_cultivar.py $s > results/experiment_logs/stdout_cultivar_$s.txt 2>&1"; done > results/experiment_logs/cultivar_queue.txt
bash scripts/run_cmds.sh results/experiment_logs/cultivar_queue.txt 3 >> results/experiment_logs/cultivar_progress.txt 2>&1
