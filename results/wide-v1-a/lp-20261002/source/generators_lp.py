"""Reproducible weight-5 lifted-product candidates built with qLDPC 0.4.0.

``candidates`` only creates serializable construction specifications.  It performs
no distance search.  ``construct`` uses qLDPC's RingArray and LPCode, including its
left/right bimodule implementation for noncommutative groups.  The common search
pipeline owns ranks, distances, witnesses, connectivity, and the trusted gate.
"""

from __future__ import annotations

import functools
import importlib.metadata
import math
import random
from typing import TYPE_CHECKING, Any, Iterator, Mapping

if TYPE_CHECKING:
    import numpy as np


QLDPC_VERSION = "0.4.0"
BOARD_REVISION = "c2ebca1713c89277dbd6ddf3ee587cbf7f1a9d23"

# (l1, l2, q) means C_l1 semidirect_q C_l2, with b*a*b^-1 = a^q.
# The first twenty specifications cycle four times through these five actual
# board gaps.  Their target k and d are goals, not measured code parameters.
_FIRST_GROUPS = (
    (35, 1, 1),
    (18, 2, 17),
    (37, 1, 1),
    (19, 2, 18),
    (13, 3, 3),
)

# Additional presentations extend those gaps and include small instances whose
# target distances may be more affordable to certify.  All have n <= 676.
_LATER_GROUPS = (
    (9, 4, 8),
    (36, 1, 1),
    (6, 6, 1),
    (38, 1, 1),
    (39, 1, 1),
    (41, 1, 1),
    (43, 1, 1),
    (22, 2, 21),
    (11, 4, 10),
    (15, 3, 1),
    (23, 2, 22),
    (47, 1, 1),
    (7, 1, 1),
    (8, 1, 1),
    (4, 2, 1),
    (9, 1, 1),
    (3, 3, 1),
    (5, 2, 4),
    (11, 1, 1),
    (6, 2, 5),
    (7, 2, 6),
    (8, 2, 7),
    (9, 2, 8),
    (10, 2, 9),
    (7, 3, 2),
    (11, 2, 10),
    (12, 2, 11),
    (13, 2, 12),
    (9, 3, 4),
    (24, 2, 23),
    (12, 4, 5),
    (49, 1, 1),
    (7, 7, 1),
    (25, 2, 24),
    (51, 1, 1),
    (26, 2, 25),
    (13, 4, 5),
)

# Conservative sufficient escape distances at k=|G|+4 and w=5, computed from
# all 1680 CSS files at BOARD_REVISION.  Higher actual k can lower the threshold;
# a current-board frontier check must therefore supersede this priority hint.
_TARGET_D = {
    7: 6, 8: 6, 9: 6, 10: 6, 11: 6,
    12: 7, 14: 7, 16: 7, 18: 7, 20: 7, 21: 7, 22: 7, 24: 7, 26: 7, 27: 7,
    35: 4, 36: 4, 37: 4, 38: 4, 39: 4, 41: 4, 43: 4,
    44: 5, 45: 5, 46: 5, 47: 5, 48: 10, 49: 9, 50: 9, 51: 9, 52: 9,
}


