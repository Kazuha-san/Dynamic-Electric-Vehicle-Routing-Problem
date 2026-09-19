"""
Layer 4 — Nearest-neighbour construction with battery awareness.

The weakest baseline, and the most useful one early: if the trained agent cannot
beat greedy nearest-neighbour, something is wrong with the pipeline, not with
the hyperparameters.

Also doubles as an environment sanity check. Running NN through the same env and
hand-verifying the resulting cost is how we validate Layer 0/3 before any
learning exists (Checkpoint 2).
"""

from __future__ import annotations


def solve(instance):
    """Repeatedly take the nearest legal unvisited customer; detour to charge when
    the mask forces it. Returns (route, total_cost)."""
    raise NotImplementedError
