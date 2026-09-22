"""
Layer 3 — The per-vehicle EVRP environment. A Gym-style MDP.

Scope of ONE episode
--------------------
One vehicle, one continuous tour: leave the depot, serve every customer in
this vehicle's assigned subset, recharge as needed, return to the depot
exactly once at the end. No early depot returns, no multi-trip.

MDP
---
state   : (position, battery, load, visited_mask) — the smallest
          representation that is still Markov (visit ORDER doesn't matter).
action  : POI index to travel to next.
reward  : -travel_cost per step, + completion bonus on returning to depot
          with all customers served.
term    : all customers served AND back at depot.

THE HARD CONSTRAINT
--------------------
step() can never produce a stranded state: every action offered by
legal_actions() satisfies the reachability-lookahead condition in
feasibility.py. An illegal action passed by the caller is a bug in the
caller, and step() raises rather than silently absorbing it.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from src.env.feasibility import assert_mask_nonempty, legal_action_mask


@dataclass
class EVRPState:
    """Small, cheaply-copyable MDP state. MCTS will clone this constantly."""

    position: int
    battery: float
    load: float
    visited: np.ndarray  # bool mask over customers, shape (num_customers,)
    step_count: int = 0

    def clone(self) -> "EVRPState":
        """Independent copy — mutating the clone must never affect the original.

        This is load-bearing for MCTS correctness (see
        tests/test_env.py::test_state_clone_is_independent): a shared numpy
        view here would silently corrupt the entire search tree.
        """
        return EVRPState(
            position=self.position,
            battery=self.battery,
            load=self.load,
            visited=self.visited.copy(),
            step_count=self.step_count,
        )


class IllegalActionError(ValueError):
    """Raised when step() is called with an action outside the legal mask.

    This is a caller bug, not something the environment should paper over —
    silently clipping to a legal action would hide errors in the agent/search
    code that produced the illegal action in the first place.
    """


class EVRPEnv:
    """Gym-style single-vehicle EVRP over a real road network."""

    def __init__(self, instance):
        self.instance = instance

    def reset(self) -> EVRPState:
        """Start a fresh episode from the depot with a full battery and load."""
        return EVRPState(
            position=self.instance.depot_index,
            battery=self.instance.battery_capacity,
            load=self.instance.vehicle_capacity,
            visited=np.zeros(self.instance.num_customers, dtype=bool),
            step_count=0,
        )

    def legal_actions(self, state: EVRPState) -> np.ndarray:
        """Boolean mask over POI indices. Delegates to feasibility.py."""
        mask = legal_action_mask(state, self.instance)
        assert_mask_nonempty(mask, state)
        return mask

    def step(self, state: EVRPState, action: int):
        """Apply `action`, return (next_state, reward, done, info).

        Functional style (state in, state out) rather than mutating in place,
        so MCTS can branch freely without defensive copying at every call site.
        """
        mask = self.legal_actions(state)
        if not mask[action]:
            raise IllegalActionError(
                f"Action {action} is not legal from state "
                f"(position={state.position}, battery={state.battery:.1f}, "
                f"load={state.load:.1f}). Legal actions: {np.flatnonzero(mask).tolist()}"
            )

        cost = self.instance.cost_matrix.cost(state.position, action)
        energy_used = self.instance.cost_matrix.energy_cost(state.position, action)
        reward = -cost

        new_visited = state.visited.copy()
        new_load = state.load
        new_battery = state.battery - energy_used

        if action in self.instance.customer_indices():
            new_visited[action - 1] = True
            new_load = state.load - self.instance.demand(action)
        elif action == self.instance.depot_index or action in self.instance.station_indices():
            # depot and charging stations both fully recharge in v1
            new_battery = self.instance.battery_capacity

        next_state = EVRPState(
            position=action,
            battery=new_battery,
            load=new_load,
            visited=new_visited,
            step_count=state.step_count + 1,
        )

        done = action == self.instance.depot_index and bool(new_visited.all())
        if done:
            reward += 0.0  # completion_bonus is 0.0 by default config; see instance/config

        info = {"cost": cost, "energy_used": energy_used}
        return next_state, reward, done, info

    def is_terminal(self, state: EVRPState) -> bool:
        return state.position == self.instance.depot_index and bool(state.visited.all())
