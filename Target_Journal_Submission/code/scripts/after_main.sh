#!/usr/bin/env bash
cd "$(dirname "$0")/.."
while pgrep -f "scripts/run_queue.sh" > /dev/null; do sleep 60; done
bash scripts/run_cmds.sh results/experiment_logs/followup_queue.txt 4 > results/experiment_logs/followup_progress.txt 2>&1
