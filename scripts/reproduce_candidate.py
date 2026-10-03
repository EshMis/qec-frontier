"""Rebuild a recorded construction and verify its final publication document."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys

import numpy as np

from search import ROOT, UPSTREAM, atomic_json, constructor

ap = argparse.ArgumentParser()
ap.add_argument("--recipe", type=Path, required=True)
ap.add_argument("--candidate", type=Path, required=True)
ap.add_argument("--out", type=Path, required=True)
ap.add_argument("--seed", type=int, default=19032027)
args = ap.parse_args()
spec = json.loads(args.recipe.read_text())
module = importlib.import_module("generators_lp" if spec["family"] == "lifted-product" else "generators_bb")
hx, hz = constructor(module, spec)(spec)
raw = args.candidate.read_bytes()
doc = json.loads(raw)
for side, matrix in (("X", hx), ("Z", hz)):
    assert [np.flatnonzero(row).tolist() for row in matrix] == doc["checks"][side], side
sys.path.insert(0, str(UPSTREAM / "verify"))
from qldpc_verify import verify
report = verify(doc, refute=True, seed=args.seed)
assert all(check["ok"] for check in report["checks"]), report
atomic_json(args.out, {"candidate_sha256": hashlib.sha256(raw).hexdigest(),
    "recipe_sha256": hashlib.sha256(args.recipe.read_bytes()).hexdigest(),
    "matrix_reproduction": "exact", "verification": report})
print("Reproduced both parity-check matrices exactly; final document passed trusted verifier.", flush=True)
