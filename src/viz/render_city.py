"""
Layer 5 — Static rendering: the road graph, depot, charging stations, orders.

Deliberately lightweight — assembled from existing components, not engineered
(planning decision: RL is where the effort goes). Static plots first, because
they are what the report needs; animation is a demo nicety.
"""

from __future__ import annotations


def plot_city(world, ax=None):
    """Draw the road network with depot and charging stations highlighted."""
    raise NotImplementedError


def plot_routes(world, routes, ax=None):
    """Overlay vehicle routes, drawn along ACTUAL road paths, not straight lines.

    Straight-line overlays would misrepresent the solution — the cost matrix
    stores the real node paths precisely so this can be drawn truthfully.
    """
    raise NotImplementedError
