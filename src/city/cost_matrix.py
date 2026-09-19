"""
Layer 0 — Precomputed shortest-path cost matrix over points of interest (POIs).

Why precompute
--------------
MCTS will ask "how far from here to there" tens of thousands of times per
planning call. Running Dijkstra live inside the search loop would dominate
runtime. Instead we precompute all-pairs shortest paths over a *small* POI set
(depot + charging stations + snapped customer nodes for the current epoch) and
hand the RL environment a plain O(1) lookup table.

This is the single most important performance decision in Layer 0.

Structure
---------
POI index order is fixed and shared with the env's action space:
    index 0            -> depot
    1 .. N             -> customers (this epoch / this vehicle's subset)
    N+1 .. N+M         -> charging stations

Keeping this ordering identical everywhere means the env, the network's action
head, and the MCTS action mask all agree without translation layers.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CostMatrix:
    """Dense distance/energy/time lookups between POIs, plus the underlying paths."""

    # distance: np.ndarray  # (P, P) metres along roads
    # energy:   np.ndarray  # (P, P) battery units
    # time:     np.ndarray  # (P, P) seconds — optional in v1
    # paths:    dict[tuple[int,int], list[int]]  # for rendering the actual driven route

    def __len__(self) -> int:
        raise NotImplementedError


def build_cost_matrix(graph, poi_nodes, energy_rate: float) -> CostMatrix:
    """All-pairs shortest paths restricted to `poi_nodes`.

    TODO(Checkpoint 1):
      - one Dijkstra per POI source (P sources, not |V| — this is the cheap part)
      - store both the scalar cost and the node path (needed by the visualizer)
      - assert symmetry is NOT assumed: real road graphs are directed (one-ways)
    """
    raise NotImplementedError
