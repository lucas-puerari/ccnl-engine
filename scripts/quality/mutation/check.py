"""Verify the mutation scores of a campaign and record what they measured.

Two campaigns use it, both reading the per-mutant exit codes mutmut keeps in
``mutants/<path>.meta``:

- the weekly campaign mutates every module of ``[tool.mutmut]
  source_paths``;
- the pull request campaign mutates only the money-moving modules the pull
  request changed.  ``--changed-since REF --print-globs`` prints the mutmut
  name patterns of those modules that yield a mutant (nothing when none
  does: mutmut refuses a filter that matches no mutant), and
  ``--changed-since REF`` then scores those modules alone.

A local run of a few modules (``make mutation MODULE=GLOB``) passes the same
mutmut patterns with ``--modules GLOB``: only the modules with a mutant
matching one of them are scored.

Every module must reach ``--min-score`` on its own, and the core (the
modules without a floor) together: a strong module never hides a weak one.
A module listed in ``baseline.json`` entered the perimeter, or was first
measured alone, below that minimum: it must keep its own floor, so its
score cannot fall, and the floor is raised as tests kill its survivors.

A surviving mutant that no test can kill, because it does not change what
the module computes, is classified in ``equivalent.json`` with the reason:
it counts neither as killed nor as survived.  Nothing else excuses a
survivor.

A score without its perimeter and its date misleads: every check writes
``mutants/mutation-score.json`` with the commit, the UTC date, the minimum,
the modules scored and the counts, and the workflows keep it as an
artifact.  A check whose perimeter is the whole of ``source_paths`` also
writes the versioned record :data:`RECORD`
(``scripts/quality/mutation/record.json``): the last full campaign the
repository vouches for.  A check of fewer modules (``--changed-since`` or
``--modules``) never rewrites it, and its artifact says ``"scope":
"partial"``, so the release dossier, which requires the whole perimeter,
refuses it.

Usage::

    uv run python scripts/quality/mutation/check.py [--min-score FLOAT]
    uv run python scripts/quality/mutation/check.py --changed-since REF \
        --print-globs
    uv run python scripts/quality/mutation/check.py --changed-since REF \
        [--min-score FLOAT]
    uv run python scripts/quality/mutation/check.py --modules GLOB [GLOB ...] \
        [--min-score FLOAT]

Exit codes:
    0   Every score meets its minimum, or no module of the perimeter
        changed.
    1   A score is below its minimum, or the results are missing/malformed.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess  # noqa: S404
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path

from mutmut.mutation.file_mutation import mutate_file_contents

ROOT = Path(__file__).resolve().parents[3]
_MUTANTS = Path("mutants")
_RECORD_PATH = _MUTANTS / "mutation-score.json"
#: Modules that entered the perimeter below the minimum, with their floor.
BASELINE = Path(__file__).with_name("baseline.json")
#: The last campaign of the whole perimeter, versioned with the code.
RECORD = Path(__file__).with_name("record.json")
#: Surviving mutants that change nothing the module computes, with why.
EQUIVALENT = Path(__file__).with_name("equivalent.json")
_DEFAULT_MIN_SCORE = 93.0
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


def has_mutants(module: str, root: Path = ROOT) -> bool:
    """Return whether mutmut generates a mutant for ``module``.

    A module of declarations only (enums, dataclasses without logic) yields
    none, and ``mutmut run`` fails on a filter that matches no mutant.

    Returns:
        ``True`` when mutmut's own generator finds a mutation in the module.
    """
    code = (root / module).read_text(encoding="utf-8")
    return bool(mutate_file_contents(module, code).mutant_names)


def matching_modules(
    globs: tuple[str, ...], perimeter: tuple[str, ...], root: Path = ROOT
) -> tuple[str, ...]:
    """Return the modules of ``perimeter`` a mutmut run filtered by ``globs`` mutates.

    mutmut matches each pattern with :func:`fnmatch.fnmatch` against the
    full mutant name (``ccnl_engine.irpef.rules.x_tax__mutmut_1``); the
    same rule, applied to the mutants mutmut's generator yields, tells
    which modules the run measured.

    Returns:
        The modules with a mutant matching one of ``globs``, in perimeter
        order.
    """
    found: list[str] = []
    for module in perimeter:
        prefix = mutant_glob(module).removesuffix("*")
        code = (root / module).read_text(encoding="utf-8")
        names = mutate_file_contents(module, code).mutant_names
        if any(
            fnmatch.fnmatch(prefix + name, glob) for name in names for glob in globs
        ):
            found.append(module)
    return tuple(found)


def load_equivalent(path: Path = EQUIVALENT) -> dict[str, str]:
    """Return the mutants classified as equivalent, with the reason of each.

    Returns:
        The reason by mutmut mutant name.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    return {str(name): str(reason) for name, reason in data["mutants"].items()}


