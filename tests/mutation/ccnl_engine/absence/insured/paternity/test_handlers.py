"""The compulsory paternity leave, paid on the pay of the month before.

Metalmeccanico Federmeccanica C3 impiegato, 2158.26 EUR a month, daily
quota by 26.  Ten working days of leave, 2-6 and 9-13 March 2026; February
paid 2400.00 with 13 monthly payments a year.  By hand (art. 29 and art. 23
D.Lgs. 151/2001): RMGG (2400 + 2400 / 12) / 30 = 86.666667; INPS indemnity
100% * 86.666667 * 10 = 866.67; deduction 2158.26 * 10 / 26 = 830.10.  On
the pay of the run the indemnity would be 779.37.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.events import InpsSicknessBase, PaternityLeaveEvent
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_HIRED = date(2025, 1, 1)
_DAYS = tuple(date(2026, 3, d) for d in (2, 3, 4, 5, 6, 9, 10, 11, 12, 13))
_FEBRUARY = InpsSicknessBase(Decimal(2400), Decimal(0))


def _run(category: WorkerCategory, base: InpsSicknessBase | None) -> PeriodResult:
    """Return March 2026 with the ten days of leave.

    Returns:
        The result of the run.
    """
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="metalmeccanico-federmeccanica",
                level_code="C3",
                category=category,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=False,
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(
                events=(PaternityLeaveEvent(_DAYS, paternity_base_pay=base),)
            ),
        )
    )


def _amounts(result: PeriodResult) -> dict[str, tuple[str, Decimal]]:
    return {
        i.kind: (i.item_id.rsplit("_", 1)[-1], i.amount)
        for i in result.pay_items
        if "_evt" in i.item_id
    }


def test_ten_days_are_paid_in_full_on_the_month_before() -> None:
    """The deduction at the CCNL quota, the indemnity at 100% of the RMGG."""
    result = _run(WorkerCategory.IMPIEGATO, _FEBRUARY)

    assert _amounts(result) == {
        "absence_deduction": ("abs", Decimal("830.10")),
        "maternity_item": ("inps", Decimal("866.67")),
    }
    (decision,) = (d for d in result.decisions if d.capability == "paternity_leave")
    assert (decision.amount, decision.status) == (Decimal("866.67"), "final")
    assert "paternity_base_pay" not in {b.detail for b in result.blockers}
    assert "paternity_daily_base" not in {lim.id for lim in result.limitations}


def test_without_the_pay_before_a_fact_is_missing() -> None:
    """The base is a fact of the payroll history: its absence blocks."""
    result = _run(WorkerCategory.IMPIEGATO, None)

    assert ("missing_fact", "paternity_base_pay") in {
        (b.code, b.detail) for b in result.blockers
    }
    (issue,) = (i for i in result.issues if i.code == "paternity_base_pay_unknown")
    assert (issue.capability, issue.fact) == ("paternity_leave", "paternity_base_pay")
    assert "PaternityLeaveEvent.paternity_base_pay" in issue.message
    assert _amounts(result)["maternity_item"] == ("inps", Decimal("779.37"))


def test_an_operaio_keeps_the_pay_of_the_run_under_a_limitation() -> None:
    """Art. 23 c. 5 is not computed: the engine says so."""
    result = _run(WorkerCategory.OPERAIO, _FEBRUARY)

    assert "paternity_daily_base" in {lim.id for lim in result.limitations}
    assert _amounts(result)["maternity_item"] == ("inps", Decimal("779.37"))


@pytest.mark.parametrize(
    ("days", "match"),
    [
        ((), "1 to 20 days"),
        (tuple(date(2026, 3, d) for d in range(1, 22)), "1 to 20 days"),
        ((date(2026, 3, 3), date(2026, 3, 2)), "in order, each day once"),
        ((date(2026, 3, 2), date(2026, 3, 2)), "in order, each day once"),
    ],
)
def test_the_days_are_one_to_twenty_in_order(
    days: tuple[date, ...], match: str
) -> None:
    """Art. 27-bis: ten working days, twenty for a multiple birth."""
    with pytest.raises(InvalidInputError, match=match):
        PaternityLeaveEvent(days)
