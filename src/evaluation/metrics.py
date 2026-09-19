"""
Layer 4 — Metric definitions. One place, so every table means the same thing.

  total_cost        : sum of road-network travel cost over all vehicle routes
  gap_vs_ortools    : (cost_method - cost_ortools) / cost_ortools  (signed;
                      negative means we beat it — report it honestly either way)
  feasibility_rate  : fraction of episodes completing all customers without
                      stranding. Expected 100% for the masked agent BY
                      CONSTRUCTION; any deviation is a bug, and that is precisely
                      why it is measured rather than assumed.
  fleet_size_used   : vs. the computed lower bound — the over-dispatch check
  solve_time        : wall-clock seconds per planning call
"""

from __future__ import annotations


def total_cost(routes, cost_matrix) -> float:
    raise NotImplementedError


def gap_vs_reference(cost: float, reference_cost: float) -> float:
    raise NotImplementedError


def feasibility_rate(episode_results) -> float:
    raise NotImplementedError
