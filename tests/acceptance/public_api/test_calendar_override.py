"""Public year input: derived calendar and validated overrides."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    PayrollEngine,
)
from ccnl_engine.inputs import CalendarOverride, CalendarOverrideReason, WorkCalendar

_ENGINE = PayrollEngine.bundled()
_EMPLOYMENT = Employment(ccnl_slug="commercio-confcommercio.json", level_code="4")
_EMPLOYER = EmployerProfile(headcount=Headcount(50))


def test_omitted_calendar_runs_the_ccnl_calendar() -> None:
    """Commercio grants 14 equivalent months: the result reports that calendar."""
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(year=2026, employment=_EMPLOYMENT, employer=_EMPLOYER)
    )

    assert year.calendar == WorkCalendar.from_additional_months(2026, 14)
    assert year.calendar_override is None


def test_bare_calendar_is_rejected() -> None:
    """A WorkCalendar without a reason is not accepted by the input."""
    with pytest.raises(InvalidInputError, match="CalendarOverride"):
        CompetenceYearPlan(
            year=2026,
            employment=_EMPLOYMENT,
            employer=_EMPLOYER,
            calendar_override=WorkCalendar(year=2026),  # type: ignore[arg-type]
        )


def test_payment_month_override_is_reported_on_the_result() -> None:
    """A quattordicesima paid in July runs right after the July payslip."""
    override = CalendarOverride(
        calendar=WorkCalendar.from_additional_months(
            2026, 14, fourteenth_payment_month=7
        ),
        reason=CalendarOverrideReason.PAYMENT_MONTH,
        note="quattordicesima paid with the July salary",
    )
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_EMPLOYMENT,
            employer=_EMPLOYER,
            calendar_override=override,
        )
    )
    run_ids = [r.run.run_id for r in year.period_results if r.run is not None]

    standard = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(year=2026, employment=_EMPLOYMENT, employer=_EMPLOYER)
    )

    assert run_ids[7] == "2026-07-fourteenth"
    # The override sets its own payment month: the run is paid on the
    # payment day of that month, not on the CCNL day of the standard one.
    assert year.period_results[7].payment_date == date(2026, 7, 28)
    assert year.annual_gross == standard.annual_gross
    assert year.calendar_override is override
