# QEC frontier search

Reproducible search for a new board-relative Pareto-frontier CSS qLDPC code in the [Unitary Foundation QEC Challenge](https://github.com/unitaryfoundation/qldpc-challenge).

Candidate families: bivariate/generalized bicycle and lifted product. Candidate generation uses `qldpc==0.4.0`. CPU searches and distance verification run in an isolated Shirokane environment.

The target is an undominated, nonduplicate, connected code under the official `(n, k, d, w)` rules. A candidate is a result only after the unmodified upstream `verify/validate_candidate.py` reports `passed: true`. A witnessed distance upper bound that survives refutation is never described as exact. Exact certification, when feasible, uses the upstream certifier separately.

Initial upstream snapshot: `c2ebca1713c89277dbd6ddf3ee587cbf7f1a9d23` (1,815 entries, retrieved 2026-10-02). Refresh the board before declaring a frontier advance and before submitting.

**Result, 2026-10-02:** `[[455,39,6]]`, maximum check weight **5**, extends the challenge's CSS `weight-6 × unrestricted` frontier at the snapshot above. The unmodified official validator returned `passed: true`, `board_advancing: true`, and no exact-fingerprint or WL-signature duplicate. The upstream SAT certifier proved both logical distances equal to 6: it returned UNSAT below 6 on each side, and both weight-6 witnesses are supplied. This is a local solver certificate; the leaderboard's exact badge requires maintainer confirmation. See [RESULT.md](RESULT.md).

A second local point, `[[468,40,4]]` with weight 5, passed the same validator and exact SAT certification. Public submission focuses on the first result. Wider literature novelty is unverified; these are new points relative to the challenge board, using an established construction family.

## Reproduction

Clone the upstream repository into `external/qldpc-challenge` and check out the pinned snapshot above. `jobs/setup.sh` builds an isolated environment and compiles the upstream accelerated verifier. Search and validation jobs must limit their thread count to the scheduler allocation and write completion records only after success.

## Work ownership

This repository and the remote `~/qec-frontier` directory belong to chat `01a0feea-38ce-7c00-b3f8-7b5db89769f2`. Existing research environments and jobs are not modified.
