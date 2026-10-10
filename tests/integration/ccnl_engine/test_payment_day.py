"""Public year input: configurable payment day of the runs."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    CompetenceYearResult,
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    PayrollEngine,
)
from ccnl_engine.inputs import Permanent

_ENGINE = PayrollEngine.bundled()
_EMPLOYMENT = Employment(
    ccnl_slug="commercio-confcommercio.json", level_code="4", contract_type=Permanent()
)
_EMPLOYER = EmployerProfile(headcount=Headcount(50))


_FOURTEENTH = "2026-06-fourteenth"
_THIRTEENTH = "2026-12-thirteenth"


def _dates(year: CompetenceYearResult) -> dict[str, date]:
    return {r.run.run_id: r.payment_date for r in year.period_results if r.run}


def test_runs_are_paid_on_the_28th_by_default() -> None:
    """Without a payment day every run is paid on the 28th of its month.

    Except the extra months: the CCNL Terziario (Testo Unico 30 July 2019)
    pays the tredicesima "in coincidenza con la vigilia di Natale" (art. 220),
    24 December, and the quattordicesima "il 1° luglio di ogni anno"
    (art. 221), for the window ending on 30 June, so the June quattordicesima
    is paid on 1 July.
    """
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(year=2026, employment=_EMPLOYMENT, employer=_EMPLOYER)
    )
    dates = _dates(year)

    assert dates.pop(_FOURTEENTH) == date(2026, 7, 1)
    assert dates.pop(_THIRTEENTH) == date(2026, 12, 24)
    assert {paid_on.day for paid_on in dates.values()} == {28}


def test_payment_day_moves_every_run_and_keeps_the_tax_year() -> None:
    """Paying on the 10th changes the payment dates, not the tax year."""
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026, employment=_EMPLOYMENT, employer=_EMPLOYER, payment_day=10
        )
    )
    dates = _dates(year)

    assert dates["2026-01-regular"] == date(2026, 1, 10)
    assert dates.pop(_FOURTEENTH) == date(2026, 7, 1)
    assert dates.pop(_THIRTEENTH) == date(2026, 12, 24)
    assert {paid_on.day for paid_on in dates.values()} == {10}
    assert {r.closing_state.tax_year for r in year.period_results} == {2026}


def test_payment_date_of_the_plan_wins_over_the_ccnl_day() -> None:
    """A date the plan names for the quattordicesima replaces 1 July."""
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_EMPLOYMENT,
            employer=_EMPLOYER,
            payment_dates={_FOURTEENTH: date(2026, 6, 20)},
        )
    )

    assert _dates(year)[_FOURTEENTH] == date(2026, 6, 20)


@pytest.mark.parametrize("payment_day", [0, 29])
def test_payment_day_outside_every_month_is_rejected(payment_day: int) -> None:
    """A day some month does not have is rejected when the input is built."""
    with pytest.raises(
        InvalidInputError,
        match=r"CompetenceYearPlan\.payment_day must be an int >= 1 and <= 28",
    ):
        CompetenceYearPlan(
            year=2026,
            employment=_EMPLOYMENT,
            employer=_EMPLOYER,
            payment_day=payment_day,
        )
