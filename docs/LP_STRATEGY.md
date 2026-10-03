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

## Improvement campaign after the first two certified points

The local artifacts for `[[455,39,6]], w=5` and `[[468,40,4]], w=5` were read
back: each has an official `passed: true` frontier verdict and a SAT certificate
with `d_exact: true` and UNSAT on both sides below its supplied witness weight.
These are local solver-certified results; public acceptance remains separate.
The live upstream HEAD still matched the snapshot above at this inspection.

`next_candidates(seed, count)` is the new deterministic campaign interface.
`candidates` and `construct` remain compatible with the original recipes;
the five saved first-campaign recipes were compared as JSON with regenerated
specifications and match exactly. The first eleven improvement slots are:

| Slot | Group and subgroup indices | Proposed n,k,d,w | Current sufficient board d | Improvement sought |
|---|---|---|---:|---|
| 0 | C32, indices 4 and 1 | 416,39,6,5 | 4 | Same k,d,w as 455-qubit point, 39 fewer qubits |
| 1 | C33, indices 3 and 1 | 429,39,6,5 | 4 | Alternate compression route |
| 2 | C35, indices 5 and 1 | 455,43,6,5 | 4 | Four more logicals at the same n,d,w |
| 3 | C36, indices 4 and 3 | 468,45,6,5 | 4 | More logicals and higher distance than 468,40,4 |
| 4 | C30, indices 5 and 6 | 390,43,4,5 | 4 | Fewer qubits and more logicals than 468,40,4 |
| 5 | C28, indices 4 and 7 | 364,41,4,5 | 4 | Smaller alternative at the same distance 4 |
| 6 | C9 semidirect(-1) C4 | 468,40,7,5 | 5 | Escape the cyclic distance-six ceiling |
| 7 | C5 semidirect(-1) C4 | 260,24,7,5 | 7 | Higher distance at smaller n |
| 8 | C4 semidirect(-1) C4 | 208,20,7,5 | 7 | Higher distance at smaller n |
| 9 | C6 semidirect(-1) C4 | 312,28,7,5 | 7 | Higher distance at smaller n |
| 10 | C11 semidirect(-1) C4 | 572,48,8,5 | 5 | More logicals with distance above the cyclic ceiling |

All table entries are **targets, not measured candidates**. The board column
was computed from the 1680-entry snapshot plus the two LP local results and
the local BB point `[[312,26,8]], w=6`, whose official validation and SAT
certificate were also read back successfully; the BB entry
does not enter a w=5 comparison. The goal distance is sometimes deliberately
higher than the minimal board threshold. The runner should use
`max(current_board_threshold, spec["target"]["d_min"])`, so the first four
slots retain their same-distance compression/rate goal. Repeating the catalog
draws fresh deterministic bases. Profile through slot 10 before a batch that
includes its larger block length.

### Complementary seed subgroups are not disconnected padding

The first campaign required each classical seed's pair to generate the whole
group. That is sufficient but unnecessarily restrictive. For a cyclic group
of order N and bases with exponents `(a,b)` and `(c,d)`, define

```
gA = gcd(N,a,b),  gB = gcd(N,c,d).
```

Each classical seed separately has gA or gB connected components. Components
of the **combined** lifted-product incidence graph are the orbits of left
multiplication by the first seed subgroup and right multiplication by the
second. For a cyclic group there are `gcd(gA,gB)` such orbits, so coprime
indices make the combined code connected. The common pipeline's actual
incidence-component check must still confirm this. No qubits or stabilizers
are appended, and no direct sum is used.

The dimension prediction for this normalized cyclic shape is

```
k = N + gA + gB + 2*gcd(gA,gB).
```

