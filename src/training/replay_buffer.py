"""
Layer 3 — Replay buffer of self-play trajectories.

Stores (state_features, mcts_policy_target, value_target) tuples across recent
generations. Sampling from a window of generations rather than only the newest
one stabilizes training — the standard AlphaZero recipe.
"""

from __future__ import annotations


class ReplayBuffer:
    def add_episode(self, records) -> None:
        raise NotImplementedError

    def sample(self, batch_size: int):
        raise NotImplementedError
