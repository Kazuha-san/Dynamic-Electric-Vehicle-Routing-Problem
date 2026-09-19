"""Layer 3 search tests."""

import pytest


@pytest.mark.skip(reason="Checkpoint 3")
def test_search_only_expands_legal_actions():
    """The safety guarantee must survive contact with the search."""


@pytest.mark.skip(reason="Checkpoint 3")
def test_more_simulations_do_not_hurt():
    """Gumbel AlphaZero's selling point: monotone improvement with budget."""


@pytest.mark.skip(reason="Checkpoint 3")
def test_search_beats_raw_policy():
    """Search-improved decisions should beat the raw network. If not, the
    self-play loop has no signal to learn from and training cannot work."""


@pytest.mark.skip(reason="Checkpoint 3")
def test_gumbel_top_k_respects_mask():
    """Illegal actions must be unsamplable, not merely unlikely."""


@pytest.mark.skip(reason="Checkpoint 3")
def test_value_sign_convention():
    """Guards the classic silent bug: we always MAXIMIZE negative cost.
    A sign flip here trains the agent to seek the worst route."""