Algebraic derivation: over `R=GF(2)[x]/(x^N-1)`, elementary invertible row and
column operations reduce a base to a contractible unit block plus
`[sA,0]`, with `sA=x^gA+1`; likewise for B. In the product, the two free
columns contribute N logical dimensions. Pairing a free column with `sA`
or `sB` contributes gA or gB. The remaining two-block complex contributes
twice the degree of `gcd(sA,sB,x^N-1)`, which is `2*gcd(gA,gB)`.
This derivation does not assume odd N or semisimplicity. It is a mathematical
prediction here; actual binary rank readback remains required for every code.

### Why this cyclic 2x3 monomial family cannot exceed distance six

The limitation is specific to this base shape, not to all cyclic LP codes.
For a normalized base over the commutative ring R,

```
A = [[1,1,1],[1,a,b]],    vA = (a+b, 1+b, 1+a)^T,
```

`A*vA=0`. With distinct nonidentity a,b, vA has exactly six binary nonzero
coordinates. Define vB analogously. Insert vA into one sector-one block
column and put zeros in the other sector; this commutes with the relevant
checks. Its nontriviality follows by multiplying the sector-one block matrix
by the cofactor vector for the opposite base, with the ring involution
`x -> x^-1` when required by the binary transpose convention: every
stabilizer maps to zero, whereas an appropriate chosen block column does not.

Why a nonzero column exists: the cofactor entries generate ideals
`IA=(x^gA+1)` and `IB=(x^gB+1)`. Their product is nonzero in R because
`gA+gB<N` for these seeds (each has at least three distinct monomials in its
support subgroup, hence each index is at most N/3). The product polynomial
has degree less than N and cannot vanish modulo `x^N-1`. Thus some cofactor
entry product is nonzero and one of the weight-six line operators is logical.
Interchanging the bases gives the other side. This supplies the algebraic
upper bound `dX<=6, dZ<=6`; it supplies no lower bound.

