"""Enforce source provenance on new reference case fixtures.

Accepts one or more paths to reference case JSON files and exits with code 1
if any file lacks a non-empty ``source`` field at the top level.

Usage::

    python scripts/ci/check_provenance.py tests/reference/cases/foo.json ...

Exit codes:
    0   All supplied files have a non-empty ``source`` field.
    1   One or more files are missing ``source``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def check_files(paths: list[Path]) -> list[Path]:
    """Return the subset of *paths* that lack a non-empty ``source`` field.

    Returns:
        Paths whose JSON top-level object has no ``source`` key or an empty
        ``source`` value.
    """
    missing: list[Path] = []
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: cannot read {path}: {exc}", file=sys.stderr)
            missing.append(path)
            continue
        if not data.get("source"):
            missing.append(path)
    return missing


def main() -> None:
    """Entry point.

    Exits with code 1 when any supplied file lacks ``source``.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        metavar="case_file",
        help="Reference case JSON files to check.",
    )
    args = parser.parse_args()

    missing = check_files(args.files)
    if missing:
        print(
            f"\n{len(missing)} reference case(s) lack a 'source' field:\n"
            + "\n".join(f"  {p}" for p in missing),
            file=sys.stderr,
        )
        print(
            "\nAdd a 'source' block documenting where the expected values "
            "were verified:\n"
            '  "source": {\n'
            '    "url": "https://...",\n'
            '    "description": "CCNL ... — Art. N salary table",\n'
            '    "verified_at": "YYYY-MM-DD"\n'
            "  }",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"OK: {len(args.files)} file(s) checked, all have source.")


if __name__ == "__main__":
    main()
