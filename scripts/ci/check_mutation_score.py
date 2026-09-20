"""Verify the mutation score meets the agreed minimum threshold.

Reads ``mutants/mutmut-cicd-stats.json`` (written by ``mutmut export-cicd-stats``)
and exits with code 1 when the kill rate falls below the configured minimum.

Usage::

    uv run python scripts/ci/check_mutation_score.py [--min-score FLOAT]

Options:
    --min-score FLOAT   Minimum acceptable kill rate 0-100 (default: 90.0).

Exit codes:
    0   Score meets or exceeds the minimum.
    1   Score is below the minimum, or the stats file is missing/malformed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_STATS_PATH = Path("mutants/mutmut-cicd-stats.json")
_DEFAULT_MIN_SCORE = 90.0


def compute_score(stats: dict[str, int]) -> float:
    """Return the kill rate as a percentage (0-100).

    Returns:
        Kill rate: ``killed / total * 100``.  Returns 0.0 when ``total`` is 0
        so a campaign with no mutants doesn't accidentally pass.
    """
    total = stats.get("total", 0)
    if total == 0:
        return 0.0
    return stats["killed"] / total * 100.0


def main() -> None:
    """Entry point.

    Exits with code 1 when the mutation score is below the minimum.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--min-score",
        type=float,
        default=_DEFAULT_MIN_SCORE,
        metavar="FLOAT",
        help=f"Minimum kill rate 0-100 (default: {_DEFAULT_MIN_SCORE}).",
    )
    args = parser.parse_args()

    if not _STATS_PATH.exists():
        print(
            f"ERROR: {_STATS_PATH} not found. "
            "Run 'uv run mutmut run && uv run mutmut export-cicd-stats' first.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        stats: dict[str, int] = json.loads(_STATS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: cannot parse {_STATS_PATH}: {exc}", file=sys.stderr)
        sys.exit(1)

    score = compute_score(stats)
    total = stats.get("total", 0)
    killed = stats.get("killed", 0)
    survived = stats.get("survived", 0)

    print(
        f"Mutation score: {score:.1f}%  "
        f"({killed} killed / {survived} survived / {total} total)"
    )

    if score < args.min_score:
        print(
            f"FAIL: score {score:.1f}% is below the minimum {args.min_score:.1f}%.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"OK: score {score:.1f}% >= minimum {args.min_score:.1f}%.")


if __name__ == "__main__":
    main()
