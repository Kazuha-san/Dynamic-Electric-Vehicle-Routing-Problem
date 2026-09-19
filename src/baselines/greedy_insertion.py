"""
Layer 4 — Greedy (cheapest) insertion.

Build a route by repeatedly inserting the unvisited customer whose best
insertion position adds the least cost, re-checking battery feasibility after
each insertion. Meaningfully stronger than nearest-neighbour and still trivial
to explain in the report.
"""

from __future__ import annotations


def solve(instance):
    """Returns (route, total_cost)."""
    raise NotImplementedError
