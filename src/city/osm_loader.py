"""
Layer 0 — Load cached road networks.

In the development sandbox this project is built in, live OSMnx downloads are
not reachable (nominatim/overpass are not on the network allowlist). The
actual extraction happens locally via scripts/extract_cities.py, which caches
the result as data/city_graphs/<city_id>.graphml. This module's job is simply
to load that cache reliably and hand back a clean, typed networkx graph — it
never talks to the network itself.

Responsibilities
----------------
- Load a cached .graphml file.
- Coerce node/edge attributes back to the right types (GraphML round-trips
  everything through strings, so 'length' comes back as text and needs
  casting back to float — this is the single most common silent-bug source
  when reloading OSMnx output).
- Validate the graph is directed and strongly connected (a precondition, not
  something this function tries to fix).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import networkx as nx


@dataclass(frozen=True)
class CitySpec:
    """Declarative description of one city. See configs/cities.yaml."""

    city_id: str
    display_name: str
    topology_label: str
    center_lat: float
    center_lon: float
    radius_m: float


class CityGraphError(ValueError):
    """Raised when a cached city graph fails a basic sanity check."""


def _coerce_numeric_attrs(graph: nx.MultiDiGraph) -> None:
    """GraphML stores everything as strings; cast back the attributes we rely on.

    Mutates the graph in place.
    """
    for _, data in graph.nodes(data=True):
        for key in ("x", "y"):
            if key in data:
                data[key] = float(data[key])

    for _, _, data in graph.edges(data=True):
        if "length" in data:
            data["length"] = float(data["length"])
        if "oneway" in data:
            data["oneway"] = str(data["oneway"]).lower() == "true"
        if "reversed" in data:
            data["reversed"] = str(data["reversed"]).lower() == "true"


def load_city_graph(city_id: str, cache_dir: str | Path) -> nx.MultiDiGraph:
    """Load and validate a cached city graph by its id.

    Raises
    ------
    CityGraphError if the file is missing or fails the connectivity check.
    """
    path = Path(cache_dir) / f"{city_id}.graphml"
    if not path.exists():
        raise CityGraphError(
            f"No cached graph for city_id={city_id!r} at {path}. "
            f"Run scripts/extract_cities.py locally and place the .graphml "
            f"file in this directory."
        )

    graph = nx.read_graphml(path)
    if not graph.is_directed():
        raise CityGraphError(f"{city_id}: expected a directed graph, got undirected.")

    _coerce_numeric_attrs(graph)

    if not nx.is_strongly_connected(graph):
        n_components = nx.number_strongly_connected_components(graph)
        raise CityGraphError(
            f"{city_id}: graph is not strongly connected "
            f"({n_components} components) — a routable graph must have no "
            f"unreachable fragments. Re-run extraction; largest_strongly_connected() "
            f"should have been applied during extraction."
        )

    return graph


def list_city_specs(config: dict) -> list[CitySpec]:
    """Parse the `cities:` section of configs/cities.yaml into CitySpec objects."""
    specs = []
    for entry in config.get("cities", []):
        specs.append(
            CitySpec(
                city_id=entry["city_id"],
                display_name=entry["display_name"],
                topology_label=entry["topology_label"],
                center_lat=entry["center"][0],
                center_lon=entry["center"][1],
                radius_m=entry["radius_m"],
            )
        )
    return specs
