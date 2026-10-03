# BB search targets

Board snapshot: upstream `unitaryfoundation/qldpc-challenge` at
`c2ebca1713c89277dbd6ddf3ee587cbf7f1a9d23`, committed
2026-10-02 19:55:12 UTC. A direct count of `codes/*.json` found 1,815 entries,
including 1,680 CSS codes. Thresholds below were computed from those CSS
entries using their claimed distance and maximum stored check-row weight.
They are board-relative thresholds, not measured candidate distances.

For a proposed `(n,k,w)`, the conservative threshold is

```
d_required = 1 + max(entry.d for entry in CSS_board
                     if entry.n <= n and entry.k >= k and entry.w <= w)
```

This exceeds every possible dominator's claimed distance, including ties on
the other axes. Recompute against the live board before promotion. A family
tag is provenance, not a separate competitive track. A witness and a passing
refutation search establish an upper-bound claim; exact certification is a
separate step. The initial strategy pass proposed the three lanes below;
the measured pilot and its next campaign are recorded afterward.

## 1. Weight-six paired supports with fixed dimension

Over `F2[Z_l x Z_m]`, use

```
A = 1 + y^a + x (y^c + y^d),   B = 1 + y
a != 0 mod m, c != d mod m
HX = [A | B],                  HZ = [B^T | A^T]
```

Every term pair in A is divisible by `1+y`. Therefore `A=BC` for some
group-ring polynomial C, `rank(HX)=rank(B)=lm-l`, and the transpose/swapped
matrix has the same rank. Thus `n=2lm`, `k=2l`, and `w=6` exactly. This
dimension calculation does not supply the distance. A coprime exponent
`x^b` is equivalent under relabeling to `x`, so the sampler normalizes it.

| l | m | n | exact k | required d | incumbent setting the bound |
|---:|---:|---:|---:|---:|---|
| 11 | 10 | 220 | 22 | 7 | `[[168,24,6]]`, w6 |
| 13 | 12 | 312 | 26 | 8 | `[[234,26,7]]`, w6 |
| 14 | 12 | 336 | 28 | 8 | `[[270,30,7]]`, w6 |
| 17 | 10 | 340 | 34 | 7 | `[[284,58,6]]`, w6 |
| 11 | 14 | 308 | 22 | 8 | `[[270,30,7]]`, w6 |

The on-board `[[700,50,8]]` uses this structural form on `Z25 x Z14`:
`A=1+y^11+x^7*y^2+x^7*y^8`, `B=1+y`. Since 7 is invertible modulo 25,
its x exponent normalizes to 1. The proposed smaller geometries and offset
mutations are an unmeasured search hypothesis. They target distances 7/8
and avoid the zero-dimension rejection rate of unconstrained random BBs.

## 2. Local Frobenius-coupled quartets

For cyclic GB over `Z_M`, let `a` have four terms, and set
`b(x)=a(x^(2^ell)) mod (x^M-1)`. Generate one/two-term mutations and some
fresh anchored quartets around:

| M | seed a | seed ell | desired k | required d at w8 |
|---:|---|---:|---:|---:|
| 62 | `1+x+x^4+x^7` | 3 | 14 | 12 |
| 89 | `1+x^9+x^10+x^12` | 5 | 24 | 14 |

The existing entries are `[[124,14,11]]` and `[[178,24,13]]`. The current
upstream UB fieldnote explicitly proposes bounded local search around
these two seeds; no completed local-neighborhood census was found in the
searched `fieldnotes/` and corresponding notes. This is a bounded search
claim, not evidence the neighborhoods are globally unexplored.

The generator uses exact GF(2) polynomial Euclid to retain only
`k=2 deg gcd(a,b,x^M-1)` at least 14/24. It rejects Frobenius images whose
terms cancel and change the intended weight. These are distance-only
targets at the seed parameters, so any survivor must also undergo the
upstream matched-depth pair audit against its existing seed.

## 3. Asymmetric 3+4 BB transfers below the n=336 step

Use the exact support lists from the on-board w7 `[[360,12,25]]` and
`[[378,12,27]]` entries, reduce them onto nearby smaller tori, and make
bounded one/two-term mutations:

```
Z30 x Z6: A={(0,0),(16,5),(29,4)}
          B={(0,0),(11,5),(17,4),(27,2)}
Z27 x Z7: A={(0,0),(1,2),(25,1)}
          B={(0,0),(12,5),(17,1),(19,2)}
```

Transfer the first to `l=24..27,m=6` and the second to
`l=20..23,m=7`. The resulting n is 280..324. At k=12 and w7, a distance
claim of 19 exceeds the board bound throughout this range. At n=336 the
threshold jumps to 25 because of `[[336,12,24]]`. The transfer has no
dimension or distance guarantee; recompute both. Higher-k survivors can
have easier thresholds: e.g. n=288,k=24,w7 requires d=9.

