"""Construct with qLDPC 0.4.0 and screen with the unmodified challenge kit.

Screening only allocates compute. Only the upstream validator can establish a
board advance, and only an exact certificate can establish an exact distance.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import itertools
import json
import os
from pathlib import Path
import socket
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "external/qldpc-challenge"
sys.path[:0] = [str(UPSTREAM / "research/kit"), str(UPSTREAM / "verify")]

import numpy as np
import gf2_fast
from css import verify_css
from surrogate import distance_rand_witness, validate_logical
from submit import make_submission, save_submission
from qldpc_verify import _tanner_component_count, admissible


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def board_rows():
    """Conservative numeric screen; the official gate handles full membership."""
    rows = []
    for path in sorted((UPSTREAM / "codes").glob("*.json")):
        doc = json.loads(path.read_text())
        if doc.get("code_type", "CSS") != "CSS":
            continue
        w = max(map(len, doc["checks"]["X"] + doc["checks"]["Z"]))
        rows.append({"n": doc["n"], "k": doc["k"],
                     "d": doc["distance"]["d"], "w": w, "file": path.name})
    if len(rows) < 1000:
        raise RuntimeError("Board snapshot missing or unexpectedly incomplete")
    # Certified local discoveries also set the next search's bar while their
    # upstream PRs await review. A repeated or inferior point is not progress.
    registry = ROOT / "evidence/frontier-points.json"
    if registry.exists():
        for point in json.loads(registry.read_text())["points"]:
            candidate = ROOT / point["candidate"]
            raw = candidate.read_bytes()
            receipt = json.loads((ROOT / point["evidence"] / "COMPLETE.json").read_text())
            if not (receipt.get("status") == "complete" and receipt["validated_frontier"] and receipt["exact"]
                    and receipt["candidate_sha256"] == hashlib.sha256(raw).hexdigest()):
                raise RuntimeError(f"Local frontier evidence is incomplete: {point['id']}")
            doc = json.loads(raw)
            w = max(map(len, doc["checks"]["X"] + doc["checks"]["Z"]))
            actual = {"n": doc["n"], "k": doc["k"], "d": doc["distance"]["d"], "w": w}
            assert all(actual[key] == point[key] for key in actual), point["id"]
            rows.append(actual | {"file": point["candidate"], "source": "local-certified"})
    return rows


def required_distance(board, n, k, w):
    # Tied parameter points are deliberately excluded: the goal is a NEW point.
    peers = [r for r in board if r["n"] <= n and r["k"] >= k and r["w"] <= w]
    return max((r["d"] for r in peers), default=2) + 1


def tighten(doc, hx, hz, found):
    if found.rejected or not found.support:
        raise RuntimeError(f"Invalid or absent search witness: {found}")
    valid, why = validate_logical(hx, hz, found.side, found.weight, found.support)
    if not valid:
        raise RuntimeError(why)
    side = doc["distance"][found.side]
    if found.weight < side["value"]:
        side.update(value=int(found.weight), witness=list(found.support), confidence="upper_bound")
    doc["distance"]["d"] = min(doc["distance"][s]["value"] for s in ("X", "Z"))
    doc["name"] = f"[[{doc['n']},{doc['k']},{doc['distance']['d']}]] QEC frontier candidate"


def constructor(module, spec):
    if spec.get("generator") == "monomial-2xc-v1":
        return module.construct_wide
    return module.construct


def screen_one(spec, construct, board, outdir, seed, stages):
    started = time.monotonic()
    ident = hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()[:20]
    dest = outdir / ident
    if (dest / "screen.json").exists():
        raise FileExistsError(f"Refusing to overwrite a measured candidate: {dest}")
    dest.mkdir(parents=True, exist_ok=True)
    atomic_json(dest / "recipe.json", spec)
    hx, hz = construct(spec)
    hx, hz = np.asarray(hx, dtype=np.int8), np.asarray(hz, dtype=np.int8)
    assert verify_css(hx, hz), "Construction fails CSS commutation"
    n = int(hx.shape[1])
    k = int(gf2_fast.compute_k(hx, hz))
    w = int(max(hx.sum(axis=1).max(), hz.sum(axis=1).max()))
    board_target = required_distance(board, n, k, w)
    target = max(board_target,
                 int(spec.get("target", {}).get("d_min", 0)),
                 int(spec.get("target_d_snapshot") or 0))
    record = {"id": ident, "spec": spec, "n": n, "k": k, "w": w,
              "needed_d": target, "board_needed_d": board_target,
              "seed": seed, "rungs": [], "status": "screening"}
    atomic_json(dest / "screen.json", record)
    supports = {"X": [np.flatnonzero(row).tolist() for row in hx],
                "Z": [np.flatnonzero(row).tolist() for row in hz]}
    if k <= 0:
        record["status"] = "no_logical_qubits"
    elif not admissible(n, w, target) or w > 32:
        record["status"] = "outside_challenge_caps"
    elif _tanner_component_count(supports, n) != 1:
        record["status"] = "disconnected"
    else:
        # The trusted kit packages both sides and independently checks witnesses.
        # One initial trial suffices here: the accelerated ladder tightens them.
        doc = make_submission(hx, hz, name="QEC frontier candidate",
                              construction=json.dumps(spec, sort_keys=True),
                              authors=["@EshMis"], family=spec["family"],
                              confidence="upper_bound", trials=1, seed=seed,
                              date="2026-10-02",
                              notes="Constructed using qLDPC v0.4.0. Distance is a witnessed upper bound.")
        errs = save_submission(doc, dest / "candidate-initial.json")
        if errs:
            raise RuntimeError(errs)
        for rung, trials in enumerate(stages):
            rung_seed = seed + 1000003 * (rung + 1)
            t0 = time.monotonic()
            found = distance_rand_witness(hx, hz, trials=trials, seed=rung_seed,
                                          backend="fast", threads=1, pair_depth=24)
            # Save the actual found operator before any subsequent filtering.
            atomic_json(dest / f"witness-{rung}.json", found._asdict())
            tighten(doc, hx, hz, found)
            doc_path = dest / f"candidate-rung-{rung}.json"
            errs = save_submission(doc, doc_path)
            if errs:
                raise RuntimeError(errs)
            record["rungs"].append({"trials": trials, "seed": rung_seed,
                                    "pair_depth": 24, "d_upper": doc["distance"]["d"],
                                    "seconds": time.monotonic() - t0,
                                    "candidate": str(doc_path.relative_to(ROOT))})
            record["d_upper"] = doc["distance"]["d"]
            atomic_json(dest / "screen.json", record)
            if doc["distance"]["d"] < target:
                record["status"] = ("below_board_bar" if doc["distance"]["d"] < board_target
                                    else "below_aspirational_goal")
                break
        else:
            record["status"] = "needs_official_validation"
            errs = save_submission(doc, dest / "candidate.json")
            if errs:
                raise RuntimeError(errs)
    record["seconds"] = time.monotonic() - started
    atomic_json(dest / "screen.json", record)
    print(json.dumps({key: record[key] for key in
                      ("id", "n", "k", "w", "needed_d", "status", "seconds")}
                     | {"d_upper": record.get("d_upper")}), flush=True)
    return record


def control():
    from qldpc.codes import BBCode
    from sympy.abc import x, y
    code = BBCode({x: 6, y: 6}, x**3 + y + y**2, y**3 + x + x**2, field=2)
    hx, hz = np.asarray(code.matrix_x, dtype=np.int8), np.asarray(code.matrix_z, dtype=np.int8)
    assert verify_css(hx, hz)
    assert hx.shape[1] == 72 and gf2_fast.compute_k(hx, hz) == 12
    found = distance_rand_witness(hx, hz, trials=1000, seed=20261002,
                                  backend="fast", threads=1, pair_depth=24)
    assert found.weight == 6 and not found.rejected, found
    out = ROOT / "evidence/control"
    out.mkdir(parents=True, exist_ok=True)
    doc = make_submission(hx, hz, name="[[72,12,6]] literature positive control",
                          construction="Bravyi et al. 2023 BB positive control, l=m=6.",
                          authors=["@EshMis"], family="bivariate-bicycle", trials=1,
                          seed=20261002, date="2026-10-02")
    tighten(doc, hx, hz, found)
    errs = save_submission(doc, out / "candidate.json")
    if errs:
        raise RuntimeError(errs)
    atomic_json(out / "witness.json", found._asdict())
    rows = board_rows()
    assert required_distance(rows, 72, 12, 6) > 6, "Known control incorrectly screened as a new point"
    record = {"status": "passed", "n": 72, "k": 12, "d_upper": 6,
              "board_css_entries": len(rows), "qldpc": importlib.metadata.version("qldpc")}
    atomic_json(out / "COMPLETE.json", record)
    print(json.dumps(record), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", choices=["bb", "lp", "control"], required=True)
    ap.add_argument("--seed", type=int, default=20261002)
    ap.add_argument("--count", type=int, default=20)
    ap.add_argument("--stages", default="300,5000,50000")
    ap.add_argument("--run", default="initial")
    ap.add_argument("--campaign", choices=["initial", "improve"], default="initial")
    ap.add_argument("--specs", type=Path, help="Optional predeclared JSON list of specifications")
    ap.add_argument("--offset", type=int, default=0)
    args = ap.parse_args()
    if args.offset < 0 or args.count < 1:
        ap.error("offset must be nonnegative and count must be positive")
    assert importlib.metadata.version("qldpc") == "0.4.0"
    if args.lane == "control":
        control()
        return
    module = importlib.import_module("generators_" + args.lane)
    outdir = ROOT / "results" / args.run / f"{args.lane}-{args.seed}"
    outdir.mkdir(parents=True, exist_ok=True)
    rows = board_rows()
    records = []
    if args.specs:
        all_specs = json.loads(args.specs.read_text())
        if not isinstance(all_specs, list) or len(all_specs) < args.offset + args.count:
            ap.error("specs must contain a list covering the requested offset and count")
        specifications = all_specs[args.offset:args.offset + args.count]
    else:
        generator = module.candidates if args.campaign == "initial" else module.next_candidates
        specifications = itertools.islice(generator(args.seed, args.offset + args.count),
                                          args.offset, None)
    for i, spec in enumerate(specifications):
        record = screen_one(spec, constructor(module, spec), rows, outdir,
                            (args.seed * 1009 + args.offset + i) % (2**31),
                            [int(x) for x in args.stages.split(",")])
        records.append(record)
    assert len(records) == args.count, (len(records), args.count)
    atomic_json(outdir / "COMPLETE.json", {"status": "complete", "count": len(records),
                "host": socket.gethostname(), "finished_unix": time.time(),
                "survivors": [r["id"] for r in records if r["status"] == "needs_official_validation"]})


if __name__ == "__main__":
    main()
