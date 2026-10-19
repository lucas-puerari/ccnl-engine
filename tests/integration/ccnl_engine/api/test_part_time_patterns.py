"""Decimal weekly hours, and vertical or mixed part time through a work pattern.

Chimica-farmaceutica Federchimica D1 earns a TEM of 2,360.26 a month from
December 2025 and 2,420.26 from July 2026, with no other component in 2026
(the EDR starts in July 2027).  Every expected amount is computed here by
hand from those minimi, rounded to the cent once: never the engine output.

Calendar: the tredicesima of the CCNL (art. 21) is paid in December and
accrues on the calendar year; a fraction of a month counts above 15 days.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import EmploymentPeriod, Permanent, WeeklyHours, WorkPattern

_ENGINE = PayrollEngine.bundled()
_EMPLOYER = EmployerProfile(headcount=Headcount(50))
_CHIMICA = "chimica-farmaceutica-federchimica"
_FULL_TIME = WeeklyHours(Decimal(40))
_TEM_SPRING = Decimal("2360.26")
_TEM_JULY = Decimal("2420.26")
_JANUARY_TO_JUNE = WorkPattern(months=frozenset(range(1, 7)))
_MON_TO_WED = WorkPattern(
    weekday_hours=(Decimal(8), Decimal(8), Decimal(8), *(Decimal(0),) * 4)
)
_CENT = Decimal("0.01")


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


def _employment(
    weekly: str,
    *,
    pattern: WorkPattern | None = None,
    period: EmploymentPeriod | None = None,
) -> Employment:
    return Employment(
        ccnl_id=_CHIMICA,
        level_code="D1",
        contract_type=Permanent(),
        employment_period=period or EmploymentPeriod(date(2025, 1, 1)),
        weekly_hours=WeeklyHours(Decimal(weekly)),
        full_time_weekly_hours=_FULL_TIME,
        work_pattern=pattern,
    )


def _run(run: PayrollRun, employment: Employment) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=run,
            payment_date=date(run.year, run.month, 27),
            employment=employment,
            employer=_EMPLOYER,
        )
    )


def _base_salary(result: PeriodResult) -> tuple[str, Decimal | None]:
    (decision,) = [
        d
        for d in result.decisions
        if d.capability == "base_salary"
        and d.reason_code != "extra_month_ratei_counted"
    ]
    return decision.reason_code, decision.amount


def _inps_minimum_reason(result: PeriodResult) -> object:
    (decision,) = [d for d in result.decisions if d.capability == "inps_employee"]
    return decision.inputs["minimum_base_reason"]


def test_decimal_weekly_hours_scale_the_minimum() -> None:
    """37.5 of 40 hours: 2,360.26 x 37.5 / 40 = 2,212.74375, so 2,212.74."""
    expected = _cents(_TEM_SPRING * Decimal("37.5") / Decimal(40))

    result = _run(PayrollRun.regular(2026, 3), _employment("37.5"))

    assert expected == Decimal("2212.74")
    assert result.period_gross == expected
    assert _base_salary(result) == ("pay_chain_applied", expected)


def test_whole_weekly_hours_keep_their_amounts() -> None:
    """20 of 40 hours, now a Decimal: half of 2,360.26 is 1,180.13."""
    result = _run(PayrollRun.regular(2026, 3), _employment("20"))

    assert result.period_gross == _cents(_TEM_SPRING / 2)


def test_a_weekday_pattern_equals_the_horizontal_ratio() -> None:
    """8 hours Monday to Wednesday are 24 weekly hours: 24 / 40 of the TEM."""
    horizontal = _run(PayrollRun.regular(2026, 3), _employment("24"))
    vertical = _run(PayrollRun.regular(2026, 3), _employment("24", pattern=_MON_TO_WED))

    assert vertical.period_gross == _cents(_TEM_SPRING * 24 / 40)
    assert vertical.period_gross == horizontal.period_gross
    assert vertical.period_net == horizontal.period_net


@pytest.fixture(scope="module")
def runs() -> dict[PayrollRun, PeriodResult]:
    """Compute 2026 for a full time worked January to June.

    Returns:
        The results of the year, by run.
    """
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_employment("40", pattern=_JANUARY_TO_JUNE),
            employer=_EMPLOYER,
        )
    )
    return {r.run: r for r in year.period_results if r.run is not None}


class TestVerticalPartTimeYear:
    """Full time January to June 2026, not worked July to December."""

    def test_a_month_worked_pays_the_whole_minimum(
        self, runs: dict[PayrollRun, PeriodResult]
    ) -> None:
        """June is worked full time: the whole TEM of 2,360.26."""
        assert runs[PayrollRun.regular(2026, 6)].period_gross == _TEM_SPRING

    @pytest.mark.parametrize("month", [7, 9, 12])
    def test_a_month_not_worked_pays_nothing(
        self, runs: dict[PayrollRun, PeriodResult], month: int
    ) -> None:
        """July to December post no base pay and no INPS minimum."""
        result = runs[PayrollRun.regular(2026, month)]

        assert result.period_gross == Decimal("0.00")
        assert _base_salary(result) == (
            "vertical_part_time_month_not_worked",
            Decimal("0.00"),
        )
        assert _inps_minimum_reason(result) == "month_not_worked"

    def test_the_tredicesima_accrues_the_months_worked(
        self, runs: dict[PayrollRun, PeriodResult]
    ) -> None:
        """6 of 12 months on the December TEM: 2,420.26 x 6 / 12 = 1,210.13."""
        result = runs[PayrollRun.thirteenth(2026, 12)]
        (counted,) = [
            d for d in result.decisions if d.reason_code == "extra_month_ratei_counted"
        ]

        assert counted.inputs["months"] == "6"
        assert result.period_gross == _cents(_TEM_JULY * 6 / 12)


def test_a_single_tredicesima_run_accrues_the_months_worked() -> None:
    """Computed on its own, the tredicesima counts the same 6 months."""
    result = _run(
        PayrollRun.thirteenth(2026, 12), _employment("40", pattern=_JANUARY_TO_JUNE)
    )

    assert result.period_gross == _cents(_TEM_JULY * 6 / 12)


def test_termination_in_a_month_not_worked_settles_the_months_worked() -> None:
    """Ended 30 September: no September pay, the ratei of January to June.

    The tredicesima of December falls after the end, so the September run
    liquidates its 6 ratei: 2,420.26 x 6 / 12 = 1,210.13.
    """
    employment = _employment(
        "40",
        pattern=_JANUARY_TO_JUNE,
        period=EmploymentPeriod(date(2025, 1, 1), date(2026, 9, 30)),
    )

    result = _run(PayrollRun.regular(2026, 9), employment)
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(year=2026, employment=employment, employer=_EMPLOYER)
    )
    (september,) = [
        r for r in year.period_results if r.run == PayrollRun.regular(2026, 9)
    ]

    assert _base_salary(result)[1] == Decimal("0.00")
    assert result.period_gross == _cents(_TEM_JULY * 6 / 12)
    assert september.period_gross == result.period_gross
