"""The employer's headcount reaches the pipeline on both public entry points."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    YearInput,
)

if TYPE_CHECKING:
    from decimal import Decimal

_ENGINE = PayrollEngine.bundled()
_EMPLOYMENT = Employment(
    ccnl_slug="metalmeccanico-federmeccanica.json", level_code="C3"
)
_SMALL = EmployerProfile(headcount=Headcount(10))
_LARGE = EmployerProfile(headcount=Headcount(100))


def _period_employer_inps(employer: EmployerProfile) -> Decimal:
    result = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            employment=_EMPLOYMENT,
            employer=employer,
        )
    )
    return result.contribution_breakdown.employer


def _annual_employer_cost(employer: EmployerProfile) -> Decimal:
    result = _ENGINE.calculate_year(
        YearInput(year=2026, employment=_EMPLOYMENT, employer=employer)
    )
    return result.annual_employer_cost


def test_period_headcount_selects_inps_tier() -> None:
    """A larger industrial employer pays more INPS (CIGS above 15 employees)."""
    assert _period_employer_inps(_LARGE) > _period_employer_inps(_SMALL)


def test_year_headcount_selects_inps_tier() -> None:
    """The year entry point forwards the employer to every run."""
    assert _annual_employer_cost(_LARGE) > _annual_employer_cost(_SMALL)
