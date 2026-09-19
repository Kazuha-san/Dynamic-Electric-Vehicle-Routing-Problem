"""
Shared graph helpers used across Layer 0 and the baselines.

Kept separate from city/ so that shortest-path utilities can be unit-tested on
tiny synthetic graphs without pulling in OSMnx.
"""

from __future__ import annotations


def shortest_path_cost(graph, source, target, weight: str = "length"):
    raise NotImplementedError


def all_pairs_from_sources(graph, sources, weight: str = "length"):
    """One Dijkstra per source. Returns costs and paths."""
    raise NotImplementedError


def largest_strongly_connected(graph):
    """Real OSM extracts contain unreachable fragments; routing needs one SCC."""
    raise NotImplementedError
