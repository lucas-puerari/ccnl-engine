"""A partly employed month pays the CCNL daily quotas of its employed days.

Metalmeccanico Federmeccanica C3 earns 2,158.26 a month until May 2026 and
2,211.43 from June; its daily quota is one twenty-sixth of the monthly pay
(``work_rules.absence_rules``: ``by_26``), counted on the Mondays to
Saturdays the employment covers.  Every expected amount is the monthly pay
times the payable days counted by hand on the 2026 calendar, divided by
26 and rounded to the cent: never the engine output.

Calendar: 1 January 2026 is a Thursday, 1 February and 1 March Sundays,
1 April a Wednesday.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.events import AbsenceEvent, HolidayWorkEvent, SickLeaveEvent
from ccnl_engine.inputs import EmploymentPeriod, WeeklyHours

_ENGINE = PayrollEngine.bundled()
_EMPLOYER = EmployerProfile(headcount=Headcount(50))
_METALMECCANICO = "metalmeccanico-federmeccanica.json"
_MONTHLY = Decimal("2158.26")


def _employment(
    period: EmploymentPeriod,
    *,
    ccnl: str = _METALMECCANICO,
    level: str = "C3",
    weekly_hours: int | None = None,
) -> Employment:
    hours = None if weekly_hours is None else WeeklyHours(weekly_hours)
    return Employment(
        ccnl_slug=ccnl,
        level_code=level,
        employment_period=period,
        weekly_hours=hours,
        full_time_weekly_hours=None if hours is None else WeeklyHours(40),
    )


def _run(
    month: int,
    employment: Employment,
    facts: PeriodFacts | None = None,
) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, month),
            payment_date=date(2026, month, 27),
            employment=employment,
            employer=_EMPLOYER,
            facts=facts or PeriodFacts(),
        )
    )


def _base_salary(result: PeriodResult) -> tuple[str, Decimal | None]:
    (decision,) = [d for d in result.decisions if d.capability == "base_salary"]
    return decision.reason_code, decision.amount


@pytest.mark.parametrize(
    ("month", "period", "expected"),
    [
        pytest.param(
            4, EmploymentPeriod(date(2026, 4, 1)), _MONTHLY, id="hire-first-day"
        ),
        # 31 March, a Tuesday: 1 payable day.
        pytest.param(
            3, EmploymentPeriod(date(2026, 3, 31)), Decimal("83.01"), id="hire-last-day"
        ),
        # 16-21, 23-28, 30-31 March: 14 payable days.
        pytest.param(
            3, EmploymentPeriod(date(2026, 3, 15)), Decimal("1162.14"), id="hire-mid"
        ),
        # Monday 2 March to 31 March: 26 payable days, a whole month.
        pytest.param(
            3, EmploymentPeriod(date(2026, 3, 2)), _MONTHLY, id="hire-first-workday"
        ),
        # 1 April, a Wednesday: 1 payable day.
        pytest.param(
            4,
            EmploymentPeriod(date(2025, 1, 1), date(2026, 4, 1)),
            Decimal("83.01"),
            id="termination-first-day",
        ),
        pytest.param(
            4,
            EmploymentPeriod(date(2025, 1, 1), date(2026, 4, 30)),
            _MONTHLY,
            id="termination-last-day",
        ),
        # 1-15 April without Sundays 5 and 12: 13 payable days.
        pytest.param(
            4,
            EmploymentPeriod(date(2025, 1, 1), date(2026, 4, 15)),
            Decimal("1079.13"),
            id="termination-mid",
        ),
        # 2-7 and 9-14 February: 12 payable days.
        pytest.param(
            2,
            EmploymentPeriod(date(2025, 1, 1), date(2026, 2, 14)),
            Decimal("996.12"),
            id="february-termination",
        ),
        # Monday 2 February to 28 February: 24 payable days, not 26.
        pytest.param(
            2,
            EmploymentPeriod(date(2026, 2, 2)),
            Decimal("1992.24"),
            id="february-hire",
        ),
    ],
)
def test_hire_and_termination_months_pay_daily_quotas(
    month: int, period: EmploymentPeriod, expected: Decimal
) -> None:
    """The month pays ``2,158.26 x payable days / 26``, at most the month."""
    result = _run(month, _employment(period))

    assert result.period_gross == expected
    assert _base_salary(result)[1] == expected


def test_prorated_month_names_its_rule() -> None:
    """A prorated month records its reason; a full month keeps the usual one."""
    partial = _run(3, _employment(EmploymentPeriod(date(2026, 3, 15))))
    full = _run(4, _employment(EmploymentPeriod(date(2026, 3, 15))))

    assert _base_salary(partial)[0] == "pay_chain_prorated"
    assert _base_salary(full)[0] == "pay_chain_applied"
    assert "partial_month_rule_missing" not in {i.code for i in partial.issues}


def test_part_time_pays_its_share_of_the_full_time_gross() -> None:
    """20 of 40 weekly hours: half of 2,158.26 is 1,079.13."""
    full_time = _run(1, _employment(EmploymentPeriod(date(2025, 1, 1))))
    part_time = _run(
        1, _employment(EmploymentPeriod(date(2025, 1, 1)), weekly_hours=20)
    )

    assert full_time.period_gross == _MONTHLY
    assert part_time.period_gross == Decimal("1079.13")


def test_part_time_hire_month_prorates_the_part_time_pay() -> None:
    """Half-time hired 15 March: 1,079.13 x 14 / 26 = 581.07."""
    result = _run(3, _employment(EmploymentPeriod(date(2026, 3, 15)), weekly_hours=20))

    assert result.period_gross == Decimal("581.07")


def test_weekday_holidays_are_paid_days() -> None:
    """Ended 6 January: 1, 2, 3, 5 and 6 January are 5 payable days.

    1 and 6 January are public holidays on weekdays: they are paid, so the
    month pays 2,158.26 x 5 / 26 = 415.05, plus the 50.00 the caller
    declares for the work on the holiday.
    """
    period = EmploymentPeriod(date(2025, 1, 1), date(2026, 1, 6))
    holiday = HolidayWorkEvent(
        event_date=date(2026, 1, 6), supplement_amount=Decimal("50.00")
    )

    plain = _run(1, _employment(period))
    worked = _run(1, _employment(period), PeriodFacts(events=(holiday,)))

    assert plain.period_gross == Decimal("415.05")
    assert worked.period_gross == Decimal("465.05")


def test_sick_leave_adds_to_the_prorated_pay() -> None:
    """A sick leave of 100.00 in the hire month: 1,162.14 + 100.00."""
    sick = SickLeaveEvent(event_date=date(2026, 3, 20), amount=Decimal("100.00"))
    result = _run(
        3,
        _employment(EmploymentPeriod(date(2026, 3, 15))),
        PeriodFacts(events=(sick,)),
    )

    assert result.period_gross == Decimal("1262.14")


def test_unpaid_absence_cannot_exceed_the_prorated_pay() -> None:
    """Hired Monday 30 March: 2 payable days, 2,158.26 x 2 / 26 = 166.02.

    Sixteen absent hours at 12.48 deduct 199.68, more than the pay of the
    run: the request is rejected, as for a full month.
    """
    period = EmploymentPeriod(date(2026, 3, 30))
    absence = AbsenceEvent(
        event_date=date(2026, 3, 30),
        end_date=date(2026, 3, 31),
        hours=Decimal(16),
        hourly_rate=Decimal("12.48"),
    )

    assert _run(3, _employment(period)).period_gross == Decimal("166.02")
    with pytest.raises(InvalidInputError, match=r"166\.02"):
        _run(3, _employment(period), PeriodFacts(events=(absence,)))


@pytest.mark.parametrize(
    ("hired_on", "march", "thirteenth", "tfr"),
    [
        # 17 days of March accrue its rateo: 10/12 of 2,211.43.
        pytest.param(
            date(2026, 3, 15),
            Decimal("1162.14"),
            Decimal("1842.86"),
            Decimal("80.27"),
            id="fifteenth",
        ),
        # 14 days do not; 12 payable days pay 2,158.26 x 12 / 26.
        pytest.param(
            date(2026, 3, 18),
            Decimal("996.12"),
            Decimal("1658.57"),
            Decimal("68.81"),
            id="eighteenth",
        ),
    ],
)
def test_accruals_follow_the_employed_days(
    hired_on: date, march: Decimal, thirteenth: Decimal, tfr: Decimal
) -> None:
    """The tredicesima counts March by its days, the TFR the prorated pay.

    The rateo threshold is 15 calendar days; the TFR of March is its gross
    divided by 13.5: 1,162.14 / 13.5 = 86.08, 996.12 / 13.5 = 73.79, less
    the 0.50% additional IVS of the same gross (L. 297/1982 art. 3 c. 16):
    1,162.14 x 0.50% = 5.81 and 996.12 x 0.50% = 4.98, so 80.27 and 68.81.
    """
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_employment(EmploymentPeriod(hired_on)),
            employer=_EMPLOYER,
        )
    )
    first = year.period_results[0]
    (extra,) = [
        r for r in year.period_results if r.run == PayrollRun.thirteenth(2026, 12)
    ]
    (tfr_item,) = [i for i in first.pay_items if i.kind == "tfr_accrual_item"]

    assert first.period_gross == march
    assert extra.period_gross == thirteenth
    assert tfr_item.amount == tfr


def test_ccnl_without_rule_never_pays_a_full_month() -> None:
    """The vetro CCNL records no daily quota: March is undetermined.

    The run posts no pay, its ``base_salary`` decision carries no amount
    and the result is not payable.
    """
    result = _run(
        3,
        _employment(
            EmploymentPeriod(date(2026, 3, 15)),
            ccnl="vetro-meccanizzato-assovetro.json",
            level="C",
        ),
    )

    assert result.period_gross == Decimal("0.00")
    assert _base_salary(result) == ("partial_month_rule_missing", None)
    assert "partial_month_rule_missing" in {i.code for i in result.issues}
    assert result.is_payable is False


def _closing_run(
    kind: str, month: int, employment: Employment, opening: PeriodResult | None
) -> PeriodResult:
    """Return a termination or adjustment run paid on the 30th of ``month``.

    Returns:
        The run, opening on the closing state of ``opening`` when given.
    """
    request = PeriodInput(
        # RunKind is not public: the constructor normalises its value.
        run=PayrollRun(run_kind=kind, month=month, year=2026),  # type: ignore[arg-type]
        payment_date=date(2026, month, 30),
        employment=employment,
        employer=_EMPLOYER,
    )
    if opening is not None:
        request = replace(request, opening_state=opening.closing_state)
    return _ENGINE.calculate_period(request)


_ENDS_15_APRIL = EmploymentPeriod(date(2025, 1, 1), date(2026, 4, 15))


def test_termination_run_closing_the_month_pays_its_daily_quotas() -> None:
    """Ended 15 April, no regular April run: 13 payable days, 1,079.13."""
    result = _closing_run("termination", 4, _employment(_ENDS_15_APRIL), None)

    assert result.period_gross == Decimal("1079.13")
    assert _base_salary(result) == ("pay_chain_prorated", Decimal("1079.13"))


def test_regular_and_termination_runs_pay_the_month_once() -> None:
    """The regular April run pays 1,079.13; the termination run after it 0.

    The two runs of April together pay 2,158.26 x 13 / 26 = 1,079.13, not
    that plus a second monthly pay.
    """
    employment = _employment(_ENDS_15_APRIL)
    regular = _run(4, employment)
    termination = _closing_run("termination", 4, employment, regular)

    assert regular.period_gross == Decimal("1079.13")
    assert termination.period_gross == Decimal("0.00")
    assert _base_salary(termination) == (
        "monthly_pay_posted_by_another_run",
        Decimal("0.00"),
    )
    assert regular.period_gross + termination.period_gross == Decimal("1079.13")


def test_adjustment_run_never_posts_the_monthly_pay_again() -> None:
    """An adjustment of the hire month after its regular run: 1,162.14 once."""
    employment = _employment(EmploymentPeriod(date(2026, 3, 15)))
    regular = _run(3, employment)
    adjustment = _closing_run("adjustment", 3, employment, regular)

    assert regular.period_gross == Decimal("1162.14")
    assert adjustment.period_gross == Decimal("0.00")
    assert _base_salary(adjustment)[0] == "monthly_pay_posted_by_another_run"
