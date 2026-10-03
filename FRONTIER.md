# Discoveries in plain English

Each entry below has passed the official challenge validator and exact distance
certification on Shirokane. "Frontier" refers to the checked challenge board;
upstream review and acceptance are separate. Physical qubits are the hardware
used. Logical qubits are the protected qubits stored. Distance d guarantees
correction of any floor((d-1)/2) physical-qubit errors under ideal error correction.
Check weight is the largest number of qubits involved in one parity check.

| Point | Physical qubits | Protected logical qubits | Guaranteed errors corrected | Largest check | Meaning |
|---|---:|---:|---:|---:|---|
| [[455,39,6]] | 455 | 39 | 2 | 5 | Our strongest initial verified protection at check weight 5. Submitted in PR #2674. |
| [[468,40,4]] | 468 | 40 | 1 | 5 | One more logical qubit, but 13 more physical qubits and less error protection. A tradeoff, not an overall improvement. |
| [[312,26,8]] | 312 | 26 | 3 | 6 | Compared with the first result: 143 fewer physical qubits and one more error corrected, but 13 fewer logical qubits and checks of six rather than five. |

There is no single overall ranking: fewer physical qubits, more logical qubits,
larger distance and smaller checks compete. A direct improvement is at least as
good on all four measures and better on at least one. Other new points are
reported as tradeoffs, with the cost stated explicitly.

Evidence is indexed in [frontier-points.json](evidence/frontier-points.json).
Review status is in [submission-status.json](evidence/submission-status.json).
Screening survivors and unproved distance estimates do not appear in this table.