## Pilot outcome and next campaign: 2026-10-02

The completed `results/profile-bb/bb-20261002` pilot contains ten candidates:
six paired-binomial, three UB, and one asymmetric transfer. Five paired
proposals were refuted below their board bars, at upper bounds 4, 4, 5, 6,
and 6. All three UB proposals fell below their bars; the asymmetric transfer
had k=0. This small pilot does not settle the usefulness of those families.

The remaining paired candidate is **[[312,26,8]], w6**, with
`l=13,m=12,A=1+y^10+x(1+y^7),B=1+y`. Its official validation passed, found no
exact/WL duplicate, and reported a board-advancing point. The preserved
weight-eight witnesses and UNSAT searches for logicals below eight on both
sides certify its overall distance. The SAT receipt records 7.2 s for X and
8.8 s for Z. See `evidence/312-26-8/validation.json`,
`evidence/312-26-8/sat-certificate.json`, and the candidate under
`results/profile-bb/bb-20261002/b04f3fb55828b690c522/`.

`next_candidates(seed,count)` keeps the original APIs intact and adds a
finite campaign. Its snapshot bars were recomputed from the 1,680 CSS board
entries plus the three locally certified points [[455,39,6]], w5;
[[468,40,4]], w5; and [[312,26,8]], w6. Local certification does not mean
upstream acceptance. The runner must recompute the bar before promotion.

The nominal allocation is 60% paired refinements, 35% shared-trinomial BB,
and 5% exploratory shared-quartic BB. Within a lane, the sampler gives each
geometry an early trial. The first ten proposals exercise six paired
geometries, three trinomial geometries, and one quartic geometry. A
ten-candidate profile followed by a bounded 128-candidate wave was the
initial recommendation; the obstruction found after eight trials, below,
supersedes that recommendation. No next-campaign candidate had been
distance-tested when this v1 generator was prepared.

### Paired refinements and exact upper bounds

Writing `b=d-c mod m`, a paired code has the algebraic upper bound

```
d <= min(m, 1 + min(a,m-a) + min(b,m-b)).
```

To see this, write `A=BC`. A vector `(C^T e,e)` is a nontrivial logical
when e is a coordinate vector outside the image of `B^T`. Each quotient
`(1+y^a)/(1+y)` can use the shorter of the two cyclic intervals, which
gives the second bound. A nonzero vector in `ker(B^T)` gives the first
bound m. These are explicit logical constructions, not lower bounds or
estimated distances. The generator omits a proposal when this ceiling is
below its search goal.

| n | exact k | w | current required d | purpose |
|---:|---:|---:|---:|---|
| 286 | 26 | 6 | 8 | shrink the certified 312-qubit point |
| 260 | 26 | 6 | 8 | a stronger shrink if distance survives |
| 312 | 26 | 6 | 9 | improve the certified point's distance |
| 264 | 22 | 6 | 8 | smaller-block tradeoff |
| 288 | 24 | 6 | 8 | smaller-block tradeoff |
| 336 | 28 | 6 | 8 | higher-dimension tradeoff |
| 400 | 40 | 6 | 7 | higher-rate frontier target |
| 440 | 40 | 6 | 7 | higher-rate frontier target |

For example, scaling the survivor blindly to m=10 with a=8,b=6 gives an
upper bound of seven and cannot meet its bar of eight. The next generator
rejects this case before any distance job. It excludes all six measured
paired pilot inputs, including the certified incumbent, under known safe
symmetries: strip exchange, y reflection, monomial shifts of A, and legal
`x -> x*y^t` shears with `m | l*t`. This is partial equivalence reduction,
not a complete isomorphism test; the official deduplication gate remains
necessary.

### Asymmetric checks with guaranteed dimension

For width r=3 or 4 dividing m, use

```
B = 1+y+...+y^(r-1)
A = 1+y^(r*a) + x*y^c*(1+y^(r*b))
q = m/r,  1 <= a,b < q
```

Since `(1+y)B=1+y^r`, B divides both A and `1+y^m`. Consequently,
`rank(B)=l*(m-r+1)` and the exact parameters are `n=2lm`,
`k=2l(r-1)`, `w=4+r`. This replaces the pilot's unconstrained asymmetric
transfer with a construction whose dimension cannot vanish. Its distance
is still unknown. The same quotient-logical argument and the weight-two
periodic patterns in `ker(B^T)` give

```
d <= min(2*m/r, 1 + 2*min(a,q-a) + 2*min(b,q-b)).
```

