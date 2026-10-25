"""Fail from 1 December while the next year's statutory data are assumed.

The payroll of January runs on the statutory files of its year: IRPEF and
deductions (``sector``), INPS rates (``contribution``), the surtaxes and the
somma esente.  Until the Budget Law and the INPS circulars are published
those files are carried over and labelled ``assumed``, and a run that reads
them is not payable.  Nothing in the repository changes when December
comes, so this check, run by the weekly freshness job and never by the
merge gate, fails from 1 December of a year while any payable rule of the
next year is ``assumed`` or ``missing``, or a yearly dataset has no file
for it.

Usage::

    python scripts/provenance/statutory/check.py [--today YYYY-MM-DD]

The script reads raw JSON with the standard library only.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Final

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from scripts.provenance.rules import KNOWLEDGE_DIR, PayableRule, inventory

__all__ = ["DATASETS", "gaps", "main"]

#: Statutory datasets with one file, or one file per sector, for each year.
DATASETS: Final = (
    "contribution",
    "sector",
    "surtax/municipal",
    "surtax/regional",
    "tax_credit/somma_esente",
)
#: Month from which the next year's payroll is in sight.
_DECEMBER: Final = 12
_WEAK: Final = frozenset({"assumed", "missing"})


def _files_of(dataset: str, year: int, root: Path) -> list[Path]:
    folder = root / dataset
    return [
        *folder.glob(f"{year}.json"),
        *(folder / str(year)).glob("*.json"),
    ]


def gaps(
    year: int,
    rules: tuple[PayableRule, ...] | None = None,
    root: Path = KNOWLEDGE_DIR,
) -> list[str]:
    """Return what keeps the statutory data of ``year`` from being payable.

    Returns:
        One line per yearly dataset without a file of ``year``, then one per
        file of ``year`` with its count of assumed or missing rules.
    """
    found = inventory(root) if rules is None else rules
    lines = [
        f"{dataset}: no file for {year}"
        for dataset in DATASETS
        if not _files_of(dataset, year, root)
    ]
    prefixes = tuple(f"{dataset}/{year}" for dataset in DATASETS)
    weak = Counter(
        rule.file
        for rule in found
        if rule.file.startswith(prefixes) and rule.status in _WEAK
    )
    lines += [
        f"{file}: {count} assumed or missing rules"
        for file, count in sorted(weak.items())
    ]
    return lines


def main(argv: list[str] | None = None) -> int:
    """Check the statutory data of the next year from 1 December.

    Returns:
        1 when ``--today`` is in December and the next year has gaps, else 0.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--today", type=date.fromisoformat, default=None)
    args = parser.parse_args(argv)
    today = args.today or datetime.now(tz=UTC).date()
    if today.month != _DECEMBER:
        print(f"{today}: the next year's payroll is not in sight yet.")
        return 0
    found = gaps(today.year + 1)
    for line in found:
        print(line)
    if found:
        print(
            f"The January {today.year + 1} payroll would run on assumed "
            "statutory data: source them or accept the blockers."
        )
        return 1
    print(f"The statutory data of {today.year + 1} are sourced.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
