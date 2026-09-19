"""
Layer 3 — Gumbel AlphaZero: the variant this project actually uses.

Why not vanilla AlphaZero
-------------------------
Vanilla PUCT assumes a large simulation budget per move. With a small budget —
which is our reality as a single-machine student project — its visit-count
statistics are noisy and action selection can actually degrade relative to just
following the raw policy. Gumbel AlphaZero (Danihelka et al., ICLR 2022) fixes
this and comes with a policy-improvement guarantee that holds even with very few
simulations.

Mechanism
---------
  1. At the root, sample a candidate action set WITHOUT replacement using
     Gumbel-perturbed policy logits (the Gumbel-Top-k trick). This gives a
     diverse, unbiased sample of promising actions rather than repeatedly
     re-deepening whichever action got lucky first.
  2. Distribute a fixed simulation budget across those candidates using
     SEQUENTIAL HALVING: run a round, drop the worst half, repeat. Budget flows
     to candidates that keep looking good.
  3. Select the final action by combining the prior with completed Q-values,
     which is what yields the "at least as good as the raw policy" guarantee.
  4. Interior (non-root) nodes use deterministic sequential-halving-free
     selection — the Gumbel machinery is a ROOT-level construct.

Precedent
---------
This exact combination (Gumbel AlphaZero + self-play + multi-constrained EVRP)
is the subject of TSS GAZ PTP (Smart Cities, 2026) — see
BACKGROUND_AND_RELATED_WORK.md. That paper also documents a failure mode worth
watching for: self-play signal degrading when the reference policy is mismatched
in strength. Reproducing or avoiding that is a legitimate result for the report.
"""

from __future__ import annotations


def gumbel_top_k(logits, k: int, rng):
    """Sample k actions without replacement via Gumbel-Top-k. Only over legal actions."""
    raise NotImplementedError


def sequential_halving_budget(num_candidates: int, num_simulations: int):
    """Split the simulation budget across sequential-halving rounds."""
    raise NotImplementedError


class GumbelMCTS:
    """Root-level Gumbel action selection + sequential halving."""

    def search(self, root_state, instance, num_simulations: int, num_candidates: int):
        """Return (improved_policy_target, chosen_action, root_value).

        The improved policy target is what the network trains toward — see
        training/selfplay.py. TODO(Checkpoint 3).
        """
        raise NotImplementedError