@functools.lru_cache(maxsize=64)
def _multiplication_table(l1: int, l2: int, action: int) -> tuple[tuple[int, ...], ...]:
    """Cayley table with index a*l2+b representing a^a b^b.

    In coordinate notation the product is (u,v)(s,t) =
    (u + action**v*s mod l1, v+t mod l2).  This is a group definition,
    not a parity-check constructor or distance implementation.
    """
    if l1 < 2 or l2 < 1:
        raise ValueError("Require l1 >= 2 and l2 >= 1")
    if math.gcd(action, l1) != 1 or pow(action, l2, l1) != 1:
        raise ValueError("The action must be a unit with action**l2 == 1 mod l1")
    order = l1 * l2
    return tuple(
        tuple(
            ((i // l2 + pow(action, i % l2, l1) * (j // l2)) % l1) * l2
            + ((i % l2 + j % l2) % l2)
            for j in range(order)
        )
        for i in range(order)
    )


def _generates(table: tuple[tuple[int, ...], ...], pair: tuple[int, int]) -> bool:
    """Require each normalized seed to use the entire declared group.

    This prevents a proper-subgroup seed from creating disconnected padding.
    The final CSS graph must still pass the common pipeline's connectivity check.
    """
    reached = {0}
    pending = [0]
    while pending:
        element = pending.pop()
        for generator in pair:
            product = table[element][generator]
            if product not in reached:
                reached.add(product)
                pending.append(product)
    return len(reached) == len(table)


def _sample_pair(
    rng: random.Random,
    table: tuple[tuple[int, ...], ...],
    forbidden: tuple[int, int] | None = None,
) -> tuple[int, int]:
    for _ in range(10_000):
        pair = tuple(sorted(rng.sample(range(1, len(table)), 2)))
        if pair != forbidden and _generates(table, pair):
            return pair
    raise RuntimeError("Could not obtain two distinct connected seed generators")


def candidates(seed: int, count: int) -> Iterator[dict[str, Any]]:
    """Yield ``count`` deterministic, JSON-serializable LP construction specs.

    Both bases are fully occupied 2x3 monomial matrices, normalized to
    [[1,1,1],[1,a,b]].  Each pair generates G.  A and B are sampled separately
    and are unequal; no claim is made that every algebraic equivalence is removed.
    Construction uses no direct sums, puncturing, or appended qubits.
    """
    if count < 0:
        raise ValueError("count must be nonnegative")
    rng = random.Random(seed)
    seen: set[tuple[Any, ...]] = set()
    for index in range(count):
        params = (
            _FIRST_GROUPS[index % len(_FIRST_GROUPS)]
            if index < 20
            else _LATER_GROUPS[(index - 20) % len(_LATER_GROUPS)]
        )
        l1, l2, action = params
        table = _multiplication_table(*params)
        for _ in range(10_000):
            pair_a = _sample_pair(rng, table)
            pair_b = _sample_pair(rng, table, forbidden=pair_a)
            # Exchanging the two bases adds no useful second specimen.
            pair_a, pair_b = sorted((pair_a, pair_b))
            identity = (params, pair_a, pair_b)
            if identity not in seen:
                seen.add(identity)
                break
        else:
            raise RuntimeError(f"Unique seed-pair space exhausted for group {params}")
        order = l1 * l2
        yield {
            "schema_version": 1,
            "family": "lifted-product",
            "generator": "monomial-2x3-v1",
            "qldpc_version": QLDPC_VERSION,
            "seed": seed,
            "index": index,
            "group": {
                "kind": "metacyclic",
                "l1": l1,
                "l2": l2,
                "action": action,
                "order": order,
                "element_index": "u*l2+v represents a^u b^v",
            },
            "entry_type": "group-element-index (one monomial per entry)",
            "matrix_a": [[0, 0, 0], [0, *pair_a]],
            "matrix_b": [[0, 0, 0], [0, *pair_b]],
            "target": {
                "board_revision": BOARD_REVISION,
                "n": 13 * order,
                "k": order + 4,
                "d_min": _TARGET_D[order],
                "w_max": 5,
                "status": "search_target_not_measurement",
            },
        }


def _seed_square(table: tuple[tuple[int, ...], ...], pair: tuple[int, int]) -> bool:
    """Structural 4-cycle test for the three-matching classical seed graph."""
    labels = {0, *pair}
    return any(
        sum(table[label][translate] in labels for label in labels) > 1
        for translate in range(1, len(table))
    )


def _element_order(table: tuple[tuple[int, ...], ...], element: int) -> int:
    current = element
    for order in range(1, len(table) + 1):
        if current == 0:
            return order
        current = table[current][element]
    raise ValueError("Invalid finite-group table")


def next_candidates(seed: int, count: int) -> Iterator[dict[str, Any]]:
    """Bounded improvement campaign; leaves the original recipe stream unchanged.

    First six slots improve size/rate using complementary cyclic seed subgroups.
    The two subgroups together generate the full group; the final CSS graph must
    also pass the common connectivity check.  The remaining slots use nonabelian
    lifts to search beyond the cyclic construction's distance-six obstruction.
    Every target is a proposal, and must be replaced by measured rank/distance.
    """
    if count < 0:
        raise ValueError("count must be nonnegative")
    # (group presentation, subgroup index A, index B, target k, target d)
    # None indices select individually connected nonabelian seeds.
    campaign = (
        ((32, 1, 1), 4, 1, 39, 6),   # same k,d as 455-39-6, 39 fewer qubits
        ((33, 1, 1), 3, 1, 39, 6),   # alternate compression route
        ((35, 1, 1), 5, 1, 43, 6),   # four more logicals at the same n,d,w
        ((36, 1, 1), 4, 3, 45, 6),   # more k and d than 468-40-4
        ((30, 1, 1), 5, 6, 43, 4),   # fewer n and more k than 468-40-4
        ((28, 1, 1), 4, 7, 41, 4),   # a smaller alternative to the preceding slot
        ((9, 4, 8), None, None, 40, 7),
        ((5, 4, 4), None, None, 24, 7),
        ((4, 4, 3), None, None, 20, 7),
        ((6, 4, 5), None, None, 28, 7),
        ((11, 4, 10), None, None, 48, 8),
    )
    rng = random.Random(seed)
    seen: set[tuple[Any, ...]] = set()
    for index in range(count):
        params, index_a, index_b, target_k, target_d = campaign[index % len(campaign)]
        l1, l2, action = params
        order = l1 * l2
        table = _multiplication_table(*params)

        def sample(subgroup_index: int | None) -> tuple[int, int]:
            for _ in range(10_000):
                if subgroup_index is not None:
                    quotient_order = order // subgroup_index
                    residual = tuple(sorted(rng.sample(range(1, quotient_order), 2)))
                    if math.gcd(quotient_order, *residual) != 1:
                        continue
                    pair = tuple(subgroup_index * exponent for exponent in residual)
                else:
                    pair = _sample_pair(rng, table)
                    inverse_a = table[pair[0]].index(0)
                    difference = table[inverse_a][pair[1]]
                    if any(_element_order(table, element) < 4
                           for element in (*pair, difference)):
                        continue
                if target_d >= 6 and _seed_square(table, pair):
                    continue
                return pair
            raise RuntimeError(f"No structurally admissible seed sampled for {params}")

        for _ in range(10_000):
            pair_a, pair_b = sample(index_a), sample(index_b)
            if pair_a == pair_b:
                continue
            identity = (params, tuple(sorted((pair_a, pair_b))))
            if identity not in seen:
                seen.add(identity)
                break
        else:
            raise RuntimeError(f"Unique improvement recipes exhausted for {params}")

        is_cyclic = index_a is not None
        if is_cyclic:
            assert index_b is not None and math.gcd(index_a, index_b) == 1
            assert target_k == order + index_a + index_b + 2
        yield {
            "schema_version": 1,
            "family": "lifted-product",
            "generator": "monomial-2x3-v1",
            "strategy": "cyclic-subgroup-improvement" if is_cyclic else "nonabelian-distance-improvement",
            "qldpc_version": QLDPC_VERSION,
            "seed": seed,
            "index": index,
            "group": {
                "kind": "metacyclic", "l1": l1, "l2": l2, "action": action,
                "order": order, "element_index": "u*l2+v represents a^u b^v",
            },
            "entry_type": "group-element-index (one monomial per entry)",
            "matrix_a": [[0, 0, 0], [0, *pair_a]],
            "matrix_b": [[0, 0, 0], [0, *pair_b]],
            "seed_subgroup_indices": [index_a, index_b],
            "connectivity_condition": "coprime cyclic subgroup indices" if is_cyclic else "both seed pairs generate G",
            "distance_upper_bound": 6 if is_cyclic else None,
            "distance_bound_basis": "commutative 2x3 cofactor logical" if is_cyclic else "no quantum bound asserted",
            "target": {
                "board_revision": BOARD_REVISION, "n": 13 * order,
                "k": target_k, "d_min": target_d, "w_max": 5,
                "status": "improvement_goal_not_measurement",
            },
        }


# Frozen projections of the official CSS board at BOARD_REVISION together with
# the seven locally certified w=5 LP points available when v2 was declared.
# Each (n,k) represents an existing code of weight <=5 and distance >= the key.
# These are the exact nondominated projections for n<=13*53; the common driver
# still recomputes its bar from the live board and local certificate registry.
_V2_EXISTING_AT_DISTANCE = {
    4: ((16, 2), (18, 4), (40, 10), (80, 18), (150, 32), (360, 38),
        (364, 41), (390, 43), (468, 45), (546, 46), (565, 51),
        (624, 54), (660, 68), (676, 71)),
    6: ((36, 4), (84, 6), (150, 32), (360, 38), (416, 39),
        (455, 43), (468, 45), (546, 46), (624, 54), (660, 68)),
}
_V2_LOCAL_POINTS = (
    (455, 39, 6, 5), (468, 40, 4, 5), (416, 39, 6, 5),
    (455, 43, 6, 5), (468, 45, 6, 5), (390, 43, 4, 5), (364, 41, 4, 5),
)


def cyclic_goal_catalog_v2() -> list[dict[str, Any]]:
    """Enumerate every connected proper-subgroup integer goal for N<=53.

    For d=6, both seed subgroup orders are at least seven.  This is precisely
    when a connected three-shift seed without a square exists: six distinct
    signed differences are necessary, and shifts (0,1,3) suffice for all M>=7.
    For d=4, subgroup orders at least three allow three distinct monomials.
    Algebraic dimensions and structural feasibility are not distance proofs.
    """
    goals: list[dict[str, Any]] = []
    for distance, minimum_order in ((6, 7), (4, 3)):
        for order in range(3, 54):
            divisors = [g for g in range(1, order // minimum_order + 1)
                        if order % g == 0]
            for index_a in divisors:
                for index_b in divisors:
                    if (index_a > index_b or index_a == index_b == 1
                            or math.gcd(index_a, index_b) != 1):
                        continue
                    n = 13 * order
                    k = order + index_a + index_b + 2
                    dominators = [list(point)
                                  for point in _V2_EXISTING_AT_DISTANCE[distance]
                                  if point[0] <= n and point[1] >= k]
                    goals.append({
                        "id": f"cyclic-N{order}-g{index_a}-{index_b}-d{distance}",
                        "order": order, "subgroup_indices": [index_a, index_b],
                        "n": n, "k": k, "d": distance, "w": 5,
                        "pruned_by_existing": dominators,
                    })
    for goal in goals:
        goal["preferred_parameter_target"] = not goal["pruned_by_existing"] and not any(
            other["d"] == goal["d"] and not other["pruned_by_existing"]
            and other["n"] <= goal["n"] and other["k"] >= goal["k"]
            and (other["n"] < goal["n"] or other["k"] > goal["k"])
            for other in goals
        )
    return goals


@functools.lru_cache(maxsize=128)
def _cyclic_pair_pool_v2(
    order: int, subgroup_index: int, square_free: bool,
) -> tuple[tuple[int, int], ...]:
    """Finite group-label combinatorics only; no parity checks or distance search."""
    modulus = order // subgroup_index
    pairs = []
    for a in range(1, modulus):
        for b in range(a + 1, modulus):
            if math.gcd(modulus, a, b) != 1:
                continue
            signed_differences = {a, b, (b - a) % modulus,
                                  (-a) % modulus, (-b) % modulus, (a - b) % modulus}
            if square_free and len(signed_differences) != 6:
                continue
            pairs.append((subgroup_index * a, subgroup_index * b))
    return tuple(pairs)


def _cyclic_equivalence_key_v2(
    order: int, pair_a: tuple[int, int], pair_b: tuple[int, int],
) -> tuple[Any, ...]:
    """Remove the stated monomial/permutation equivalences, not all isomorphisms."""
    def normalize(pair: tuple[int, int], unit: int) -> tuple[int, int]:
        labels = (0, (unit * pair[0]) % order, (unit * pair[1]) % order)
        return min(
            tuple(sorted((sign * (label - pivot)) % order
                         for label in labels if label != pivot))
            for pivot in labels for sign in (1, -1)
        )

    return (order, *min(
        tuple(sorted((normalize(pair_a, unit), normalize(pair_b, unit))))
        for unit in range(1, order) if math.gcd(unit, order) == 1
    ))


def next_candidates_v2(seed: int, count: int) -> Iterator[dict[str, Any]]:
    """Enumerated cyclic goals, pruned against frozen certified results.

    Every goal is declared before any seed is drawn.  Preferred size/capacity
    targets come first, interleaving one d6 goal with up to three compact d4
    goals.  Other undominated integer goals remain available as fallbacks.
    Original candidates, next_candidates, and construct are intentionally
    unchanged.  No target or structural filter establishes a distance.
    """
    if count < 0:
        raise ValueError("count must be nonnegative")
    goals = [goal for goal in cyclic_goal_catalog_v2() if not goal["pruned_by_existing"]]
    preferred = {
        distance: sorted((goal for goal in goals if goal["d"] == distance
                           and goal["preferred_parameter_target"]),
                         key=lambda goal: (goal["n"], -goal["k"], goal["subgroup_indices"]))
        for distance in (6, 4)
    }
    campaign = []
    while preferred[6] or preferred[4]:
        if preferred[6]:
            campaign.append(preferred[6].pop(0))
        for _ in range(3):
            if preferred[4]:
                campaign.append(preferred[4].pop(0))
    campaign.extend(sorted((goal for goal in goals if not goal["preferred_parameter_target"]),
                           key=lambda goal: (goal["n"], -goal["d"], -goal["k"],
                                             goal["subgroup_indices"])))
    rng = random.Random(seed)
    seen: set[tuple[Any, ...]] = set()
    exhausted: set[str] = set()
    cursor = 0
    for index in range(count):
        while True:
            if len(exhausted) == len(campaign):
                raise RuntimeError("Distinct v2 cyclic recipe space exhausted")
            goal = campaign[cursor % len(campaign)]
            cursor += 1
            if goal["id"] in exhausted:
                continue
            order = goal["order"]
            index_a, index_b = goal["subgroup_indices"]
            pool_a = _cyclic_pair_pool_v2(order, index_a, goal["d"] == 6)
            pool_b = _cyclic_pair_pool_v2(order, index_b, goal["d"] == 6)
            for _ in range(256):
                pair_a, pair_b = rng.choice(pool_a), rng.choice(pool_b)
                identity = _cyclic_equivalence_key_v2(order, pair_a, pair_b)
                if identity not in seen:
                    seen.add(identity)
                    break
            else:
                exhausted.add(goal["id"])
                continue
            break
        yield {
            "schema_version": 1, "family": "lifted-product",
            "generator": "monomial-2x3-v1", "strategy": "cyclic-catalog-v2",
            "qldpc_version": QLDPC_VERSION, "seed": seed, "index": index,
            "goal_id": goal["id"],
            "group": {
                "kind": "metacyclic", "l1": order, "l2": 1, "action": 1,
                "order": order, "element_index": "u*l2+v represents a^u b^v",
            },
            "entry_type": "group-element-index (one monomial per entry)",
            "matrix_a": [[0, 0, 0], [0, *pair_a]],
            "matrix_b": [[0, 0, 0], [0, *pair_b]],
            "seed_subgroup_indices": [index_a, index_b],
            "seed_square_free_required": goal["d"] == 6,
            "connectivity_condition": "coprime cyclic subgroup indices",
            "distance_upper_bound": 6,
            "distance_bound_basis": "commutative 2x3 cofactor logical",
            "equivalence_key": identity,
            "equivalence_scope": "seed translations/reversals, common cyclic unit, base exchange",
            "target": {
                "board_revision": BOARD_REVISION,
                "local_certified_points_snapshot": _V2_LOCAL_POINTS,
                "n": goal["n"], "k": goal["k"], "d_min": goal["d"], "w_max": 5,
                "status": "improvement_goal_not_measurement",
            },
        }


@functools.lru_cache(maxsize=64)
def _qldpc_group(l1: int, l2: int, action: int) -> tuple[Any, tuple[Any, ...]]:
    import numpy as np
    from qldpc import abstract

    table = np.asarray(_multiplication_table(l1, l2, action), dtype=int)
    group = abstract.Group.from_table(table)
    members = tuple(group.generate())
    if len(members) != l1 * l2 or members[0] != group.identity:
        raise RuntimeError("qLDPC did not preserve the table's identity-first enumeration")
    if any(members[i] * members[j] != members[int(table[i, j])]
           for i in range(len(members)) for j in range(len(members))):
        raise RuntimeError("qLDPC member indices disagree with the specified Cayley table")
    return group, members


def construct(spec: Mapping[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    """Construct binary HX,HZ with qLDPC 0.4.0; compute no distance.

    qLDPC's noncommutative ring Kronecker product induces the left/right
    bimodule internally.  Expanding the two classical seeds and applying
    ``numpy.kron`` would be a different construction and is deliberately avoided.
    """
    import numpy as np
    from qldpc import abstract, codes

    installed = importlib.metadata.version("qldpc")
    if installed != QLDPC_VERSION or spec.get("qldpc_version") != QLDPC_VERSION:
        raise RuntimeError(f"Require qLDPC {QLDPC_VERSION}; installed {installed}")
    if spec.get("generator") != "monomial-2x3-v1":
        raise ValueError("Unknown LP generator specification")
    group_spec = spec["group"]
    if group_spec.get("kind") != "metacyclic":
        raise ValueError("Unknown LP group kind")
    l1, l2, action = (int(group_spec[key]) for key in ("l1", "l2", "action"))
    if int(group_spec["order"]) != l1 * l2:
        raise ValueError("Group order does not match its presentation")
    group, members = _qldpc_group(l1, l2, action)
    ring = abstract.GroupRing(group, field=2)

    def ring_matrix(key: str) -> Any:
        matrix = spec[key]
        if len(matrix) != 2 or any(len(row) != 3 for row in matrix):
            raise ValueError("This generator requires two 2x3 monomial bases")
        if any(not isinstance(value, int) or not 0 <= value < len(members)
               for row in matrix for value in row):
            raise ValueError("Invalid group-element index")
        return abstract.RingArray.build(
            [[members[value] for value in row] for row in matrix], ring=ring
        )

    code = codes.LPCode(ring_matrix("matrix_a"), ring_matrix("matrix_b"), set_logicals=False)
    hx = np.asarray(code.matrix_x, dtype=np.uint8).copy()
    hz = np.asarray(code.matrix_z, dtype=np.uint8).copy()
    expected_shape = (6 * l1 * l2, 13 * l1 * l2)
    if hx.shape != expected_shape or hz.shape != expected_shape:
        raise RuntimeError(f"Unexpected lifted-product shapes: {hx.shape}, {hz.shape}")
    return hx, hz


# Frozen d>=6 projections of the official CSS board at BOARD_REVISION plus the
# 18 locally certified points recorded at this campaign's declaration.  The
# local points do not change either projection.  The runner owns live pruning.
_WIDE_EXISTING_D6 = {
    6: ((24, 2), (30, 4), (42, 6), (54, 8), (62, 10), (72, 12),
        (96, 16), (140, 20), (150, 32), (284, 58), (540, 112),
        (675, 139), (864, 146), (900, 182), (960, 258)),
    7: ((24, 2), (30, 4), (42, 6), (48, 8), (62, 10), (72, 12),
        (90, 16), (96, 20), (124, 22), (150, 32), (228, 34),
        (230, 40), (249, 42), (278, 44), (284, 58), (330, 60),
        (443, 74), (540, 112), (675, 139), (864, 146),
        (896, 194), (960, 258)),
}


def _wide_sidon_possible(modulus: int, columns: int) -> bool:
    # Four shifts: (0,1,4,6) works at every M>=13.
    # Five shifts: (0,1,4,14,16) works at M=21; (0,1,4,9,11) at M>=23.
    # All 5985 normalized five-subsets at M=22 were checked: none is Sidon.
    return modulus >= 13 if columns == 4 else modulus == 21 or modulus >= 23


def wide_goal_catalog() -> list[dict[str, Any]]:
    """Enumerate cyclic 2xc Sidon-seed integer goals for c=4,5 under n<=1000."""
    goals: list[dict[str, Any]] = []
    for columns in (4, 5):
        free = columns - 2
        for order in range(columns * (columns - 1) + 1, 1000 // (columns**2 + 4) + 1):
            divisors = [g for g in range(1, order + 1) if order % g == 0
                        and _wide_sidon_possible(order // g, columns)]
            for index_a in divisors:
                for index_b in divisors:
                    if index_a > index_b or math.gcd(index_a, index_b) != 1:
                        continue
                    n = (columns**2 + 4) * order
                    k = free**2 * order + free * (index_a + index_b) + 2
                    weight = columns + 2
                    goals.append({
                        "id": f"wide-c{columns}-N{order}-g{index_a}-{index_b}-d6",
                        "columns": columns, "order": order,
                        "subgroup_indices": [index_a, index_b],
                        "n": n, "k": k, "d": 6, "w": weight,
                        "pruned_by_existing": [list(point) for point in _WIDE_EXISTING_D6[weight]
                                               if point[0] <= n and point[1] >= k],
                    })
    for goal in goals:
        goal["preferred_parameter_target"] = not goal["pruned_by_existing"] and not any(
            not other["pruned_by_existing"] and other["w"] <= goal["w"]
            and other["n"] <= goal["n"] and other["k"] >= goal["k"]
            and any(other[key] != goal[key] for key in ("n", "k", "w"))
            for other in goals
        )
    return goals


def _wide_shift_sample(
    rng: random.Random, order: int, subgroup_index: int, columns: int,
) -> tuple[int, ...]:
    modulus = order // subgroup_index
    if not _wide_sidon_possible(modulus, columns):
        raise ValueError("No admitted Sidon seed exists for this subgroup order")
    for _ in range(10_000):
        tail = tuple(sorted(rng.sample(range(1, modulus), columns - 1)))
        if math.gcd(modulus, *tail) != 1:
            continue
        shifts = (0, *tail)
        if len({(a - b) % modulus for a in shifts for b in shifts if a != b}) != columns * (columns - 1):
            continue
        return tuple(subgroup_index * x for x in shifts)
    raise RuntimeError("Bounded Sidon seed sampling failed")


def _wide_equivalence_key(
    order: int, shifts_a: tuple[int, ...], shifts_b: tuple[int, ...],
) -> tuple[Any, ...]:
    def normalize(shifts: tuple[int, ...], unit: int) -> tuple[int, ...]:
        return min(tuple(sorted((sign * unit * (x - pivot)) % order for x in shifts))
                   for pivot in shifts for sign in (1, -1))

    return (len(shifts_a), order, *min(
        tuple(sorted((normalize(shifts_a, unit), normalize(shifts_b, unit))))
        for unit in range(1, order) if math.gcd(unit, order) == 1
    ))


def wide_candidates(seed: int, count: int) -> Iterator[dict[str, Any]]:
    """Separate higher-rate campaign; construct these specs with construct_wide.

    The first four recipes use c4 and orders13..16, followed by the c5/order21
    probe.  All targets seek global distance6, which remains to be measured.
    """
    if count < 0:
        raise ValueError("count must be nonnegative")
    goals = [g for g in wide_goal_catalog() if not g["pruned_by_existing"]]
    queues = {
        columns: sorted((g for g in goals if g["columns"] == columns
                         and g["preferred_parameter_target"]),
                        key=lambda g: (g["n"], -g["k"], g["subgroup_indices"]))
        for columns in (4, 5)
    }
    campaign = []
    while queues[4] or queues[5]:
        for _ in range(4):
            if queues[4]:
                campaign.append(queues[4].pop(0))
        if queues[5]:
            campaign.append(queues[5].pop(0))
    campaign.extend(sorted((g for g in goals if not g["preferred_parameter_target"]),
                           key=lambda g: (g["n"], g["w"], -g["k"], g["subgroup_indices"])))
    rng = random.Random(seed)
    seen: set[tuple[Any, ...]] = set()
    for index in range(count):
        goal = campaign[index % len(campaign)]
        order, columns = goal["order"], goal["columns"]
        index_a, index_b = goal["subgroup_indices"]
        for attempt in range(10_000):
            if index == 0 and attempt == 0:
                shifts_a, shifts_b = (0, 1, 3, 9), (0, 1, 4, 6)
            elif index == 4 and attempt == 0:
                shifts_a, shifts_b = (0, 1, 4, 14, 16), (0, 1, 6, 8, 18)
            else:
                shifts_a = _wide_shift_sample(rng, order, index_a, columns)
                shifts_b = _wide_shift_sample(rng, order, index_b, columns)
            identity = _wide_equivalence_key(order, shifts_a, shifts_b)
            if identity not in seen:
                seen.add(identity)
                break
        else:
            raise RuntimeError("Bounded sampling found no new wide recipe equivalence class")
        yield {
            "schema_version": 1, "family": "lifted-product",
            "generator": "monomial-2xc-v1", "strategy": "cyclic-wide-sidon-v1",
            "base_columns": columns, "qldpc_version": QLDPC_VERSION,
            "seed": seed, "index": index, "goal_id": goal["id"],
            "group": {
                "kind": "metacyclic", "l1": order, "l2": 1, "action": 1,
                "order": order, "element_index": "u*l2+v represents a^u b^v",
            },
            "entry_type": "group-element-index (one monomial per entry)",
            "matrix_a": [[0] * columns, list(shifts_a)],
            "matrix_b": [[0] * columns, list(shifts_b)],
            "seed_subgroup_indices": [index_a, index_b],
            "seed_square_free_required": True,
            "connectivity_condition": "coprime cyclic subgroup indices",
            "distance_upper_bound": 6,
            "distance_bound_basis": "commutative 2xc three-column cofactor logical",
            "equivalence_key": identity,
            "equivalence_scope": "seed translations/reversals, common cyclic unit, base exchange",
            "target": {
                "board_revision": BOARD_REVISION,
                "n": goal["n"], "k": goal["k"], "d_min": 6, "w_max": goal["w"],
                "status": "improvement_goal_not_measurement",
            },
        }


def construct_wide(spec: Mapping[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    """Build the separate cyclic 2x4/2x5 family using qLDPC 0.4.0 LPCode."""
    import numpy as np
    from qldpc import abstract, codes

    installed = importlib.metadata.version("qldpc")
    if installed != QLDPC_VERSION or spec.get("qldpc_version") != QLDPC_VERSION:
        raise RuntimeError(f"Require qLDPC {QLDPC_VERSION}; installed {installed}")
    if spec.get("generator") != "monomial-2xc-v1":
        raise ValueError("Unknown wide LP generator specification")
    columns = spec.get("base_columns")
    if columns not in (4, 5):
        raise ValueError("Wide construction requires four or five columns")
    group_spec = spec["group"]
    order = int(group_spec["order"])
    if (group_spec.get("kind") != "metacyclic" or group_spec.get("l1") != order
            or group_spec.get("l2") != 1 or group_spec.get("action") != 1):
        raise ValueError("This wide campaign requires a cyclic group")
    group, members = _qldpc_group(order, 1, 1)
    ring = abstract.GroupRing(group, field=2)

    def ring_matrix(key: str) -> Any:
        matrix = spec[key]
        if len(matrix) != 2 or any(len(row) != columns for row in matrix):
            raise ValueError("Wide base shape disagrees with base_columns")
        if any(not isinstance(value, int) or not 0 <= value < order
               for row in matrix for value in row):
            raise ValueError("Invalid group-element index")
        if matrix[0] != [0] * columns or matrix[1][0] != 0 or len(set(matrix[1])) != columns:
            raise ValueError("Require normalized, distinct wide seed shifts")
        return abstract.RingArray.build(
            [[members[value] for value in row] for row in matrix], ring=ring
        )

    code = codes.LPCode(ring_matrix("matrix_a"), ring_matrix("matrix_b"), set_logicals=False)
    hx = np.asarray(code.matrix_x, dtype=np.uint8).copy()
    hz = np.asarray(code.matrix_z, dtype=np.uint8).copy()
    expected_shape = (2 * columns * order, (columns**2 + 4) * order)
    if hx.shape != expected_shape or hz.shape != expected_shape:
        raise RuntimeError(f"Unexpected wide LP shapes: {hx.shape}, {hz.shape}")
    return hx, hz
