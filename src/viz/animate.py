"""
Layer 5 — Time-stepped animation of vehicles moving through the city.

Intended as the demo: a marker per vehicle advancing along its committed route,
with battery level and epoch boundaries visible. Built on an existing map /
animation component rather than a custom renderer.

Lowest priority in the build order. It is the last checkpoint on purpose.
"""

from __future__ import annotations


def animate_epochs(world, epoch_results, out_path):
    """Render the full simulation to an animation artifact. TODO(Checkpoint 7)."""
    raise NotImplementedError