This is an explicit construction argument, related to the classical
cofactor/permanent upper-bound mechanism of
[Smarandache and Vontobel](https://arxiv.org/abs/0901.4129), not a conclusion
drawn from several RIS runs returning six. The lead should review the
argument before using it outside this search plan. Candidate claims continue
to rely on the official witnesses and certificate. There is no reason to
spend a cyclic 2x3 campaign trying to prove d>=7.

For the nonabelian slots, the cofactor cancellation uses commutativity and
does not apply. The generator removes seed 4-cycles and short element-order
obstructions, but these are structural sampling filters, **not quantum-distance
certificates**. No universal nonabelian distance bound is asserted. These slots
retain the same qLDPC LPCode constructor and check weight 5; changing the
group action, rather than raising the check weight, is the controlled change.

Implementation checks for the improvement campaign: eleven deterministic,
JSON-serializable specifications, exact prescribed cyclic subgroup indices,
coprime combined indices, algebraic dimension targets, and unchanged original
recipes. No matrix construction or quantum-distance computation was run locally.

### Driver contract review for the improvement campaign

The actual `board_rows` implementation loaded 1680 upstream CSS records and
the three locally certified records. Each local candidate's byte hash matched
its completion receipt; the official validation files passed and advanced the
board, and both SAT sides were UNSAT at the claimed distances. In-memory
negative controls using the actual function rejected modified candidate bytes,
`exact: false`, `validated_frontier: false`, and a mismatched registry k value.
The receipt producer binds the successful official validation and exact result
to the same bytes. These checks read JSON only; they do not rerun a solver.

Two driver issues were reported to the lead without changing that shared file:
`--offset` initially skipped entries only with `--specs`, so generated streams
needed equivalent slicing or an explicit restriction; short or invalid spec
slices needed rejection before construction rather than after screening.
The lead owns their fixes and remote deployment. The generator was frozen once
the first eight improvement recipes were snapshotted for Shirokane job
129135034. That job's results, including ranks and distances, are separate from
the algebraic targets documented above.

## V2: exhaustive proper-subgroup integer targets through N=53

Before freezing v2, the local result files were read back for five additional
points: `[[416,39,6]]`, `[[455,43,6]]`, `[[468,45,6]]`, `[[390,43,4]]`, and
`[[364,41,4]]`, all with w=5. Each has an official passed/advancing verdict,
an exact SAT certificate, and a completion hash matching its candidate bytes.
These measurements join the first two LP points in v2's pruning snapshot.
Upstream acceptance is still a separate event.

`cyclic_goal_catalog_v2()` enumerates **integer goals before seed generation**.
It covers every N from 3 through 53 and unordered divisor pair `gA<=gB`, with
`gcd(gA,gB)=1` and at least one proper seed subgroup (`gA>1` or `gB>1`). It
uses the dimension formula above, with d6 and d4 as separate objectives.
This is exhaustive for those integer choices, not exhaustive over all qLDPC
constructions or graph isomorphism classes. Individually connected seed pairs
`gA=gB=1` are outside this new catalog and remain in the original generator.

For the distance-six objective, both subgroup orders `M=N/g` must be at least
seven. A three-shift seed has no square precisely when its six signed nonzero
differences are distinct. This is impossible at M<7, and `{0,1,3}` supplies
an existence witness for every M>=7. The generated seeds also undergo this
explicit difference check. For the distance-four objective, M>=3 suffices for
three distinct monomials; squares are allowed. These conditions prove only
structural feasibility. They do not establish quantum-distance lower bounds.

Measured catalog counts, from the frozen board snapshot plus seven certified
local LP points:

| Objective | Admissible integer goals | Not dominated by existing points | Preferred parameter goals |
|---|---:|---:|---:|
| d6, no seed square | 56 | 23 | 6 |
| d4, squares allowed | 133 | 61 | 13 |

The preferred goals maximize k while minimizing n among currently unmeasured
goals of the same target distance. This preference does not certify a goal or
discard lower-priority alternatives: all 84 goals surviving existing-point
pruning remain in the stream. Two distinct subgroup choices with the same
parameters are retained where they describe different seed geometry.

The six preferred d6 choices are:

| N | gA,gB | Target n,k,d,w |
|---:|---|---|
| 27 | 1,3 | 351,33,6,5 |
| 40 | 4,5 | 520,51,6,5 |
| 45 | 3,5 | 585,55,6,5 |
| 48 | 1,6 | 624,57,6,5 |
| 48 | 3,4 | 624,57,6,5 |
| 49 | 1,7 | 637,59,6,5 |

The preferred d4 choices are `(N,gA,gB,k)` = `(6,1,2,11)`,
`(21,3,7,33)`, `(24,3,8,37)`, `(27,1,9,39)`, `(30,3,10,45)`,
`(33,3,11,49)`, `(36,1,12,51)`, `(36,4,9,51)`, `(39,3,13,57)`,
`(42,3,14,61)`, `(45,1,15,63)`, `(48,3,16,69)`, and `(51,3,17,73)`.
All have n=13N and w=5. In particular, the N6 choice seeks a new small point
`[[78,11,4]]`; it is not a claimed result.

`next_candidates_v2(seed,count)` interleaves one preferred d6 target with up to
three preferred d4 targets, then visits the remaining undominated goals. For
seed 20261002, its first eight recipes have the following second-row exponents;
both first rows are `[0,0,0]` (three identity monomials):

| Slot | N | A second row | B second row | Target n,k,d,w |
|---:|---:|---|---|---|
| 0 | 27 | 0,5,8 | 0,6,9 | 351,33,6,5 |
| 1 | 6 | 0,4,5 | 0,2,4 | 78,11,4,5 |
| 2 | 21 | 0,6,12 | 0,7,14 | 273,33,4,5 |
| 3 | 24 | 0,3,12 | 0,8,16 | 312,37,4,5 |
| 4 | 40 | 0,8,36 | 0,10,15 | 520,51,6,5 |
| 5 | 27 | 0,15,26 | 0,9,18 | 351,39,4,5 |
| 6 | 30 | 0,3,6 | 0,10,20 | 390,45,4,5 |
| 7 | 33 | 0,6,21 | 0,11,22 | 429,49,4,5 |

The first-eight batch needs a new cluster profile at slot 4 (n520). The full
catalog reaches n663 among goals surviving the snapshot's pruning, so a larger
batch requires a corresponding largest-instance profile. Every row above is
a construction target pending rank, connectivity, official witness, and exact
certificate checks.

Recipes are deduplicated under independent seed translations and reversals,
common multiplication of both seeds by a unit modulo N, and exchange of A/B.
These moves are monomial/permutation equivalences. This is not a complete code
isomorphism test; the official novelty check remains authoritative. The seven
certified LP tuples prune every integer goal matching an already tested v1
cyclic target, so those results are not recycled as new progress. The generator
freezes the pruning projection for reproducibility; the common driver must
still raise the bar using newer board entries and certified local results.

Nonabelian search remains a possible route beyond six, but v1's two tested
nonabelian recipes found witnessed upper bounds of six at n468 and five at
n260. These are individual screening outcomes, not a family impossibility
result. No new nonabelian campaign is mixed into v2: the concrete next tests
exploit the remaining cyclic size/capacity gaps while keeping w=5 fixed.

Implementation checks: the pruning decision for all 189 integer goals agrees
with all 1680 upstream CSS records plus the seven local points; 84 generated
specs are deterministic and JSON serializable, satisfy their prescribed
subgroup indices and square filters, and have distinct recorded equivalence
keys. Canonical keys are invariant under the documented moves. The original
five saved recipes and eight v1 recipes reproduce exactly. These are lightweight
integer/JSON checks; no local matrix construction or distance computation was
performed. The shared driver and frozen constructor were not edited.

### Algebra and reporting recheck at the v2 launch

The dimension formula can also be checked directly by ranks, avoiding a
semisimple-ring assumption. After cancellation of the contractible unit blocks,
the two seed rows become `[sA,0]` and `[sB,0]`. Their reduced product has 5N
qubits. Put `h=gcd(gA,gB)`. Multiplication by sA has binary rank `N-gA`, and
the map with image ideal `(sA,sB)` has rank `N-h`; hence

```
rank(HX) = (N-gA) + (N-h)
rank(HZ) = (N-gB) + (N-h)
k = 5N - rank(HX) - rank(HZ) = N+gA+gB+2h.
```

For the distance ceiling, qLDPC's commutative HGP convention is
`HX=[A tensor I, I tensor B†]` and `HZ=[I tensor B, A† tensor I]`, where
the dagger incorporates the ring involution. The weight-six vector
`c=vA tensor e_j`, supported in the first sector, lies in `ker(HX)`.
The map `I tensor vB†` annihilates every Z boundary but sends c to
`vA*bar(vB_j)`. Some j yields a nonzero vector because the cofactor ideals'
product is nonzero as shown above. This explicitly establishes a logical
operator, rather than merely a low-weight vector in a classical kernel.
Exchanging A and B proves the other side's upper bound. No step supplies a
distance lower bound or extends the claim to noncommuting group algebras.

The upstream SAT certifier's per-side `value` is the **tested global threshold**,
not an independently located per-side minimum. In the measured `[[364,41,4]]`
case, the candidate has an X witness of weight 4 and a Z witness of weight 6;
the certificate proves both sides have no logical below 4. This proves global
d=4 exactly and only `4<=dZ<=6`. Reporting exact Z distance 6 would be incorrect.

The lead's `collect_points.read_point` was exercised directly on all five v1
receipts and accepts that asymmetric case correctly. In-memory negative
controls rejected a false global exact flag, a TIMEOUT marked exact, a side
threshold incorrectly replaced by its heavier witness weight, and a wrong
candidate hash. The collector's main routine was not run during this review,
so the registry was not mutated. An AST comparison also confirmed that the
original `candidates`, `construct`, and group-construction helper remain
unchanged from the repository HEAD.
