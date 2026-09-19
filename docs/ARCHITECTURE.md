# Architecture & Design Decisions

This document records **what was decided and why**. When a future question is
"why is it built this way?", the answer should be here rather than reconstructed.

---

## 1. Why layered rather than end-to-end

An end-to-end policy that outputs "how many vehicles AND every route" is a much harder
learning problem and a much weaker artifact: you cannot test its parts, cannot ablate
them, and cannot justify its fleet-size choice to anyone.

Splitting the system means the RL agent solves exactly one well-posed problem —
single-vehicle routing — while fleet sizing stays deterministic and **justifiable**. It
also makes every layer independently testable, which is what makes the evaluation
chapter of the report possible.

---

## 2. Locked decisions

| Decision | Choice | Rationale |
|---|---|---|
| Fleet sizing vs routing | Two-stage: deterministic sizing, then RL routing | A fleet size must be defensible, not guessed. Keeps the learning problem clean. |
| Order arrival | Dynamic, batched into fixed-interval epochs | Standard real-world dispatch (epoch-based dispatching). Per-order replanning causes route thrashing. |
| Mid-route replanning | In-flight vehicles finish committed routes | v1 simplicity; full re-optimization needs "start mid-route with partial battery" as an initial condition. Stretch goal. |
| Vehicle interaction | Independent after partitioning | Makes each episode a clean single-agent MDP. |
| Charging station capacity | Unlimited concurrent (v1) | Queueing is a realism upgrade, not a core contribution. |
| Map | Real road graphs via OSMnx, 3 topologies | Shortest-path costs, not Euclidean. Enables the cross-topology generalization experiment. |
| Depot | Single fixed HQ per city | Multi-depot is a different problem class (MDVRP); out of scope for v1. |
| Episode | One continuous tour, no early depot return | Bounded horizon, unambiguous feasibility semantics. |
| Feasibility | Hard reachability-lookahead masking | "Never gets stuck" is a product requirement, not a soft preference. |
| Reward | Dense negative step cost + terminal bonus | Low-variance, debuggable against baselines. Sparse terminal reward makes early training nearly signal-free. |
| Search | Gumbel AlphaZero | Designed for small simulation budgets; has a policy-improvement guarantee vanilla PUCT lacks at low budgets. |
| Network | Attention encoder over the POI set | Permutation-equivariant; variable instance sizes come free. |
| Effort priority | RL core > visualization | The RL engine is the contribution; visualization is assembled, not engineered. |

---

## 3. The state, and why it is that small

```
state = (position, battery, load, visited_mask)
```

The Markov property says the future depends only on the present. Here, **the order in
which customers were visited does not affect anything reachable from now on** — only
where the vehicle is, what it has left, and who remains. So visit order is excluded.

This is not a simplification for convenience. It is what makes this a clean MDP, which
is what licenses using MCTS and RL at all. Adding route history would produce a larger
state space with no additional predictive power, and would slow every MCTS clone.

Contrast: route-based MDP formulations for stochastic dynamic VRP (Ulmer et al.) expand
the state to include the full plan, and scale poorly as a result.

---

## 4. The safety layer — the project's central claim

### The trap naive masking falls into

The obvious check is "can I reach node X with my current battery?". It is not enough.
The vehicle arrives at X with 2% charge, and from X nothing is in range. The check
passed; the vehicle is dead.

### The check actually implemented

An action to X is legal iff:

1. `energy(position → X) ≤ battery` — can I get there
2. capacity/demand constraints hold — can I serve it
3. after arriving, some **safe node** (charging station or depot) is still reachable —
   **can I escape**

Condition 3 is the lookahead.

### Why it is affordable

`nearest_safe_energy[X]` — the energy from X to its closest safe node — depends only on
the city, not the episode. Precompute it once per instance, and condition 3 becomes a
single float comparison. That is what turns a hard safety guarantee into something MCTS
can afford to call tens of thousands of times per planning call.

### What is deliberately NOT attempted

A *full* completion-feasibility check ("is there a feasible route serving all remaining
customers from here?") is strictly stronger and NP-hard in general. We implement depth-1
escape and **say so plainly in the report**. Overclaiming here would be worse than the
limitation itself.

---

## 5. Sign conventions (get these wrong and everything silently breaks)

- Rewards are **negative costs**. Search always **maximizes**. There is no "minimize"
  branch anywhere in the codebase.
- The value head predicts **negative normalized remaining cost**, not P(win) — this is a
  single-player cost-minimization problem, not a two-player game.
- Value targets are normalized per instance against a cheap reference (e.g.
  nearest-neighbour cost), because raw costs vary by orders of magnitude across sizes
  and topologies.
- Illegal actions are masked on the **logits** (set to `-inf` before softmax), never
  zeroed after softmax — post-hoc zeroing corrupts the distribution MCTS depends on.

`tests/test_mcts.py::test_value_sign_convention` exists specifically to guard this.

---

## 6. What "self-play" means here

There is no opponent. The term is used in the single-agent combinatorial-optimization
sense: the network bootstraps off its own search-improved decisions.

- **Teacher** = network + MCTS (slow, deliberate, looks ahead)
- **Student** = the raw network (fast, instinctive)

Every generation, the student is trained toward what the teacher worked out. Search can
only help, so the teacher is always at least as good as the student — and next
generation the teacher is built on the improved student. The agent improves against its
own prior self, round after round.

---

## 7. Open sub-decisions

These are deliberately unresolved and will be settled with evidence at the checkpoint
noted. Where a comparison is cheap, the comparison itself becomes a result.

| Question | Options | Resolved at |
|---|---|---|
| City subgraph size | node/edge count per city | CP1 |
| Charging station placement | manual / kmeans / coverage | CP1 |
| Range lower bound | analytical estimate vs bin-packing ILP | CP2 |
| Partitioning | sweep / kmeans / balanced | CP2 |
| Network architecture details | layer count, embedding dim; attention vs GNN | CP3 |
| Epoch length | fixed interval; hybrid interval-or-count | CP5 |
| Training instance sizes | which sizes to train on for best transfer | CP4/CP6 |

---

## 8. Known limitations, to state honestly in the report

- Depth-1 escape feasibility, not full completion feasibility (NP-hard).
- Linear energy consumption; real batteries and terrain are not linear.
- Full recharge only; partial recharging is a documented extension.
- Single depot; unlimited concurrent charging capacity.
- OR-Tools under a time limit is a strong heuristic, **not** a proof of optimality — the
  report says "gap vs OR-Tools", never "gap vs optimal".
- Committed routes are not re-optimized mid-epoch.
