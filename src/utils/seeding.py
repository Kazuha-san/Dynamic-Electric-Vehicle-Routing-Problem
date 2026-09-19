"""
Reproducibility. Every reported number must be reproducible from (config, seed).

Seeds python, numpy, and torch, and returns the numpy Generator that instance
sampling should use — passing an explicit rng around beats global state.
"""

from __future__ import annotations


def seed_everything(seed: int):
    raise NotImplementedError
