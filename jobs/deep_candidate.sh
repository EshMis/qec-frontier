#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -N qec_deep
#$ -pe def_slot 4
#$ -l h_rt=2:00:00
#$ -l mem_req=1G
#$ -l s_vmem=1G
#$ -o logs/
#$ -e logs/
set -euo pipefail
ulimit -c 0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 OMP_THREAD_LIMIT=1 VECLIB_MAXIMUM_THREADS=1
export HIGHS_NUM_THREADS=1 NUMBA_NUM_THREADS=1
.venv/bin/python -u scripts/deep_candidate.py "$@"
