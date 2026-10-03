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
