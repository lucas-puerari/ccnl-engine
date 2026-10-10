"""Observed payslips: well formed and internally consistent.

``tests/fixtures/observed_payslips/`` holds transcriptions of payslips that
workers published online.  They are evidence of how real payrolls apply
the rules, never a signed source: no record identifies a person, an
employer or a bank account, and every amount is copied as printed.
"""

from __future__ import annotations

import json
import re
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "observed_payslips"
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


@pytest.mark.parametrize("path", _FILES, ids=lambda p: p.stem)
def test_record_is_well_formed(path: Path) -> None:
    """Each record names itself, its legibility and, when printed, its period."""
    record = _load(path)

    assert record["id"] == path.stem
    assert str(record["legibility"]).split(":")[0] in _LEGIBILITY
    if record.get("period") is not None:
        assert _PERIOD.match(record["period"]), record["period"]


def _amount(value: object) -> Decimal | None:
    if not isinstance(value, str) or value.startswith("("):
        return None
    return Decimal(value)


@pytest.mark.parametrize("path", _FILES, ids=lambda p: p.stem)
def test_net_matches_the_totals(path: Path) -> None:
    """Earnings less deductions give the printed net, within the rounding."""
    record = _load(path)
    totals = record.get("totals") or {}
    earnings = _amount(totals.get("earnings"))
    deductions = _amount(totals.get("deductions"))
    net = _amount(record.get("net"))
    if earnings is None or deductions is None or net is None:
        pytest.skip("the payslip does not print both totals and the net")
    if record.get("totals_reconcile") is False:
        pytest.skip("the printed totals leave items out; the note says which")

    assert abs(earnings - deductions - net) <= _ROUNDING
