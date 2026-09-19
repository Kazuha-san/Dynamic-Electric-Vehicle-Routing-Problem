"""
Layer 2 — Fleet sizing. Answers "how many vehicles do we send?" BEFORE routing.

This is a hard requirement from the project brief: never over-dispatch. Sending
five vehicles when three suffice is a failure, even if the routes are pretty.

Why this is deterministic and not learned (decided in planning)
--------------------------------------------------------------
We want a number we can *justify*, ideally with a provable lower bound, not a
number a network guessed. It also keeps the learning problem clean: the RL agent
solves single-vehicle routing, full stop.

Bounds
------
lower bound 1 (capacity):  ceil(sum(demand) / vehicle_capacity)
lower bound 2 (range):     driven by battery feasibility — a vehicle cannot serve
                           a customer set whose required tour energy exceeds what
                           it can achieve even with optimal recharging
final:                     max(lb_capacity, lb_range), then feasibility-repaired
                           upward if partitioning cannot produce feasible subsets

Open sub-decision
-----------------
Whether lb_range stays a cheap analytical estimate, or becomes a small
bin-packing / set-cover ILP for a tighter, more defensible bound. Leaning
analytical-first (RL is where the engineering effort should go), with the ILP
as a comparison point in the report.
"""

from __future__ import annotations


def lower_bound_capacity(demands, vehicle_capacity: float) -> int:
    """ceil(total demand / capacity). Trivially a valid lower bound."""
    raise NotImplementedError


def lower_bound_range(orders, world, battery_capacity: float, energy_rate: float) -> int:
    """Battery-range-driven lower bound.

    TODO(Checkpoint 2): start with a simple, defensible estimate, and document
    precisely why it is a valid bound (or, if it is only a heuristic estimate,
    say so plainly in the report rather than overclaiming).
    """
    raise NotImplementedError


def minimum_vehicles(orders, world, config) -> int:
    """max of the bounds, then repaired upward until a feasible partition exists."""
    raise NotImplementedError
