"""Layer 1 tests — epoch scheduling."""

import pytest


@pytest.mark.skip(reason="Checkpoint 5")
def test_every_order_eventually_served():
    """No order may be dropped or starved across epochs."""


@pytest.mark.skip(reason="Checkpoint 5")
def test_in_flight_vehicles_are_not_reassigned():
    """The v1 commitment policy: committed routes run to completion."""


@pytest.mark.skip(reason="Checkpoint 5")
def test_orders_arriving_mid_epoch_wait_for_next_window():
    """"""
