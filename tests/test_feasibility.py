"""
THE safety tests. The project's central claim is "the vehicle never gets stuck",
and these are what back that claim up.
"""

import numpy as np
import pytest

from src.city.city_world import build_city_world
from src.env.evrp_env import EVRPEnv
from src.env.instance import synthetic_instance

CACHE_DIR = "data/city_graphs"
CITIES = ["us_grid", "uk_organic", "in_dense"]

# Established empirically in Checkpoint 1 (see docs/checkpoints/checkpoint1.md):
# with 6 charging stations, battery >= 6000 gives 100% servability in all
# three cities. Tests use 8000+ to stay comfortably clear of the boundary.
SAFE_BATTERY = 10000.0


def _world(city_id, num_stations=6, seed=0):
    return build_city_world(
        city_id=city_id, display_name=city_id, topology_label="x",
        cache_dir=CACHE_DIR, num_charging_stations=num_stations,
        energy_rate=1.0, station_strategy="coverage", seed=seed,
    )


@pytest.mark.parametrize("city_id", CITIES)
def test_mask_never_allows_unreachable_node(city_id):
    """Condition 1: cannot select a node we lack the battery to reach."""
    world = _world(city_id)
    rng = np.random.default_rng(1)
    inst = synthetic_instance(world, 10, 200.0, SAFE_BATTERY, (5.0, 20.0), rng)
    env = EVRPEnv(inst)
    state = env.reset()
    mask = env.legal_actions(state)
    for j in np.flatnonzero(mask):
        assert inst.cost_matrix.energy_cost(state.position, j) <= state.battery + 1e-6


@pytest.mark.parametrize("city_id", CITIES)
def test_mask_never_allows_a_trap(city_id):
    """Condition 3 — the important one.

    Construct a state where a customer IS immediately reachable but has no
    charging station in range afterwards, and confirm it is masked out. This
    is the exact scenario a naive "can I reach it" check gets wrong, and the
    exact bug this project's own implementation hit and fixed during
    Checkpoint 1 (see docs/RESEARCH_LOG.md).

    The crafted battery is set just high enough to leave the depot for its
    NEAREST STATION (so the mask is not empty for the unrelated reason of
    "can't leave the depot at all") but too low to survive a detour to a
    farther customer that has no station nearby.
    """
    world = _world(city_id)
    rng = np.random.default_rng(2)
    inst = synthetic_instance(world, 15, 200.0, SAFE_BATTERY, (5.0, 20.0), rng)
    env = EVRPEnv(inst)

    nearest_station_from_depot = min(
        inst.cost_matrix.energy_cost(inst.depot_index, s) for s in inst.station_indices()
    )
    trap_battery = nearest_station_from_depot + 1.0  # just enough to leave depot safely

    from src.env.evrp_env import EVRPState

    found_trap = False
    for cust_idx in inst.customer_indices():
        energy_there = inst.cost_matrix.energy_cost(inst.depot_index, cust_idx)
        escape_needed = inst.nearest_safe_energy[cust_idx]
        reachable_but_trapped = (
            energy_there <= trap_battery
            and energy_there + escape_needed > trap_battery
        )
        if reachable_but_trapped:
            state = EVRPState(
                position=inst.depot_index, battery=trap_battery,
                load=inst.vehicle_capacity,
                visited=np.zeros(inst.num_customers, dtype=bool),
            )
            mask = env.legal_actions(state)  # must not raise: leaving for the
                                              # nearest station is still legal
            assert mask.any(), "mask should not be empty — station escape still exists"
            assert not mask[cust_idx], (
                f"Trap not caught: cust_idx={cust_idx} was allowed with "
                f"battery={trap_battery}, needing {energy_there} to arrive and "
                f"{escape_needed} more to escape."
            )
            found_trap = True
            break

    if not found_trap:
        pytest.skip("Could not construct a trap scenario for this instance/seed")


@pytest.mark.parametrize("city_id", CITIES)
def test_mask_is_never_empty_along_random_rollouts(city_id):
    """Walk many random LEGAL trajectories; assert a legal action always exists.

    Non-emptiness is the whole safety argument, so it is brute-forced here
    across many instances rather than merely asserted for one.
    """
    world = _world(city_id)
    for trial in range(15):
        rng = np.random.default_rng(trial)
        n_cust = int(rng.integers(3, 20))
        inst = synthetic_instance(world, n_cust, 200.0, SAFE_BATTERY, (5.0, 20.0), rng)
        env = EVRPEnv(inst)
        state = env.reset()
        steps = 0
        while not env.is_terminal(state) and steps < 3000:
            mask = env.legal_actions(state)  # raises RuntimeError if empty
            assert mask.any()
            assert state.battery >= -1e-6, "negative battery observed"
            action = rng.choice(np.flatnonzero(mask))
            state, _, _, _ = env.step(state, action)
            steps += 1


@pytest.mark.parametrize("city_id", CITIES)
def test_capacity_respected(city_id):
    """Cannot serve a customer whose demand exceeds remaining load."""
    world = _world(city_id)
    rng = np.random.default_rng(3)
    # tiny capacity forces this to bind quickly
    inst = synthetic_instance(world, 8, 15.0, SAFE_BATTERY, (10.0, 20.0), rng)
    env = EVRPEnv(inst)
    state = env.reset()
    mask = env.legal_actions(state)
    for j in inst.customer_indices():
        if mask[j]:
            assert inst.demand(j) <= state.load + 1e-6
