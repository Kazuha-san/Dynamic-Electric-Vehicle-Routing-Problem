"""
Layer 4 — The benchmarking harness. Produces the numbers that go in the report.

Comparison grid
---------------
  methods  x  cities  x  instance sizes  x  seeds

  methods : nearest_neighbour | greedy_insertion | ortools | mcts_agent
  cities  : the 2-3 CityWorlds (grid / organic / dense-irregular)
  sizes   : customers per vehicle, and fleet-level scenarios
  seeds   : multiple, because single-seed results are not results

Metrics (see metrics.py)
------------------------
  total cost, gap vs OR-Tools, feasibility rate, fleet size used,
  wall-clock solve time

Every run writes a row to results/tables/ and a record to the research log, so
the final report is assembled from recorded data rather than reconstructed from
memory at the end.
"""

from __future__ import annotations


def run_benchmark(config) -> None:
    """Execute the full grid and persist results. TODO(Checkpoint 6)."""
    raise NotImplementedError
