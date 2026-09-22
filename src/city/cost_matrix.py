"""
Layer 0 — Precomputed shortest-path cost matrix over points of interest (POIs).

Why precompute
--------------
MCTS will ask "how far from here to there" tens of thousands of times per
planning call. Running Dijkstra live inside the search loop would dominate
runtime. Instead we precompute all-pairs shortest paths over a *small* POI set
(depot + charging stations + snapped customer nodes for the current instance)
and hand the RL environment a plain O(1) lookup table.

POI index order (fixed, shared with the env's action space)
-------------------------------------------------------------
    index 0            -> depot
    1 .. N             -> customers (this instance's subset)
    N+1 .. N+M         -> charging stations

Keeping this ordering identical everywhere means the env, the network's action
head, and the MCTS action mask all agree without translation layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import networkx as nx
import numpy as np


@dataclass
class CostMatrix:
    """Dense distance/energy lookups between POIs, plus the underlying paths.

    Distances are NOT assumed symmetric — real road graphs are directed
    (one-way streets), so distance[i, j] can differ from distance[j, i].
    """

    poi_nodes: tuple                     # graph node id per POI index
    distance: np.ndarray                 # (P, P) metres along roads
    energy: np.ndarray                   # (P, P) battery units
    paths: dict = field(default_factory=dict)   # (i, j) -> [graph_node, ...]

    def __len__(self) -> int:
        return len(self.poi_nodes)

    def cost(self, i: int, j: int) -> float:
        return float(self.distance[i, j])

    def energy_cost(self, i: int, j: int) -> float:
        return float(self.energy[i, j])

    def path(self, i: int, j: int) -> list:
        """Actual node path from POI i to POI j, for rendering the driven route."""
        return self.paths.get((i, j), [])


def build_cost_matrix(
    graph: nx.MultiDiGraph,
    poi_nodes: tuple,
    energy_rate: float,
    store_paths: bool = True,
) -> CostMatrix:
    """All-pairs shortest paths restricted to `poi_nodes`.

    One Dijkstra per POI source (P sources, not |V| — this is the cheap part:
    P is typically tens of nodes, |V| is thousands).

    Raises
    ------
    nx.NetworkXNoPath propagates if some POI cannot reach another at all —
    this should be unreachable given a strongly-connected graph, so a failure
    here indicates a bug upstream (e.g. graph connectivity check was skipped).
    """
    P = len(poi_nodes)
    distance = np.full((P, P), np.inf, dtype=np.float64)
    energy = np.full((P, P), np.inf, dtype=np.float64)
    paths: dict = {}

    for i, source in enumerate(poi_nodes):
        dist_map, path_map = nx.single_source_dijkstra(graph, source=source, weight="length")
        for j, target in enumerate(poi_nodes):
            if target not in dist_map:
                raise nx.NetworkXNoPath(
                    f"No path from POI {i} ({source}) to POI {j} ({target}); "
                    f"graph should be strongly connected — check upstream."
                )
            d = dist_map[target]
            distance[i, j] = d
            energy[i, j] = d * energy_rate
            if store_paths:
                paths[(i, j)] = path_map[target]

    np.fill_diagonal(distance, 0.0)
    np.fill_diagonal(energy, 0.0)

    return CostMatrix(poi_nodes=tuple(poi_nodes), distance=distance, energy=energy, paths=paths)
