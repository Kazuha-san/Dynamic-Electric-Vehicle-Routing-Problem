"""
Checkpoint 1 entry point — build and cache the CityWorlds.

Run this ONCE per machine. Everything downstream assumes the caches exist.

    python scripts/build_cities.py --config configs/cities.yaml

Produces, per city:
  data/city_graphs/<city_id>.graphml     cached road network
  results/figures/<city_id>_map.png      eyeball check: depot + stations sane?
  a coverage validation report           are all nodes servable given battery range?
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cities.yaml")
    parser.add_argument("--force", action="store_true", help="rebuild even if cached")
    args = parser.parse_args()
    raise NotImplementedError("Checkpoint 1")


if __name__ == "__main__":
    main()
