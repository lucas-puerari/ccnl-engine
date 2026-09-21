"""Enforce source provenance on reference case fixtures.

New fixtures (``--new`` mode, default) must have a ``source`` dict with
``verification_status``.  Modified fixtures (``--modified`` mode) must
retain a non-empty ``source`` dict.

Usage::

    python scripts/ci/check_provenance.py new.json ...
    python scripts/ci/check_provenance.py --modified changed.json ...

Exit codes:
    0   All supplied files pass the applicable checks.
    1   One or more files fail.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_NEW_REQUIRED_FIELDS = ("verification_status",)


def _load(path: Path) -> dict[str, object] | None:
    try:
        data: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read {path}: {exc}", file=sys.stderr)
        return None
    else:
        return data


def check_new(paths: list[Path]) -> list[tuple[Path, str]]:
    """Return (path, reason) pairs that fail the new-fixture checks.

    New fixtures must have a ``source`` dict that includes
    ``verification_status``.

    Returns:
        List of ``(path, reason)`` for each failing file.
    """
    failures: list[tuple[Path, str]] = []
    for path in paths:
        data = _load(path)
        if data is None:
            failures.append((path, "unreadable"))
            continue
        src = data.get("source")
        if not src:
            failures.append((path, "missing 'source' field"))
            continue
        if not isinstance(src, dict):
            failures.append((path, "'source' must be a JSON object"))
            continue
        missing = [f for f in _NEW_REQUIRED_FIELDS if not src.get(f)]
        if missing:
            failures.append((path, f"'source' missing required fields: {missing}"))
    return failures


def check_modified(paths: list[Path]) -> list[tuple[Path, str]]:
    """Return (path, reason) pairs that lost their ``source`` field.

    Modified fixtures that previously had a source must not remove it.

    Returns:
        List of ``(path, reason)`` for each failing file.
    """
    failures: list[tuple[Path, str]] = []
    for path in paths:
        data = _load(path)
        if data is None:
            failures.append((path, "unreadable"))
            continue
        if not data.get("source"):
            failures.append((path, "lost 'source' field on modification"))
    return failures


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--modified",
        action="store_true",
        help="Check modified fixtures (looser rules — only requires source present).",
    )
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        metavar="case_file",
        help="Reference case JSON files to check.",
    )
    args = parser.parse_args()

    if args.modified:
        failures = check_modified(args.files)
        mode = "modified"
    else:
        failures = check_new(args.files)
        mode = "new"

    if failures:
        print(
            f"\n{len(failures)} {mode} reference case(s) failed provenance check:\n"
            + "\n".join(f"  {p}: {reason}" for p, reason in failures),
            file=sys.stderr,
        )
        if not args.modified:
            print(
                "\nNew fixtures must include a 'source' dict with "
                "'verification_status'. Example:\n"
                '  "source": {\n'
                '    "type": "official_ccnl",\n'
                '    "document_id": "CCNL ...",\n'
                '    "effective_date": "YYYY-MM-DD",\n'
                '    "reviewed_by": "name@example.com",\n'
                '    "verified_at": "YYYY-MM-DD",\n'
                '    "verification_status": "unverified"\n'
                "  }",
                file=sys.stderr,
            )
        sys.exit(1)

    print(f"OK: {len(args.files)} {mode} file(s) checked.")


if __name__ == "__main__":
    main()
