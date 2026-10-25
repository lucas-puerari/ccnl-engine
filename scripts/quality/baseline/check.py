"""Fail when a shrink-only baseline grows against the base of a pull request.

Two baselines record debt the repository promises to pay down:

- ``scripts/provenance/readiness/baseline.json``: the outputs each
  production CCNL still misses, per evidence level;
- ``scripts/architecture/baseline.json``: the modules over the size limit,
  with their length.

Their own checks compare them with the tree, so a hand edit that adds an
entry, or raises a length, passes them.  This check compares each baseline
with its version at ``--base`` and fails on growth: a new readiness gap, a
new module, a longer one.  ``--allow-growth`` accepts it; CI passes it only
when the pull request body carries an ``allow-growth:`` line that justifies
the growth.

Usage::

    python scripts/quality/baseline/check.py --base origin/main [--allow-growth]

The script uses the standard library only.
"""

from __future__ import annotations

import argparse
import json
import subprocess  # noqa: S404
import sys
from pathlib import Path
from typing import Any, Final

__all__ = ["READINESS", "SIZE", "main", "readiness_growth", "size_growth"]

#: Baseline of the readiness gaps: level -> CCNL -> missing outputs.
READINESS: Final = "scripts/provenance/readiness/baseline.json"
#: Baseline of the module sizes: path -> physical lines.
SIZE: Final = "scripts/architecture/baseline.json"


Gaps = dict[str, list[str]]


def _readiness_items(data: dict[str, Gaps]) -> set[str]:
    return {
        f"{level} / {ccnl} / {output}"
        for level, gaps in data.items()
        for ccnl, outputs in gaps.items()
        for output in outputs
    }


def readiness_growth(base: dict[str, Gaps], head: dict[str, Gaps]) -> list[str]:
    """Return the readiness gaps ``head`` lists and ``base`` does not.

    Returns:
        One line per new gap.
    """
    added = _readiness_items(head) - _readiness_items(base)
    return [f"{READINESS}: new gap {item}" for item in sorted(added)]


def size_growth(base: dict[str, int], head: dict[str, int]) -> list[str]:
    """Return the modules ``head`` adds to the size baseline or lists longer.

    Returns:
        One line per new or longer module.
    """
    return [
        f"{SIZE}: {module} {base.get(module, 'new')} -> {lines} lines"
        for module, lines in sorted(head.items())
        if lines > base.get(module, 0)
    ]


def _at(ref: str, path: str) -> Any:  # noqa: ANN401
    shown = subprocess.run(  # noqa: S603
        ["git", "show", f"{ref}:{path}"],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    return json.loads(shown.stdout) if shown.returncode == 0 else {}


def main(argv: list[str] | None = None) -> int:
    """Compare both baselines with ``--base``.

    Returns:
        0 when nothing grew or growth is allowed, 1 otherwise.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, help="git ref of the base")
    parser.add_argument("--allow-growth", action="store_true")
    args = parser.parse_args(argv)

    def head(path: str) -> Any:  # noqa: ANN401
        return json.loads(Path(path).read_text(encoding="utf-8"))

    grown = readiness_growth(_at(args.base, READINESS), head(READINESS))
    grown += size_growth(_at(args.base, SIZE), head(SIZE))
    for line in grown:
        print(line)
    if grown and not args.allow_growth:
        print(
            "A shrink-only baseline grew. If intended, justify it with an"
            " 'allow-growth:' line in the pull request body."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
