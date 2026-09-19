"""Layer 2 tests — fleet sizing and partitioning."""

import pytest


@pytest.mark.skip(reason="Checkpoint 2")
def test_capacity_lower_bound_is_valid():
    """No feasible solution can use fewer vehicles than the capacity bound."""


@pytest.mark.skip(reason="Checkpoint 2")
def test_never_over_dispatches():
    """The brief's hard requirement: fleet size must not exceed what is needed.
    Construct instances with a known-minimal answer and assert we match it."""


@pytest.mark.skip(reason="Checkpoint 2")
def test_partition_covers_every_order_exactly_once():
    """"""


@pytest.mark.skip(reason="Checkpoint 2")
def test_infeasible_partition_triggers_increment():
    """The sizer/partitioner retry loop must terminate at a feasible k."""
