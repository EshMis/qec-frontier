#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -N qec_strip
#$ -pe def_slot 1
#$ -l h_rt=0:15:00
#$ -l mem_req=1G
#$ -l s_vmem=1G
#$ -o logs/
#$ -e logs/
set -euo pipefail
ulimit -c 0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
.venv/bin/python -u scripts/strip_bounds.py "$@"
