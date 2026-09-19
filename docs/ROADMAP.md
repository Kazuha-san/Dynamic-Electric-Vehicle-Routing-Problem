# Project Roadmap

Seven checkpoints. Each has a concrete, demonstrable deliverable — something that can be
shown, not just described.

---

## Checkpoint 1 — City World & Environment Foundation

**Build**
- OSMnx loader with graph caching; pick the three real districts and record the choices
- Depot placement + sparse charging station placement (+ coverage validation)
- POI cost matrix (all-pairs shortest paths over points of interest)
- `EVRPEnv`: state, actions, reward, termination
- `feasibility.py`: reachability-lookahead masking + precomputed nearest-safe-node energy

**Deliverable**
- Three cached city graphs, with a rendered map per city
- `tests/test_city.py`, `test_env.py`, `test_feasibility.py` passing
- Demonstrated: a vehicle cannot be stranded, including on a hand-built trap instance

**Why first:** every other layer consumes real distance data. Nothing downstream can be
validated before this exists.

---

## Checkpoint 2 — Fleet Sizing & Baselines

**Build**
- Capacity and range lower bounds; the sizer/partitioner retry loop
- Partitioning (`sweep` first, then `kmeans` / `balanced` for comparison)
- Nearest-neighbour and greedy insertion, both routed through the same env and mask
- OR-Tools encoding (charging stations as optional repeatable visits, battery dimension)

**Deliverable**
- First real numbers: baseline route costs across cities and sizes
- Over-dispatch check: fleet size never exceeds the computed lower bound
- Environment validated — baseline replay through the env reproduces reported costs

---

## Checkpoint 3 — Policy/Value Network + MCTS

**Build**
- Attention encoder, policy head (masked logits), value head
- PUCT MCTS as the ablation baseline
- Gumbel AlphaZero: Gumbel-Top-k root sampling + sequential halving

**Deliverable**
- Untrained agent produces valid routes; masking holds under search
- Verified: search-improved decisions beat the raw policy (otherwise self-play has no
  signal and training cannot work)
- Value sign convention tested

---

## Checkpoint 4 — Self-Play Training Loop

**Build**
- Episode generation, replay buffer, training step, generation loop
- Value normalization against a cheap reference
- Per-generation metric logging

**Deliverable**
- Training curves: route cost decreasing over generations
- Trained agent beating nearest-neighbour and greedy insertion on the training
  distribution
- 100% feasibility rate confirmed empirically

---

## Checkpoint 5 — Dynamic Dispatch Integration

**Build**
- Synthetic + interactive order streams
- Epoch scheduler: poll → size fleet → partition → route → commit
- Wire Layers 0–3 into one pipeline

**Deliverable**
- End-to-end run: orders arriving over a simulated horizon, served by a dynamically
  sized fleet
- Per-epoch records logged for the report

---

## Checkpoint 6 — Full Evaluation & Cross-City Generalization

**Build**
- The benchmark grid: methods × cities × sizes × seeds
- Result tables and figures generated from recorded logs

**Deliverable**
- Complete comparison tables including gap vs OR-Tools
- The generalization result: does a policy trained on one topology transfer to another,
  and to instance sizes it never saw?
- Ablations: Gumbel vs PUCT; partitioning strategies; analytical vs ILP fleet sizing

---

## Checkpoint 7 — Visualization & Final Report

**Build**
- Static city/route rendering along real road paths
- Animated simulation playback
- Report assets assembled from `results/logs/`

**Deliverable**
- Demo: vehicles navigating the city, battery and epoch boundaries visible
- Final report, built from recorded data rather than reconstructed at the end

---

## Dependency order

```
CP1 ──> CP2 ──> CP3 ──> CP4 ──> CP6 ──> CP7
         │                │       ^
         └──> CP5 ────────┴───────┘
```

CP5 (dispatch) needs the router from CP4 to be meaningful end-to-end, but the scheduler
itself can be built against baselines as soon as CP2 lands.
