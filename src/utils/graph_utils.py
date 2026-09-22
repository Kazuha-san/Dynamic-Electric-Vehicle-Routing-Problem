"""
Shared graph helpers used across Layer 0 and the baselines.

Kept separate from city/ so that shortest-path utilities can be unit-tested on
tiny synthetic graphs without pulling in OSMnx or any cached city data.
"""

from __future__ import annotations

import networkx as nx


def shortest_path_cost(graph: nx.DiGraph, source, target, weight: str = "length") -> float:
    """Shortest-path cost between two nodes. Raises nx.NetworkXNoPath if unreachable."""
    return nx.shortest_path_length(graph, source=source, target=target, weight=weight)


def shortest_path_nodes(graph: nx.DiGraph, source, target, weight: str = "length") -> list:
    """The actual sequence of graph nodes along the shortest path (for rendering)."""
    return nx.shortest_path(graph, source=source, target=target, weight=weight)


def all_pairs_from_sources(graph: nx.DiGraph, sources, weight: str = "length"):
    """One Dijkstra per source, restricted to a target set the caller cares about.

    Returns
    -------
    costs : dict[source] -> dict[target] -> cost
    paths : dict[source] -> dict[target] -> [node, node, ...]

    This is deliberately "one Dijkstra per source over the WHOLE graph", not an
    all-pairs-shortest-path over just the POIs — Dijkstra from a single source
    already gives us distances to every other node for free, so restricting the
    *targets* afterward is cheap and simpler than a specialized multi-target
    algorithm.
    """
    costs: dict = {}
    paths: dict = {}
    for s in sources:
        dist, path = nx.single_source_dijkstra(graph, source=s, weight=weight)
        costs[s] = dist
        paths[s] = path
    return costs, paths


def largest_strongly_connected(graph: nx.DiGraph) -> nx.DiGraph:
    """Real OSM extracts can contain unreachable fragments; routing needs one SCC.

    Returns a new graph (a copy), restricted to the largest strongly connected
    component. No-op (returns a copy of the whole graph) if already connected.
    """
    largest = max(nx.strongly_connected_components(graph), key=len)
    return graph.subgraph(largest).copy()
