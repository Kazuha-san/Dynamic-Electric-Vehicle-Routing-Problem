# EVRP Self-Play RL

Self-play reinforcement learning (Gumbel AlphaZero-style neural-guided MCTS) for
**dynamic electric vehicle routing over real city road networks**.

Orders arrive over time on a real street map. The system batches them into
planning windows, computes the **minimum** fleet needed, partitions customers
across vehicles, and routes each vehicle with a learned agent that is
**structurally incapable of stranding itself** on an empty battery.

- Formal problem definition → [`PROBLEM_STATEMENT.md`](./PROBLEM_STATEMENT.md)
- Full system design and locked decisions → [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md)
- Literature survey and contribution positioning → [`docs/BACKGROUND_AND_RELATED_WORK.md`](./docs/BACKGROUND_AND_RELATED_WORK.md)
- Checkpoint plan → [`docs/ROADMAP.md`](./docs/ROADMAP.md)
- Running record of experiments and results → [`docs/RESEARCH_LOG.md`](./docs/RESEARCH_LOG.md)

---

## The system in one picture

```
Layer 0  CityWorld        real road graph (OSMnx) + single HQ + sparse charging stations
   |                      precomputed shortest-path cost matrix over POIs
   v
Layer 1  Dispatch         orders arrive dynamically -> batched into fixed time windows
   |                      (epoch-based dispatch; in-flight vehicles finish committed routes)
   v
Layer 2  Fleet            minimum vehicle count (deterministic, justifiable bound)
   |                      -> partition customers into per-vehicle subsets
   v
Layer 3  Router (RL)      per vehicle: Gumbel AlphaZero MCTS + policy/value net
   |                      hard reachability-lookahead masking = never strands
   v
Layer 4  Evaluation       vs nearest-neighbour / greedy insertion / OR-Tools
   |                      across 3 city topologies and multiple instance sizes
   v
Layer 5  Visualization    static maps + animated simulation playback
```

Each layer is independently testable. That modularity is deliberate: it is what
makes ablations possible and what keeps the RL problem clean (the agent solves
single-vehicle routing, nothing else).

---

## Repository layout

```
evrp-selfplay-rl/
├── configs/
│   ├── default.yaml            # all hyperparameters, single source of truth
│   └── cities.yaml             # city definitions (Layer 0)
├── src/
│   ├── city/                   # Layer 0 — road networks, stations, cost matrices
│   │   ├── osm_loader.py
│   │   ├── city_world.py
│   │   ├── charging_stations.py
│   │   └── cost_matrix.py
│   ├── dispatch/               # Layer 1 — order arrival + epoch scheduling
│   │   ├── order_stream.py
│   │   └── epoch_scheduler.py
│   ├── fleet/                  # Layer 2 — fleet sizing + partitioning
│   │   ├── fleet_sizer.py
│   │   └── partitioner.py
│   ├── env/                    # Layer 3 — the MDP
│   │   ├── evrp_env.py
│   │   ├── feasibility.py      # <- the safety layer; the core claim lives here
│   │   └── instance.py
│   ├── agent/
│   │   └── policy_value_net.py # attention encoder + policy/value heads
│   ├── mcts/
│   │   ├── mcts.py             # PUCT baseline (ablation)
│   │   └── gumbel.py           # Gumbel AlphaZero (the method we use)
│   ├── training/
│   │   ├── selfplay.py         # the self-play loop
│   │   └── replay_buffer.py
│   ├── baselines/              # Layer 4 — classical comparisons
│   │   ├── nearest_neighbour.py
│   │   ├── greedy_insertion.py
│   │   └── ortools_solver.py
│   ├── evaluation/
│   │   ├── benchmark.py
│   │   └── metrics.py
│   ├── viz/                    # Layer 5
│   │   ├── render_city.py
│   │   └── animate.py
│   └── utils/
│       ├── config.py
│       ├── seeding.py
│       ├── graph_utils.py
│       └── research_log.py     # every run recorded -> feeds the final report
├── scripts/
│   ├── build_cities.py         # Checkpoint 1
│   ├── run_baselines.py        # Checkpoint 2
│   ├── train.py                # Checkpoint 4
│   ├── run_simulation.py       # Checkpoint 5
│   ├── evaluate.py             # Checkpoint 6
│   └── make_report_assets.py   # Checkpoint 7
├── tests/                      # one test module per layer
├── data/city_graphs/           # cached OSM graphs (gitignored)
├── results/{logs,figures,tables}/
└── docs/
```

---

## Getting started

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Checkpoint 1 — build and cache the city road networks (run once)
python scripts/build_cities.py --config configs/cities.yaml

# Checkpoint 2 — classical baselines, no learning yet (environment sanity check)
python scripts/run_baselines.py --config configs/default.yaml --city us_grid

# Checkpoint 4 — self-play training
python scripts/train.py --config configs/default.yaml

# Checkpoint 5 — full dynamic simulation with a trained agent
python scripts/run_simulation.py --config configs/default.yaml \
    --city us_grid --checkpoint checkpoints/gen_050.pt

# Checkpoint 6 — full benchmark grid
python scripts/evaluate.py --config configs/default.yaml \
    --checkpoint checkpoints/gen_050.pt
```

---

## Status

**Checkpoint 1 complete** — see [`docs/checkpoints/checkpoint1.md`](./docs/checkpoints/checkpoint1.md).
Real road-network cities extracted and validated (Chicago/York/Old Delhi), the EVRP
environment and hard feasibility-masking safety layer implemented and tested (34
passing tests, 300-trial stress test, zero safety violations). A real design bug in
the escape-feasibility check was found and fixed during this checkpoint — full
account in the report.

Next: **Checkpoint 2 — Fleet Sizing & Baselines**.
