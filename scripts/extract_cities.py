"""
Checkpoint 1 — City extraction script (RUN THIS LOCALLY, not in the sandbox).

The sandbox this project is being built in cannot reach OpenStreetMap's servers
(nominatim / overpass are not on its network allowlist). This script has no such
restriction on your own machine.

Usage
-----
    pip install osmnx networkx
    python scripts/extract_cities.py

Produces
--------
    data/city_graphs/us_grid.graphml
    data/city_graphs/uk_organic.graphml
    data/city_graphs/in_dense.graphml
    a printed summary table (node/edge counts, connectivity, area)

Send the three .graphml files (and the printed summary) back — everything
downstream (cost matrix, environment, feasibility masking) runs in the sandbox
against these cached files, no further internet access needed.

What is kept vs discarded from the source data
------------------------------------------------
KEPT   : road geometry only — which nodes connect to which, edge length,
         one-way direction.
DISCARD: everything else OSM tags onto a graph (street names, POI tags,
         addresses). We never load or display real-world labels anywhere in
         the system — this is a synthetic city built on a real street
         skeleton, nothing more.
"""

from __future__ import annotations

import os
import networkx as nx
import osmnx as ox

ox.settings.log_console = True
ox.settings.use_cache = True

# All three use the SAME radius so the cities are comparable in physical area —
# a fair cross-topology comparison needs similar ground covered, with any
# difference in node/edge count reflecting genuine street-density differences
# (grid vs organic vs dense), not an accidental size mismatch.
#
# NOTE: uk_organic previously got extracted via the old place-name method,
# which pulled the ENTIRE city of York (~344 km^2) instead of a central
# district (~10-15 km^2) — that run is invalid for comparison purposes.
# Redoing all three together here, at a consistent radius, fixes it.
RADIUS_M = 2000

CITY_SPECS = [
    {
        "city_id": "us_grid",
        "display_name": "Downtown Chicago (Loop)",
        "topology_label": "grid",
        "center": (41.8786, -87.6298),  # The Loop
        "radius_m": RADIUS_M,
    },
    {
        "city_id": "uk_organic",
        "display_name": "Central York",
        "topology_label": "organic",
        "center": (53.9600, -1.0873),  # York Minster area
        "radius_m": RADIUS_M,
    },
    {
        "city_id": "in_dense",
        "display_name": "Old Delhi (Chandni Chowk)",
        "topology_label": "dense_irregular",
        "center": (28.6562, 77.2410),  # Chandni Chowk, heart of Old Delhi
        "radius_m": RADIUS_M,
    },
]

OUT_DIR = "./data/city_graphs"


def strip_real_world_tags(G: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """Keep only geometry-relevant attributes. Drop names/refs/addresses.

    This is what makes the "synthetic city, real skeleton only" claim literally
    true rather than just a stated intention.
    """
    keep_edge_keys = {"length", "oneway", "reversed"}
    for _, _, _, data in G.edges(keys=True, data=True):
        for k in list(data.keys()):
            if k not in keep_edge_keys:
                del data[k]
    keep_node_keys = {"x", "y"}
    for _, data in G.nodes(data=True):
        for k in list(data.keys()):
            if k not in keep_node_keys:
                del data[k]
    return G


def extract_one(spec: dict) -> dict:
    print(f"\n=== {spec['display_name']} ({spec['city_id']}) ===")
    G = ox.graph_from_point(
        spec["center"], dist=spec["radius_m"], network_type="drive", simplify=True
    )

    # Project to metres so edge lengths / distances are real-world accurate,
    # not lat/lon degrees.
    G = ox.project_graph(G)

    # Keep only the largest strongly connected component. A routable graph
    # must have no unreachable fragments — see tests/test_city.py.
    largest_scc_nodes = max(nx.strongly_connected_components(G), key=len)
    G = G.subgraph(largest_scc_nodes).copy()

    G = strip_real_world_tags(G)

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"{spec['city_id']}.graphml")
    ox.save_graphml(G, out_path)

    # Rough area from the convex hull of node positions (m^2 -> km^2), since we
    # projected to metres above.
    try:
        area_km2 = ox.utils_graph.graph_to_gdfs(G, edges=False).unary_union.convex_hull.area / 1e6
    except Exception:
        area_km2 = float("nan")

    summary = {
        "city_id": spec["city_id"],
        "display_name": spec["display_name"],
        "topology_label": spec["topology_label"],
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
        "area_km2": round(area_km2, 2),
        "is_strongly_connected": nx.is_strongly_connected(G),
        "out_path": out_path,
    }
    print(summary)
    return summary


def main():
    results = []
    for spec in CITY_SPECS:
        try:
            results.append(extract_one(spec))
        except Exception as e:
            print(f"  FAILED on {spec['city_id']}: {type(e).__name__}: {e}")
            print(f"  (skipping — adjust 'center'/'radius_m' for this city and rerun)")

    if not results:
        print("\nNo cities extracted successfully.")
        return

    print("\n\n=== SUMMARY ===")
    header = f"{'city_id':<12} {'nodes':>7} {'edges':>7} {'area_km2':>9} {'connected':>10}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(f"{r['city_id']:<12} {r['num_nodes']:>7} {r['num_edges']:>7} "
              f"{r['area_km2']:>9} {str(r['is_strongly_connected']):>10}")

    target_lo, target_hi = 3000, 8000
    print(f"\nTarget node-count range for this project: {target_lo}-{target_hi}")
    for r in results:
        if not (target_lo <= r["num_nodes"] <= target_hi):
            print(f"  NOTE: {r['city_id']} has {r['num_nodes']} nodes — "
                  f"outside target range, may want to widen/narrow the query area.")


if __name__ == "__main__":
    main()
