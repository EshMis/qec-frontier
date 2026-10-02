#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -N qec_tools
#$ -pe def_slot 1
#$ -l h_rt=0:20:00
#$ -l mem_req=8G
#$ -l s_vmem=8G
#$ -o logs/
#$ -e logs/
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 OMP_THREAD_LIMIT=1 VECLIB_MAXIMUM_THREADS=1
export HIGHS_NUM_THREADS=1 NUMBA_NUM_THREADS=1
.venv/bin/python external/qldpc-challenge/verify/check_validator_integrity.py
.venv/bin/python -m pytest external/qldpc-challenge/verify/test_sat_certify.py -q
.venv/bin/python - <<'PY'
import json, sys, time
from pathlib import Path
sys.path.insert(0, 'external/qldpc-challenge/verify')
from validate_candidate import validate_candidate
doc = json.loads(Path('evidence/control/candidate.json').read_text())
verdict = validate_candidate(doc, seed=20261002)
assert verdict['gates']['novelty']['board_advancing'] is not True
Path('evidence/control/official-known-code-verdict.json').write_text(json.dumps(verdict, indent=2) + '\n')
Path('evidence/tools-complete.json').write_text(json.dumps({'status': 'complete', 'finished_unix': time.time()}) + '\n')
print('Known-code control did not advance the official board; SAT regression tests passed.')
PY
