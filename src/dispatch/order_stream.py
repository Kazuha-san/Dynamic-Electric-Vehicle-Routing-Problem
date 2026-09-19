"""
Layer 1 — Dynamic order arrival.

Orders (customers) appear over time rather than all at once. Two sources:

- `InteractiveOrderStream` : markers placed live on the map by a user
                             (this is the demo mode your professor clicks through)
- `SyntheticOrderStream`   : reproducible, seeded arrivals for training and for
                             benchmarking — a Poisson process over time with
                             spatial sampling over the road graph

Both emit the same `Order` records, so nothing downstream knows or cares which
one is running.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    order_id: str
    node: int            # snapped road node
    demand: float
    arrival_time: float  # simulation clock, seconds


class OrderStream:
    """Interface: pull all orders that arrived in [t_start, t_end)."""

    def poll(self, t_start: float, t_end: float) -> list[Order]:
        raise NotImplementedError


class SyntheticOrderStream(OrderStream):
    """Seeded Poisson arrivals with configurable spatial distribution.

    TODO(Checkpoint 5): uniform-over-nodes first; clustered (hotspot) arrivals
    later, since real demand is never uniform and clustering changes how much
    the router can exploit geography.
    """


class InteractiveOrderStream(OrderStream):
    """Buffer of user-placed markers, drained by the epoch scheduler."""
