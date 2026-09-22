"""
Layer 3 — Reachability-lookahead feasibility masking. The safety layer.

This module is the reason the system can claim "the vehicle never gets stuck".
It is a hard constraint, not a learned preference.

The naive check (NOT sufficient)
--------------------------------
    "can I reach node X with my current battery?"
This permits a trap: you arrive at X with 2% battery, and from X there is no
charging station or depot in range. You are stranded. The check passed and the
vehicle still died.

A SECOND, subtler trap this module specifically guards against
-----------------------------------------------------------------
The obvious fix is "arriving at X must leave enough battery to reach SOME safe
node (a charging station or the depot)". But the depot is not actually a
general-purpose safe node in this project's rules: it only becomes a legal
target once every customer has been served (v1 = single continuous tour, no
early return). So a check that treats the depot as always-available as an
escape target is WRONG — it will say a move is safe when the vehicle is
actually stuck, because the "safe" node it computed a route to is one the
mask won't let it enter yet.

The check actually implemented
-------------------------------
An action to node X is legal iff:
    1. energy(position -> X) <= battery                        [can I get there]
    2. demand(X) <= remaining load, if X is a customer          [can I serve it]
    3. after arriving at X:
         - if X is a charging station: automatically safe (full recharge there)
         - if X is the depot: only reachable once all customers are visited
           (enforced directly, not via the escape table)
         - if X is a customer: remaining battery must be enough to reach
             (a) the nearest charging station (ALWAYS a valid escape), OR
             (b) the depot directly, BUT ONLY IF visiting X completes the
                 tour (i.e. X is the last unvisited customer) — since only
                 then does the mask actually permit a subsequent move to the
                 depot.

`instance.nearest_safe_energy[X]` (see instance.py) is precomputed against
CHARGING STATIONS ONLY for exactly this reason — it is always a valid escape
distance, unlike a depot-inclusive version would be.

Deliberately NOT attempted: full completion feasibility ("is there a route
serving every remaining customer from here?") is strictly stronger and
NP-hard in general. Depth-1 escape (as described above) is what is
implemented, and that limitation is stated plainly rather than overclaimed.
"""

from __future__ import annotations

import numpy as np


def legal_action_mask(state, instance) -> np.ndarray:
    """Boolean mask over POI indices: which moves are safe AND useful right now.

    Guaranteed non-empty for any state reachable from a valid reset() — see
    tests/test_feasibility.py::test_mask_is_never_empty_along_random_rollouts,
    which brute-forces this claim rather than merely asserting it.
    """
    P = instance.num_pois
    mask = np.zeros(P, dtype=bool)

    for j in range(P):
        if j == state.position:
            continue  # never "move" to where you already are

        energy_to_j = instance.cost_matrix.energy_cost(state.position, j)
        if energy_to_j > state.battery + 1e-9:
            continue  # condition 1: can't even get there

        battery_after = state.battery - energy_to_j

        if j == instance.depot_index:
            # Depot is only a meaningful (and legal) target once every
            # customer has been served — v1: single continuous tour.
            if not state.visited.all():
                continue
            # condition 1 already confirmed we can physically reach it; once
            # there, the episode ends, so there is no further escape to check.
            mask[j] = True
            continue

        if j in instance.customer_indices():
            if state.visited[j - 1]:
                continue  # already served, nothing to do there
            if instance.demand(j) > state.load + 1e-9:
                continue  # condition 2: can't carry it

            would_complete_tour = (
                state.visited.sum() + 1 == instance.num_customers
            )
            can_reach_station = instance.nearest_safe_energy[j] <= battery_after + 1e-9
            can_reach_depot_directly = (
                would_complete_tour
                and instance.cost_matrix.energy_cost(j, instance.depot_index) <= battery_after + 1e-9
            )
            if not (can_reach_station or can_reach_depot_directly):
                continue  # condition 3: no way to survive after this move

            mask[j] = True
            continue

        # otherwise, j is a charging station: reaching it is automatically
        # safe (it fully recharges the vehicle), so condition 1 alone suffices.
        mask[j] = True

    return mask


def assert_mask_nonempty(mask: np.ndarray, state) -> None:
    """Loud failure if we ever produce a dead-end state. Should be unreachable
    for any state produced by EVRPEnv.step() starting from EVRPEnv.reset()."""
    if not mask.any():
        raise RuntimeError(
            f"Feasibility mask is empty at position={state.position}, "
            f"battery={state.battery}, load={state.load}. This means a prior "
            f"step allowed a move without verifying the escape condition — "
            f"a bug in legal_action_mask() or its caller, not a property of "
            f"a well-formed EVRP instance."
        )
