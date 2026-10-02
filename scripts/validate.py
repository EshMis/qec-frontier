"""Persist official validation and optional exact SAT certification receipts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "external/qldpc-challenge"
sys.path[:0] = [str(UPSTREAM / "verify"), str(ROOT / "scripts")]

from validate_candidate import validate_candidate
from search import atomic_json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("candidate", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=713904281)
    ap.add_argument("--exact", action="store_true")
    ap.add_argument("--tlim", type=float, default=300)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(UPSTREAM / "verify/check_validator_integrity.py")], check=True)
    raw = args.candidate.read_bytes()
    doc = json.loads(raw)
    atomic_json(args.out / "input.json", {"candidate_sha256": hashlib.sha256(raw).hexdigest(),
                "candidate": str(args.candidate), "seed": args.seed, "started_unix": time.time()})
    verdict = validate_candidate(doc, seed=args.seed)
    atomic_json(args.out / "validation.json", verdict)
    print(json.dumps(verdict), flush=True)
    if not verdict["passed"]:
        raise SystemExit(1)
    if not verdict["gates"]["novelty"]["board_advancing"]:
        raise SystemExit(2)
    if args.exact:
        from sat_certify import certify
        cert = certify(doc, tlim=args.tlim)
        atomic_json(args.out / "sat-certificate.json", cert)
        print(json.dumps(cert), flush=True)
    atomic_json(args.out / "COMPLETE.json", {"status": "complete", "finished_unix": time.time(),
                "candidate_sha256": hashlib.sha256(raw).hexdigest(),
                "validated_frontier": True, "exact": cert["d_exact"] if args.exact else False})


if __name__ == "__main__":
    main()
