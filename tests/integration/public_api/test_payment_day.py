"""Public year request: configurable payment day of the runs."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine import InvalidInputError, PayrollEngine, PayrollYearRequest

_ENGINE = PayrollEngine.bundled()
_CCNL = "commercio-confcommercio.json"


def test_runs_are_paid_on_the_28th_by_default() -> None:
    """Without a payment day every run is paid on the 28th of its month."""
    year = _ENGINE.calculate_year(
        PayrollYearRequest(year=2026, ccnl_slug=_CCNL, level_code="4")
    )

    assert {r.payment_date.day for r in year.period_results} == {28}


def test_payment_day_moves_every_run_and_keeps_the_tax_year() -> None:
    """Paying on the 10th changes the payment dates, not the tax year."""
    year = _ENGINE.calculate_year(
        PayrollYearRequest(year=2026, ccnl_slug=_CCNL, level_code="4", payment_day=10)
    )

    first = year.period_results[0]
    assert first.payment_date == date(2026, 1, 10)
    assert {r.payment_date.day for r in year.period_results} == {10}
    assert {r.closing_state.tax_year for r in year.period_results} == {2026}


@pytest.mark.parametrize("payment_day", [0, 29])
def test_payment_day_outside_every_month_is_rejected(payment_day: int) -> None:
    """A day some month does not have is rejected before any run."""
    request = PayrollYearRequest(
        year=2026, ccnl_slug=_CCNL, level_code="4", payment_day=payment_day
    )

    with pytest.raises(InvalidInputError, match="payment day"):
        _ENGINE.calculate_year(request)
