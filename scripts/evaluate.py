"""
Checkpoint 6 entry point — the full benchmark grid.

    python scripts/evaluate.py --config configs/default.yaml \
        --checkpoint checkpoints/gen_050.pt

Runs methods x cities x sizes x seeds, writes result tables to results/tables/
and records every run via utils/research_log.py.
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--methods", nargs="+",
                        default=["nearest_neighbour", "greedy_insertion", "ortools", "mcts_agent"])
    args = parser.parse_args()
    raise NotImplementedError("Checkpoint 6")


if __name__ == "__main__":
    main()
