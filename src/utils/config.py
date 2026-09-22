"""Config loading and validation. Single source of truth for every hyperparameter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    """Raised on a malformed or unrecognized config."""


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a YAML config file into a plain dict.

    We deliberately do NOT validate a fixed schema here (the config has grown
    organically across layers) but we do fail loudly on basic structural
    problems: a missing file, or a file that isn't a mapping at the top level.
    """
    path = Path(path)
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")
    with open(path) as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ConfigError(f"Config at {path} must be a top-level mapping, got {type(data)}")
    return data


def get(config: dict, dotted_key: str, default: Any = "__no_default__") -> Any:
    """Fetch config['a']['b']['c'] via get(config, 'a.b.c').

    Fails loudly (KeyError) on a missing key unless a default is supplied —
    a silently-defaulted typo'd hyperparameter is a week of confused debugging.
    """
    node = config
    for part in dotted_key.split("."):
        if not isinstance(node, dict) or part not in node:
            if default != "__no_default__":
                return default
            raise KeyError(f"Config key '{dotted_key}' not found (missing at '{part}')")
        node = node[part]
    return node
