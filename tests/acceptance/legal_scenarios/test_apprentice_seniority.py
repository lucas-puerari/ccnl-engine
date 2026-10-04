"""Apprentice seniority: the CCNL apprentice amount is paid in full.

CCNL Acconciatura Estetica Confartigianato, 2024 renewal Art. 25 (see the
coverage note of the bundle): apprentices mature a scatto of EUR 6.00 of
their own from 2024-10-01, every 24 months, at most five.  The amount is
already the apprentice one, so the apprenticeship percentage of the track
does not reduce it a second time.

Regular run of March 2026, level 3, track ``gruppo_1`` at month 0 (70%),
48 months of recognised seniority on 2026-03-01:

- minimo 1472.00 x 0.70 = 1030.40;
- seniority 2 scatti x 6.00 = 12.00, not 12.00 x 0.70 = 8.40.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Employment
from ccnl_engine.inputs import Apprentice, SeniorityFact, SenioritySource
from tests.acceptance.legal_scenarios._support import regular_period

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario

_D = Decimal


def _run() -> PeriodResult:
    return regular_period(
        month=3,
        employment=Employment(
            ccnl_slug="acconciatura-estetica-confartigianato.json",
            level_code="3",
            contract_type=Apprentice(months_elapsed=0, track="gruppo_1"),
            seniority=SeniorityFact(48, date(2026, 3, 1), SenioritySource.PAYSLIP),
        ),
    )


def _amount(result: PeriodResult, kind: str) -> Decimal:
    (item,) = (i for i in result.pay_items if i.kind == kind)
    return item.amount


def test_apprentice_amount_is_not_reduced_by_the_percentage() -> None:
    """The base is 70% of the minimo; the two apprentice scatti are paid in full."""
    result = _run()
    assert _amount(result, "base_salary_earning") == _D("1030.40")
    assert _amount(result, "seniority_earning") == _D("12.00")


def test_scaling_decision_lists_the_seniority_as_unscaled() -> None:
    """The apprenticeship decision says the seniority was paid at full value."""
    (decision,) = (
        d for d in _run().decisions if d.capability == "apprenticeship_scaling"
    )
    assert decision.inputs["scaled"] == "base_salary"
    assert decision.inputs["unscaled"] == "seniority"
