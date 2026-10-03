"""Prepare publication metadata only after checking an exact evidence chain."""
import argparse
import hashlib
import json

from collect_points import ROOT, read_point

ap = argparse.ArgumentParser()
ap.add_argument("point_id")
args = ap.parse_args()
registry = json.loads((ROOT / "evidence/frontier-points.json").read_text())
point, = [p for p in registry["points"] if p["id"] == args.point_id]
assert not point["dominated_by"], "Do not prepare a superseded point"
measured = read_point(ROOT / point["evidence"])
assert measured and measured["id"] == point["id"]
source = ROOT / point["candidate"]
raw = source.read_bytes()
doc = json.loads(raw)
recipe = source.parent / "recipe.json"
spec = json.loads(recipe.read_text())
slug = f"{point['n']}-{point['k']}-{point['d']}"
dest = ROOT / "submission" / (slug + ".json")
assert not dest.exists(), dest
assert spec["family"] == "lifted-product", "This metadata formatter is LP-specific"
order = spec["group"]["order"]
assert spec["group"]["l2"] == 1, "This formatter is cyclic-only"
doc["name"] = f"[[{point['n']},{point['k']},{point['d']}]] weight-{point['w']} cyclic lifted-product code"
for side in ("X", "Z"):
    # UNSAT is below global d. A heavier side witness is still only an upper bound.
    doc["distance"][side]["confidence"] = (
        "exact" if doc["distance"][side]["value"] == point["d"] else "upper_bound")
doc["provenance"] = {
    "authors": ["@EshMis"],
    "construction": f"Lifted product over F_2[C_{order}], generator x. "
        f"A exponent rows={spec['matrix_a']}; B exponent rows={spec['matrix_b']}. "
        "Each exponent e denotes the monomial x^e. Constructed with qLDPC v0.4.0 LPCode(A,B).",
    "references": [], "date": "2026-10-02", "origin": "submission",
    "novelty": "unknown", "model": "GPT-6",
    "notes": f"Exact global distance {point['d']} certified by the unchanged upstream SAT "
        "certifier plus a matching logical witness. New frontier point relative to board "
        "c2ebca1713c89277dbd6ddf3ee587cbf7f1a9d23. Wider literature novelty unverified. "
        "Local solver certification is distinct from a maintainer-confirmed exact badge.",
}
original = json.loads(raw)
for key in ("checks", "n", "k", "code_type", "family"):
    assert doc[key] == original[key]
for side in ("X", "Z"):
    for key in ("value", "witness"):
        assert doc["distance"][side][key] == original["distance"][side][key]
assert doc["distance"]["d"] == original["distance"]["d"]
final = (json.dumps(doc, indent=2) + "\n").encode()
dest.write_bytes(final)
evidence = ROOT / "evidence" / slug
evidence.mkdir(parents=True, exist_ok=True)
(evidence / "publication.json").write_text(json.dumps({
    "source_candidate": point["candidate"], "source_evidence": point["evidence"],
    "source_sha256": hashlib.sha256(raw).hexdigest(),
    "publication_sha256": hashlib.sha256(final).hexdigest(),
    "recipe": str(recipe.relative_to(ROOT)),
    "unchanged": ["checks", "n", "k", "code_type", "family", "distance values and witnesses"],
    "next_required": "Independent matrix reconstruction and verification of final JSON",
}, indent=2) + "\n")
print(json.dumps({"candidate": str(dest.relative_to(ROOT)), "recipe": str(recipe.relative_to(ROOT)),
                  "side_labels": {s: doc['distance'][s]['confidence'] for s in ('X', 'Z')}}))
