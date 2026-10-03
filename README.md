# QEC frontier search

Reproducible search for a new board-relative Pareto-frontier CSS qLDPC code in the [Unitary Foundation QEC Challenge](https://github.com/unitaryfoundation/qldpc-challenge).

Candidate families: bivariate/generalized bicycle and lifted product. Candidate generation uses `qldpc==0.4.0`. CPU searches and distance verification run in an isolated Shirokane environment.

The target is an undominated, nonduplicate, connected code under the official `(n, k, d, w)` rules. A candidate is a result only after the unmodified upstream `verify/validate_candidate.py` reports `passed: true`. A witnessed distance upper bound that survives refutation is never described as exact. Exact certification, when feasible, uses the upstream certifier separately.

Initial upstream snapshot: `c2ebca1713c89277dbd6ddf3ee587cbf7f1a9d23` (1,815 entries, retrieved 2026-10-02). Refresh the board before declaring a frontier advance and before submitting.

**Results, 2026-10-02:** 30 exact-certified discoveries, of which 27 remain nondominated after including our own improvements. Every recorded point passed the official validator and its board-advancement test. Highlights include `[[416,39,6]]` with check weight 5 (39 fewer physical qubits than our original result), `[[264,22,8]]` with weight 6 (three-error correction), `[[260,58,6]]` with weight 6, and `[[986,314,6]]` with weight 7 (our largest verified capacity).

These are local solver certifications; leaderboard acceptance and the exact badge require maintainer confirmation. Wider literature novelty is unverified. The original, now superseded result is preserved in [RESULT.md](RESULT.md).

The selected code is submitted in [challenge PR #2674](https://github.com/unitaryfoundation/qldpc-challenge/pull/2674). Upstream workflow execution currently awaits maintainer approval; submission is not leaderboard acceptance. The [status snapshot](evidence/submission-status.json) records the exact submitted revision and workflow runs.

See [FRONTIER.md](FRONTIER.md) for a plain-English comparison of every verified discovery and [the registry](evidence/frontier-points.json) for the complete evidence paths and dominance relationships. The active search continues during upstream review. The user-requested removal of the scheduled follow-up is complete.

## Reproduction

Clone the upstream repository into `external/qldpc-challenge` and check out the pinned snapshot above. `jobs/setup.sh` builds an isolated environment and compiles the upstream accelerated verifier. Search and validation jobs must limit their thread count to the scheduler allocation and write completion records only after success.

## Work ownership

This repository and the remote `~/qec-frontier` directory belong to chat `01a0feea-38ce-7c00-b3f8-7b5db89769f2`. Existing research environments and jobs are not modified.
