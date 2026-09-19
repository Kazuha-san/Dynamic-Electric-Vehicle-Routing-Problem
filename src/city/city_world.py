"""
Layer 0 — The `CityWorld`: a road graph plus everything fixed about the city.

A CityWorld is the *static* half of the problem. It knows nothing about orders,
vehicles, or time — only geography. Orders (Layer 1) and vehicles (Layer 3)
are laid on top of it.

Contents
--------
- the routable road graph
- the single HQ / depot node
- the fixed, sparse set of charging station nodes
- snapping of arbitrary (lat, lon) markers to the nearest road node
- the precomputed cost matrix over "points of interest" (see cost_matrix.py)

Why this exists as its own object
---------------------------------
Every downstream layer needs "how far is A from B, along real roads". Making
that a single well-tested object means the RL environment never touches OSMnx
or shortest-path internals — it just asks the world for a cost.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CityWorld:
    """Static city state. Built once per city, reused across every episode."""

    city_id: str
    topology_label: str
    # graph: networkx.MultiDiGraph          # routable, projected road network
    # depot_node: int                        # single HQ
    # charging_nodes: tuple[int, ...]        # fixed, sparse
    # cost_matrix: CostMatrix                # see cost_matrix.py

    def snap(self, lat: float, lon: float) -> int:
        """Snap a map marker (a customer placed by the user) to the nearest road node.

        TODO(Checkpoint 1): osmnx.distance.nearest_nodes, with a sanity check that
        the snapped node is within a reasonable radius of the marker.
        """
        raise NotImplementedError

    def travel_cost(self, from_node: int, to_node: int) -> float:
        """Road-network shortest-path cost between two nodes.

        NOTE: this is *road distance*, never Euclidean. The whole point of Layer 0
        is that a vehicle cannot fly diagonally through buildings.
        """
        raise NotImplementedError

    def energy_cost(self, from_node: int, to_node: int) -> float:
        """Battery consumed travelling from_node -> to_node.

        v1: linear in distance (energy_rate * distance). Nonlinear / grade-aware
        consumption is noted as a future extension.
        """
        raise NotImplementedError


def build_city_world(spec, config) -> CityWorld:
    """Assemble a CityWorld: load graph, place depot + charging stations, build matrices.

    TODO(Checkpoint 1):
      - load_city_graph(spec)
      - choose depot node (config-driven, or graph-centroid-nearest)
      - place charging stations (see charging_stations.py)
      - build the POI cost matrix
    """
    raise NotImplementedError
