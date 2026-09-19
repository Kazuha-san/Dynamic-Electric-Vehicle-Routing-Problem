"""
Layer 3 — Reachability-lookahead feasibility masking. The safety layer.

This module is the reason the system can claim "the vehicle never gets stuck".
It is the most algorithmically interesting piece in Layer 3, and it is a hard
constraint, not a learned preference.

The naive check (NOT sufficient)
--------------------------------
    "can I reach node X with my current battery?"
This permits a trap: you arrive at X with 2% battery, and from X there is no
charging station or depot in range. You are stranded. The check passed and the
vehicle still died.

The correct check (what we implement)
-------------------------------------
An action to node X is legal iff:
    1. energy(position -> X) <= battery                       [can I get there]
    2. capacity/demand constraints hold                        [can I serve it]
    3. AFTER arriving at X with the remaining battery, there still exists a
       reachable "safe node" — a charging station or the depot                [can I escape]

Condition 3 is the lookahead. With recharging allowed, the escape check is:
    min over safe nodes S of energy(X -> S) <= battery_after_arrival

Performance
-----------
MCTS calls this on every node expansion, so it must be fast. The saving grace is
that "distance from X to the nearest safe node" does not depend on the episode
at all — it is a property of the city. So precompute, per POI:
    nearest_safe_energy[X] = min over safe nodes S of energy(X -> S)
once per instance, and condition 3 collapses to a single float comparison.

That precomputation is what makes a hard safety guarantee affordable.

Stronger variants (worth discussing in the report as an ablation)
-----------------------------------------------------------------
- Depth-1 escape (implemented): can I reach SOME safe node from X?
- Full completion feasibility: is there a feasible completion serving ALL
  remaining customers from X? This is strictly stronger but NP-hard in general —
  we deliberately do not attempt it, and the report should say so honestly.
"""

from __future__ import annotations


def precompute_nearest_safe_energy(cost_matrix, safe_poi_indices):
    """For each POI, the energy cost to its nearest charging station or depot.

    Instance-level, computed once. Turns the escape check into an O(1) compare.
    """
    raise NotImplementedError


def legal_action_mask(state, instance):
    """Boolean mask over POI indices: which moves are safe AND useful right now.

    Conditions per the module docstring. Returns a mask that is guaranteed
    non-empty for any state reachable from reset() — proving that non-emptiness
    is the whole safety argument, and tests/test_feasibility.py asserts it.
    """
    raise NotImplementedError


def assert_mask_nonempty(mask, state) -> None:
    """Loud failure if we ever produce a dead-end state. Should be unreachable."""
    raise NotImplementedError
