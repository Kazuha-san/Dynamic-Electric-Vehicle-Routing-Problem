"""Layer 3 environment tests — MDP mechanics."""

import numpy as np
import pytest

from src.city.city_world import build_city_world
from src.env.evrp_env import EVRPEnv, EVRPState, IllegalActionError
from src.env.instance import synthetic_instance

CACHE_DIR = "data/city_graphs"
SAFE_BATTERY = 10000.0


def _instance(seed=0, n_cust=10):
    world = build_city_world(
        city_id="us_grid", display_name="x", topology_label="x",
        cache_dir=CACHE_DIR, num_charging_stations=6, energy_rate=1.0,
        station_strategy="coverage", seed=0,
    )
    rng = np.random.default_rng(seed)
    return world, synthetic_instance(world, n_cust, 200.0, SAFE_BATTERY, (5.0, 20.0), rng)


def test_reset_starts_at_depot_full_battery():
    _, inst = _instance()
    env = EVRPEnv(inst)
    state = env.reset()
    assert state.position == inst.depot_index
    assert state.battery == inst.battery_capacity
    assert state.load == inst.vehicle_capacity
    assert not state.visited.any()


def test_step_rejects_illegal_action():
    """An illegal action is a CALLER bug; the env must raise, not absorb it."""
    _, inst = _instance()
    env = EVRPEnv(inst)
    state = env.reset()
    with pytest.raises(IllegalActionError):
        env.step(state, state.position)  # moving to self is always illegal


def test_reward_equals_negative_travel_cost():
    """Hand-compute a step and assert the reward matches exactly."""
    _, inst = _instance()
    env = EVRPEnv(inst)
    state = env.reset()
    mask = env.legal_actions(state)
    action = np.flatnonzero(mask)[0]
    expected_cost = inst.cost_matrix.cost(state.position, action)
    next_state, reward, done, info = env.step(state, action)
    assert abs(reward - (-expected_cost)) < 1e-9
    assert abs(info["cost"] - expected_cost) < 1e-9


def test_recharge_restores_battery():
    _, inst = _instance()
    env = EVRPEnv(inst)
    state = env.reset()
    mask = env.legal_actions(state)
    for station_idx in inst.station_indices():
        if mask[station_idx]:
            next_state, _, _, _ = env.step(state, station_idx)
            assert next_state.battery == inst.battery_capacity
            return
    pytest.skip("no station reachable from depot in this instance")


def test_terminal_only_when_all_served_and_at_depot():
    _, inst = _instance(n_cust=3)
    env = EVRPEnv(inst)
    state = env.reset()
    assert not env.is_terminal(state)  # nothing visited yet
    # partially visited, still not terminal even if somehow back at depot
    partial = EVRPState(
        position=inst.depot_index, battery=inst.battery_capacity,
        load=inst.vehicle_capacity, visited=np.array([True, False, False]),
    )
    assert not env.is_terminal(partial)
    complete = EVRPState(
        position=inst.depot_index, battery=inst.battery_capacity,
        load=inst.vehicle_capacity, visited=np.array([True, True, True]),
    )
    assert env.is_terminal(complete)


def test_state_clone_is_independent():
    """MCTS correctness depends on this: mutating a clone must not touch the
    original. A shared numpy view here would corrupt the entire search."""
    _, inst = _instance()
    env = EVRPEnv(inst)
    state = env.reset()
    clone = state.clone()
    clone.visited[0] = True
    clone.battery = 0.0
    assert not state.visited[0]
    assert state.battery == inst.battery_capacity


def test_state_is_markov():
    """Given two states with IDENTICAL (position, battery, load, visited),
    the legal actions and transition dynamics must be identical regardless of
    how each state was reached (different step_count / history).

    Note: this is not the same claim as "different visit orders converge to
    the same state" — with real road distances they generally do NOT (a
    different order produces different battery/position), which is expected
    and not a Markov violation. The property under test is narrower and more
    precise: the four Markov-relevant fields are a SUFFICIENT statistic for
    the future; nothing else (like step_count, or "how we got here") may
    influence legal_actions() or step()."""
    _, inst = _instance(n_cust=4)
    env = EVRPEnv(inst)

    visited = np.array([True, False, False, False])
    state_early = EVRPState(
        position=1, battery=5000.0, load=150.0, visited=visited, step_count=1,
    )
    state_late = EVRPState(
        position=1, battery=5000.0, load=150.0, visited=visited, step_count=17,
    )

    mask_early = env.legal_actions(state_early)
    mask_late = env.legal_actions(state_late)
    assert np.array_equal(mask_early, mask_late)

    legal = np.flatnonzero(mask_early)
    if len(legal) == 0:
        pytest.skip("no legal action from this hand-built state")
    action = legal[0]
    next_early, r_early, done_early, _ = env.step(state_early, action)
    next_late, r_late, done_late, _ = env.step(state_late, action)
    assert next_early.position == next_late.position
    assert abs(next_early.battery - next_late.battery) < 1e-9
    assert abs(next_early.load - next_late.load) < 1e-9
    assert np.array_equal(next_early.visited, next_late.visited)
    assert abs(r_early - r_late) < 1e-9
    assert done_early == done_late
