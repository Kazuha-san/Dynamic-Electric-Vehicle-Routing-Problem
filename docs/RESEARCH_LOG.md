# Research Log

Running record of experiments, decisions, and results. **The final report is assembled
from this file plus `results/logs/`** — not reconstructed from memory at the end.

Append entries as work happens. Never rewrite history; if a decision is reversed, add a
new entry explaining why rather than editing the old one.

---

## Entry format

```
## [YYYY-MM-DD] Checkpoint N — short title

**What was done**

**Result / numbers**

**Decision made** (if any) and why

**Open questions raised**
```

---

## [Planning phase] Architecture and scope

**What was done**
Full system design settled through discussion: layered architecture, MDP formulation,
feasibility strategy, dispatch model, evaluation plan. Literature survey completed and
written to `BACKGROUND_AND_RELATED_WORK.md`.

**Decisions made**
All entries in `ARCHITECTURE.md` §2. Most consequential:
- Hard reachability-lookahead masking instead of a learned soft penalty, because "never
  gets stuck" is a hard product requirement.
- Real road networks instead of Euclidean coordinates, enabling a cross-topology
  generalization experiment absent from the surveyed literature.
- Deterministic fleet sizing decoupled from the learned router.

**Open questions raised**
Logged in `ARCHITECTURE.md` §7.

---

## [pending] Checkpoint 1 — City World & Environment Foundation

**To record when done**
- Which three districts were chosen, and their node/edge counts
- Charging station placement strategy chosen, and the coverage validation report
- Cost matrix build time per city (this determines whether the POI-restricted approach
  scales to the sizes we want)
- Confirmation that the trap instance is correctly masked

---

## [pending] Checkpoint 2 — Fleet Sizing & Baselines

**To record when done**
- Baseline costs: nearest-neighbour / greedy insertion / OR-Tools, per city and size
- Fleet sizes chosen vs lower bounds (the over-dispatch check)
- Partitioning strategy comparison
- OR-Tools encoding details and solver status at the chosen time limit

---

## [pending] Checkpoint 3 — Network + MCTS

**To record when done**
- Final architecture and parameter count
- Evidence that search beats the raw policy (and by how much)
- Simulation-budget sweep: cost vs `num_simulations`

---

## [pending] Checkpoint 4 — Self-Play Training

**To record when done**
- Training curves; generations to beat each baseline
- Feasibility rate (expect 100%; any deviation is a masking bug)
- Wall-clock per generation
- Any instance of the self-play degradation reported in TSS GAZ PTP

---

## [pending] Checkpoint 5 — Dynamic Dispatch

**To record when done**
- End-to-end runs: orders served, epochs, fleet sizes per epoch
- Effect of epoch length on total cost and on vehicles dispatched

---

## [pending] Checkpoint 6 — Full Evaluation

**To record when done**
- The full grid: methods × cities × sizes × seeds
- Gap vs OR-Tools
- **Cross-topology transfer**: train on one city, test on the others
- **Cross-size transfer**: train on small, test on larger
- Ablations: Gumbel vs PUCT, partitioning strategies, fleet-sizing methods

---

## [pending] Checkpoint 7 — Visualization & Report
