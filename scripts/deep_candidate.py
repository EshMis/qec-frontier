"""Run the unchanged upstream deep gate against an isolated code-file fixture."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "external/qldpc-challenge"
SOURCE_SHA = "c2ebca1713c89277dbd6ddf3ee587cbf7f1a9d23"
ap = argparse.ArgumentParser()
ap.add_argument("slug")
ap.add_argument("--seed", type=int, required=True)
args = ap.parse_args()
candidate = ROOT / "submission" / (args.slug + ".json")
doc = json.loads(candidate.read_text())
assert args.slug == f"{doc['n']}-{doc['k']}-{doc['distance']['d']}"
subprocess.run([sys.executable, str(UPSTREAM / "verify/check_validator_integrity.py")], check=True)
fixture = ROOT / "scratch" / ("gate-" + args.slug)
fixture.mkdir(parents=True, exist_ok=False)
shutil.copytree(UPSTREAM / "codes", fixture / "codes")
def git(*parts):
    return subprocess.check_output(["git", *parts], cwd=fixture, text=True).strip()
git("init", "-q", "-b", "main")
git("config", "user.name", "QEC local gate snapshot")
git("config", "user.email", "local-gate@example.invalid")
git("add", "codes")
git("commit", "-q", "-m", "Pinned upstream board code snapshot")
base = git("rev-parse", "HEAD")
shutil.copyfile(candidate, fixture / "codes" / candidate.name)
git("add", "codes/" + candidate.name)
git("commit", "-q", "-m", "Candidate under test")
evidence = ROOT / "evidence" / args.slug
evidence.mkdir(parents=True, exist_ok=True)
(evidence / "gate-snapshot.json").write_text(json.dumps({
    "snapshot_base": base, "snapshot_head": git("rev-parse", "HEAD"),
    "upstream_source": SOURCE_SHA,
    "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
    "note": "Fixture SHAs identify a local code-only Git fixture. Verifier source stays at the unchanged pinned upstream snapshot."}, indent=2) + "\n")
subprocess.run([sys.executable, "-u", str(UPSTREAM / "verify/gate_changed.py"), base,
    "--code-root", str(fixture), "--receipt-dir", str(evidence / "deep-gate"),
    "--seed", str(args.seed), "codes/" + candidate.name], check=True)
