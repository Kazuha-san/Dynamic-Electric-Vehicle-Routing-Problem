"""
Layer 1 — Epoch-based (windowed) dispatch. The system's outer loop.

This is the "window" design from planning. Its formal name in the literature is
*epoch-based dispatching* (cf. the EURO-NeurIPS 2022 dynamic VRPTW formulation):
the planning horizon is cut into fixed intervals; at the end of each interval we
solve a static problem for whatever accumulated.

Why not replan on every single order
------------------------------------
Replanning per-order causes route thrashing (vehicles zig-zag as new stops get
spliced in) and burns compute for marginal gain. Batching is what real
dispatch systems do.

Commitment policy (decided in planning)
---------------------------------------
Vehicles already en route FINISH their committed route. Only unassigned orders
plus currently-free vehicles enter the next planning round. Full mid-route
re-optimization (pulling in-flight vehicles' remaining stops back into the pool)
is a stretch goal, NOT v1 — it requires the router to accept "vehicle starts
mid-route with partial battery" as an initial condition.

Open sub-decision
-----------------
Window length. Fixed-interval only in v1; hybrid (interval OR order-count,
whichever first) noted as an extension.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EpochResult:
    """Everything that happened in one planning window — recorded for the report."""

    epoch_index: int
    t_start: float
    t_end: float
    new_orders: list = field(default_factory=list)
    fleet_size: int = 0
    assignments: dict = field(default_factory=dict)   # vehicle_id -> [order_id, ...]
    routes: dict = field(default_factory=dict)        # vehicle_id -> [poi_index, ...]
    total_cost: float = 0.0
    planning_seconds: float = 0.0


class EpochScheduler:
    """Drive the simulation: poll orders, size the fleet, partition, route, commit."""

    def run(self, horizon_seconds: float) -> list[EpochResult]:
        """Main loop.

        For each epoch:
          1. poll new orders from the stream
          2. pool = unassigned orders (carried over + new)
          3. fleet_size = FleetSizer.minimum_vehicles(pool)
          4. subsets  = Partitioner.partition(pool, fleet_size)
          5. for each free vehicle + subset: route via the RL router (Layer 3)
          6. commit routes; advance clock
          7. append an EpochResult for the results log

        TODO(Checkpoint 5).
        """
        raise NotImplementedError
