"""Public year input: configurable payment day of the runs."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    PayrollEngine,
    YearInput,
)

_ENGINE = PayrollEngine.bundled()
_EMPLOYMENT = Employment(ccnl_slug="commercio-confcommercio.json", level_code="4")
_EMPLOYER = EmployerProfile(headcount=Headcount(50))


def test_runs_are_paid_on_the_28th_by_default() -> None:
    """Without a payment day every run is paid on the 28th of its month."""
    year = _ENGINE.calculate_year(
        YearInput(year=2026, employment=_EMPLOYMENT, employer=_EMPLOYER)
    )

    assert {r.payment_date.day for r in year.period_results} == {28}


def test_payment_day_moves_every_run_and_keeps_the_tax_year() -> None:
    """Paying on the 10th changes the payment dates, not the tax year."""
    year = _ENGINE.calculate_year(
        YearInput(year=2026, employment=_EMPLOYMENT, employer=_EMPLOYER, payment_day=10)
    )

    first = year.period_results[0]
    assert first.payment_date == date(2026, 1, 10)
    assert {r.payment_date.day for r in year.period_results} == {10}
    assert {r.closing_state.tax_year for r in year.period_results} == {2026}


@pytest.mark.parametrize("payment_day", [0, 29])
def test_payment_day_outside_every_month_is_rejected(payment_day: int) -> None:
    """A day some month does not have is rejected when the input is built."""
    with pytest.raises(InvalidInputError, match="payment day"):
        YearInput(
            year=2026,
            employment=_EMPLOYMENT,
            employer=_EMPLOYER,
            payment_day=payment_day,
        )
