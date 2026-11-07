"""Fail when a test directory does not mirror the code it tests.

The rule of ``tests/README.md``: under ``tests/<category>/ccnl_engine/`` a
directory that holds a test module is a directory of ``src/ccnl_engine/``,
or the directory of one module (``period/services/`` for
``period/services.py``), which holds the tests of that module.  The
directories listed in :data:`EXCEPTIONS` group knowledge tests by theme
and say why; nothing else is allowed.  ``tests/mutation/`` is a category
like the others: it holds the tests mutmut runs (``[tool.mutmut]``).

mutmut kills mutants with ``tests/mutation`` alone, so a test of a module of
``[tool.mutmut] source_paths`` that sits in another category kills none: a
test file named after such a module (``test_rules.py`` or
``test_rules_<x>.py`` next to where ``rules.py`` mirrors, or any test in the
``rules/`` directory of the module) must be under ``tests/mutation``.  The
files listed in :data:`OUTSIDE_MUTATION` stay out, each with its reason.

Usage::

    python scripts/quality/test_tree/check.py

The script uses the standard library only.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path
from typing import Final

__all__ = [
    "EXCEPTIONS",
    "OUTSIDE_MUTATION",
    "ROOT",
    "main",
    "misplaced",
    "outside_mutation",
]

ROOT: Final = Path(__file__).resolve().parents[3]
_CATEGORIES: Final = ("unit", "integration", "knowledge", "mutation")
_MUTATION: Final = "mutation"
#: Test directories that mirror no code, each with its reason.
EXCEPTIONS: Final = {
    "knowledge/boundary": "thresholds and tranches tested across concepts",
    "knowledge/period/sector": "scenarios of the sector tax files, end to end",
    "knowledge/period/validation_packet": "validation packets and their runner",
    "integration/seniority/earned": "seniority earned across runs",
    "integration/year/change": "employment changes inside a competence year",
    "mutation/compensation/afam": "the pay of one public CCNL, end to end",
    "mutation/seniority/fasce": "seniority bands of the CCNL data",
    "mutation/seniority/promotion": "promotions across CCNL levels",
}

#: Tests of a ``source_paths`` module kept out of ``tests/mutation``, with why.
OUTSIDE_MUTATION: Final = {
    "integration/ccnl_engine/assurance/rules/test_assessment_bundle.py": (
        "runs every bundled CCNL end to end; not yet moved to mutation/"
    ),
    "integration/ccnl_engine/assurance/rules/test_assessment_bundle_modes.py": (
        "runs every bundled CCNL in each mode; not yet moved to mutation/"
    ),
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


def _source_paths(root: Path) -> list[str]:
    config = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    return list(config["tool"]["mutmut"]["source_paths"])


def outside_mutation(root: Path = ROOT) -> list[str]:
    """Return the tests of a mutated module that mutmut does not run.

    A test file outside ``tests/mutation`` mirrors a module of
    ``[tool.mutmut] source_paths`` when it is named after it
    (``x/test_rules.py``, ``x/test_rules_<y>.py``) or sits in its directory
    (``x/rules/test_*.py``).  The files of :data:`OUTSIDE_MUTATION` are not
    reported.

    Returns:
        One ``<category>/ccnl_engine/<path>`` per file, sorted.
    """
    found: set[str] = set()
    for module in _source_paths(root):
        rel = Path(module).relative_to("src/ccnl_engine")
        for category in _CATEGORIES:
            if category == _MUTATION:
                continue
            base = root / "tests" / category / "ccnl_engine" / rel.parent
            tests = [
                *base.glob(f"test_{rel.stem}.py"),
                *base.glob(f"test_{rel.stem}_*.py"),
                *(base / rel.stem).glob("test_*.py"),
            ]
            for test in tests:
                name = test.relative_to(root / "tests").as_posix()
                if name not in OUTSIDE_MUTATION:
                    found.add(name)
    return sorted(found)


def main() -> int:
    """Print the misplaced test directories and the tests mutmut misses.

    Returns:
        1 when any is found, else 0.
    """
    found = misplaced()
    for name in found:
        print(f"{name}: mirrors no directory or module of src/ccnl_engine")
    missed = outside_mutation()
    for name in missed:
        print(f"{name}: tests a mutated module: move it to mutation/")
    return 1 if found or missed else 0


if __name__ == "__main__":
    sys.exit(main())
