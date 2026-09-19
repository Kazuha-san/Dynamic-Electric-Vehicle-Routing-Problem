"""
Experiment record-keeping — feeds the final report.

Every training run, benchmark, and design experiment appends a structured record
(config hash, seed, git commit, metrics, notes) to results/logs/. The final
report is then ASSEMBLED FROM RECORDED DATA rather than reconstructed from
memory months later.

Record shape
------------
    timestamp, checkpoint_id, experiment_name, config_hash, seed,
    git_commit, metrics{...}, notes
"""

from __future__ import annotations


def log_experiment(experiment_name: str, config: dict, metrics: dict, notes: str = "") -> None:
    raise NotImplementedError


def load_experiments(filter_by: dict | None = None):
    """Load records for building result tables/plots."""
    raise NotImplementedError
