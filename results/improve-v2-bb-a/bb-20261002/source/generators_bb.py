"""Deterministic BB/GB proposals; construction requires qldpc==0.4.0.

``candidates(seed, count)`` needs only the Python standard library. It yields
JSON-serializable descriptions, without constructing matrices or searching
distance. ``construct(spec)`` returns binary NumPy arrays. The search runner
owns ranks, distance witnesses, board comparison, and trusted validation.

The original proposal mix favors a fixed-dimension, weight-six family,
with smaller UB and asymmetric BB lanes. ``next_candidates`` is the
bounded, pilot-informed campaign. See docs/BB_STRATEGY.md for the board
snapshot and the distinction between a target and a measured distance.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from functools import lru_cache
from importlib.metadata import version
from typing import TYPE_CHECKING, Any, Iterator

if TYPE_CHECKING:
    import numpy as np


Spec = dict[str, Any]
QLDPC_VERSION = "0.4.0"

# These all have exact k=2*l, w=6. The default mix stays at n<=340.
# d_required is a snapshot target, never a distance claim or a pruning proof.
_PAIRED_TARGETS = (
    (11, 10, 7),
    (13, 12, 8),
    (14, 12, 8),
    (17, 10, 7),
    (11, 14, 8),
    (11, 12, 8),
    (12, 12, 8),
    (13, 10, 8),
    (15, 10, 8),
)

# Published/reproduced seeds; unchanged seeds are controls, not discoveries.
_UB_SEEDS = (
    (62, (0, 1, 4, 7), 14, 12),
    (89, (0, 9, 10, 12), 24, 14),
)

_ASYMMETRIC_SEEDS = (
    ((30, 6), ((0, 0), (16, 5), (29, 4)),
     ((0, 0), (11, 5), (17, 4), (27, 2))),
    ((27, 7), ((0, 0), (1, 2), (25, 1)),
     ((0, 0), (12, 5), (17, 1), (19, 2))),
)


def _gf2_remainder(a: int, b: int) -> int:
    """Polynomial remainder for nonnegative GF(2) coefficient bit masks."""
    if not b:
        raise ZeroDivisionError("zero GF(2) polynomial")
    while a and a.bit_length() >= b.bit_length():
        a ^= b << (a.bit_length() - b.bit_length())
    return a


def _gf2_gcd(a: int, b: int) -> int:
    while b:
        a, b = b, _gf2_remainder(a, b)
    return a


def _cyclic_k(order: int, a: list[int], b: list[int]) -> int:
    """Exact GB dimension, not a distance surrogate."""
    pa = sum(1 << exponent for exponent in a)
    pb = sum(1 << exponent for exponent in b)
    common = _gf2_gcd(_gf2_gcd(pa, pb), (1 << order) | 1)
    return 2 * (common.bit_length() - 1)


def _parity_support(exponents: list[int], order: int) -> list[int]:
    """Reduce a polynomial in GF(2)[x]/(x**order-1), including cancellation."""
    support: set[int] = set()
    for exponent in exponents:
        reduced = exponent % order
        support.symmetric_difference_update((reduced,))
    return sorted(support)


def _spec(family: str, mode: str, orders: tuple[int, ...],
          a: list[list[int]], b: list[list[int]], *,
          expected_k: int | None = None,
          target_d: int | None = None,
          reference: str | None = None) -> Spec:
    parameters = {"orders": list(orders), "a": sorted(a), "b": sorted(b)}
    key = json.dumps({"family": family, "parameters": parameters},
                     sort_keys=True, separators=(",", ":"))
    result: Spec = {
        "family": family,
        "mode": mode,
        "id": f"bb-{mode}-{hashlib.sha256(key.encode()).hexdigest()[:16]}",
        "parameters": parameters,
        "expected_n": 2 * math.prod(orders),
        "expected_w": len(a) + len(b),
    }
    if expected_k is not None:
        result["expected_k"] = expected_k
    if target_d is not None:
        result["target_d_snapshot"] = target_d
    if reference is not None:
        result["seed_reference"] = reference
    return result


def _paired_binomial(rng: random.Random) -> Spec:
    l, m, target_d = rng.choice(_PAIRED_TARGETS)
    # Start with the n=700 seed's relative offsets on each smaller geometry
    # frequently, while allowing all nonzero interval lengths and offsets.
    if rng.randrange(4) == 0:
        a = (11 + rng.choice((-2, -1, 0, 1, 2))) % m or 1
        c = (2 + rng.choice((-2, -1, 0, 1, 2))) % m
        d = (8 + rng.choice((-2, -1, 0, 1, 2))) % m
        if c == d:
            d = (d + 1) % m
    else:
        a = rng.randrange(1, m)
        c, d = rng.sample(range(m), 2)
    # An invertible x->x**b makes coprime b equivalent to b=1. Normalize it.
    return _spec(
        "bivariate-bicycle", "paired-binomial", (l, m),
        [[0, 0], [0, a], [1, c], [1, d]], [[0, 0], [0, 1]],
        expected_k=2*l, target_d=target_d,
        reference="codes/700-50-8.json",
    )


def _ub_local(rng: random.Random) -> Spec | None:
    order, original, min_k, target_d = rng.choice(_UB_SEEDS)
    # Exact polynomial arithmetic avoids building zero-rate candidates. A
    # bounded attempt count keeps this lane from stalling the common runner.
    for _ in range(256):
        a = list(original)
        move = rng.randrange(5)
        if move == 4:
            a = [0, *rng.sample(range(1, order), 3)]
        else:
            for slot in rng.sample((1, 2, 3), 1 if move < 3 else 2):
                choices = [x for x in range(1, order) if x not in a]
                a[slot] = rng.choice(choices)
        a.sort()
        if a == list(original):
            continue
        # Distinct nonidentity Frobenius multipliers in the two seed rings.
        ell = rng.randint(1, 5 if order == 62 else 10)
        b = _parity_support([pow(2, ell, order) * x for x in a], order)
        if len(b) != 4 or a == b:
            continue
        k = _cyclic_k(order, a, b)
        if k < min_k:
            continue
        result = _spec(
            "generalized-bicycle", "ub-local", (order,),
            [[x] for x in a], [[x] for x in b],
            expected_k=k, target_d=target_d,
            reference=f"codes/{2*order}-{min_k}-{target_d-1}.json",
        )
        result["frobenius_ell"] = ell
        return result
    return None


def _asymmetric_bb(rng: random.Random) -> Spec:
    original_orders, a_seed, b_seed = rng.choice(_ASYMMETRIC_SEEDS)
    m = original_orders[1]
    # Transfer the n=360/378 seeds below the n=336 incumbent step. Most
    # proposals change geometry; a smaller part also changes one/two terms.
    l = rng.choice((24, 25, 26, 27) if m == 6 else (20, 21, 22, 23))
    a = sorted({(u % l, v % m) for u, v in a_seed})
    b = sorted({(u % l, v % m) for u, v in b_seed})
    for support, required in ((a, 3), (b, 4)):
        while len(support) < required:
            term = (rng.randrange(l), rng.randrange(m))
            if term not in support:
                support.append(term)
        if rng.randrange(3):
            for _ in range(1 + (rng.randrange(5) == 0)):
                slot = rng.randrange(1, len(support))  # retain anchor (0,0)
                term = (rng.randrange(l), rng.randrange(m))
                while term in support:
                    term = (rng.randrange(l), rng.randrange(m))
                support[slot] = term
        support.sort()
    return _spec(
        "bivariate-bicycle", "asymmetric-transfer", (l, m),
        [list(t) for t in a], [list(t) for t in b],
        reference="codes/360-12-25.json" if m == 6 else "codes/378-12-27.json",
    )


def candidates(seed: int, count: int) -> Iterator[Spec]:
    """Yield exactly ``count`` parameter-distinct, deterministic proposals.

    Nominal allocation: 60% paired-binomial, 30% UB, 10% asymmetric BB.
    A UB slot falls back to paired-binomial after its bounded algebraic
    prefilter budget. No proposal carries a measured distance.
    """
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        raise ValueError("count must be a nonnegative integer")
    rng = random.Random(seed)
    seen: set[str] = set()
    yielded = 0
    attempts = 0
    while yielded < count:
        attempts += 1
        if attempts > max(10_000, count * 200):
            raise RuntimeError("proposal pool exhausted before requested count")
        slot = (attempts - 1) % 10
        spec = (_paired_binomial(rng) if slot < 6 else
                _ub_local(rng) if slot < 9 else _asymmetric_bb(rng))
        if spec is None:
            spec = _paired_binomial(rng)
        key = json.dumps(spec["parameters"], sort_keys=True, separators=(",", ":"))
        if key in seen:
            continue
        seen.add(key)
        yielded += 1
        yield spec


# (l, m, current board threshold, search goal). The threshold includes the
# pinned CSS board and locally certified (455,39,6,5), (468,40,4,5), and
# (312,26,8,6). The common driver must still recompute the live frontier bar.
_NEXT_PAIRED_TARGETS = (
    (13, 11, 8, 8),  # shrink the certified 312-qubit point
    (13, 10, 8, 8),
    (13, 12, 9, 9),  # improve its distance at the same n, k, w
    (11, 12, 8, 8),
    (12, 12, 8, 8),
    (14, 12, 8, 8),
    (20, 10, 7, 7),
    (20, 11, 7, 7),
    (20, 12, 7, 7),
    (21, 12, 7, 7),
)

# Shared factor B=1+y+...+y**(width-1), with width dividing m.
# n=2*l*m, k=2*l*(width-1), w=4+width are exact construction invariants.
_NEXT_TRINOMIAL_TARGETS = (
    (9, 12, 5, 6),
    (11, 12, 5, 6),
    (13, 12, 7, 7),
    (14, 12, 7, 7),
    (7, 15, 7, 7),
    (8, 15, 7, 7),
    (10, 15, 9, 9),
    (13, 15, 7, 7),
    (6, 18, 9, 9),
    (8, 18, 9, 9),
    (9, 18, 9, 9),
    (12, 18, 7, 7),
)
_NEXT_QUARTIC_TARGETS = (
    (3, 24, 11, 11),
    (5, 28, 13, 13),
    (6, 28, 13, 13),
    (4, 32, 15, 15),
    (5, 32, 13, 13),
    (6, 32, 13, 13),
)

# Frozen measured pilot inputs: (l,m,a,c,d) in
# A=1+y**a+x*(y**c+y**d), B=1+y. The last is now certified and is an
# incumbent, not another proposal. Exclude their known symmetry orbits.
_PILOT_PAIRED = (
    (11, 12, 1, 2, 8),
    (11, 12, 9, 1, 10),
    (14, 12, 9, 5, 6),
    (13, 10, 1, 3, 7),
    (11, 14, 9, 1, 8),
    (13, 12, 10, 0, 7),
)


def _two_strip_key(l: int, m: int, width: int,
                   a: int, c: int, d: int) -> tuple[Any, ...]:
    """A safe partial equivalence key, not a complete code isomorphism test.

    Quotient by exchanging x strips, reflecting y, multiplying A by a y
    monomial, and valid x -> x*y**t shears. Reflection changes B only by
    a monomial. All of these preserve the code's n, k, d, and w.
    """
    representations = []
    shears = range(0, m, m // math.gcd(l, m))
    for left, right in (((0, a), (c, d)), ((c, d), (0, a))):
        for sign in (-1, 1):
            for anchor in left:
                normalized_left = tuple(sorted(sign * (v-anchor) % m for v in left))
                for shear in shears:
                    normalized_right = tuple(sorted(
                        (sign * (v-anchor) + shear) % m for v in right
                    ))
                    representations.append((normalized_left, normalized_right))
    return l, m, width, *min(representations)


def _round_robin_buckets(buckets: list[list[Spec]]) -> list[Spec]:
    """Give each geometry an early trial before revisiting a geometry."""
    return [bucket[index]
            for index in range(max(map(len, buckets), default=0))
            for bucket in buckets if index < len(bucket)]


def _improvement_pool(rng: random.Random, width: int,
                      targets: tuple[tuple[int, int, int, int], ...]) -> list[Spec]:
    """Finite, dimension-preserving proposals with algebraic ceiling pruning."""
    excluded = {
        _two_strip_key(l, m, 2, a, c, d)
        for l, m, a, c, d in _PILOT_PAIRED
    }
    buckets: list[list[Spec]] = []
    for l, m, target, goal in targets:
        # Width two retains arbitrary interval lengths. Wider B divides
        # 1+y**width, so each interval length must be a multiple of width.
        step = 1 if width == 2 else width
        q = m // step
        best: dict[tuple[Any, ...], tuple[tuple[Any, ...], Spec]] = {}
        for first in range(1, q):
            for second in range(1, q):
                short_first = min(first, q-first)
                short_second = min(second, q-second)
                ceiling = min(
                    m if width == 2 else 2*m // width,
                    1 + (1 if width == 2 else 2) * (short_first + short_second),
                )
                if ceiling < goal:
                    continue
                a = step * first
                for c in range(m):
                    d = (c + step*second) % m
                    key = _two_strip_key(l, m, width, a, c, d)
                    if key in excluded:
                        continue
                    mode = ("paired-binomial-improve" if width == 2 else
                            "shared-trinomial" if width == 3 else "shared-quartic")
                    spec = _spec(
                        "bivariate-bicycle", mode, (l, m),
                        [[0, 0], [0, a], [1, c], [1, d]],
                        [[0, j] for j in range(width)],
                        expected_k=2*l*(width-1), target_d=target,
                        reference=("results/profile-bb/bb-20261002/b04f3fb55828b690c522"
                                   if width == 2 else "docs/BB_STRATEGY.md"),
                    )
                    spec.update({
                        "campaign": "bb-improve-v1",
                        "search_goal_d": goal,
                        "algebraic_distance_upper_bound": ceiling,
                    })
                    if width == 2:
                        # Relative offsets of the measured survivor, scaled
                        # to the new circumference. The ceiling may require
                        # a departure from these offsets on smaller tori.
                        seed_a, seed_b = round(10*m/12), round(7*m/12)
                        score = (min((a-seed_a) % m, (seed_a-a) % m)
                                 + min((second-seed_b) % m, (seed_b-second) % m)
                                 + min(c, m-c))
                        priority = (score, rng.random())
                    else:
                        # Prefer unequal interval lengths and useful ceilings;
                        # these are search heuristics, not distance estimates.
                        priority = (short_first == short_second, -ceiling, rng.random())
                    if key not in best or priority < best[key][0]:
                        best[key] = priority, spec
        ranked = list(best.values())
        ranked.sort(key=lambda item: item[0])
        buckets.append([spec for _, spec in ranked])
    return _round_robin_buckets(buckets)


def next_candidates(seed: int, count: int) -> Iterator[Spec]:
    """Yield a bounded next campaign, without repeating measured pilot orbits.

    Nominal mix per 20 proposals: 12 paired-binomial, 7 shared-trinomial,
    1 exploratory shared-quartic. Exhausted subpools use another subpool.
    A request larger than the complete finite pool raises before yielding.
    No rank computation, matrix construction, or distance search runs here.
    """
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        raise ValueError("count must be a nonnegative integer")
    if count == 0:
        return
    rng = random.Random(seed)
    pools = [
        _improvement_pool(rng, 2, _NEXT_PAIRED_TARGETS),
        _improvement_pool(rng, 3, _NEXT_TRINOMIAL_TARGETS),
        _improvement_pool(rng, 4, _NEXT_QUARTIC_TARGETS),
    ]
    available = sum(map(len, pools))
    if count > available:
        raise ValueError(f"next campaign has {available} symmetry-distinct proposals; "
                         f"requested {count}")
    schedule = (0, 0, 1, 0, 1, 0, 0, 1, 0, 2, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1)
    indices = [0, 0, 0]
    for index in range(count):
        preferred = schedule[index % len(schedule)]
        lane = next(lane for lane in (preferred, 0, 1, 2)
                    if indices[lane] < len(pools[lane]))
        yield pools[lane][indices[lane]]
        indices[lane] += 1


def next_candidates_v2(seed: int, count: int) -> Iterator[Spec]:
    """Select viable paired proposals from frozen v1 after its first wave.

    This separate callable leaves v1 enumeration and construction untouched.
    It removes shared-factor modes with a proved sub-threshold logical,
    strengthens paired ceilings, and targets compression or distance > 8.
    The nominal mix is 50% compression, 30% distance, 20% higher rate.
    """
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        raise ValueError("count must be a nonnegative integer")
    if count == 0:
        return
    completed = (
        (13, 11, 9, 0, 6),
        (13, 10, 8, 0, 5),
        (13, 12, 10, 0, 6),
        (11, 12, 10, 0, 7),
        (12, 12, 10, 0, 7),
    )
    excluded = {_two_strip_key(l, m, 2, a, c, d)
                for l, m, a, c, d in completed}
    shapes = (
        ((13, 11), (13, 10)),  # same k, fewer qubits than the 312-qubit point
        ((13, 12), (11, 12), (12, 12)),  # improve locally certified d=8
        ((20, 10), (20, 11)),  # n/k=10 or 11, rather than the measured 12
    )
    buckets: dict[tuple[int, int], list[Spec]] = {
        shape: [] for lane in shapes for shape in lane
    }
    for source_index, original in enumerate(next_candidates(seed, 579)):
        if original["mode"] != "paired-binomial-improve":
            continue
        parameters = original["parameters"]
        l, m = parameters["orders"]
        if (l, m) not in buckets:
            continue
        a = next(y for x, y in parameters["a"] if x == 0 and y)
        c, d = sorted(y for x, y in parameters["a"] if x == 1)
        b = (d-c) % m
        if _two_strip_key(l, m, 2, a, c, d) in excluded:
            continue
        short_a, short_b = min(a, m-a), min(b, m-b)
        ceiling = min(
            original["algebraic_distance_upper_bound"],
            m // math.gcd(m, a, b),
            m + 2 - 2*abs(short_a-short_b),
        )
        # The two additional exact d=8 points raise the 264/288 bars to 9.
        # No generic n=12*k, d=8 scaling proposals enter this campaign.
        target = 9 if m == 12 else original["target_d_snapshot"]
        goal = max(target, original["search_goal_d"])
        if ceiling < goal:
            continue
        spec = dict(original)
        spec.update({
            "campaign": "bb-improve-v2",
            "source_v1_index": source_index,
            "target_d_snapshot": target,
            "search_goal_d": goal,
            "target": {"d_min": goal},
            "algebraic_distance_upper_bound": ceiling,
        })
        buckets[(l, m)].append(spec)
    pools = [_round_robin_buckets([buckets[shape] for shape in lane])
             for lane in shapes]
    available = sum(map(len, pools))
    if count > available:
        raise ValueError(f"v2 campaign has {available} viable proposals; requested {count}")
    schedule = (0, 1, 0, 2, 1, 0, 0, 1, 0, 2)
    indices = [0, 0, 0]
    for index in range(count):
        preferred = schedule[index % len(schedule)]
        lane = next(lane for lane in (preferred, 0, 1, 2)
                    if indices[lane] < len(pools[lane]))
        yield pools[lane][indices[lane]]
        indices[lane] += 1


@lru_cache(maxsize=1)
def _construction_dependencies() -> tuple[Any, Any, Any]:
    if version("qldpc") != QLDPC_VERSION:
        raise RuntimeError(f"construction requires qldpc=={QLDPC_VERSION}")
    import numpy as np
    import sympy
    from qldpc import codes
    return np, sympy, codes


def construct(spec: Spec) -> tuple[np.ndarray, np.ndarray]:
    """Build ``(HX, HZ)`` with the pinned library, without finding logicals.

    qLDPC v0.4.0's BBCode/QCCode constructors have no ``set_logicals``
    keyword. Their logical operators are lazy; this function reads matrices
    only and never calls a dimension, logical-operator, or distance method.
    """
    np, sympy, codes = _construction_dependencies()
    parameters = spec["parameters"]
    orders = tuple(parameters["orders"])
    if len(orders) not in (1, 2) or any(type(n) is not int or n < 2 for n in orders):
        raise ValueError("expected one or two cyclic orders, each >=2")
    expected_family = "bivariate-bicycle" if len(orders) == 2 else "generalized-bicycle"
    if spec.get("family") != expected_family:
        raise ValueError("family does not match the number of cyclic factors")
    symbols = sympy.symbols("x y")[:len(orders)]
    polynomials = []
    for name in ("a", "b"):
        terms = parameters[name]
        if not terms or len({tuple(t) for t in terms}) != len(terms):
            raise ValueError("polynomial supports must be nonempty and distinct")
        poly = sympy.Integer(0)
        for term in terms:
            if len(term) != len(orders) or any(
                type(v) is not int or not 0 <= v < order
                for v, order in zip(term, orders)
            ):
                raise ValueError("support exponent outside its cyclic order")
            poly += math.prod(symbol**exponent for symbol, exponent in zip(symbols, term))
        polynomials.append(poly)
    constructor = codes.BBCode if len(orders) == 2 else codes.QCCode
    code = constructor(dict(zip(symbols, orders)), *polynomials, field=2)
    hx = np.asarray(code.matrix_x, dtype=np.uint8).copy()
    hz = np.asarray(code.matrix_z, dtype=np.uint8).copy()
    expected_shape = (math.prod(orders), 2*math.prod(orders))
    if hx.shape != expected_shape or hz.shape != expected_shape:
        raise RuntimeError("qLDPC constructor returned unexpected matrix dimensions")
    return hx, hz
