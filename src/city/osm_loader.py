"""
Layer 0 — Download and cache real road networks via OSMnx.

Responsibilities
----------------
- Pull a drivable street network for a named bounding box / place from OpenStreetMap.
- Cache the raw graph to `data/city_graphs/<city_id>.graphml` so we never re-download.
- Expose a small, stable interface the rest of the system depends on, so that
  swapping OSMnx for a synthetic generator later does not ripple outward.

Design notes (decided in planning)
----------------------------------
- Cities are *inspired by* real places, not 1:1 recreations. We pull real
  districts purely to get genuine topological variety:
    * grid-like        (US city district)
    * organic          (UK city district)
    * dense/irregular  (Indian city district)
- Single fixed HQ (depot) per city. No multi-depot VRP in v1.
- Graph must be *routable*: strongly connected, projected to metres.

Open sub-decision
-----------------
- Concrete size of each city subgraph (node/edge count). Needs to be big enough
  that routing is non-trivial, small enough that all-pairs shortest paths over
  the points-of-interest set stay cheap. TBD in Checkpoint 1.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CitySpec:
    """Declarative description of one city to build. See configs/cities.yaml."""

    city_id: str          # short slug, e.g. "us_grid"
    display_name: str     # human label for plots/report
    query: str            # OSMnx place query or bbox
    network_type: str     # e.g. "drive"
    topology_label: str   # "grid" | "organic" | "dense_irregular" — used in results tables


def load_city_graph(spec: CitySpec, cache_dir: Path):
    """Return a routable, projected road graph for `spec`, using the cache if present.

    TODO(Checkpoint 1):
      - download via osmnx if not cached
      - project to metres, take largest strongly connected component
      - annotate edges with length (and later: travel time / energy cost)
      - write to cache_dir / f"{spec.city_id}.graphml"
    """
    raise NotImplementedError


def list_city_specs(config_path: Path) -> list[CitySpec]:
    """Parse configs/cities.yaml into CitySpec objects."""
    raise NotImplementedError
