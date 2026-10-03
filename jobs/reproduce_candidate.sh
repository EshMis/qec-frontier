#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -N qec_repro
#$ -pe def_slot 1
#$ -l h_rt=0:15:00
#$ -l mem_req=4G
#$ -l s_vmem=4G
#$ -o logs/
#$ -e logs/
set -euo pipefail
ulimit -c 0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 OMP_THREAD_LIMIT=1 VECLIB_MAXIMUM_THREADS=1
export HIGHS_NUM_THREADS=1 NUMBA_NUM_THREADS=1
.venv/bin/python -u scripts/reproduce_candidate.py "$@"