| r | n | exact k | w | current required d | search goal d |
|---:|---:|---:|---:|---:|---:|
| 3 | 216 | 36 | 7 | 5 | 6 |
| 3 | 264 | 44 | 7 | 5 | 6 |
| 3 | 312 | 52 | 7 | 7 | 7 |
| 3 | 336 | 56 | 7 | 7 | 7 |
| 3 | 210 | 28 | 7 | 7 | 7 |
| 3 | 240 | 32 | 7 | 7 | 7 |
| 3 | 300 | 40 | 7 | 9 | 9 |
| 4 | 144 | 18 | 8 | 11 | 11 |
| 4 | 280 | 30 | 8 | 13 | 13 |

These are algebraic dimensions and computed board thresholds, not measured
new distances. The weight-eight lane is deliberately small: its high
distance goals and short x circumference may prove unproductive. The
weight-seven m=9 regime is omitted because its quotient-logical ceiling
is at most five, even though its kernel bound alone is six.

Deleting one term to try to turn the paired family into weight five is
also omitted: after a term is removed from A, its residue modulo `1+y`
is a unit (1 or x), forcing k=0; removing one term from B makes B a unit
directly. A weight-five campaign needs a different construction.

The frozen v1 pool has 343 paired, 117 trinomial, and 119 quartic
proposals after partial symmetry reduction. These are proposal counts,
not experiments or distinct-code certificates. Requests above 579 raise
before yielding; exhausted subpools spill into another lane. The specs
add `campaign`, `search_goal_d`, and `algebraic_distance_upper_bound`.
Neither upper-bound metadata nor a goal can substitute for an observed
witness or an official distance check.

## After the first eight v1 trials: prune, then compress

The eight stored screens in `results/improve-v1-bb/bb-20261002` show two
additional exact-certified points, **[[264,22,8]], w6** and
**[[288,24,8]], w6**. Both have `A=1+y^10+x(1+y^7),B=1+y` on m=12, with
l=11 and 12 respectively. Their official validation and SAT receipts are
under candidate directories `fd7e894a716c72d15fe4` and
`64fa3696093921271395`. This establishes two more instances of the
same-support family; it does not yet demonstrate improved n/k or distance.

The other six stored screens were below their required distance:

| construction | measured upper bound | required distance |
|---|---:|---:|
| n286, k26, w6; a=9, b=6, m=11 | 7 | 8 |
| n260, k26, w6; a=8, b=5, m=10 | 6 | 8 |
| n312, k26, w6; a=10, b=6, m=12 | 6 | 9 |
| n216, k36, w7; m=12 | 4 | 5 |
| n264, k44, w7; m=12 | 4 | 5 |
| n312, k52, w7; m=12 | 4 | 7 |

Here b is the separation of the two x-strip terms. These failed screens
are witnessed upper bounds, not exact-distance certificates.

### A periodic logical rules out the entire proposed shared-factor slice

For the shared-trinomial/quartic construction above, put

```
q = m/r,  g = gcd(q,a,b),  u = q/g
S = sum(y^(r*g*j) for j=0,...,u-1)
T = sum(y^(r*j) for j=0,...,q-1).
```

The second-block vector `(0,S)` is a nontrivial logical of weight u,
giving the stronger bound

```
d <= m / (r*gcd(m/r,a,b)) <= m/r.
```

Both interval shifts leave S invariant, so `A^T S=0`. For nontriviality,
write A=BC: every X stabilizer has the form `(C^T t,t)` with t in the
image of `B^T`. If u is odd, `S mod B=1`, so S is outside that image.
If u is even, at least one of a/g and b/g is odd, and

```
C*S = (1+y)*T*((a/g mod 2) + x*y^c*(b/g mod 2)) != 0.
```

The two x strips and the two residue classes in `(1+y)T` cannot cancel.
Transposition preserves this nonzero conclusion. Thus `(0,S)` is outside
the stabilizer graph in either parity case. The three measured w7
witnesses are exactly four-site period-three patterns in one second-block
strip: supports `[144,147,150,153]`, `[228,231,234,237]`, and
`[301,304,307,310]` in their respective candidate files.

Consequently, every one of the **117 trinomial proposals** is bounded by
4, 5, or 6 at m=12, 15, or 18; every one of the **119 quartic proposals**
is bounded by 6, 7, or 8 at m=24, 28, or 32. All fall below their current
board thresholds. Stop this slice without further distance jobs. This
obstruction concerns the explicit common-factor construction used here,
not arbitrary weight-seven or weight-eight BB codes. The earlier
quotient-logical ceiling remains valid but missed this lighter logical.

### Two stronger ceilings sharpen paired proposals

For the original paired family, the same periodic argument gives
`d <= m/gcd(m,a,b)`. There is also a two-site logical with

