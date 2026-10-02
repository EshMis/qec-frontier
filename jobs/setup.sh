#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -N qec_setup
#$ -pe def_slot 1
#$ -l h_rt=0:30:00
#$ -l mem_req=8G
#$ -l s_vmem=8G
#$ -o logs/
#$ -e logs/
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 OMP_THREAD_LIMIT=1 VECLIB_MAXIMUM_THREADS=1
export HIGHS_NUM_THREADS=1 NUMBA_NUM_THREADS=1
mkdir -p evidence
~/faceflow/conda/envs/ff/bin/python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
(cd external/qldpc-challenge/verify && ../../../.venv/bin/python setup_gf2_fast.py build_ext --inplace)
.venv/bin/python -m pip freeze > evidence/environment-lock.txt
.venv/bin/python - <<'PY'
import importlib.metadata, json, pathlib, platform, socket, time
import qldpc
version = importlib.metadata.version('qldpc')
assert version == '0.4.0', version
record = {'status': 'complete', 'qldpc': version, 'python': platform.python_version(),
          'host': socket.gethostname(), 'finished_unix': time.time()}
pathlib.Path('evidence/setup-complete.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record))
PY
