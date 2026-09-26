"""The employer's headcount reaches the pipeline on both public entry points."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine import (
    Employer,
    EmploymentFacts,
    Headcount,
    PayrollEngine,
    PayrollRequest,
    PayrollRun,
    PayrollYearRequest,
)

if TYPE_CHECKING:
    from decimal import Decimal

_ENGINE = PayrollEngine.bundled()
_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_SMALL = Employer(headcount=Headcount(10))
_LARGE = Employer(headcount=Headcount(100))


def _period_employer_inps(employer: Employer) -> Decimal:
    result = _ENGINE.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            employment_facts=EmploymentFacts(),
            employer=employer,
        )
    )
    return result.contribution_breakdown.employer


def _annual_employer_cost(employer: Employer) -> Decimal:
    result = _ENGINE.calculate_year(
        PayrollYearRequest(
            year=2026,
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            employer=employer,
        )
    )
    return result.annual_employer_cost


def test_period_headcount_selects_inps_tier() -> None:
    """A larger industrial employer pays more INPS (CIGS above 15 employees)."""
    assert _period_employer_inps(_LARGE) > _period_employer_inps(_SMALL)


def test_year_headcount_selects_inps_tier() -> None:
    """The year entry point forwards the employer to every run."""
    assert _annual_employer_cost(_LARGE) > _annual_employer_cost(_SMALL)
