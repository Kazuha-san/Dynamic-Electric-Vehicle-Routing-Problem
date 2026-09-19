"""
Checkpoint 4 entry point — the self-play training loop.

    python scripts/train.py --config configs/default.yaml

Writes checkpoints to checkpoints/, per-generation metrics to results/logs/.
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--resume", default=None)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    raise NotImplementedError("Checkpoint 4")


if __name__ == "__main__":
    main()
