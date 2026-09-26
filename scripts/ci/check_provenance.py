"""Enforce verification status and provenance on reference case fixtures.

Every case in ``tests/reference/cases/`` declares a top-level ``verification``
field: ``verified``, ``source_linked`` or ``engine_generated``. ``verified``
and ``source_linked`` cases must carry a non-empty ``source`` object.

Modes:

- default (new fixtures): each file must be valid and must not be
  ``engine_generated``; new cases have to cite a source.
- ``--modified``: each file must be valid and must not drop a ``source``
  object it had at ``--base`` (default ``HEAD~1``).
- ``--all``: validate every case in the fixture directory.

Every mode prints the number of checked cases per verification status.
The script uses the standard library only, so CI can run it without
installing the project.

Usage::

    python scripts/ci/check_provenance.py new.json ...
    python scripts/ci/check_provenance.py --modified changed.json ...
    python scripts/ci/check_provenance.py --all

Exit codes:
    0   All checked files pass.
    1   One or more files fail.
"""

from __future__ import annotations

import argparse
import json
import subprocess  # noqa: S404
import sys
from collections import Counter
from pathlib import Path

CASES_DIR = Path(__file__).resolve().parents[2] / "tests" / "reference" / "cases"
STATUSES = ("verified", "source_linked", "engine_generated")
_SOURCED = frozenset({"verified", "source_linked"})


def _parse(text: str) -> dict[str, object] | None:
    data: object = json.loads(text)
    return data if isinstance(data, dict) else None


def _load(path: Path) -> dict[str, object] | None:
    try:
        return _parse(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read {path}: {exc}", file=sys.stderr)
        return None


def _load_at(ref: str, path: Path) -> dict[str, object] | None:
    """Read the case as it was at git ``ref``.

    Returns:
        The decoded case, or ``None`` if it did not exist or was invalid.
    """
    result = subprocess.run(  # noqa: S603
        ["git", "show", f"{ref}:{path.as_posix()}"],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    try:
        return _parse(result.stdout)
    except json.JSONDecodeError:
        return None


def verification_error(case: dict[str, object]) -> str | None:
    """Check the verification status against the ``source`` block.

    Returns:
        The first violated rule, or ``None`` when the case is valid.
    """
    status = case.get("verification")
    if status is None:
        return "missing 'verification' field"
    if status not in STATUSES:
        return f"unknown verification {status!r}; allowed: {list(STATUSES)}"
    source = case.get("source")
    if source is not None and not isinstance(source, dict):
        return "'source' must be a JSON object"
    if status in _SOURCED and not source:
        return f"verification {status!r} requires a non-empty 'source' object"
    return None


def check(
    paths: list[Path], *, mode: str, base: str
) -> tuple[list[tuple[Path, str]], Counter[str]]:
    """Validate ``paths`` under ``mode``.

    Returns:
        ``(failures, counts)``: failing ``(path, reason)`` pairs and the
        number of readable cases per verification status.
    """
    failures: list[tuple[Path, str]] = []
    counts: Counter[str] = Counter()
    for path in paths:
        case = _load(path)
        if case is None:
            failures.append((path, "unreadable or not a JSON object"))
            continue
        counts[str(case.get("verification"))] += 1
        reason = verification_error(case)
        if reason is None and mode == "new" and case["verification"] not in _SOURCED:
            reason = "new cases must cite a source (verified or source_linked)"
        if reason is None and mode == "modified":
            previous = _load_at(base, path)
            if previous and previous.get("source") and not case.get("source"):
                reason = f"lost 'source' object present at {base}"
        if reason is not None:
            failures.append((path, reason))
    return failures, counts


def _print_counts(counts: Counter[str]) -> None:
    total = sum(counts.values())
    print(f"Reference cases checked: {total}")
    for status in STATUSES:
        print(f"  {status}: {counts[status]}")
    other = total - sum(counts[status] for status in STATUSES)
    if other:
        print(f"  invalid or missing: {other}")


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--modified",
        action="store_true",
        help="Check modified fixtures: valid status, no source removed.",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help=f"Check every case in {CASES_DIR}.",
    )
    parser.add_argument(
        "--base",
        default="HEAD~1",
        help="Git ref to compare modified fixtures against (default: HEAD~1).",
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        metavar="case_file",
        help="Reference case JSON files to check.",
    )
    args = parser.parse_args()

    if args.all:
        paths = sorted(CASES_DIR.glob("*.json"))
        mode = "all"
    else:
        if not args.files:
            parser.error("case_file arguments are required unless --all is given")
        paths = args.files
        mode = "modified" if args.modified else "new"

    failures, counts = check(paths, mode=mode, base=args.base)
    _print_counts(counts)

    if failures:
        print(
            f"\n{len(failures)} {mode} reference case(s) failed provenance check:\n"
            + "\n".join(f"  {p}: {reason}" for p, reason in failures),
            file=sys.stderr,
        )
        print(
            "\nEach case needs a top-level 'verification' field. Example:\n"
            '  "verification": "source_linked",\n'
            '  "source": {\n'
            '    "document": "CCNL ...",\n'
            '    "url": "https://...",\n'
            '    "section": "Art. ...",\n'
            '    "notes": "Expected values computed by the engine"\n'
            "  }",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"OK: {len(paths)} {mode} file(s) checked.")


if __name__ == "__main__":
    main()