def module_stats(
    modules: tuple[str, ...],
    mutants: Path = _MUTANTS,
    equivalent: frozenset[str] = frozenset(),
) -> dict[str, int]:
    """Count the mutants of ``modules`` by outcome, from mutmut's results.

    Returns:
        ``killed``, ``survived``, ``other`` (timeout, suspicious, no tests),
        ``not_checked`` and ``equivalent`` (classified, left out of the
        rest); ``total`` counts every other mutant that ran.  A module
        without results raises :class:`FileNotFoundError`.
    """
    codes: list[int | None] = []
    skipped = 0
    for module in modules:
        meta = json.loads((mutants / f"{module}.meta").read_text(encoding="utf-8"))
        for name, code in meta["exit_code_by_key"].items():
            if name in equivalent:
                skipped += 1
            else:
                codes.append(code)
    ran = [code for code in codes if code is not None]
    killed = sum(code in _KILLED for code in ran)
    survived = sum(code == _SURVIVED for code in ran)
    return {
        "killed": killed,
        "survived": survived,
        "other": len(ran) - killed - survived,
        "not_checked": len(codes) - len(ran),
        "equivalent": skipped,
        "total": len(ran),
    }


def record(
    scores: dict[str, dict[str, float]],
    perimeter: tuple[str, ...],
    min_score: float,
    *,
    versioned: bool = False,
) -> dict[str, object]:
    """Write and return what the scores measured, when and where.

    Args:
        scores: The score of the core and of each module with a floor.
        perimeter: The modules scored.
        min_score: The minimum the core was held to.
        versioned: Also write :data:`RECORD`, for a campaign of the whole
            perimeter.

    Returns:
        The record written to ``mutants/mutation-score.json``; its
        ``scope`` is ``full`` when ``perimeter`` is the whole of
        ``source_paths``, else ``partial``.

    Raises:
        ValueError: When ``versioned`` asks to record a partial perimeter
            as the last full campaign.
    """
    full = list(perimeter) == list(source_paths())
    if versioned and not full:
        msg = "only a campaign of the whole source_paths writes record.json"
        raise ValueError(msg)
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    ).stdout.strip()
    entry: dict[str, object] = {
        "commit": commit,
        "date": datetime.now(tz=UTC).date().isoformat(),
        "min_score": min_score,
        "perimeter": list(perimeter),
        "scores": scores,
    }
    _RECORD_PATH.parent.mkdir(exist_ok=True)
    artifact = {**entry, "scope": "full" if full else "partial"}
    _RECORD_PATH.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    if versioned:
        RECORD.write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
    return artifact


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--min-score",
        type=float,
        default=_DEFAULT_MIN_SCORE,
        metavar="FLOAT",
        help=f"Minimum kill rate 0-100 (default: {_DEFAULT_MIN_SCORE}).",
    )
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument(
        "--changed-since",
        metavar="REF",
        help="Score only the modules of the perimeter changed since REF.",
    )
    scope.add_argument(
        "--modules",
        nargs="+",
        metavar="GLOB",
        help="Score only the modules a mutmut run filtered by GLOB mutated.",
    )
    parser.add_argument(
        "--print-globs",
        action="store_true",
        help="With --changed-since, print the mutmut patterns and exit.",
    )
    return parser


