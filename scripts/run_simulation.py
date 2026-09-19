"""
Checkpoint 5 entry point — the full end-to-end dynamic pipeline.

Orders arrive over time -> epochs close -> fleet sized -> customers partitioned
-> each vehicle routed by the trained agent -> routes committed.

    python scripts/run_simulation.py --config configs/default.yaml \
        --city us_grid --checkpoint checkpoints/gen_050.pt --horizon 7200

This is the script that produces the demo your professor watches.
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--city", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--horizon", type=float, default=7200.0, help="sim seconds")
    parser.add_argument("--interactive", action="store_true", help="user places markers")
    args = parser.parse_args()
    raise NotImplementedError("Checkpoint 5")


if __name__ == "__main__":
    main()
