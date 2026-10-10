"""Days without any pay leave the days of the art. 13 TUIR deductions.

AdE circ. 15/E/2007 par. 1.5.1: "i giorni per i quali spetta la detrazione
coincidono con quelli che hanno dato diritto alla retribuzione [...] vanno
sottratti i giorni per i quali non spetta alcuna retribuzione", while
"nessuna riduzione delle detrazioni va effettuata [...] in caso di giornate
di sciopero".

Commercio level 4, March 2026, an absence from 2 to 11 March: 10 days.  As
an aspettativa senza assegni the year counts 365 - 10 = 355 days and the
annual art. 13 deduction is proportioned to them; as a strike the year
keeps 365 days.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.events import AbsenceEvent
from tests.knowledge.ccnl_engine.payroll.support import regular_period
from tests.knowledge.ccnl_engine.payroll.taxation.builders_current_year import (
    employment_only,
)

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario


def _march(no_pay_due: bool | None) -> PeriodResult:
    leave = AbsenceEvent(
        date(2026, 3, 2),
        Decimal(80),
        Decimal("10.00"),
        end_date=date(2026, 3, 11),
        suspends_accrual=False,
        no_pay_due=no_pay_due,
    )
    return regular_period(month=3, events=(leave,), current_year=employment_only())


def _days(result: PeriodResult) -> str:
    (decision,) = [
        d for d in result.decisions if d.capability == "ulteriore_detrazione_lavoro"
    ]
    return str(decision.inputs["eligible_work_days"])


def _work_deduction(result: PeriodResult) -> Decimal:
    (amount,) = [
        c.amount
        for c in result.tax_computation.components
        if c.name == "work_deduction"
    ]
    return amount


def test_unpaid_leave_leaves_the_deduction_days() -> None:
    """355 days, and the art. 13 deduction in 355 365ths of the strike one."""
    leave, strike = _march(True), _march(False)
    assert (_days(leave), _days(strike)) == ("355", "365")
    expected = (_work_deduction(strike) * 355 / 365).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    assert _work_deduction(leave) == expected


def test_unknown_pay_of_the_days_is_a_missing_fact() -> None:
    """The days stay counted and the run names the fact."""
    result = _march(None)
    assert _days(result) == "365"
    (issue,) = [i for i in result.issues if i.code == "deduction_days_unknown"]
    assert issue.fact == "no_pay_due"
    assert not result.is_payable
