"""
Layer 0 — Placement of the fixed charging station set.

Charging stations are FIXED per city (decided in planning) — they are company /
public infrastructure, not something the optimizer gets to move. They are also
deliberately SPARSE, because that is what makes the battery constraint bite and
makes the reachability-feasibility problem interesting rather than trivial.

Placement strategies (to compare in Checkpoint 1)
-------------------------------------------------
- "manual"    : explicit node ids / coordinates from configs/cities.yaml
- "kmeans"    : k-means over road nodes, snap centroids to nearest intersection
- "coverage"  : greedy max-coverage so that most of the graph is within
                (battery_capacity / 2) of some station — closest to how real
                charging infrastructure is sited

Sanity property we want to hold and TEST
----------------------------------------
Every road node should be within a one-way reachable distance of *some* station
or the depot, given a full battery. If that fails, some customers are
fundamentally unservable and the instance is broken — better to catch that here
than to discover it as a mysterious training failure later.
"""

from __future__ import annotations


def place_charging_stations(graph, depot_node, num_stations: int, strategy: str = "coverage"):
    """Return a tuple of node ids to host charging stations.

    TODO(Checkpoint 1): implement `manual` first (fast, deterministic, easy to
    eyeball on a map), then `coverage` as the principled default.
    """
    raise NotImplementedError


def validate_station_coverage(graph, depot_node, station_nodes, battery_capacity, energy_rate) -> dict:
    """Check every node is servable given battery range. Returns a diagnostic report.

    This is a *precondition check on the instance*, not a runtime check.
    """
    raise NotImplementedError
