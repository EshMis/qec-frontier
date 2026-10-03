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

## Wider cyclic bases: 2x4 and 2x5

This is a separate construction campaign. `wide_candidates(seed,count)` emits
`generator="monomial-2xc-v1"`, and its matrices must be built by
`construct_wide(spec)`. The original `construct` and all three earlier recipe
streams remain unchanged. The lead owns dispatch in the shared runner.

Both bases have c columns, a first row of identity monomials, and a second row
of distinct cyclic shifts including zero. For subgroup indices gA,gB and
`h=gcd(gA,gB)`, the algebraic parameter predictions are

```
n = (c^2+4)N
w = c+2
k = (c-2)^2 N + (c-2)(gA+gB) + 2h.
```

These identities describe the proposed qLDPC construction; every instantiated
code still needs the pipeline's independent n,k,w and connectivity readback.
With individually connected seeds, c=4 gives `n=20N,k=4N+6,w=6`, and c=5
gives `n=29N,k=9N+8,w=7`. This raises the logical-qubit rate while retaining
the challenge's bounded-weight classes.

### Dimension derivation and the distance-six ceiling

Put `f=c-2`. The same unit/Smith cancellation reduces each base to the row
`[sA,0,...,0]` with f zero entries, where `sA=x^gA+1`, and similarly for B.
The reduced product has `((f+1)^2+1)N` qubits. One coupled check row has image
ideal `(sA,sB)` of dimension `N-h`, and the f remaining independent rows each
contribute `N-gA` or `N-gB`. Therefore

```
rank(HX_reduced) = (f+1)N - f*gA - h
rank(HZ_reduced) = (f+1)N - f*gB - h
k = f^2 N + f(gA+gB) + 2h.
```

This derivation applies to even N as well; it makes no semisimplicity
assumption. Coprime gA,gB again give a connected combined incidence graph in
the algebraic model, subject to the actual graph check.

Wider bases do **not** escape the cyclic distance-six ceiling. On any three
columns, the cofactor construction gives a kernel vector with six binary
nonzero entries. Taken across all triples, the cofactor entries generate
the ideal `(x^gA+1)`; the opposite base generates `(x^gB+1)`. Their product
is nonzero because `gA+gB<=2N/c<N`. Consequently some pair of triples gives
the nonzero boundary-annihilating pairing used in the earlier proof. There
is a weight-six logical on each side, so `dX<=6` and `dZ<=6`. An arbitrary
selected triple need not itself yield a nontrivial logical: the assertion is
existence across all triples. No quantum lower bound follows from this.

### Exact Sidon feasibility in the allowed size range

A seed with c shifts avoids a square when all `c(c-1)` ordered nonzero
differences are distinct. Thus its subgroup order M must satisfy
`M>=c(c-1)+1`. For these two widths:

- c=4: `{0,1,4,6}` is Sidon for every M>=13. In C13, the alternative
  `{0,1,3,9}` is also a perfect difference set.
- c=5: `{0,1,4,14,16}` works in C21. `{0,1,4,9,11}` works for every M>=23.
- c=5, M=22 is impossible. Twenty directed differences would occupy all
  nonzero residues except 11, since differences occur in opposite pairs.
  They would therefore contain ten odd residues. If e of the five shifts
  are even, the number of odd differences is `2e(5-e)`, which is never ten
  for integer e. This parity proof agrees with enumeration of all 5985
  normalized five-subsets of C22.

The necessary size bound alone would incorrectly include C22. The new
catalog explicitly excludes it and verifies the constructive templates over
the complete modulus range it uses.

### Board gaps and first recipes

The upstream cap allows n<=700, or n<=1000 with w<=8 and a claimed d<=40.
All proposed wide targets have d6 and w6 or w7, so the extended tier applies.
The frozen catalog scans c4 group orders 13..50 and c5 orders 21..34, along
with every unordered coprime pair of divisor indices admitting Sidon seeds.

At declaration, the registry held 18 locally exact-certified points, 15
nondominated within that registry. All 18 candidate hashes, official
passed/advancing receipts, and global exact certificates were read back.
These local points do not change the official board's d>=6 projection at
w<=6 or w<=7. Pruning used all 1680 CSS records plus those 18 local points.

| Width | Structurally feasible integer goals | Survive existing-point pruning | Preferred parameter goals |
|---|---:|---:|---:|
| c4, w6 | 57 | 50 | 34 |
| c5, w7 | 13 | 13 | 13 |

The c4 choices at N48..50 are already dominated by an official point at
n960,k258,d>=6,w<=6. Surviving c4 goals reach n940; c5 goals reach n986.
The catalog is exhaustive over these integer choices, not over all codes.
Lower-priority surviving subgroup choices remain available after the preferred
ones; unmeasured goals are never treated as certified dominators.

