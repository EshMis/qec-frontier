#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -N qec_solver
#$ -pe def_slot 1
#$ -l h_rt=0:10:00
#$ -l mem_req=4G
#$ -l s_vmem=4G
#$ -o logs/
#$ -e logs/
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
.venv/bin/python -m pip install 'pycryptosat>=5.11'
.venv/bin/python -m pip freeze > evidence/environment-lock.txt
.venv/bin/python - <<'PY'
from pycryptosat import Solver
s = Solver(threads=1)
s.add_clause([1])
assert s.solve()[0] is True
s.add_clause([-1])
assert s.solve()[0] is False
print('CryptoMiniSat satisfiable and unsatisfiable controls passed')
PY
