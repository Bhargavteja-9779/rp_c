#!/usr/bin/env bash
# Run one shell command per line of a file with N parallel single-threaded workers.
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NJOBS=1 TORCH_THREADS=1
cat "$1" | xargs -P "${2:-4}" -I CMD bash -c 'CMD; echo "finished rc=$? :: CMD"'
