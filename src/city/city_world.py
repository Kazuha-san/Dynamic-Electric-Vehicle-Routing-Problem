"""
Layer 0 — The `CityWorld`: a road graph plus everything fixed about the city.

A CityWorld is the *static* half of the problem. It knows nothing about orders,
vehicles, or time — only geography. Orders (Layer 1) and vehicles (Layer 3)
are laid on top of it.
"""

from __future__ import annotations

from dataclasses import dataclass

import networkx as nx
import numpy as np

from src.city.charging_stations import place_charging_stations, validate_station_coverage
from src.city.cost_matrix import CostMatrix, build_cost_matrix
from src.city.osm_loader import CitySpec, load_city_graph


@dataclass
class CityWorld:
    """Static city state. Built once per city, reused across every episode."""

    city_id: str
    topology_label: str
    graph: nx.MultiDiGraph
    depot_node: object
    charging_nodes: tuple
    energy_rate: float
    _base_cost_matrix: CostMatrix  # covers depot + all charging stations only

    def snap(self, lat: float, lon: float) -> object:
        """Snap a map marker to the nearest road node by projected (x, y).

        NOTE: expects (lat, lon) already converted to the graph's projected
        (x, y) coordinate system by the caller — this project does not re-do
        the lat/lon -> projected-metres conversion here to avoid depending on
        pyproj/osmnx at runtime for a one-line nearest-node lookup.
        """
        best_node, best_dist = None, float("inf")
        for n, data in self.graph.nodes(data=True):
            d = (data["x"] - lon) ** 2 + (data["y"] - lat) ** 2
            if d < best_dist:
                best_node, best_dist = n, d
        return best_node

    def travel_cost(self, from_node, to_node) -> float:
        """Road-network shortest-path cost between two arbitrary graph nodes."""
        return nx.shortest_path_length(self.graph, from_node, to_node, weight="length")

    def energy_cost(self, from_node, to_node) -> float:
        return self.travel_cost(from_node, to_node) * self.energy_rate

    @property
    def safe_nodes(self) -> tuple:
        """Charging stations plus the depot — the set that makes a state 'escapable'."""
        return (self.depot_node,) + self.charging_nodes

    def coverage_report(self, battery_capacity: float) -> dict:
        return validate_station_coverage(
            self.graph, self.depot_node, self.charging_nodes, battery_capacity, self.energy_rate
        )


def _pick_depot_centroid(graph: nx.MultiDiGraph):
    """Depot = the graph node nearest the centroid of all node positions."""
    xs = np.array([d["x"] for _, d in graph.nodes(data=True)])
    ys = np.array([d["y"] for _, d in graph.nodes(data=True)])
    cx, cy = xs.mean(), ys.mean()
    nodes = list(graph.nodes(data=True))
    best_node, best_dist = None, float("inf")
    for n, data in nodes:
        d = (data["x"] - cx) ** 2 + (data["y"] - cy) ** 2
        if d < best_dist:
            best_node, best_dist = n, d
    return best_node


def build_city_world(
    city_id: str,
    display_name: str,
    topology_label: str,
    cache_dir: str,
    num_charging_stations: int,
    energy_rate: float,
    station_strategy: str = "coverage",
    seed: int = 0,
) -> CityWorld:
    """Assemble a CityWorld: load graph, place depot + charging stations, build matrices."""
    graph = load_city_graph(city_id, cache_dir)

    depot_node = _pick_depot_centroid(graph)

    rng = np.random.default_rng(seed)
    charging_nodes = place_charging_stations(
        graph, depot_node, num_charging_stations, strategy=station_strategy, rng=rng
    )

    poi_nodes = (depot_node,) + charging_nodes
    base_cost_matrix = build_cost_matrix(graph, poi_nodes, energy_rate)

    return CityWorld(
        city_id=city_id,
        topology_label=topology_label,
        graph=graph,
        depot_node=depot_node,
        charging_nodes=charging_nodes,
        energy_rate=energy_rate,
        _base_cost_matrix=base_cost_matrix,
    )
