"""Bundled sugar award: 1,204.74 + 515.31 + 10.33 + 65.70 = EUR 1,796.08.

The 25-year clerical award is EUR 1,796.08; the manual award is
200 x 1,796.08 / 174 = EUR 2,064.46, rounded to cents (punto 14, PDF p.
212: the normal hourly pay is the monthly one over 174, not the 173 of
Art. 51).  The preceding month and the other food-industry branches pay
EUR 0.  This monthly chain is an approximation of normal pay, not an
additional source wage table.

An employment ending before 25 years by death or permanent incapacity
settles the ratei of 8 hours (operai) or 7 hours (impiegati) a whole year
(punto 25, second paragraph, PDF p. 230).
"""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.decision.models import CalculationStatus
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.period.inputs import EmploymentPeriod, TerminationCause
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.models import PayrollRun, RunKind
from ccnl_engine.run.types import PeriodId


def _run(category: WorkerCategory, subsector: str, month: int) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(20), subsector=subsector),
            period_id=PeriodId(2026, month),
            payment_date=date(2026, month, 27),
            ccnl_id="alimentari-federalimentare",
            level_code="6",
            category=category,
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            events=(),
            employment_period=EmploymentPeriod(started_on=date(2001, 4, 15)),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )


@pytest.mark.parametrize(
    ("category", "expected"),
    [
        (WorkerCategory.IMPIEGATO, Decimal("1796.08")),
        (WorkerCategory.OPERAIO, Decimal("2064.46")),
    ],
)
def test_sugar_award_on_twenty_fifth_anniversary(
    category: WorkerCategory, expected: Decimal
) -> None:
    """At EUR 1,796.08 normal pay, award EUR 1,796.08 or 200/174 times it."""
    april = _run(category, "saccarifero", 4)
    march = _run(category, "saccarifero", 3)
    other = _run(category, "carni", 4)
    assert [
        item.amount for item in april.pay_items if item.kind == "bonus_earning"
    ] == [expected]
    assert not [item for item in march.pay_items if item.kind == "bonus_earning"]
    assert not [item for item in other.pay_items if item.kind == "bonus_earning"]


def _end(
    category: WorkerCategory,
    cause: TerminationCause | None,
    *,
    incapacity: bool | None = None,
    started: date = date(2001, 4, 15),
    service_from: date | None = None,
    ended: date = date(2026, 3, 31),
    run_month: int | None = None,
) -> PeriodResult:
    month = ended.month if run_month is None else run_month
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(20), subsector="saccarifero"),
            period_id=PeriodId(ended.year, month),
            payment_date=date(ended.year, month, 27),
            ccnl_id="alimentari-federalimentare",
            level_code="6",
            category=category,
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            events=(),
            employment_period=EmploymentPeriod(
                started_on=started,
                uninterrupted_service_started_on=service_from,
                ended_on=ended,
                ended_by=cause,
                permanent_incapacity=incapacity,
            ),
            run=PayrollRun(run_kind=RunKind.TERMINATION, year=ended.year, month=month),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )


def _bonus(result: PeriodResult) -> list[Decimal]:
    return [i.amount for i in result.pay_items if i.kind == "bonus_earning"]


@pytest.mark.parametrize(
    ("category", "expected"),
    [
        (WorkerCategory.OPERAIO, Decimal("1981.88")),
        (WorkerCategory.IMPIEGATO, Decimal("1734.15")),
    ],
)
def test_death_before_25_years_settles_the_whole_years(
    category: WorkerCategory, expected: Decimal
) -> None:
    """15 April 2001 to 31 March 2026: 24 whole years, not 25.

    Operai 24 x 8 = 192 hours x 1,796.08 / 174 = 1,981.88; impiegati
    24 x 7 = 168 hours = 1,734.15.
    """
    result = _end(category, TerminationCause.DEATH)
    assert _bonus(result) == [expected]
    (decision,) = (
        d for d in result.decisions if d.reason_code == "loyalty_early_ratei"
    )
    assert decision.inputs == {
        "whole_years": "24",
        "hours": "8" if category is WorkerCategory.OPERAIO else "7",
    }


def test_permanent_incapacity_settles_as_death() -> None:
    """A dismissal for permanent incapacity pays the same ratei."""
    result = _end(WorkerCategory.OPERAIO, TerminationCause.DISMISSAL, incapacity=True)
    assert _bonus(result) == [Decimal("1981.88")]


@pytest.mark.parametrize(
    ("cause", "incapacity"),
    [
        (TerminationCause.RESIGNATION, False),
        (TerminationCause.DISMISSAL, False),
    ],
)
def test_another_end_settles_nothing(cause: TerminationCause, incapacity: bool) -> None:
    """A resignation or a dismissal for another reason pays no ratei."""
    assert _bonus(_end(WorkerCategory.OPERAIO, cause, incapacity=incapacity)) == []


@pytest.mark.parametrize(
    ("cause", "fact"),
    [(None, "ended_by"), (TerminationCause.DISMISSAL, "permanent_incapacity")],
)
def test_an_unstated_cause_blocks(cause: TerminationCause | None, fact: str) -> None:
    """The ratei turn on the cause: unstated, the run names the fact."""
    result = _end(WorkerCategory.OPERAIO, cause)
    assert _bonus(result) == []
    (issue,) = (i for i in result.issues if i.code == f"loyalty_{fact}_unknown")
    assert issue.fact == fact
    assert issue.status is CalculationStatus.INCOMPLETE


@pytest.mark.parametrize(
    ("started", "ended", "run_month"),
    [
        (date(2025, 6, 1), date(2026, 3, 31), None),
        (date(2001, 3, 1), date(2026, 3, 31), None),
        (date(2001, 4, 15), date(2026, 2, 28), 3),
    ],
)
def test_no_ratei_below_one_year_from_25_or_in_another_month(
    started: date, ended: date, run_month: int | None
) -> None:
    """No whole year, 25 years reached, or a run of another month.

    The award is due at 25 years instead; a March run does not settle an
    employment that ended in February.
    """
    result = _end(
        WorkerCategory.OPERAIO,
        TerminationCause.DEATH,
        started=started,
        ended=ended,
        run_month=run_month,
    )
    assert _bonus(result) == []


def test_the_service_start_counts_the_transferred_years() -> None:
    """Hired in 2010 after a direct transfer: 24 whole years.

    The caller states the uninterrupted service start of 15 April 2001.
    """
    result = _end(
        WorkerCategory.OPERAIO,
        TerminationCause.DEATH,
        started=date(2010, 4, 15),
        service_from=date(2001, 4, 15),
    )
    assert _bonus(result) == [Decimal("1981.88")]


def test_permanent_incapacity_is_a_bool() -> None:
    """Any other value is rejected."""
    with pytest.raises(InvalidInputError, match="permanent_incapacity"):
        EmploymentPeriod(started_on=date(2001, 4, 15), permanent_incapacity="yes")  # type: ignore[arg-type]


def test_no_hourly_pay_settles_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without a divisor the hours have no value: nothing is posted."""
    monkeypatch.setattr(
        "ccnl_engine.compensation.loyalty.termination._hourly_pay",
        lambda *_: None,
    )
    assert _bonus(_end(WorkerCategory.OPERAIO, TerminationCause.DEATH)) == []
