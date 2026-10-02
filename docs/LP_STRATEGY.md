# Lifted-product lane

Snapshot: upstream `unitaryfoundation/qldpc-challenge` commit
`c2ebca1713c89277dbd6ddf3ee587cbf7f1a9d23`, inspected 2026-10-02. The snapshot
contains **1680 CSS entries**, of which **66** have the `lifted-product` family
tag. These are measured file counts, not an estimate of all published codes.

## Immediate targets

The first lane uses full 2x3 monomial base matrices A and B over GF(2)[G]:

```
A = [[1, 1, 1], [1, a, b]]
B = [[1, 1, 1], [1, c, d]]
```

Every entry is a single group element. Each pair `(a,b)` and `(c,d)` must
generate G, and the two bases are chosen independently and are unequal. The
lift has **n = 13|G|** and maximum check weight **w = 5**. The stored target
`k = |G|+4` is a search threshold, not an assertion about the constructed
code. The common runner must compute k from the actual binary ranks.

The following are sufficient targets to escape domination by every CSS entry
in the snapshot. The values are **computed board-relative thresholds**, not
candidate measurements or predictions of attainable distances.

| First lane group | n | Target k | Sufficient d | w |
|---|---:|---:|---:|---:|
| C35 | 455 | 39 | 4 | 5 |
| C18 semidirect(-1) C2 | 468 | 40 | 4 | 5 |
| C37 | 481 | 41 | 4 | 5 |
| C19 semidirect(-1) C2 | 494 | 42 | 4 | 5 |
| C13 semidirect(3) C3 | 507 | 43 | 4 | 5 |

For each target `(n,k,w)`, the threshold was calculated as
`1 + max(existing d for n_existing <= n, k_existing >= k, w_existing <= w)`.
This is deliberately sufficient: equal parameters can sometimes coexist on
the frontier, but they are not counted as a new parameter target here. The
live official frontier check must replace these priority hints before a claim.

The next moderate-size gaps are `(533,45,d>=4,w=5)`,
`(559,47,d>=4,w=5)`, and `(572..611,k=48..51,d>=5,w=5)` at the included group
orders. The small-instance lane targets `(91,11,6,5)`, `(104,12,6,5)`,
`(117,13,6,5)`, `(130,14,6,5)`, and `(143,15,6,5)`. The latter may make exact
certification more affordable; this is an unmeasured scheduling hypothesis.

The initial twenty specifications cycle through the five first-lane groups
four times. Subsequent specifications visit additional presentations and small
groups, then repeat that catalog with fresh deterministic bases. Sizes stop
at n=676. Every specification preserves its random seed, sequence index,
group presentation, numeric element convention, and both complete bases.

## Construction API and reproducibility

The implementation is `scripts/generators_lp.py`:

```python
for spec in candidates(seed=20261002, count=20):
    hx, hz = construct(spec)
```

Construction requires exactly **qLDPC 0.4.0**, release tag
[`v0.4.0`](https://github.com/qLDPCOrg/qLDPC/tree/v0.4.0), resolved to
`02ee765f1a2b315152b8627c5d3effe3e258e5a2` when inspected.
The implementation builds a Cayley table and passes it to
`qldpc.abstract.Group.from_table`, builds the bases with
`GroupRing` and `RingArray.build`, and invokes
`qldpc.codes.LPCode(A, B, set_logicals=False)`. It returns copies of
`code.matrix_x` and `code.matrix_z` as `numpy.uint8` arrays.

For `G = C_l1 semidirect_q C_l2`, numeric element `u*l2+v` denotes `a^u b^v`
and multiplication is `(u,v)(s,t) = (u + q^v*s mod l1, v+t mod l2)`.
The constructor checks that every product of qLDPC's enumerated members agrees
with the specified numeric table, not only that the identity has index zero.

qLDPC's own ring Kronecker product handles the left/right bimodule when G is
noncommutative. A binary Kronecker product of already-expanded seed matrices
would give a different construction and is not used. These API details were
checked against the tagged sources for
[`LPCode`](https://github.com/qLDPCOrg/qLDPC/blob/v0.4.0/src/qldpc/codes/quantum.py),
[`Group.from_table`](https://github.com/qLDPCOrg/qLDPC/blob/v0.4.0/src/qldpc/abstract/groups.py),
and [`abstract.kron`](https://github.com/qLDPCOrg/qLDPC/blob/v0.4.0/src/qldpc/abstract/linalg.py).

No direct sums, appended qubits, or puncturing are used. Requiring each seed's
pair to generate G removes proper-subgroup copies before construction; the
final CSS incidence graph still needs the common pipeline's connectivity
check. Algebraic equivalence beyond identical/swapped bases is not eliminated
by this generator; the trusted deduplication gate remains necessary.

## Why this is a targeted lane

The upstream September 16 fieldnote reports 16000 sampled nonabelian 2x3
monomial products on 122 groups, with screen distances 8–9 at larger sizes.
Those numbers are the authors' reported finite-budget observations, not
independently reproduced results here. The current snapshot has only six
weight-5 LP entries: `(416,36,8)`, `(520,44,8)`, `(546,46,8)`,
`(624,52,9)`, `(624,54,8)`, and `(676,71,4)`. This lane targets the newly
computed parameter gaps instead of repeating the old broad efficiency sweep.

Do not prioritize the already-studied one-row binomial/trinomial weight-6/8
routes without a new mechanism. Upstream's bounded surveys found short
seed-cycle logicals and large current-board dominators. Likewise, its random
3x3 radial LP run produced no surviving frontier advance after the initial
distance estimates were reduced by deeper searches. Those surveys limit their
tested draws and budgets; they do not prove the whole families exhausted.

Source fieldnotes, pinned to the inspected snapshot:

- [2x3 monomial and one-row LP sweep](https://github.com/unitaryfoundation/qldpc-challenge/blob/c2ebca1713c89277dbd6ddf3ee587cbf7f1a9d23/fieldnotes/2026-09-16-lifted-product-girth-cap.md)
- [Weight-8 one-row seam](https://github.com/unitaryfoundation/qldpc-challenge/blob/c2ebca1713c89277dbd6ddf3ee587cbf7f1a9d23/fieldnotes/2026-09-18-nonabelian-lifted-product-weight8-seam.md)
- [Radial sweep and distance refutations](https://github.com/unitaryfoundation/qldpc-challenge/blob/c2ebca1713c89277dbd6ddf3ee587cbf7f1a9d23/fieldnotes/2026-09-11-lifted-surgery-imports-radial-and-koszul-leads.md)

## Verification and claim boundary

Run all matrix construction, searches, and certification on Shirokane. Profile
one cyclic and one nonabelian candidate before a batch, then the largest
instance before extending to all groups. Preserve every discovered witness
through upstream `make_submission` and `save_submission` before escalation.

The generator contains no distance solver. A reported RIS result is an upper
bound. A passing official refutation gate is still an upper bound. Exactness
requires the trusted SAT/MILP certificate; a timeout establishes no lower
bound. In particular, finding a weight-4 logical does not prove d=4.

Only `verify/validate_candidate.py` returning `passed: true`, together with
the current official board-advance verdict, makes a candidate a frontier
submission. New `(n,k,d,w)` on this board does not establish worldwide
construction novelty. Record acceptance/merge separately from local validation.

Local checks completed during implementation: AST parsing, deterministic and
JSON-serializable output across 57 specifications, first-twenty ordering,
unequal connected seed pairs, valid group presentations, and recalculation of
every stored target threshold against the 1680 CSS files. No matrix
construction or distance computation was performed locally. Cluster
construction and end-to-end validation are owned by the lead pipeline.
