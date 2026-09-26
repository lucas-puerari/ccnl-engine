"""Public year request: derived calendar and validated overrides."""

from __future__ import annotations

import pytest

from ccnl_engine import (
    CalendarOverride,
    CalendarOverrideReason,
    InvalidInputError,
    PayrollCalendar,
    PayrollEngine,
    PayrollYearRequest,
)

_ENGINE = PayrollEngine.bundled()
_CCNL = "commercio-confcommercio.json"


def test_omitted_calendar_runs_the_ccnl_calendar() -> None:
    """Commercio grants 14 equivalent months: the result reports that calendar."""
    year = _ENGINE.calculate_year(
        PayrollYearRequest(year=2026, ccnl_slug=_CCNL, level_code="4")
    )

    assert year.calendar == PayrollCalendar.from_additional_months(2026, 14)
    assert year.calendar_override is None


def test_bare_calendar_is_rejected() -> None:
    """A WorkCalendar without a reason is not accepted by the request."""
    with pytest.raises(InvalidInputError, match="CalendarOverride"):
        PayrollYearRequest(
            year=2026,
            ccnl_slug=_CCNL,
            level_code="4",
            calendar=PayrollCalendar(year=2026),  # type: ignore[arg-type]
        )


def test_payment_month_override_is_reported_on_the_result() -> None:
    """A quattordicesima paid in July runs right after the July payslip."""
    override = CalendarOverride(
        calendar=PayrollCalendar.from_additional_months(
            2026, 14, fourteenth_payment_month=7
        ),
        reason=CalendarOverrideReason.PAYMENT_MONTH,
        note="quattordicesima paid with the July salary",
    )
    year = _ENGINE.calculate_year(
        PayrollYearRequest(
            year=2026, ccnl_slug=_CCNL, level_code="4", calendar=override
        )
    )
    run_ids = [r.run.run_id for r in year.period_results if r.run is not None]

    standard = _ENGINE.calculate_year(
        PayrollYearRequest(year=2026, ccnl_slug=_CCNL, level_code="4")
    )

    assert run_ids[7] == "2026-07-fourteenth"
    assert year.annual_gross == standard.annual_gross
    assert year.calendar_override is override
