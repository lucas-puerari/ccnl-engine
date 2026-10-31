"""The partial-month rule a run reads from the bundled CCNL data."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.compensation.proration.services import (
    FULL_MONTH,
    HOURS_UNKNOWN,
    MONTH_NOT_WORKED,
    PAID_BY_THE_HOUR,
    POSTED_BY_ANOTHER_RUN,
    PRORATED,
    RULE_MISSING,
    run_proration,
)
from ccnl_engine.decision.models import CalculationStatus
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.fact.inputs import (
    ContributableHours,
    WeeklyHours,
    WorkPattern,
)
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.run.models import PayrollRun, RunKind

if TYPE_CHECKING:
    from ccnl_engine.period.requests import PeriodCalculationRequest
    from ccnl_engine.run.models import PayrollRunId

_FEDERMECCANICA = "metalmeccanico-federmeccanica"
_VETRO = "vetro-meccanizzato-assovetro"
_SANITA = "dirigenza-sanitaria-area-sanita-aran"
_EDILIZIA = "edilizia-ance"
_CHAIN = MonthlyPayChain(
    base=Decimal("2158.26"), seniority=Decimal("0.00"), allowances=()
)


def _request(
    started_on: date,
    year: int = 2026,
    month: int = 3,
    closed: tuple[PayrollRunId, ...] = (),
    pattern: WorkPattern | None = None,
) -> PeriodCalculationRequest:
    """Return the fields of a request the proration reads.

    Returns:
        A request of ``year``-``month`` for an employment from ``started_on``,
        opening on a state that closed the runs ``closed``, with the work
        pattern ``pattern``.
    """
    fake = SimpleNamespace(
        employment_period=EmploymentPeriod(started_on=started_on),
        period_id=SimpleNamespace(year=year, month=month),
        opening_state=SimpleNamespace(accrual=SimpleNamespace(competence_runs=closed)),
        work_pattern=pattern,
    )
    return cast("PeriodCalculationRequest", fake)


def test_full_month_keeps_the_monthly_pay() -> None:
    """A month employed from its first day is not prorated."""
    proration = run_proration(
        _request(date(2026, 3, 1)), load_ccnl(_FEDERMECCANICA), RunKind.REGULAR
    )

    assert proration is FULL_MONTH
    assert proration.reason is None
    assert proration.inputs() == {}
    assert proration.issue() is None
    assert proration.apply(_CHAIN) is _CHAIN


@pytest.mark.parametrize("kind", [RunKind.THIRTEENTH, RunKind.FOURTEENTH])
def test_extra_month_runs_keep_their_own_rule(kind: RunKind) -> None:
    """An extra-month run is scaled by its ratei, not by the month's days."""
    proration = run_proration(
        _request(date(2026, 3, 15)), load_ccnl(_FEDERMECCANICA), kind
    )

    assert proration is FULL_MONTH


def test_termination_run_closing_the_month_is_prorated() -> None:
    """Without a closed regular run of March the termination run pays it."""
    proration = run_proration(
        _request(date(2026, 3, 15)), load_ccnl(_FEDERMECCANICA), RunKind.TERMINATION
    )

    assert proration.reason == PRORATED
    assert proration.apply(_CHAIN).base == Decimal("1162.14")


def test_termination_run_after_the_regular_run_posts_no_monthly_pay() -> None:
    """The regular run of March already posted its 14 daily quotas."""
    regular = PayrollRun.regular(2026, 3).identifier
    proration = run_proration(
        _request(date(2026, 3, 15), closed=(regular,)),
        load_ccnl(_FEDERMECCANICA),
        RunKind.TERMINATION,
    )

    assert proration.reason == POSTED_BY_ANOTHER_RUN
    assert proration.inputs() == {"monthly_pay_posted_by": "2026-03-regular"}
    assert proration.apply(_CHAIN).base == Decimal("0.00")
    assert proration.issue() is None


def test_adjustment_run_posts_no_monthly_pay() -> None:
    """An adjustment corrects a closed run, which posted the monthly pay."""
    proration = run_proration(
        _request(date(2020, 1, 1)), load_ccnl(_FEDERMECCANICA), RunKind.ADJUSTMENT
    )

    assert proration.reason == POSTED_BY_ANOTHER_RUN
    assert proration.inputs() == {"monthly_pay_posted_by": "corrected_run"}
    assert proration.apply(_CHAIN).base == Decimal("0.00")


def test_untracked_employment_is_a_full_month() -> None:
    """Without an employment period every month is a full month."""
    fake = SimpleNamespace(
        employment_period=None,
        period_id=SimpleNamespace(year=2026, month=3),
        work_pattern=None,
    )
    proration = run_proration(
        cast("PeriodCalculationRequest", fake),
        load_ccnl(_FEDERMECCANICA),
        RunKind.REGULAR,
    )

    assert proration is FULL_MONTH


