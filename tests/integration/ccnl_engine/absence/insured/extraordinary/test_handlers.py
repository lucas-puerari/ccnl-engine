"""The extraordinary leave, paid by INPS on the last pay up to a yearly maximum.

Metalmeccanico Federmeccanica C3 impiegato, 2158.26 EUR a month, 13 monthly
payments a year.  By hand (art. 42 c. 5-ter D.Lgs. 151/2001):

- the whole of March 2026, last pay 2158.26: 2158.26 * 13 / 365 =
  76.869534 a day, below the 2026 maximum of 119.14, for 31 days = 2382.96;
  the whole monthly pay 2158.26 is deducted;
- last pay 4000.00: 142.47 a day, capped at 119.14, 31 days = 3693.34;
- a year the bundle does not list is paid uncapped: 4416.44.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

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
from ccnl_engine.events import ExtraordinaryLeaveEvent, WorkEvent
from ccnl_engine.extra_month.qualification.services import non_accruing_days
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.pay_item.facade import AbsenceDeduction, MaternityItem
from tests.integration.ccnl_engine.year.builders import NextYearRepository

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult

_HIRED = date(2025, 1, 1)


def _run(*events: WorkEvent, year: int = 2026) -> PeriodResult:
    """Return March of ``year`` with ``events``.

    Returns:
        The result of the run.
    """
    engine = (
        PayrollEngine.bundled()
        if year == 2026
        else PayrollEngine(repository=NextYearRepository())
    )
    return engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year, 3),
            payment_date=date(year, 3, 27),
            employment=Employment(
                ccnl_id="metalmeccanico-federmeccanica",
                level_code="C3",
                category=WorkerCategory.IMPIEGATO,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=False,
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(events=events),
        )
    )


def _march(last_pay: Decimal | None, year: int = 2026) -> ExtraordinaryLeaveEvent:
    return ExtraordinaryLeaveEvent(date(year, 3, 1), date(year, 3, 31), last_pay)


def _amounts(result: PeriodResult) -> dict[str, tuple[Decimal, Decimal]]:
    return {
        i.kind: (i.amount, i.absence_days)
        for i in result.pay_items
        if isinstance(i, AbsenceDeduction | MaternityItem)
    }


def _codes(result: PeriodResult) -> set[str]:
    return {i.code for i in result.issues}


def test_a_whole_month_on_the_last_pay() -> None:
    """31 days at 13 monthly payments over 365, the month deducted."""
    result = _run(_march(Decimal("2158.26")))

    assert _amounts(result) == {
        "absence_deduction": (Decimal("2158.26"), Decimal(26)),
        "maternity_item": (Decimal("2382.96"), Decimal(31)),
    }
    assert {i.item_id.rsplit("_", 1)[-1] for i in result.pay_items} >= {"abs", "inps"}
    (decision,) = (d for d in result.decisions if d.capability == "extraordinary_leave")
    assert (decision.amount, decision.status) == (Decimal("2382.96"), "final")
    assert "extraordinary_leave_daily_base" in {lim.id for lim in result.limitations}
    assert "inps_minimum_base_undetermined" not in _codes(result)


def test_the_daily_maximum_of_the_year_caps_the_indemnity() -> None:
    """2026: 119.14 a day."""
    result = _run(_march(Decimal(4000)))

    assert _amounts(result)["maternity_item"] == (Decimal("3693.34"), Decimal(31))
    assert "extraordinary_leave_ceiling_unknown" not in _codes(result)


def test_a_year_without_a_maximum_is_paid_uncapped() -> None:
    """The bundle lists no maximum of 2027: the run says so."""
    result = _run(_march(Decimal(4000), 2027), year=2027)

    assert _amounts(result)["maternity_item"] == (Decimal("4416.44"), Decimal(31))
    (issue,) = (
        i for i in result.issues if i.code == "extraordinary_leave_ceiling_unknown"
    )
    assert (issue.status, "for 2027:" in issue.message) == ("provisional", True)


def test_without_the_last_pay_a_fact_is_missing() -> None:
    """The run takes its own monthly pay meanwhile."""
    result = _run(_march(None))

    (issue,) = (i for i in result.issues if i.fact == "last_fixed_pay")
    assert (issue.code, issue.capability) == (
        "extraordinary_last_pay_unknown",
        "extraordinary_leave",
    )
    assert _amounts(result)["maternity_item"] == (Decimal("2382.96"), Decimal(31))


def test_the_leave_accrues_no_13th_no_leave_and_no_tfr() -> None:
    """Art. 42 c. 5-quinquies."""
    leave = _march(Decimal("2158.26"))
    worked, away = _run(), _run(leave)

    assert non_accruing_days((leave,)) == frozenset(
        date(2026, 3, day) for day in range(1, 32)
    )
    assert away.closing_state.accrual.leave != worked.closing_state.accrual.leave
    (tfr,) = (d.amount for d in away.decisions if d.capability == "tfr")
    assert tfr == Decimal(0)