For seed 20261002, the first eight recipes are below. First rows consist only
of c identity indices; table entries give the full second-row shift lists.
Every n,k,d,w entry is an **unmeasured target** at campaign declaration.

| Slot | c,N | A shifts | B shifts | Target n,k,d,w |
|---:|---|---|---|---|
| 0 | 4,13 | 0,1,3,9 | 0,1,4,6 | 260,58,6,6 |
| 1 | 4,14 | 0,8,9,12 | 0,2,5,6 | 280,62,6,6 |
| 2 | 4,15 | 0,5,11,12 | 0,6,7,10 | 300,66,6,6 |
| 3 | 4,16 | 0,1,3,12 | 0,1,10,14 | 320,70,6,6 |
| 4 | 5,21 | 0,1,4,14,16 | 0,1,6,8,18 | 609,197,6,7 |
| 5 | 4,17 | 0,8,12,14 | 0,11,13,16 | 340,74,6,6 |
| 6 | 4,18 | 0,1,3,7 | 0,2,7,8 | 360,78,6,6 |
| 7 | 4,19 | 0,1,6,17 | 0,2,13,14 | 380,82,6,6 |

Slots 0 and 4 are the first separate cluster profiles. The snapshot's
sufficient board thresholds are five at `(260,58,w6)` and three at
`(609,197,w7)`. If the latter fails the d6 goal but has a genuine d4 or d5
witness, it remains eligible for an explicit lower-distance frontier attempt;
it must still pass official validation and exact certification before being
reported as a discovery. Changing the search target is not a distance proof.

Implementation checks covered all 70 catalog pruning decisions and 63
deterministically generated recipes, one for every surviving integer goal.
They are JSON serializable, have the specified subgroup indices, pass the
complete directed-difference condition, stay inside the challenge's size and
weight caps, and are distinct under the recorded monomial/permutation
equivalences. Translation, reversal, common-unit, and base-exchange controls
preserve their canonical keys. All frozen functions present in HEAD have
unchanged ASTs. No local parity-check matrices or distances were computed;
cluster construction and certificate results remain separate evidence.

## Rectangular bases and compact higher-rate probes

The first wide profiles were read back as exact, officially advancing points:
`[[260,58,6]],w6` and `[[609,197,6]],w7`. The rectangular campaign's frozen
numeric snapshot contains 21 locally certified points. It extends the base
shapes while preserving every earlier callable and recorded recipe.

The new interfaces are `rectangular_candidates(seed,count)` and
`construct_rectangular(spec)`. Their tag is `monomial-2xcd-v1`, with
`base_columns=[c,d]`. Each seed still has two rows, but A has c columns and B
has d. The qLDPC constructor consequently produces different check counts:

```
HX.shape = (2dN, (cd+4)N)
HZ.shape = (2cN, (cd+4)N).
```

The formulas, including arbitrary cyclic subgroup indices, are

```
n = (cd+4)N
wX = c+2,  wZ = d+2,  w = max(c,d)+2
k = (c-2)(d-2)N + (d-2)gA + (c-2)gB + 2gcd(gA,gB).
```

For a direct derivation, put `fA=c-2`, `fB=d-2`, and `h=gcd(gA,gB)`.
After the same unit/Smith cancellation, there are
`((fA+1)(fB+1)+1)N` qubits. The X rank is
`(fB+1)N-fB*gA-h`; the Z rank is `(fA+1)N-fA*gB-h`.
Subtracting these ranks gives the stated k. In particular, the subgroup-index
coefficients are crossed: gA multiplies d-2, not c-2. Actual constructor/rank
readback remains mandatory.

For c,d>=3, the earlier cofactor argument still gives `dX,dZ<=6`.
The two cofactor ideals have a nonzero product because
`gA+gB<=N/c+N/d<N`. Rectangular geometry therefore opens size/rate gaps, not
a route above distance six within this cyclic two-row family.

### Six-shift Sidon feasibility

Check weight at most eight allows widths through six. The additional
six-shift templates are `{0,1,3,8,12,18}` in C31 and
`{0,1,4,10,12,17}` in every C_M with M>=35. Orders 32, 33, and 34 admit no
six-shift Sidon set. A complete small label scan established this as follows:
each hypothetical set would use 30 distinct nonzero differences. There are
only 15, 12, and 17 nonzero nonunits in those three groups, respectively, so
some difference is a unit. Translation and multiplication by its inverse
normalize the set to contain 0 and 1. Exhaustively checking all remaining
four-mark choices found no witness:

| M | Normalized subsets checked | Sidon witnesses |
|---:|---:|---:|
| 32 | 27,405 | 0 |
| 33 | 31,465 | 0 |
| 34 | 35,960 | 0 |

This is a finite group-label enumeration, not a matrix or distance computation.
Together with the templates and the counting lower bound, it resolves the
six-shift feasibility question over the group orders used by this campaign.

