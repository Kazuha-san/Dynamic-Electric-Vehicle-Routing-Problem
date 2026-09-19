"""
Checkpoint 2 entry point — run classical baselines, no learning involved.

This is the environment sanity check. If nearest-neighbour produces absurd
routes here, the bug is in Layer 0/3, and no amount of RL will fix it.

    python scripts/run_baselines.py --config configs/default.yaml --city us_grid
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--city", required=True)
    parser.add_argument("--sizes", nargs="+", type=int, default=[10, 20, 50])
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    args = parser.parse_args()
    raise NotImplementedError("Checkpoint 2")


if __name__ == "__main__":
    main()
