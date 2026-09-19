"""
Layer 3 — The self-play loop. Where learning actually happens.

There is no opponent. "Self-play" here means the network bootstraps off its own
search-improved decisions, generation after generation:

    1. Generate episodes with GumbelMCTS guided by the CURRENT network.
       At every step record (state, mcts_improved_policy).
    2. At episode end, record the achieved total cost -> value targets.
    3. Train the network: policy head toward the MCTS targets (cross-entropy),
       value head toward the achieved cost (MSE).
    4. The network is now slightly better -> its search is better -> the next
       generation of targets is better. Repeat.

The teacher (network + search, slow, deliberate) is always at least as good as
the student (raw network, fast, instinctive). Training distils teacher into
student; next round the teacher is built on a better student.

Value normalization
-------------------
Raw route costs vary wildly across instance sizes and city topologies, which
makes the value head's job impossible if fed unnormalized. Normalize per
instance (e.g. against a cheap reference such as the nearest-neighbour cost) and
keep the convention documented HERE, since mcts/ and agent/ both depend on it.

What gets logged every generation (for the report)
--------------------------------------------------
mean/best route cost, policy loss, value loss, feasibility rate (expected to be
100% by construction — if it is not, the masking has a bug), mean simulations
per move, wall-clock per generation.
"""

from __future__ import annotations


def run_episode(env, instance, net, search, config):
    """One self-play episode. Returns trajectory records + final cost."""
    raise NotImplementedError


def train_generation(net, replay_buffer, optimizer, config) -> dict:
    """One optimization pass. Returns a dict of losses for the log."""
    raise NotImplementedError


def selfplay_loop(config) -> None:
    """Outer loop over generations. TODO(Checkpoint 4)."""
    raise NotImplementedError
