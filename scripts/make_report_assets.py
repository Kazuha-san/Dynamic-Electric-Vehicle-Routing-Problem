"""
Checkpoint 7 entry point — build figures and tables for the final report.

Reads recorded experiments from results/logs/ and emits publication-ready
assets into results/figures/ and results/tables/. Nothing is recomputed here;
if a number is not in the log, it does not go in the report.
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--logs", default="results/logs")
    args = parser.parse_args()
    raise NotImplementedError("Checkpoint 7")


if __name__ == "__main__":
    main()