```
s = min(a,m-a),  t = min(b,m-b)
d <= m + 2 - 2*abs(s-t).
```

Choose a second-block vector v supported at two y sites separated by
floor(m/2) in a single x strip. Its two components under `C^T` have weights
2s and 2t. Add a full first-block y ring to the heavier component.
That ring is a nontrivial logical, while `(C^T v,v)` is a stabilizer
because v has even parity. The resulting logical has the displayed
weight. The formula is independent of the shift c.

This bound predicts ceilings 7, 6, and 6 for the three failed paired
proposals, matching their stored witnesses. It motivates balanced
interval lengths for compression. A proposal is viable only if its goal
does not exceed all three available ceilings:

```
min(m/gcd(m,a,b), 1+s+t, m+2-2*abs(s-t)).
```

### Bounded v2 selection

The separate `next_candidates_v2(seed,count)` callable leaves all frozen
v1 functions and `construct` unchanged. It selects from that existing
pool, excludes measured v1 paired orbits, applies the stronger ceilings,
and raises the n264/k22 and n288/k24 snapshot bars to nine. It keeps seven
geometries, with 143 surviving proposals:

| purpose | n | exact k | enforced goal d | proposal count |
|---|---:|---:|---:|---:|
| compression | 286 | 26 | 8 | 30 |
| compression | 260 | 26 | 8 | 11 |
| greater distance | 312 | 26 | 9 | 23 |
| greater distance | 264 | 22 | 9 | 23 |
| greater distance | 288 | 24 | 9 | 4 |
| higher rate | 400 | 40 | 7 | 4 |
| higher rate | 440 | 40 | 7 | 48 |

All have w6. These are proposal counts and target distances; no v2
distance measurements were made in preparing this selection. The nominal
mix is 50% compression, 30% greater distance, 20% higher rate, with finite
pool fallback. Requests above 143 fail before yielding. A **16-candidate
wave** is recommended before expansion. For seed 20261002 its source
indices into frozen v1 are:

```
[33,20,18,26,72,100,85,23,116,12,101,53,133,76,105,135]
```

Materialize v2 specs, not the raw v1 entries: v2 records the revised
ceiling/bar, `source_v1_index`, and `target.d_min`, which the current
driver enforces. Dynamic board comparison still applies before promotion.
The polynomial annihilation/nontriviality identities were checked with
small GF(2) bit-polynomial arithmetic for all 579 frozen proposals;
the two-site weight identity was checked for all 343 paired proposals.
This check constructed no matrices and performed no distance search.

## Implementation and confirmation

`scripts/generators_bb.py` exposes `candidates(seed,count)`, the frozen
`next_candidates(seed,count)`, `next_candidates_v2(seed,count)`, and
`construct(spec)`. The original proposal mix is 60% fixed-dimension paired
supports, 30% UB, and 10% asymmetric transfers. UB proposals fall back to
paired supports if a bounded polynomial prefilter finds no survivor.
Specs contain family, mode, parameter-derived id, parameters, and exact
expected n/w; expected k is present only when established algebraically.
`target_d_snapshot` is explicitly a target, never a measured field.

Construction uses qLDPC **0.4.0** exactly:

```python
code = codes.BBCode({x: l, y: m}, a, b, field=2)
code = codes.QCCode({x: M}, a, b, field=2)
hx, hz = np.asarray(code.matrix_x, dtype=np.uint8), np.asarray(code.matrix_z, dtype=np.uint8)
```

Those constructors do not accept `set_logicals`. The module reads matrices
only. Enumeration imports no qLDPC/NumPy/SymPy; construction loads them
lazily and rejects a qLDPC version mismatch. Distance searches run on
Shirokane and must preserve per-side witnesses through upstream submission
packaging. Only the official `verify/validate_candidate.py` gate decides
whether a candidate is a find. Avoid blind odd-cover or free-Z2 doubling
campaigns: upstream already records substantial failed sweeps in those
regimes, including a supposedly stable d38 claim refuted to d36.

Sources: [track rules](https://github.com/unitaryfoundation/qldpc-challenge/blob/c2ebca1713c89277dbd6ddf3ee587cbf7f1a9d23/TRACKS.md),
[paired-support seed](https://github.com/unitaryfoundation/qldpc-challenge/blob/c2ebca1713c89277dbd6ddf3ee587cbf7f1a9d23/notes/700-50-8.md),
[UB search note](https://github.com/unitaryfoundation/qldpc-challenge/blob/c2ebca1713c89277dbd6ddf3ee587cbf7f1a9d23/fieldnotes/2026-08-23-univariate-bicycle-sweep.md),
[v0.4.0 constructors](https://github.com/qLDPCOrg/qLDPC/blob/v0.4.0/src/qldpc/codes/quantum.py).
