"""Bounded enumeration of explicit bicycle logical upper bounds; no exact claims."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time

import generators_bb

ap = argparse.ArgumentParser()
ap.add_argument("--start", type=int, required=True)
ap.add_argument("--end", type=int, required=True)
ap.add_argument("--out", type=Path, required=True)
args = ap.parse_args()
assert 2 <= args.start <= args.end <= 20
args.out.mkdir(parents=True, exist_ok=False)
source = Path(generators_bb.__file__)
(args.out / "generators_bb.py").write_bytes(source.read_bytes())
start = time.time()
records = []
for order in range(args.start, args.end + 1):
    began = time.time()
    record = generators_bb.paired_strip_bounds(order)
    record["elapsed_seconds"] = time.time() - began
    tmp = args.out / f"m{order}.tmp"
    tmp.write_text(json.dumps(record, indent=2) + "\n")
    tmp.replace(args.out / f"m{order}.json")
    records.append({"order": order, "max_upper_bound": record["max_upper_bound"],
                    "elapsed_seconds": record["elapsed_seconds"]})
    print(json.dumps(records[-1]), flush=True)
(args.out / "COMPLETE.json").write_text(json.dumps({
    "status": "complete", "job_id": os.environ.get("JOB_ID"),
    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "elapsed_seconds": time.time() - start, "records": records,
    "scope": "Explicit logical upper bounds, pending independent witness replay; not exact distances",
}, indent=2) + "\n")
