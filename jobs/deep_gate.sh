#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -N qec_deep
#$ -pe def_slot 4
#$ -l h_rt=2:00:00
#$ -l mem_req=4G
#$ -l s_vmem=4G
#$ -o logs/
#$ -e logs/
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 OMP_THREAD_LIMIT=1 VECLIB_MAXIMUM_THREADS=1
export HIGHS_NUM_THREADS=1 NUMBA_NUM_THREADS=1
.venv/bin/python - <<'PY'
import json, pathlib, shutil, subprocess
root = pathlib.Path.cwd()
tree = root / 'scratch/gate-455-39-6'
tree.mkdir(parents=True, exist_ok=False)
shutil.copytree(root / 'external/qldpc-challenge/codes', tree / 'codes')
def git(*args):
    return subprocess.check_output(['git', *args], cwd=tree, text=True).strip()
git('init', '-q', '-b', 'main')
git('config', 'user.name', 'QEC local gate snapshot')
git('config', 'user.email', 'local-gate@example.invalid')
git('add', 'codes')
git('commit', '-q', '-m', 'Pinned board code snapshot for local gate')
base = git('rev-parse', 'HEAD')
shutil.copyfile(root / 'submission/455-39-6.json', tree / 'codes/455-39-6.json')
git('add', 'codes/455-39-6.json')
git('commit', '-q', '-m', 'Candidate under test')
meta = {'snapshot_base': base, 'snapshot_head': git('rev-parse','HEAD'),
        'upstream_source': 'c2ebca1713c89277dbd6ddf3ee587cbf7f1a9d23',
        'note': 'Local git fixture contains the exact upstream code files plus the candidate; verifier source stays in the unchanged upstream snapshot.'}
(root / 'evidence/455-39-6/gate-snapshot.json').write_text(json.dumps(meta, indent=2)+'\n')
(tree / 'base-sha.txt').write_text(base+'\n')
PY
BASE_SHA=$(cat scratch/gate-455-39-6/base-sha.txt)
.venv/bin/python -u external/qldpc-challenge/verify/gate_changed.py \
  "$BASE_SHA" --code-root scratch/gate-455-39-6 \
  --receipt-dir evidence/455-39-6/deep-gate --seed 847392151 codes/455-39-6.json
