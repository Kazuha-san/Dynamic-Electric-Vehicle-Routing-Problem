"""
Reproducibility. Every reported number must be reproducible from (config, seed).

Seeds python, numpy, and torch (if installed), and returns the numpy Generator
that instance sampling should use — passing an explicit rng around beats
relying on global random state, especially once MCTS starts forking things.
"""

from __future__ import annotations

import random

import numpy as np


def seed_everything(seed: int) -> np.random.Generator:
    """Seed all relevant global RNGs and return a fresh, seeded numpy Generator.

    Callers should prefer the returned Generator (`rng.integers(...)`,
    `rng.choice(...)`) over `np.random.*` module-level calls, so that two
    pieces of code seeded from the same `seed` don't silently interfere with
    each other's random draws via shared global state.
    """
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass
    return np.random.default_rng(seed)
