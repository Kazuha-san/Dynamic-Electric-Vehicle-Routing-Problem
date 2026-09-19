"""Layer 3 environment tests — MDP mechanics."""

import pytest


@pytest.mark.skip(reason="Checkpoint 1")
def test_reset_starts_at_depot_full_battery():
    """"""


@pytest.mark.skip(reason="Checkpoint 1")
def test_step_rejects_illegal_action():
    """An illegal action is a CALLER bug; the env must raise, not absorb it."""


@pytest.mark.skip(reason="Checkpoint 1")
def test_reward_equals_negative_travel_cost():
    """Hand-compute a two-step route and assert the reward matches exactly."""


@pytest.mark.skip(reason="Checkpoint 1")
def test_recharge_restores_battery():
    """"""


@pytest.mark.skip(reason="Checkpoint 1")
def test_terminal_only_when_all_served_and_at_depot():
    """"""


@pytest.mark.skip(reason="Checkpoint 1")
def test_state_clone_is_independent():
    """MCTS correctness depends on this: mutating a clone must not touch the
    original. A shared numpy view here would corrupt the entire search."""


@pytest.mark.skip(reason="Checkpoint 1")
def test_state_is_markov():
    """Two episodes reaching the same (position, battery, load, visited) via
    DIFFERENT orders must expose identical legal actions — the formal property
    the whole MDP framing rests on."""
