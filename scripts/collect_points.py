"""Consolidate completed exact certificates without promoting screening guesses."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def dominates(a, b):
    weak = a["n"] <= b["n"] and a["k"] >= b["k"] and a["d"] >= b["d"] and a["w"] <= b["w"]
    return weak and any(a[key] != b[key] for key in ("n", "k", "d", "w"))


def read_point(evidence):
    complete = json.loads((evidence / "COMPLETE.json").read_text())
    if complete.get("status") != "complete" or not complete.get("exact"):
        return None
    inp = json.loads((evidence / "input.json").read_text())
    candidate = ROOT / inp["candidate"]
    raw = candidate.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == complete["candidate_sha256"] == inp["candidate_sha256"], candidate
    assert complete["validated_frontier"], candidate
    verdict = json.loads((evidence / "validation.json").read_text())
    cert = json.loads((evidence / "sat-certificate.json").read_text())
    assert verdict["passed"] and verdict["gates"]["novelty"]["board_advancing"], candidate
    assert cert["d_exact"], candidate
    doc = json.loads(raw)
    # The upstream solver tests both sides below the GLOBAL claim d. Its
    # per-side value is that tested threshold, not an independently located
    # per-side minimum; one stored witness can be heavier than the global d.
    assert cert["d"] == doc["distance"]["d"], candidate
    assert min(doc["distance"][s]["value"] for s in ("X", "Z")) == cert["d"], candidate
    for side in ("X", "Z"):
        assert cert["sides"][side]["exact"] and cert["sides"][side]["status"] == "UNSAT", candidate
        assert cert["sides"][side]["value"] == cert["d"], candidate
    n, k, d = doc["n"], doc["k"], doc["distance"]["d"]
    assert (n, k, d) == tuple(verdict["candidate"][key] for key in ("n", "k", "d")), candidate
    w = max(map(len, doc["checks"]["X"] + doc["checks"]["Z"]))
    return {"id": f"{n}-{k}-{d}-w{w}", "n": n, "k": k, "d": d, "w": w,
            "candidate": str(candidate.relative_to(ROOT)), "evidence": str(evidence.relative_to(ROOT)),
            "pull_request": None, "certified_unix": complete["finished_unix"]}


def main():
    registry = ROOT / "evidence/frontier-points.json"
    data = json.loads(registry.read_text())
    known = {point["id"] for point in data["points"]}
    measured = []
    for path in (ROOT / "results").glob("**/verification/COMPLETE.json"):
        point = read_point(path.parent)
        if point:
            measured.append(point)
    added = []
    for point in sorted(measured, key=lambda p: p["certified_unix"]):
        if point["id"] not in known:
            data["points"].append(point)
            added.append(point)
            known.add(point["id"])
    for point in data["points"]:
        point["dominated_by"] = [other["id"] for other in data["points"] if dominates(other, point)]
        point["status"] = "superseded_locally" if point["dominated_by"] else "locally_nondominated"
    tmp = registry.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    tmp.replace(registry)
    print(json.dumps({"new_points": added, "total_verified": len(data["points"]),
                      "currently_nondominated": sum(not p["dominated_by"] for p in data["points"])}, indent=2))


if __name__ == "__main__":
    main()