def test_federmeccanica_reads_its_absence_rule() -> None:
    """Hired 15 March 2026: 14 twenty-sixths of 2,158.26 is 1,162.14."""
    proration = run_proration(
        _request(date(2026, 3, 15)), load_ccnl(_FEDERMECCANICA), RunKind.REGULAR
    )

    assert proration.reason == PRORATED
    assert [rule for rule, _ in proration.rules] == [
        "ccnl/metalmeccanico-federmeccanica:work_rules.absence_rules"
    ]
    assert proration.source is not None
    assert proration.inputs() == {
        "employed_from": "2026-03-15",
        "employed_until": "2026-03-31",
        "divisor_method": "by_26",
        "payable_days": "14",
        "divisor": Decimal(26),
    }
    assert proration.apply(_CHAIN).base == Decimal("1162.14")


def test_span_worth_a_month_keeps_the_monthly_pay() -> None:
    """Hired Monday 2 March 2026: 26 payable days, the full monthly pay."""
    proration = run_proration(
        _request(date(2026, 3, 2)), load_ccnl(_FEDERMECCANICA), RunKind.REGULAR
    )

    assert proration.reason == PRORATED
    assert proration.apply(_CHAIN) is _CHAIN


def test_ccnl_without_rule_pays_nothing_and_raises_an_issue() -> None:
    """The vetro CCNL records no daily divisor: the month is undetermined."""
    proration = run_proration(
        _request(date(2026, 3, 15)), load_ccnl(_VETRO), RunKind.REGULAR
    )
    issue = proration.issue()

    assert proration.reason == RULE_MISSING
    assert proration.rules == ()
    assert proration.apply(_CHAIN).base == Decimal("0.00")
    assert proration.inputs()["payable_days"] == "none"
    assert issue is not None
    assert issue.code == RULE_MISSING
    assert issue.status is CalculationStatus.INCOMPLETE
    assert issue.fact is None


def test_hourly_rule_reads_the_hourly_divisor() -> None:
    """16-30 April 2026: 11 weekdays of 7.6 hours over 165 monthly hours."""
    proration = run_proration(
        _request(date(2026, 4, 16), month=4), load_ccnl(_SANITA), RunKind.REGULAR
    )

    assert proration.proration is not None
    assert proration.proration.method is DailyDivisorMethod.BY_HOURLY
    assert proration.proration.units == Decimal("83.6")
    assert [rule for rule, _ in proration.rules] == [
        "ccnl/dirigenza-sanitaria-area-sanita-aran:work_rules.absence_rules",
        "ccnl/dirigenza-sanitaria-area-sanita-aran:hourly_divisor[2019-12-19]",
    ]


def test_hourly_rule_before_the_divisor_series_is_missing() -> None:
    """The hourly divisor starts on 19 December 2019: no quota before it."""
    proration = run_proration(
        _request(date(2019, 6, 16), year=2019, month=6),
        load_ccnl(_SANITA),
        RunKind.REGULAR,
    )

    assert proration.reason == RULE_MISSING
    assert proration.rules[-1] == (
        "ccnl/dirigenza-sanitaria-area-sanita-aran:hourly_divisor",
        None,
    )


def _hourly_request(
    started_on: date,
    hours: Decimal | None,
    weekly: int | None = None,
) -> PeriodCalculationRequest:
    """Return the fields of a March 2026 request of a worker paid by the hour.

    Returns:
        A request with the ordinary hours worked and the weekly hours.
    """
    fake = SimpleNamespace(
        employment_period=EmploymentPeriod(started_on=started_on),
        period_id=SimpleNamespace(year=2026, month=3),
        opening_state=SimpleNamespace(accrual=SimpleNamespace(competence_runs=())),
        ordinary_hours_worked=None if hours is None else ContributableHours(hours),
        weekly_hours=None if weekly is None else WeeklyHours(Decimal(weekly)),
        full_time_weekly_hours=None if weekly is None else WeeklyHours(Decimal(40)),
        events=(),
        work_pattern=None,
    )
    return cast("PeriodCalculationRequest", fake)


