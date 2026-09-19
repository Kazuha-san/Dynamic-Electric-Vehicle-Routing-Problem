"""Layer 4 baseline tests — these also validate the environment itself."""

import pytest


@pytest.mark.skip(reason="Checkpoint 2")
def test_nearest_neighbour_produces_feasible_route():
    """Every baseline must go through the same mask the agent does — otherwise
    the comparison is not apples to apples."""


@pytest.mark.skip(reason="Checkpoint 2")
def test_greedy_insertion_beats_nearest_neighbour_on_average():
    """Sanity: a stronger heuristic should, on average, be stronger."""


@pytest.mark.skip(reason="Checkpoint 2")
def test_baseline_cost_matches_env_replay():
    """Replay a baseline route through the env and assert the accumulated
    reward equals the reported cost. Catches cost-accounting drift between the
    baselines and the environment."""
