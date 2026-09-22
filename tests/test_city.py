"""Layer 0 tests — geography must be correct before anything else matters."""

import networkx as nx
import numpy as np
import pytest

from src.city.city_world import build_city_world
from src.city.osm_loader import load_city_graph

CACHE_DIR = "data/city_graphs"
CITIES = ["us_grid", "uk_organic", "in_dense"]


@pytest.mark.parametrize("city_id", CITIES)
def test_graph_is_strongly_connected(city_id):
    """A routable graph has no unreachable fragments."""
    graph = load_city_graph(city_id, CACHE_DIR)
    assert nx.is_strongly_connected(graph)


@pytest.mark.parametrize("city_id", CITIES)
def test_no_real_world_tags_survived_extraction(city_id):
    """Only geometry attributes should exist — no street names/OSM metadata.
    This is what makes the 'synthetic city, real skeleton only' claim true."""
    graph = load_city_graph(city_id, CACHE_DIR)
    allowed_node_keys = {"x", "y"}
    allowed_edge_keys = {"length", "oneway", "reversed"}
    for _, data in graph.nodes(data=True):
        assert set(data.keys()) <= allowed_node_keys, f"unexpected node keys: {data.keys()}"
    for _, _, data in graph.edges(data=True):
        assert set(data.keys()) <= allowed_edge_keys, f"unexpected edge keys: {data.keys()}"


@pytest.mark.parametrize("city_id", CITIES)
def test_cost_matrix_matches_direct_dijkstra(city_id):
    """Precomputed costs must equal a fresh shortest-path query.
    Catches index-ordering bugs, which are otherwise near-invisible."""
    world = build_city_world(
        city_id=city_id, display_name=city_id, topology_label="x",
        cache_dir=CACHE_DIR, num_charging_stations=6, energy_rate=1.0,
        station_strategy="coverage", seed=0,
    )
    poi_nodes = world._base_cost_matrix.poi_nodes
    for i in range(len(poi_nodes)):
        for j in range(len(poi_nodes)):
            if i == j:
                continue
            direct = nx.shortest_path_length(
                world.graph, poi_nodes[i], poi_nodes[j], weight="length"
            )
            assert abs(world._base_cost_matrix.cost(i, j) - direct) < 1e-6


@pytest.mark.parametrize("city_id", CITIES)
def test_cost_matrix_not_assumed_symmetric(city_id):
    """One-way streets exist: cost(a,b) != cost(b,a) must be representable
    (not necessarily different for every pair, just not forced equal)."""
    world = build_city_world(
        city_id=city_id, display_name=city_id, topology_label="x",
        cache_dir=CACHE_DIR, num_charging_stations=6, energy_rate=1.0,
        station_strategy="coverage", seed=0,
    )
    m = world._base_cost_matrix.distance
    assert not np.allclose(m, m.T), (
        "Distance matrix is perfectly symmetric — suspicious for a real road "
        "network with one-way streets; check that directed edges are respected."
    )


@pytest.mark.parametrize("city_id", CITIES)
def test_all_nodes_within_battery_range_of_a_charging_station(city_id):
    """Instance precondition established in Checkpoint 1: at battery >= 6000
    with 6 stations, every node is servable (see docs/checkpoints/checkpoint1.md)."""
    world = build_city_world(
        city_id=city_id, display_name=city_id, topology_label="x",
        cache_dir=CACHE_DIR, num_charging_stations=6, energy_rate=1.0,
        station_strategy="coverage", seed=0,
    )
    report = world.coverage_report(battery_capacity=10000.0)
    assert report["depot_egress_ok"]
    assert report["fraction_servable_conservative"] >= 0.999
