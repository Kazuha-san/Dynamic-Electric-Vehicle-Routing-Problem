"""
THE safety tests. The project's central claim is "the vehicle never gets stuck",
and these are what back that claim up.
"""

import pytest


@pytest.mark.skip(reason="Checkpoint 1")
def test_mask_never_allows_unreachable_node():
    """Condition 1: cannot select a node we lack the battery to reach."""


@pytest.mark.skip(reason="Checkpoint 1")
def test_mask_never_allows_a_trap():
    """Condition 3 — the important one. Construct a state where a node IS
    reachable but has no safe node in range afterwards, and assert it is masked
    out. This is exactly the case naive masking gets wrong."""


@pytest.mark.skip(reason="Checkpoint 1")
def test_mask_is_never_empty_along_random_rollouts():
    """Walk many random LEGAL trajectories; assert a legal action always exists.
    Non-emptiness is the whole safety argument, so it gets brute-forced."""


@pytest.mark.skip(reason="Checkpoint 1")
def test_capacity_respected():
    """Cannot serve a customer whose demand exceeds remaining load."""
