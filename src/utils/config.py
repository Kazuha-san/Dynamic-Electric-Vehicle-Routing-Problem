"""Config loading and validation. Single source of truth for every hyperparameter."""

from __future__ import annotations

from pathlib import Path


def load_config(path: Path) -> dict:
    """Load YAML, apply defaults, validate required keys.

    Fail LOUDLY on unknown keys — a silently-ignored typo'd hyperparameter is a
    week of confused debugging.
    """
    raise NotImplementedError
