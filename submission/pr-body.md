Adds [[455,39,6]] with maximum check weight 5, constructed with qLDPC 0.4.0 as a cyclic lifted product over GF(2)[C35]. The code adds a nondominated point to the CSS weight-6 x unrestricted frontier; no existing entry with n <=455, k >=39 and w <=5 has d >=4 at the checked board revision.

The unchanged trusted validator returned passed=true and board_advancing=true, with no exact-fingerprint or WL-signature duplicate. The upstream SAT certifier returned UNSAT below weight 6 on both sides, and both weight-6 witnesses are included. This is local solver certification; maintainer confirmation is requested for the leaderboard's exact tier. Wider literature novelty remains unverified.

Construction, search budgets, failed bicycle candidates and a complete matrix-reproduction recipe are in notes/455-39-6.md. The public evidence repository is [EshMis/qec-frontier at 2bba8b9](https://github.com/EshMis/qec-frontier/tree/2bba8b9).

Validation: the known [[72,12,6]] control, all 11 upstream SAT regression tests, official candidate validation, exact SAT checks, and an independent reconstruction of both submitted parity-check matrices passed. The final JSON also passed the trusted verifier with a fresh seed. This PR adds one code and its research note.

The full local frontier gate also passed: all 8,000,000 accelerated trials completed, plus the Python RIS pass (79,600-trial target, 240-second cap), with no lighter logical. The [deep-gate receipt](https://github.com/EshMis/qec-frontier/blob/4c1f9a9/evidence/455-39-6/deep-gate/455-39-6.json) records the actual budgets; its fixture SHAs are explained in the adjacent [snapshot mapping](https://github.com/EshMis/qec-frontier/blob/4c1f9a9/evidence/455-39-6/gate-snapshot.json). Shirokane terminal accounting confirms exit 0 and failed=0.