def test_operaio_is_paid_the_hours_worked() -> None:
    """Edilizia operaio, 160 hours: 2,158.26 x 160 / 173 = 1,996.08."""
    proration = run_proration(
        _hourly_request(date(2020, 1, 1), Decimal(160)),
        load_ccnl(_EDILIZIA),
        RunKind.REGULAR,
        WorkerCategory.OPERAIO,
    )

    assert proration.reason == PAID_BY_THE_HOUR
    assert not proration.missing
    assert proration.issue() is None
    assert proration.inputs() == {
        "ordinary_hours_worked": Decimal(160),
        "hourly_divisor": Decimal(173),
    }
    assert [rule for rule, _ in proration.rules] == [
        "ccnl/edilizia-ance:hourly_pay",
        "ccnl/edilizia-ance:hourly_divisor[2025-02-01]",
    ]
    assert proration.apply(_CHAIN).base == Decimal("1996.08")


def test_hours_replace_the_days_of_a_partial_month() -> None:
    """Hired 16 March: the 80 hours worked carry the days, not 16 / 26."""
    proration = run_proration(
        _hourly_request(date(2026, 3, 16), Decimal(80)),
        load_ccnl(_EDILIZIA),
        RunKind.TERMINATION,
        WorkerCategory.OPERAIO,
    )

    assert proration.partial
    assert proration.apply(_CHAIN).base == Decimal("998.04")


def test_hours_unknown_pay_nothing_and_name_the_fact() -> None:
    """Without the hours the pay is undetermined: a missing_fact issue."""
    proration = run_proration(
        _hourly_request(date(2020, 1, 1), None),
        load_ccnl(_EDILIZIA),
        RunKind.REGULAR,
        WorkerCategory.OPERAIO,
    )
    issue = proration.issue()

    assert proration.reason == HOURS_UNKNOWN
    assert proration.missing
    assert proration.inputs()["ordinary_hours_worked"] == "none"
    assert proration.apply(_CHAIN).base == Decimal("0.00")
    assert issue is not None
    assert issue.status is CalculationStatus.INCOMPLETE
    assert issue.fact == "ordinary_hours_worked"


def test_part_time_divides_by_the_part_time_hours() -> None:
    """20 of 40 weekly hours: the halved chain over 86.5 pays the full rate."""
    proration = run_proration(
        _hourly_request(date(2020, 1, 1), Decimal("86.5"), weekly=20),
        load_ccnl(_EDILIZIA),
        RunKind.REGULAR,
        WorkerCategory.OPERAIO,
    )
    half = MonthlyPayChain(
        base=Decimal("1079.13"), seniority=Decimal("0.00"), allowances=()
    )

    assert proration.inputs()["hourly_divisor"] == Decimal("86.5")
    assert proration.apply(half).base == Decimal("1079.13")


@pytest.mark.parametrize(
    ("kind", "category"),
    [
        (RunKind.REGULAR, WorkerCategory.IMPIEGATO),
        (RunKind.REGULAR, None),
        (RunKind.THIRTEENTH, WorkerCategory.OPERAIO),
    ],
    ids=["other_category", "unknown_category", "extra_month"],
)
def test_other_workers_and_runs_are_paid_by_the_month(
    kind: RunKind, category: WorkerCategory | None
) -> None:
    """Only the hourly category, on a run posting the monthly pay, is hourly."""
    proration = run_proration(
        _hourly_request(date(2020, 1, 1), Decimal(160)),
        load_ccnl(_EDILIZIA),
        kind,
        category,
    )

    assert proration is FULL_MONTH


_JANUARY_TO_JUNE = WorkPattern(months=frozenset(range(1, 7)))


@pytest.mark.parametrize("kind", [RunKind.REGULAR, RunKind.TERMINATION])
def test_a_month_not_worked_posts_no_monthly_pay(kind: RunKind) -> None:
    """A vertical part time worked January to June is paid nothing in July."""
    request = _request(date(2026, 1, 1), month=7, pattern=_JANUARY_TO_JUNE)
    proration = run_proration(request, load_ccnl(_FEDERMECCANICA), kind)

    assert proration.idle
    assert not proration.posts_pay
    assert proration.reason == MONTH_NOT_WORKED
    assert proration.inputs() == {"month_worked": "false"}
    assert proration.issue() is None
    assert not proration.missing
    assert proration.apply(_CHAIN).base == Decimal("0.00")


def test_a_month_worked_is_a_full_month() -> None:
    """In a month of the pattern the monthly pay is posted in full."""
    request = _request(date(2026, 1, 1), month=6, pattern=_JANUARY_TO_JUNE)
    assert run_proration(request, load_ccnl(_FEDERMECCANICA), RunKind.REGULAR) == (
        FULL_MONTH
    )


def test_an_extra_month_run_is_not_idle() -> None:
    """The tredicesima paid in a month not worked keeps its own chain."""
    request = _request(date(2026, 1, 1), month=12, pattern=_JANUARY_TO_JUNE)
    proration = run_proration(request, load_ccnl(_FEDERMECCANICA), RunKind.THIRTEENTH)
    assert proration == FULL_MONTH
