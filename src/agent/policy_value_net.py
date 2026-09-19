"""
Layer 3 — Policy + value network. The agent's "intuition".

Two heads, one shared encoder:
  policy(state) -> distribution over POI actions   ("which move looks good")
  value(state)  -> scalar                          ("how good is this position")

The value target is NOT "probability of winning" — this is a single-player cost
minimization problem. It predicts (normalized) remaining cost-to-go. Getting
this sign/normalization convention right and CONSISTENT with the MCTS backup is
a classic source of silent bugs; see mcts/ for the matching convention.

Architecture (leaning, per planning; finalize at Checkpoint 3)
--------------------------------------------------------------
Attention-based encoder over the POI set, in the lineage of Kool et al. and the
EVRP-DRL work cited in BACKGROUND_AND_RELATED_WORK.md:

  encoder : per-POI features -> self-attention -> node embeddings
            (permutation-equivariant: the customer set is a SET, and an MLP over
            a padded vector would wrongly treat position-in-vector as meaningful)
  context : current position embedding + battery + load + visited summary
  policy  : attention compatibility between context and each node -> logits
            -> masked softmax over LEGAL actions only
  value   : pooled embedding + context -> scalar

Why attention rather than a fixed-size MLP
------------------------------------------
Variable instance sizes come free, which is what makes the cross-size and
cross-city generalization experiments in Checkpoint 6 possible at all.

Masking discipline
------------------
The illegal-action mask is applied to the LOGITS (set to -inf before softmax),
never post-hoc to probabilities. Post-hoc zeroing silently corrupts the
distribution MCTS relies on.
"""

from __future__ import annotations


class PolicyValueNet:
    """Shared encoder + policy head + value head.

    TODO(Checkpoint 3): implement as torch.nn.Module.
    """

    def forward(self, batch):
        """Return (policy_logits, value)."""
        raise NotImplementedError


def encode_state_features(state, instance):
    """Turn (state, instance) into network input tensors.

    Per-POI features (first pass):
      - coordinates, normalized per instance
      - demand (0 for depot/stations)
      - is_depot / is_customer / is_station one-hot
      - visited flag
      - energy cost from current position
      - precomputed nearest-safe-node energy
    Context features:
      - battery fraction, load fraction, fraction of customers remaining

    Keeping feature construction in one function means the env, MCTS, and
    training loop cannot drift apart on representation.
    """
    raise NotImplementedError
