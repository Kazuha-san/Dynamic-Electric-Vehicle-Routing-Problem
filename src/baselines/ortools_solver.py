"""
Layer 4 — Google OR-Tools reference solver. The strong classical baseline.

This is what the "optimality gap" in the results tables is measured against.
OR-Tools does not solve EVRP natively, so the encoding matters and must be
documented honestly in the report:

  - charging stations are modelled as OPTIONAL, REPEATABLE visit nodes
    (duplicated a bounded number of times, since OR-Tools nodes are visit-once)
  - battery is a dimension that is consumed by travel and RESET at station/depot
    nodes
  - road-network distances come from our own cost matrix, so both methods are
    scored on identical geography

Caveat to state plainly: OR-Tools with this encoding is a strong heuristic under
a time limit, not a proof of optimality. The report should say "gap vs OR-Tools",
never "gap vs optimal".
"""

from __future__ import annotations


def solve(instance, time_limit_seconds: int = 30):
    """Returns (route, total_cost, solver_status)."""
    raise NotImplementedError