def load_floors(path: Path = BASELINE) -> dict[str, float]:
    """Return the minimum score of each module below the general minimum.

    Returns:
        The floor of each module listed in ``baseline.json``.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    return {module: float(floor) for module, floor in data["floors"].items()}


def _perimeter(args: argparse.Namespace) -> tuple[str, ...]:
    """Return the modules the arguments ask to score.

    Returns:
        Every module of ``source_paths``, those changed since the ref, or
        those the ``--modules`` patterns match.

    Raises:
        SystemExit: After printing the mutmut patterns with
            ``--print-globs``, or when no module of the perimeter changed
            (with status 0); when no module matches ``--modules`` (with
            status 1).
    """
    if args.modules:
        matched = matching_modules(tuple(args.modules), source_paths())
        if not matched:
            patterns = " ".join(args.modules)
            print(
                f"ERROR: no module of source_paths matches {patterns}.", file=sys.stderr
            )
            raise SystemExit(1)
        return matched
    if args.changed_since is None:
        return source_paths()
    modules = changed_modules(args.changed_since, source_paths())
    if args.print_globs:
        print(" ".join(mutant_glob(m) for m in modules if has_mutants(m)))
        raise SystemExit(0)
    if not modules:
        print(f"No mutated module changed since {args.changed_since}.")
        raise SystemExit(0)
    return modules


def evaluate(
    perimeter: tuple[str, ...],
    floors: dict[str, float],
    min_score: float,
    mutants: Path = _MUTANTS,
    equivalent: frozenset[str] = frozenset(),
) -> tuple[dict[str, dict[str, float]], list[str]]:
    """Score the perimeter: the core together, and every module alone.

    Each module must reach ``min_score``, or its floor when
    ``baseline.json`` lists it; the modules without a floor must also reach
    it together.  A module with no mutant scores nothing and is skipped.

    Returns:
        The counts and score of the core and of each module, and one
        message per failure.
    """
    scores: dict[str, dict[str, float]] = {}
    failures: list[str] = []
    core = tuple(m for m in perimeter if m not in floors)
    groups = [("core", core, min_score)] if core else []
    groups += [(m, (m,), floors.get(m, min_score)) for m in perimeter]
    for name, modules, minimum in groups:
        stats = module_stats(modules, mutants, equivalent)
        if not stats["total"]:
            continue
        score = compute_score(stats)
        scores[name] = {**stats, "score": round(score, 1), "minimum": minimum}
        if score < minimum:
            failures.append(f"{name}: {score:.1f}% is below {minimum:.1f}%")
    return scores, failures


def main() -> None:
    """Entry point.

    Exits with code 1 when a score is below its minimum.
    """
    args = _parser().parse_args()
    perimeter = _perimeter(args)
    try:
        scores, failures = evaluate(
            perimeter,
            load_floors(),
            args.min_score,
            equivalent=frozenset(load_equivalent()),
        )
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as exc:
        print(f"ERROR: cannot read the mutmut results: {exc}", file=sys.stderr)
        sys.exit(1)
    full = list(perimeter) == list(source_paths())
    entry = record(scores, perimeter, args.min_score, versioned=full)
    for name, result in scores.items():
        print(
            f"{name}: {result['score']:.1f}% ({int(result['killed'])} killed / "
            f"{int(result['survived'])} survived / {int(result['total'])} total), "
            f"minimum {result['minimum']:.1f}%"
        )
    print(f"Commit {str(entry['commit'])[:12]}, {entry['date']}.")
    if not full:
        print(
            f"Partial run: {len(perimeter)} of {len(source_paths())} modules; "
            f"{RECORD.name} left unchanged."
        )
    if failures:
        print("FAIL:\n  " + "\n  ".join(failures), file=sys.stderr)
        sys.exit(1)
    print("OK: every score meets its minimum.")


if __name__ == "__main__":
    main()
