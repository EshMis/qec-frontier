"""Reproduce the selected candidate, then compare every check with its JSON."""
import json
from pathlib import Path
import sys

import numpy as np

from generators_lp import construct

ROOT = Path(__file__).resolve().parents[1]
recipe = json.loads((ROOT / "results/profile-lp/lp-20261002/5f3a6a45fb0e94615da1/recipe.json").read_text())
hx, hz = construct(recipe)
doc = json.loads((ROOT / "submission/455-39-6.json").read_text())
for side, matrix in (("X", hx), ("Z", hz)):
    supports = [np.flatnonzero(row).tolist() for row in matrix]
    assert supports == doc["checks"][side], f"{side} reproduction mismatch"
np.savez_compressed(ROOT / "submission/455-39-6.npz", hx=hx, hz=hz)
sys.path.insert(0, str(ROOT / "external/qldpc-challenge/verify"))
from qldpc_verify import verify
report = verify(doc, refute=True, seed=30102026)
assert all(c["ok"] for c in report["checks"]), report
(ROOT / "evidence/455-39-6/reproduction.json").write_text(json.dumps(report, indent=2) + "\n")
print("Reproduced both parity-check matrices exactly; final submission passed trusted verifier.")