### Frozen first eight and the weight-five correction

The first eight recipes are frozen in `campaigns/rectangular-v1/lp-specs.json`.
Both first rows contain identity indices. Their declared targets were:

| Slot | c,d,N | A shifts | B shifts | Original target n,k,d,w |
|---:|---|---|---|---|
| 0 | 5,5,5 | 0,1,2,3,4 | 0,1,2,3,4 | 145,53,4,7 |
| 1 | 5,6,6 | 0,1,2,3,4 | 0,1,2,3,4,5 | 204,81,4,8 |
| 2 | 6,6,6 | 0,1,2,3,4,5 | 0,1,2,3,4,5 | 240,106,4,8 |
| 3 | 4,5,21 | 0,1,4,6 | 0,1,4,14,16 | 504,133,6,7 |
| 4 | 4,4,12 | 0,2,4,6 | 0,3,6,9 | 240,60,4,6 |
| 5 | 3,4,14 | 0,2,6 | 0,1,4,6 | 224,35,6,6 |
| 6 | 3,4,16 | 0,2,6 | 0,1,4,6 | 256,39,6,6 |
| 7 | 3,3,3 | 0,1,2 | 0,1,2 | 39,7,4,5 |

These are original search aspirations, not a table of certified distances.
The largest first-eight instance is n504, below the already profiled n609
block. The first three points need only d3 to advance the frozen board;
their goal is d4. The n39 point needs d4.

After freezing, a stronger obstruction was found for slots 5 and 6:
`-{0,2,6}+6={0,4,6}` is contained in the opposite four-shift seed. This
produces a weight-five logical even though both seeds are Sidon. Thus these
two recipes cannot attain their original d6 goal. Both numeric tuples can
still advance the snapshot at d5, subject to official validation and an exact
certificate. Their recipes remain unchanged so the missed aspiration and any
fallback result retain honest provenance.

The weight-five construction uses two second-sector qubits of different
base-check row types and one first-sector edge in each of the three layers.
The required edge labels exist precisely for the translated/reversed
three-shift inclusion. The three edges occupy distinct base columns.
Multiplication by the opposite cofactor vector therefore leaves a nonzero
entry, proving that the commuting operator is not a stabilizer.

This was also checked at the label level across the small seed spaces:

| Geometry | Seed pairs checked | Pairs avoiding triple containment |
|---|---:|---:|
| C14, c3/d4, indices2/1 | 48 | 0 |
| C14, c3/d4, indices1/1 | 288 | 144 |
| C16, c3/d4, indices2/1 | 288 | 96 |

The frozen integer catalog contains 300 d6 targets and 1419 d4 targets;
58 and 520, respectively, survive existing-point pruning. Its priority
comparison also considers previously declared wide targets, but these
unmeasured proposals affect ordering only. The catalog's Sidon test alone
does not establish feasibility at d6 when a width is three, as the above
correction demonstrates. A broad continuation should apply the additional
noncontainment test rather than blindly running all d6 targets.

### Separate, provenance-preserving refinements

`rectangular_refinements(seed,count)` is deliberately bounded to two fixed
probes (`0<=count<=2`). It preserves the original constructor and generator
tag, and records each source slot plus the SHA256 of its canonical original
recipe. The revised targets are:

| New slot | Source slot | c,d,N | A shifts | B shifts | Target n,k,d,w |
|---:|---:|---|---|---|---|
| 0 | 5 | 3,4,14 | 0,1,3 | 0,1,4,6 | 224,33,6,6 |
| 1 | 6 | 3,4,16 | 0,2,6 | 0,1,3,12 | 256,39,6,6 |

The C14 refinement uses individually connected seeds and accepts two fewer
predicted logical qubits to remove the obstruction. The C16 refinement changes
only the four-shift seed and retains its parameter target. Both pass Sidon and
noncontainment checks; they remain search targets until officially certified.

A possible stronger lower-bound lemma was derived for lead review: distinct
shifts in these two-row bases exclude nonzero check-kernel vectors of weight
at most three. When both seeds are Sidon and both widths are at least four,
layer parity/counting also excludes weights four and five. Combined with the
cofactor upper bound this would characterize those wider Sidon instances at
distance six. This structural argument does not replace the project's required
official SAT certificates. The width-three mixed-sector exception is precisely
why merely assuming a seed-girth lower bound would have been unsafe.

Implementation checks: all 1719 frozen pruning decisions agree with the full
1680-entry CSS snapshot plus the first 21 certified local points. Sixty-four
generated rectangular specs passed deterministic JSON, subgroup/dimension,
required Sidon, cap, and equivalence checks. The frozen original eight reproduce
exactly; source hashes for both refinement recipes match the frozen file.
No local matrices or distances, scheduler jobs, Git operations, or shared-driver
edits were performed in this expansion.
