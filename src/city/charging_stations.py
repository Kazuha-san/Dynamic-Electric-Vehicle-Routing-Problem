"""
Layer 0 — Placement of the fixed charging station set.

Charging stations are FIXED per city — they are company/public infrastructure,
not something the optimizer gets to move. They are also deliberately SPARSE,
because that is what makes the battery constraint bite and makes the
reachability-feasibility problem interesting rather than trivial.

Implemented strategies
-----------------------
- "manual"   : explicit node ids supplied by the caller/config.
- "coverage" : greedy farthest-point dispersion — repeatedly add the node
               that is farthest (by road distance) from every station chosen
               so far. This spreads stations out to cover the whole graph
               rather than clustering them in one area, which is the
               practical goal of "coverage" without needing a full
               max-coverage ILP.

`kmeans` (geometric clustering) is noted as an alternative in the design docs
but not implemented — greedy dispersion needs no extra dependency, is
deterministic given a seed, and validates cleanly against the coverage check
below.
"""

from __future__ import annotations

import networkx as nx
import numpy as np


def place_charging_stations_coverage(
    graph: nx.MultiDiGraph,
    depot_node,
    num_stations: int,
    rng: np.random.Generator,
) -> tuple:
    """Greedy farthest-point dispersion, seeded from the depot.

    Algorithm
    ---------
    1. Start the "chosen" set as {depot_node} (depot acts as a free anchor —
       it's already a safe node, we just don't double-count it as a station).
    2. Repeat num_stations times: for every candidate node, compute its
       distance to the NEAREST already-chosen node; pick the candidate that
       maximizes that (i.e. the point currently worst-served).
    3. Return the chosen station nodes (NOT including the depot itself).

    This is O(num_stations * |V|) single-source Dijkstra calls from the
    growing chosen set — fine at our graph sizes (thousands of nodes), and
    only ever run once per city, not at runtime.
    """
    nodes = list(graph.nodes())
    if num_stations >= len(nodes):
        raise ValueError(
            f"Requested {num_stations} stations but graph only has {len(nodes)} nodes."
        )

    chosen = [depot_node]
    stations = []

    # min_dist[v] = shortest-path distance from v to the nearest chosen node so far
    dist_from_depot = nx.single_source_dijkstra_path_length(graph, depot_node, weight="length")
    min_dist = {v: dist_from_depot.get(v, float("inf")) for v in nodes}

    for _ in range(num_stations):
        # pick the node that is currently farthest from every chosen node
        candidate = max(nodes, key=lambda v: min_dist[v] if v not in chosen and v not in stations else -1)
        stations.append(candidate)

        dist_from_candidate = nx.single_source_dijkstra_path_length(
            graph, candidate, weight="length"
        )
        for v in nodes:
            d = dist_from_candidate.get(v, float("inf"))
            if d < min_dist[v]:
                min_dist[v] = d

    return tuple(stations)


def place_charging_stations(
    graph: nx.MultiDiGraph,
    depot_node,
    num_stations: int,
    strategy: str = "coverage",
    manual_nodes: tuple | None = None,
    rng: np.random.Generator | None = None,
) -> tuple:
    """Dispatch to the requested placement strategy."""
    if strategy == "manual":
        if not manual_nodes:
            raise ValueError("strategy='manual' requires manual_nodes to be provided")
        return tuple(manual_nodes)
    elif strategy == "coverage":
        rng = rng or np.random.default_rng(0)
        return place_charging_stations_coverage(graph, depot_node, num_stations, rng)
    else:
        raise ValueError(f"Unknown charging station placement strategy: {strategy!r}")


def validate_station_coverage(
    graph: nx.MultiDiGraph,
    depot_node,
    station_nodes: tuple,
    battery_capacity: float,
    energy_rate: float,
) -> dict:
    """Check the instance's physical parameters are even viable, before we ever
    build an episode from them.

    Two checks, matching the runtime masking logic in env/feasibility.py
    exactly (this function previously treated the depot as a general escape
    target, which does not match runtime behaviour — the depot is only
    reachable once all customers are served, so it must NOT be counted as a
    mid-route safe node here either):

    1. depot_egress: can the vehicle leave the depot and reach at least one
       charging station at all? If not, NO instance at this battery capacity
       is solvable in this city, regardless of customer placement — this is
       the most basic possible precondition.
    2. escape_from_every_node: for every node, is some CHARGING STATION
       (not the depot) within range? A node failing this can still be
       served if it happens to be reachable directly from the depot AND is
       the only/last customer (the depot-direct completion case) — this
       function reports the conservative (stricter) count on purpose, since
       "requires being the last customer visited" is a fragile property to
       rely on for general servability.

    Returns a diagnostic dict rather than raising, so a partially-bad city can
    still be inspected (e.g. via scripts/build_cities.py) rather than crashing.
    """
    max_range_m = battery_capacity / energy_rate

    dist_depot_to_station = {
        s: nx.shortest_path_length(graph, depot_node, s, weight="length")
        for s in station_nodes
    }
    nearest_station_from_depot = min(dist_depot_to_station.values())
    depot_egress_ok = nearest_station_from_depot <= max_range_m

    # distance from every node to its NEAREST CHARGING STATION ONLY (matches
    # the runtime escape condition, not depot-inclusive).
    reverse_graph = graph.reverse(copy=False)
    nearest_station_dist = {v: float("inf") for v in graph.nodes()}
    for s in station_nodes:
        dist_to_s = nx.single_source_dijkstra_path_length(reverse_graph, s, weight="length")
        for v, d in dist_to_s.items():
            if d < nearest_station_dist[v]:
                nearest_station_dist[v] = d

    dist_from_depot = nx.single_source_dijkstra_path_length(graph, depot_node, weight="length")

    unreachable_from_depot = []
    cannot_escape_to_station = []
    for v in graph.nodes():
        if v == depot_node:
            continue
        if dist_from_depot.get(v, float("inf")) > max_range_m:
            unreachable_from_depot.append(v)
        if nearest_station_dist.get(v, float("inf")) > max_range_m:
            cannot_escape_to_station.append(v)

    total = graph.number_of_nodes() - 1  # excluding depot
    report = {
        "total_nodes": total,
        "max_range_m": max_range_m,
        "depot_egress_ok": depot_egress_ok,
        "nearest_station_from_depot_m": nearest_station_from_depot,
        "num_unreachable_from_depot": len(unreachable_from_depot),
        "num_cannot_escape_to_station": len(cannot_escape_to_station),
        "fraction_servable_conservative": (
            1.0 - len(set(unreachable_from_depot) | set(cannot_escape_to_station)) / total
            if total else 1.0
        ),
        "unreachable_from_depot_sample": unreachable_from_depot[:5],
        "cannot_escape_sample": cannot_escape_to_station[:5],
    }
    return report
