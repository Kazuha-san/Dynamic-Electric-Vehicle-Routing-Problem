"""
Layer 2 — Split the order pool into one feasible subset per vehicle.

After fleet sizing says "k vehicles", something has to decide WHICH customers
each vehicle serves. Each subset then becomes an independent single-vehicle
EVRP instance handed to the RL router.

Candidate strategies (to compare in Checkpoint 2 — this comparison is itself a
result worth putting in the report)
---------------------------------------------------------------------------
- "sweep"    : classical sweep algorithm — sort by polar angle around the depot,
               cut into capacity-feasible arcs. Cheap, surprisingly strong.
- "kmeans"   : geographic clustering, then capacity repair.
- "balanced" : greedy assignment balancing load across vehicles.

Feasibility contract
--------------------
A partition is only valid if EVERY subset is routable by a single vehicle
subject to capacity AND battery feasibility. If a subset fails, we report back
to the fleet sizer, which increments k and we retry. That retry loop is why
these two modules live in the same package.

Non-conflict assumption (decided in planning)
---------------------------------------------
Once partitioned, vehicles are independent: no shared-resource contention, and
charging stations are treated as having unlimited concurrent capacity in v1.
"""

from __future__ import annotations


def partition(orders, world, k: int, config, strategy: str = "sweep") -> list[list]:
    """Return k order subsets. Raises InfeasiblePartition if k is too small."""
    raise NotImplementedError


class InfeasiblePartition(Exception):
    """Signals the fleet sizer to increment k and retry."""
