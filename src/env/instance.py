"""
Layer 3 — `EVRPInstance`: one concrete routing problem handed to the agent.

An instance is what you get after Layers 0-2 have done their jobs:
    CityWorld (static geography)
  + this vehicle's assigned customer subset (from the partitioner)
  + vehicle parameters (capacity, battery, energy rate)
  = one solvable single-vehicle EVRP

Everything in here is immutable for the duration of an episode. The mutable part
lives in EVRPState.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EVRPInstance:
    """Immutable problem definition for one episode."""

    # world: CityWorld
    # cost_matrix: CostMatrix        # restricted to this instance's POIs
    # demands: np.ndarray            # per customer
    # nearest_safe_energy: np.ndarray  # precomputed escape distances
    num_customers: int = 0
    num_stations: int = 0
    vehicle_capacity: float = 0.0
    battery_capacity: float = 0.0
    energy_rate: float = 1.0

    @property
    def num_pois(self) -> int:
        return 1 + self.num_customers + self.num_stations

    @property
    def depot_index(self) -> int:
        return 0

    def customer_indices(self) -> range:
        return range(1, 1 + self.num_customers)

    def station_indices(self) -> range:
        return range(1 + self.num_customers, self.num_pois)


def synthetic_instance(world, config, rng):
    """Sample a training instance: random customers on the road graph.

    Used by the self-play loop, which needs a fresh instance per episode.
    """
    raise NotImplementedError
