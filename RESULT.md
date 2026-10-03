# [[455,39,6]] with weight-5 checks

The selected code is the lifted product over GF(2)[C35] of

```
A = [[1, 1, 1], [1, x^10, x^11]]
B = [[1, 1, 1], [1, x^24, x^26]],  x^35 = 1.
```

Construction uses **qLDPC 0.4.0**. The two parity-check matrices each have 210 rows and 455 columns. The dimension is 39 and the maximum check weight is 5. Both sides have a weight-6 logical witness.

The unmodified challenge validator at commit `c2ebca1713c89277dbd6ddf3ee587cbf7f1a9d23` accepts the code, finds no exact-fingerprint or WL-signature duplicate, and reports it undominated in CSS `weight-6 × unrestricted`. No existing code is strictly dominated: this extends a frontier tradeoff rather than replacing a specific incumbent. The upstream main branch was fetched again before publication and had not advanced beyond that snapshot.

The upstream SAT certifier returned **UNSAT for weight ≤5 on both sides**, establishing dX=dZ=6 together with the supplied witnesses. The certificate is a solver verdict, not a standalone proof object. Local certification is distinct from the leaderboard's maintainer-confirmed exact badge.

The code and construction note are public in [challenge PR #2674](https://github.com/unitaryfoundation/qldpc-challenge/pull/2674), at submitted revision `e81369a9799f740799cf58b2788351e69d5f2914`. Both upstream workflows await maintainer approval. No upstream acceptance or exact badge is claimed; see the [submission status snapshot](evidence/submission-status.json).

## Evidence

- [Final code](submission/455-39-6.json), including both witnesses.
- [Construction recipe](results/profile-lp/lp-20261002/5f3a6a45fb0e94615da1/recipe.json).
- [Search ladder](results/profile-lp/lp-20261002/5f3a6a45fb0e94615da1/screen.json): fresh seeds at 300, 5,000 and 50,000 accelerated trials, pair depth 24; all retained d≤6. Trial counts are the accelerator's overall API budgets, not per-side counts.
- [Official validation](evidence/455-39-6/validation.json): accepted, frontier-advancing, no duplicate; fresh 8,000-trial refutation found nothing lighter.
- [SAT certificate](evidence/455-39-6/sat-certificate.json): both sides UNSAT, 39 logical classes checked, no symmetry pruning, 300-second per-side cap; measured solves 5.8 and 5.5 seconds.
- [Full deep-gate receipt](evidence/455-39-6/deep-gate/455-39-6.json): the official frontier gate completed all 8,000,000 accelerated trials, plus the Python RIS pass (79,600-trial target, 240-second cap), without refutation. The [fixture mapping](evidence/455-39-6/gate-snapshot.json) distinguishes local fixture SHAs from the actual upstream verifier snapshot.
- [Terminal scheduler accounting](evidence/accounting.json): validation and certification job exited 0 with failed=0. The separate deep-gate job also exited 0 with failed=0.
- [Environment](evidence/environment-lock.txt), [known-code positive control](evidence/control/COMPLETE.json), and [official known-code comparison](evidence/control/official-known-code-verdict.json). All 11 upstream SAT regression tests passed, including overclaim-refutation and missing-logical-class controls.

The publication JSON replaces the provisional name/provenance and changes the two confidence labels from upper_bound to exact. Matrices, n, k, d and witnesses are unchanged from the audited candidate. The separate reproduction job rebuilds both matrices from the saved recipe and verifies the final JSON.

## Scope of the search

Five independent-base lifted-product candidates were screened in the initial pilot, over groups of orders 35–39. They produced `(n,k,d_upper)` of (455,39,6), (468,40,4), (481,41,6), (494,42,4), and (507,43,6), all at weight 5. Only the first two received exact certification in this run. The five full pipelines took 86.73 seconds combined, including the first import/JIT overhead; this is not total project compute.

Ten bicycle-family candidates were also screened. Eight fell below their board-relative numeric bar, one had k=0, and one remained a screening survivor. That survivor has not been validated or certified and is not reported as a result. Every measured witness and screening outcome is retained.

This result claims a new challenge-board parameter point, not a new code family or an exhaustive literature record. No circuit-level performance or logical error rate is claimed.

## Reproduce

Use the pinned environment and upstream snapshot in README.md. Run `python scripts/reproduce_455.py` to rebuild and compare both parity-check matrices exactly. Run `python scripts/validate.py submission/455-39-6.json --out evidence/recheck --exact --tlim 300` to run the official candidate gate and SAT certifier. Both scripts assume the upstream checkout under `external/qldpc-challenge`.
