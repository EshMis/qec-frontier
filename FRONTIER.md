# Discoveries in plain English

We have 18 exact-certified discoveries; 15 remain nondominated among our own
results. Three earlier points have been superseded by direct improvements. Every entry
passed the official challenge validator against the checked board. Upstream
acceptance is separate: PR #2674 remains under review.

Physical qubits are the hardware used. Logical qubits are the protected qubits
stored. A distance-d code guarantees correction of any floor((d-1)/2) physical-qubit
errors under ideal error correction. Check weight is the largest number of qubits
involved in one parity check. Distance is certified globally; this does not claim
separate exact X and Z distances when a stored side witness is heavier than d.

| Physical qubits | Logical qubits | Distance | Errors corrected | Largest check | Status | Meaning |
|---:|---:|---:|---:|---:|---|---|
| 455 | 39 | 6 | 2 | 5 | Superseded locally | Initial result; now superseded by smaller or higher-capacity codes. |
| 468 | 40 | 4 | 1 | 5 | Superseded locally | Initial tradeoff; now superseded by smaller, higher-capacity and better-protected codes. |
| 312 | 26 | 8 | 3 | 6 | Current local frontier | Corrects three errors. Versus the initial455-qubit code:143 fewer physical qubits,13 fewer logical qubits, and checks of six instead of five. |
| 264 | 22 | 8 | 3 | 6 | Current local frontier | Same three-error protection as312/26, using48 fewer physical qubits and storing four fewer logical qubits. |
| 288 | 24 | 8 | 3 | 6 | Current local frontier | Same three-error protection as312/26, using24 fewer physical qubits and storing two fewer logical qubits. |
| 416 | 39 | 6 | 2 | 5 | Current local frontier | Direct improvement over455/39: same capacity and protection,39 fewer physical qubits. |
| 455 | 43 | 6 | 2 | 5 | Current local frontier | Direct improvement over455/39: four more logical qubits with the same size, protection and checks. |
| 468 | 45 | 6 | 2 | 5 | Current local frontier | Direct improvement over468/40: five more logical qubits and two-error rather than one-error protection. |
| 390 | 43 | 4 | 1 | 5 | Superseded locally | Direct improvement over468/40:78 fewer physical qubits and three more logical qubits, with the same protection. |
| 364 | 41 | 4 | 1 | 5 | Current local frontier | Direct improvement over468/40:104 fewer physical qubits and one more logical qubit, with the same protection. |
| 520 | 51 | 6 | 2 | 5 | Current local frontier | Six more logical qubits than468/45, using52 more physical qubits, with the same two-error protection. |
| 351 | 33 | 6 | 2 | 5 | Current local frontier | Six fewer logical qubits than416/39, using65 fewer physical qubits, with the same two-error protection. |
| 78 | 11 | 4 | 1 | 5 | Current local frontier | Smallest verified block so far:11 logical qubits in78 physical qubits, correcting one error. |
| 273 | 33 | 4 | 1 | 5 | Current local frontier | Same33-logical capacity as351/33, saving78 physical qubits but correcting one error instead of two. |
| 312 | 37 | 4 | 1 | 5 | Current local frontier | Four more logical qubits than273/33, using39 additional physical qubits, with equal one-error protection. |
| 351 | 39 | 4 | 1 | 5 | Current local frontier | Same39-logical capacity as416/39, saving65 physical qubits but correcting one error instead of two. |
| 390 | 45 | 4 | 1 | 5 | Current local frontier | Direct improvement over390/43: two more logical qubits with equal size, protection and checks. |
| 429 | 49 | 4 | 1 | 5 | Current local frontier | Four more logical qubits than390/45, using39 additional physical qubits, with equal one-error protection. |

There is no single overall ranking: fewer physical qubits, more logical qubits,
larger distance and smaller checks compete. A direct improvement is at least as
good on all four measures and better on at least one. Other new points are
reported as tradeoffs, with the cost stated explicitly.

Evidence and dominance relationships are indexed in
[frontier-points.json](evidence/frontier-points.json). Screening survivors and
unproved distance estimates are excluded. The user requested continuous active
search; the scheduled follow-up was deleted.
