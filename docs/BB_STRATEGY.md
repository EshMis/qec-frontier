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
separate step. No new candidate was constructed or distance-tested in this
strategy pass.

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

## Implementation and confirmation

`scripts/generators_bb.py` exposes `candidates(seed,count)` and
`construct(spec)`. The nominal proposal mix is 60% fixed-dimension paired
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
