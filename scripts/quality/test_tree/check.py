"""Fail when a test directory does not mirror the code it tests.

The rule of ``tests/README.md``: under ``tests/<category>/ccnl_engine/`` a
directory that holds a test module is a directory of ``src/ccnl_engine/``,
or the directory of one module (``period/services/`` for
``period/services.py``), which holds the tests of that module.  The
directories listed in :data:`EXCEPTIONS` group knowledge tests by theme
and say why; nothing else is allowed.

Usage::

    python scripts/quality/test_tree/check.py

The script uses the standard library only.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Final

__all__ = ["EXCEPTIONS", "ROOT", "main", "misplaced"]

ROOT: Final = Path(__file__).resolve().parents[3]
_CATEGORIES: Final = ("unit", "integration", "knowledge")
#: Test directories that mirror no code, each with its reason.
EXCEPTIONS: Final = {
    "knowledge/boundary": "thresholds and tranches tested across concepts",
    "knowledge/compensation/afam": "the pay of one public CCNL, end to end",
    "knowledge/period/sector": "scenarios of the sector tax files, end to end",
    "knowledge/period/validation_packet": "validation packets and their runner",
    "knowledge/seniority/fasce": "seniority bands of the CCNL data",
    "knowledge/seniority/promotion": "promotions across CCNL levels",
    "integration/seniority/earned": "seniority earned across runs",
    "integration/year/change": "employment changes inside a competence year",
}


def misplaced(root: Path = ROOT) -> list[str]:
    """Return the test directories that mirror no code and are not exceptions.

    Returns:
        One ``<category>/<path>`` per directory, sorted.
    """
    src = root / "src" / "ccnl_engine"
    found: set[str] = set()
    for category in _CATEGORIES:
        base = root / "tests" / category / "ccnl_engine"
        for test in base.rglob("test_*.py"):
            rel = test.parent.relative_to(base)
            mirrored = (
                rel == Path()
                or (src / rel).is_dir()
                or (src / rel).with_suffix(".py").is_file()
            )
            name = f"{category}/{rel.as_posix()}"
            if not mirrored and name not in EXCEPTIONS:
                found.add(name)
    return sorted(found)


def main() -> int:
    """Print the misplaced test directories.

    Returns:
        1 when any is found, else 0.
    """
    found = misplaced()
    for name in found:
        print(f"{name}: mirrors no directory or module of src/ccnl_engine")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
