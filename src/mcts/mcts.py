"""
Layer 3 — Neural-guided Monte Carlo Tree Search.

The network gives fast intuition; MCTS spends compute to turn that intuition
into a better-considered decision. The improved decision is then used as a
training target — that gap between "raw policy" and "policy after search" is
exactly what the self-play loop learns from.

Four phases per simulation
--------------------------
  select      : descend the tree by a PUCT-style rule balancing the network's
                prior against accumulated value estimates
  expand      : add the newly reached state, query the network for its prior
                and value, apply the legality mask
  evaluate    : use the network's value head — NOT random rollouts. Random
                rollouts in a routing problem are nearly worthless signal.
  backup      : propagate the value up the visited path

Sign convention (state it once, honour it everywhere)
-----------------------------------------------------
Rewards are negative costs and we always MAXIMIZE. The value head predicts
negative normalized remaining cost. Do not introduce a "minimize" branch
anywhere; mixing conventions is the single most common way this class of
implementation silently breaks.

Safety
------
Nodes are only ever expanded over `legal_action_mask(...)`. The search cannot
even represent a stranding move, so a stranded route is not merely unlikely —
it is unconstructible.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Node:
    """One search-tree node. Statistics per AlphaZero."""

    # prior: np.ndarray      # P(a|s) from the network, masked
    # children: dict[int, "Node"]
    visit_count: int = 0
    value_sum: float = 0.0
    children: dict = field(default_factory=dict)

    @property
    def value(self) -> float:
        return self.value_sum / self.visit_count if self.visit_count else 0.0


class MCTS:
    """Vanilla AlphaZero-style PUCT search. Baseline for the Gumbel variant."""

    def search(self, root_state, instance, num_simulations: int):
        """Return (improved_policy, root_value). TODO(Checkpoint 3)."""
        raise NotImplementedError
