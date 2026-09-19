"""
Layer 3 — The per-vehicle EVRP environment. A Gym-style MDP.

Scope of ONE episode
--------------------
One vehicle, one continuous tour: leave the depot, serve every customer in this
vehicle's assigned subset, recharge as needed, return to the depot exactly once
at the end. No early depot returns, no multi-trip (decided in planning) — this
keeps the horizon bounded and makes "feasible" unambiguous.

MDP
---
state   : (position, battery, load, visited_mask)
          This is deliberately the SMALLEST representation that is still Markov.
          The ORDER in which customers were visited does not affect what is
          reachable next, so it is not in the state.
action  : POI index to travel to next
          0 = depot, 1..N = customers, N+1..N+M = charging stations
          (ordering matches cost_matrix.py and the policy head — on purpose)
reward  : -travel_cost per step, + completion bonus on returning to depot with
          all customers served. Dense, because a dense signal is far easier to
          debug against baselines than a single terminal number.
term    : all customers served AND back at depot

THE HARD CONSTRAINT
-------------------
The vehicle must never be able to strand itself. This is enforced by masking in
feasibility.py, NOT by a penalty the network is supposed to learn its way
around. `step()` should be incapable of producing a stranded state, and there is
a test that asserts exactly that.

Cloning
-------
MCTS forks the state thousands of times per move, so the mutable state is kept
tiny and copy-cheap (`EVRPState` is a small dataclass of scalars + one bool
array). Do not add heavy objects to it; keep the road graph and cost matrix in
the env, shared by reference, never copied.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EVRPState:
    """Small, cheaply-copyable MDP state. MCTS clones this constantly."""

    position: int          # POI index
    battery: float
    load: float
    # visited: np.ndarray  # bool mask over customers
    step_count: int = 0

    def clone(self) -> "EVRPState":
        raise NotImplementedError


class EVRPEnv:
    """Gym-style single-vehicle EVRP over a real road network."""

    def reset(self, instance) -> EVRPState:
        """Start a fresh episode from the depot with a full battery."""
        raise NotImplementedError

    def step(self, state: EVRPState, action: int):
        """Apply `action`, return (next_state, reward, done, info).

        Functional style (state in, state out) rather than mutating `self`, so
        MCTS can branch freely without defensive copying everywhere.

        MUST assert the action is legal under the current mask. An illegal action
        is a bug in the caller, not something to silently absorb.
        """
        raise NotImplementedError

    def legal_actions(self, state: EVRPState):
        """Delegates to feasibility.py. See that module for the real work."""
        raise NotImplementedError

    def is_terminal(self, state: EVRPState) -> bool:
        raise NotImplementedError
