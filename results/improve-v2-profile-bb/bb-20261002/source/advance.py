"""Bounded improvement batch: screen, official validation, then exact SAT.

Workers write only their own result directory. They never publish, mutate the
shared frontier registry, or call a screening estimate a verified discovery.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from search import ROOT, UPSTREAM, atomic_json, board_rows, screen_one
from validate_candidate import validate_candidate
from sat_certify import certify


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", choices=["bb", "lp"], required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--count", type=int, required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--specs", type=Path)
    ap.add_argument("--stages", default="300,5000,50000")
    ap.add_argument("--tlim", type=float, default=300)
    args = ap.parse_args()
    if args.offset < 0 or args.count < 1:
        ap.error("offset must be nonnegative and count must be positive")
    assert importlib.metadata.version("qldpc") == "0.4.0"
    subprocess.run([sys.executable, str(UPSTREAM / "verify/check_validator_integrity.py")], check=True)
    module = importlib.import_module("generators_" + args.lane)
    if args.specs:
        all_specs = json.loads(args.specs.read_text())
        if not isinstance(all_specs, list) or len(all_specs) < args.offset + args.count:
            ap.error("specs must contain a list covering the requested offset and count")
        specs = all_specs[args.offset:args.offset + args.count]
    else:
        specs = list(module.next_candidates(args.seed, args.count + args.offset))[args.offset:]
    assert len(specs) == args.count
    out = ROOT / "results" / args.run / f"{args.lane}-{args.seed}"
    if out.exists():
        raise FileExistsError(f"Use a fresh run name; existing evidence: {out}")
    out.mkdir(parents=True)
    source_paths = [Path(__file__), Path(module.__file__), ROOT / "scripts/search.py"]
    (out / "source").mkdir()
    for source in source_paths:
        (out / "source" / source.name).write_bytes(source.read_bytes())
    atomic_json(out / "RUN.json", {
        "arguments": vars(args) | {"specs": str(args.specs) if args.specs else None},
        "job_id": os.environ.get("JOB_ID"), "started_unix": time.time(),
        "sources": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in source_paths}, "specifications": specs,
    })
    board = board_rows()
    points, outcomes = [], []
    for i, spec in enumerate(specs):
        seed = (args.seed * 1009 + args.offset + i) % (2**31)
        record = screen_one(spec, module.construct, board, out, seed,
                            [int(x) for x in args.stages.split(",")])
        outcomes.append(record)
        if record["status"] != "needs_official_validation":
            continue
        dest = out / record["id"]
        raw = (dest / "candidate.json").read_bytes()
        doc = json.loads(raw)
        ev = dest / "verification"
        atomic_json(ev / "input.json", {
            "candidate": str((dest / "candidate.json").relative_to(ROOT)),
            "candidate_sha256": hashlib.sha256(raw).hexdigest(), "seed": seed + 31,
        })
        verdict = validate_candidate(doc, seed=seed + 31)
        atomic_json(ev / "validation.json", verdict)
        if not (verdict["passed"] and verdict["gates"]["novelty"]["board_advancing"]):
            atomic_json(ev / "COMPLETE.json", {"status": "rejected", "validated_frontier": False,
                "exact": False, "candidate_sha256": hashlib.sha256(raw).hexdigest()})
            print(json.dumps({"event": "official_rejection", "id": record["id"]}), flush=True)
            continue
        cert = certify(doc, tlim=args.tlim)
        atomic_json(ev / "sat-certificate.json", cert)
        exact = bool(cert["d_exact"])
        atomic_json(ev / "COMPLETE.json", {"status": "complete", "finished_unix": time.time(),
            "validated_frontier": True, "exact": exact,
            "candidate_sha256": hashlib.sha256(raw).hexdigest()})
        point = {key: record[key] for key in ("id", "n", "k", "w")}
        point.update(d=doc["distance"]["d"], exact=exact,
                     candidate=str((dest / "candidate.json").relative_to(ROOT)),
                     evidence=str(ev.relative_to(ROOT)))
        if exact:
            points.append(point)
            board.append(point | {"file": point["candidate"]})
            atomic_json(out / "DISCOVERIES.json", {"points": points})
        print(json.dumps({"event": "verified_point" if exact else "exact_unresolved", **point}), flush=True)
    atomic_json(out / "COMPLETE.json", {"status": "complete", "count": len(outcomes),
        "finished_unix": time.time(), "exact_points": points,
        "screened": {r["id"]: r["status"] for r in outcomes}})


if __name__ == "__main__":
    main()
