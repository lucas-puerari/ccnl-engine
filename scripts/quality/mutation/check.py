"""Verify the mutation score of a campaign and record what it measured.

Two campaigns use it:

- the weekly campaign mutates every module of ``[tool.mutmut]
  source_paths`` and reads ``mutants/mutmut-cicd-stats.json`` (written by
  ``mutmut export-cicd-stats``);
- the pull request campaign mutates only the money-moving modules the pull
  request changed.  ``--changed-since REF --print-globs`` prints the mutmut
  name patterns of those modules (nothing when none changed), and
  ``--changed-since REF`` then scores the mutants of those modules alone,
  from the per-mutant exit codes mutmut keeps in ``mutants/<path>.meta``.

A score without its perimeter and its date misleads: every check writes
``mutants/mutation-score.json`` with the commit, the UTC date, the modules
scored and the counts, and the workflows keep it as an artifact.

Usage::

    uv run python scripts/quality/mutation/check.py [--min-score FLOAT]
    uv run python scripts/quality/mutation/check.py --changed-since REF \
        --print-globs
    uv run python scripts/quality/mutation/check.py --changed-since REF \
        [--min-score FLOAT]

Exit codes:
    0   Score meets or exceeds the minimum, or no module of the perimeter
        changed.
    1   Score is below the minimum, or the results are missing/malformed.
"""

from __future__ import annotations

import argparse
import json
import subprocess  # noqa: S404
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
_MUTANTS = Path("mutants")
_STATS_PATH = _MUTANTS / "mutmut-cicd-stats.json"
_RECORD_PATH = _MUTANTS / "mutation-score.json"
_DEFAULT_MIN_SCORE = 90.0
#: Exit codes of a mutant run that kill it (mutmut ``status_by_exit_code``).
_KILLED = frozenset({1, 3})
#: Exit code of a mutant that survived.
_SURVIVED = 0


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


def source_paths(pyproject: Path = ROOT / "pyproject.toml") -> tuple[str, ...]:
    """Return the modules the mutation campaigns mutate.

    Returns:
        The ``[tool.mutmut] source_paths``, relative to the repository.
    """
    config = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    return tuple(config["tool"]["mutmut"]["source_paths"])


def changed_modules(ref: str, perimeter: tuple[str, ...]) -> tuple[str, ...]:
    """Return the modules of ``perimeter`` that changed since ``ref``.

    Returns:
        The changed modules, in perimeter order.
    """
    diff = subprocess.run(  # noqa: S603
        ["git", "diff", "--name-only", f"{ref}...HEAD"],  # noqa: S607
        capture_output=True,
        text=True,
        check=True,
        cwd=ROOT,
    ).stdout.split()
    return tuple(path for path in perimeter if path in diff)


def mutant_glob(module: str) -> str:
    """Return the mutmut name pattern of the mutants of ``module``.

    Returns:
        ``ccnl_engine.irpef.rules.*`` for ``src/ccnl_engine/irpef/rules.py``.
    """
    dotted = module.removeprefix("src/").removesuffix(".py").replace("/", ".")
    return f"{dotted}.*"


def module_stats(modules: tuple[str, ...], mutants: Path = _MUTANTS) -> dict[str, int]:
    """Count the mutants of ``modules`` by outcome, from mutmut's results.

    Returns:
        ``killed``, ``survived``, ``other`` (timeout, suspicious, no tests)
        and ``not_checked``; ``total`` counts every mutant that ran.  A
        module without results raises :class:`FileNotFoundError`.
    """
    codes: list[int | None] = []
    for module in modules:
        meta = json.loads((mutants / f"{module}.meta").read_text(encoding="utf-8"))
        codes.extend(meta["exit_code_by_key"].values())
    ran = [code for code in codes if code is not None]
    killed = sum(code in _KILLED for code in ran)
    survived = sum(code == _SURVIVED for code in ran)
    return {
        "killed": killed,
        "survived": survived,
        "other": len(ran) - killed - survived,
        "not_checked": len(codes) - len(ran),
        "total": len(ran),
    }


def record(
    stats: dict[str, int], perimeter: tuple[str, ...], score: float
) -> dict[str, object]:
    """Write and return what the score measured, when and where.

    Returns:
        The record written to ``mutants/mutation-score.json``.
    """
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    ).stdout.strip()
    entry = {
        "commit": commit,
        "date": datetime.now(tz=UTC).date().isoformat(),
        "perimeter": list(perimeter),
        "score": round(score, 1),
        **stats,
    }
    _RECORD_PATH.parent.mkdir(exist_ok=True)
    _RECORD_PATH.write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
    return entry


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--min-score",
        type=float,
        default=_DEFAULT_MIN_SCORE,
        metavar="FLOAT",
        help=f"Minimum kill rate 0-100 (default: {_DEFAULT_MIN_SCORE}).",
    )
    parser.add_argument(
        "--changed-since",
        metavar="REF",
        help="Score only the modules of the perimeter changed since REF.",
    )
    parser.add_argument(
        "--print-globs",
        action="store_true",
        help="With --changed-since, print the mutmut patterns and exit.",
    )
    return parser


def _campaign(args: argparse.Namespace) -> tuple[dict[str, int], tuple[str, ...]]:
    """Return the counts and perimeter of the campaign the arguments name.

    Returns:
        The counts by outcome and the modules scored.

    Raises:
        SystemExit: When the results are missing or malformed, or when no
            module of the perimeter changed (with status 0).
    """
    if args.changed_since is None:
        if not _STATS_PATH.exists():
            print(
                f"ERROR: {_STATS_PATH} not found. "
                "Run 'uv run mutmut run && uv run mutmut export-cicd-stats' first.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        try:
            stats: dict[str, int] = json.loads(_STATS_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"ERROR: cannot parse {_STATS_PATH}: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
        return stats, source_paths()
    modules = changed_modules(args.changed_since, source_paths())
    if args.print_globs:
        print(" ".join(mutant_glob(m) for m in modules))
        raise SystemExit(0)
    if not modules:
        print(f"No mutated module changed since {args.changed_since}.")
        raise SystemExit(0)
    try:
        return module_stats(modules), modules
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as exc:
        print(f"ERROR: cannot read the mutmut results: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def main() -> None:
    """Entry point.

    Exits with code 1 when the mutation score is below the minimum.
    """
    args = _parser().parse_args()
    stats, perimeter = _campaign(args)
    score = compute_score(stats)
    entry = record(stats, perimeter, score)
    print(
        f"Mutation score: {score:.1f}%  "
        f"({stats.get('killed', 0)} killed / {stats.get('survived', 0)} survived / "
        f"{stats.get('total', 0)} total) on {len(perimeter)} module(s), "
        f"commit {str(entry['commit'])[:12]}, {entry['date']}"
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
