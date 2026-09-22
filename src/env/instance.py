"""
Layer 3 — `EVRPInstance`: one concrete routing problem handed to the agent.

An instance is what you get after Layer 0 (+ eventually Layer 2's partitioner)
have done their jobs:

    CityWorld (static geography)
  + this vehicle's assigned customer subset
  + vehicle parameters (capacity, battery, energy rate)
  = one solvable single-vehicle EVRP

Everything in here is immutable for the duration of an episode. The mutable
part (position, battery, load, visited) lives in EVRPState (evrp_env.py).

POI index layout (fixed, matches cost_matrix.py):
    0            -> depot
    1..N         -> customers
    N+1..N+M     -> charging stations
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from src.city.cost_matrix import CostMatrix, build_cost_matrix


@dataclass(frozen=True)
class EVRPInstance:
    """Immutable problem definition for one episode."""

    cost_matrix: CostMatrix
    demands: np.ndarray                 # (N,) demand per customer, 0 for depot/stations implied
    nearest_safe_energy: np.ndarray     # (P,) energy cost from POI i to its nearest CHARGING
                                         # STATION (depot deliberately excluded — see build_instance)
    num_customers: int
    num_stations: int
    vehicle_capacity: float
    battery_capacity: float
    energy_rate: float

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

    def is_safe_index(self, idx: int) -> bool:
        return idx == self.depot_index or idx in self.station_indices()

    def demand(self, poi_index: int) -> float:
        """Demand at a POI index; 0 for depot and charging stations."""
        if poi_index in self.customer_indices():
            return float(self.demands[poi_index - 1])
        return 0.0


def _compute_nearest_safe_energy(cost_matrix: CostMatrix, safe_indices: list[int]) -> np.ndarray:
    """For each POI, the energy cost to its nearest safe node (depot or station).

    This is what turns the "can I escape from here" check in feasibility.py
    into an O(1) comparison instead of a live graph search per candidate move.
    """
    P = len(cost_matrix)
    out = np.full(P, np.inf, dtype=np.float64)
    for i in range(P):
        for s in safe_indices:
            e = cost_matrix.energy_cost(i, s)
            if e < out[i]:
                out[i] = e
    return out


def build_instance(
    world,
    customer_nodes: list,
    demands: list[float],
    vehicle_capacity: float,
    battery_capacity: float,
) -> EVRPInstance:
    """Build an EVRPInstance for a specific vehicle's assigned customer subset.

    `world` is a CityWorld (src/city/city_world.py). The POI cost matrix here
    is instance-specific (depot + THESE customers + all charging stations),
    distinct from CityWorld's own base matrix (depot + stations only).
    """
    poi_nodes = (world.depot_node,) + tuple(customer_nodes) + world.charging_nodes
    cost_matrix = build_cost_matrix(world.graph, poi_nodes, world.energy_rate)

    num_customers = len(customer_nodes)
    num_stations = len(world.charging_nodes)
    # NOTE: depot is deliberately EXCLUDED from the escape-target set here.
    # The depot is only a legal target once ALL customers are visited (v1:
    # single continuous tour, no early return) — so it cannot be relied on as
    # a general-purpose "safe node to flee to" mid-route. Only charging
    # stations are unconditionally available as an escape target at any point
    # in the episode. The one exception (completing the tour on this exact
    # move) is handled directly in feasibility.py using the cost matrix,
    # not through this precomputed table.
    station_indices = list(range(1 + num_customers, 1 + num_customers + num_stations))
    nearest_safe_energy = _compute_nearest_safe_energy(cost_matrix, station_indices)

    return EVRPInstance(
        cost_matrix=cost_matrix,
        demands=np.array(demands, dtype=np.float64),
        nearest_safe_energy=nearest_safe_energy,
        num_customers=num_customers,
        num_stations=num_stations,
        vehicle_capacity=vehicle_capacity,
        battery_capacity=battery_capacity,
        energy_rate=world.energy_rate,
    )


def synthetic_instance(
    world,
    num_customers: int,
    vehicle_capacity: float,
    battery_capacity: float,
    demand_range: tuple[float, float],
    rng: np.random.Generator,
) -> EVRPInstance:
    """Sample a training instance: random customers on the road graph.

    Used by baselines and (later) the self-play loop, which need a fresh
    instance per episode. Customers are sampled uniformly from graph nodes,
    excluding the depot and charging stations (a customer and a charging
    station occupying the identical node is a modelling edge case we simply
    avoid by construction here).
    """
    excluded = {world.depot_node} | set(world.charging_nodes)
    candidates = [n for n in world.graph.nodes() if n not in excluded]
    if num_customers > len(candidates):
        raise ValueError(
            f"Requested {num_customers} customers but only {len(candidates)} "
            f"eligible nodes exist in this city."
        )
    chosen_idx = rng.choice(len(candidates), size=num_customers, replace=False)
    customer_nodes = [candidates[i] for i in chosen_idx]
    demands = rng.uniform(demand_range[0], demand_range[1], size=num_customers).tolist()

    return build_instance(world, customer_nodes, demands, vehicle_capacity, battery_capacity)
