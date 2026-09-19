"""Layer 0 tests — geography must be correct before anything else matters."""

import pytest


@pytest.mark.skip(reason="Checkpoint 1")
def test_graph_is_strongly_connected():
    """A routable graph has no unreachable fragments."""


@pytest.mark.skip(reason="Checkpoint 1")
def test_cost_matrix_matches_direct_dijkstra():
    """Precomputed costs must equal a fresh shortest-path query. Catches
    index-ordering bugs, which are otherwise near-invisible."""


@pytest.mark.skip(reason="Checkpoint 1")
def test_cost_matrix_not_assumed_symmetric():
    """One-way streets exist: cost(a,b) != cost(b,a) must be representable."""


@pytest.mark.skip(reason="Checkpoint 1")
def test_snapping_is_within_tolerance():
    """A marker snaps to a road node near where the user actually clicked."""


@pytest.mark.skip(reason="Checkpoint 1")
def test_all_nodes_within_battery_range_of_a_safe_node():
    """Instance precondition: no fundamentally unservable regions."""
