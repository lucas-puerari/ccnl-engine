"""Observed payslips: well formed and internally consistent.

``tests/knowledge/ccnl_engine/period/observed_payslip/`` holds transcriptions
of payslips that workers published online, two worked examples the Cassa
Edile di Vicenza published (p65, p66) and two example payslips of a payroll
package (p67, p68), each with its ``source``; p69 to p74 are payslip images
posted on Reddit that the maintainer collected.  They are
evidence of how real payrolls apply the rules, never a signed source: no
record identifies a person, an employer or a bank account, and every amount
is copied as printed.
"""

from __future__ import annotations

import json
import re
from decimal import Decimal
from pathlib import Path
from typing import Any

_DIR = Path(__file__).resolve().parents[1] / "observed_payslip"
_FILES = sorted(_DIR.glob("*.json"))
_LEGIBILITY = frozenset({
    "full",
    "partial",
    "duplicate",
    "unreadable",
    "not_a_payslip",
})
_PERIOD = re.compile(r"^\d{4}-(\d{2}|\?\?)$")
_ROUNDING = Decimal(1)


def _load(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def test_the_folder_holds_payslips() -> None:
    """The fixture folder is not empty."""
    assert len(_FILES) >= 20


def test_every_record_is_well_formed() -> None:
    """Each record names itself, its legibility and, when printed, its period."""
    wrong = []
    for path in _FILES:
        record = _load(path)
        period = record.get("period")
        if (
            record["id"] != path.stem
            or str(record["legibility"]).split(":")[0] not in _LEGIBILITY
            or (period is not None and not _PERIOD.match(period))
        ):
            wrong.append(path.stem)
    assert wrong == []


def _amount(value: object) -> Decimal | None:
    if not isinstance(value, str) or value.startswith("("):
        return None
    return Decimal(value)


def _gap(path: Path) -> Decimal | None:
    """Return how far earnings less deductions are from the printed net.

    Returns:
        The difference; ``None`` when the payslip does not print both totals
        and the net, or its note says the printed totals leave items out.
    """
    record = _load(path)
    totals = record.get("totals") or {}
    earnings = _amount(totals.get("earnings"))
    deductions = _amount(totals.get("deductions"))
    net = _amount(record.get("net"))
    if earnings is None or deductions is None or net is None:
        return None
    if record.get("totals_reconcile") is False:
        return None
    return abs(earnings - deductions - net)


def test_net_matches_the_totals() -> None:
    """Earnings less deductions give the printed net, within the rounding."""
    gaps = {path.stem: gap for path in _FILES if (gap := _gap(path)) is not None}
    assert gaps, "some payslip prints both totals and the net"
    assert {stem: gap for stem, gap in gaps.items() if gap > _ROUNDING} == {}
