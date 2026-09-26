"""Integration tests: Employment fields wired through the pipeline."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    EmploymentPeriod,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    SeniorityMonths,
    WeeklyHours,
    YearInput,
)

_CCNL = "metalmeccanico-federmeccanica.json"
_EMPLOYER = EmployerProfile(headcount=Headcount(50))


@pytest.fixture(scope="module")
def engine() -> PayrollEngine:
    """Shared engine instance for the module.

    Returns:
        A :class:`PayrollEngine` backed by the bundled knowledge data.
    """
    return PayrollEngine.bundled()


def _run(engine: PayrollEngine, **fields: Any) -> Decimal:  # noqa: ANN401
    result = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 1),
            payment_date=date(2026, 1, 28),
            employment=Employment(ccnl_slug=_CCNL, level_code="C3", **fields),
            employer=_EMPLOYER,
        )
    )
    return result.period_gross


def test_part_time_reduces_gross(engine: PayrollEngine) -> None:
    """Part-time fraction applied: half-time gross == half full-time gross."""
    full = _run(engine)
    half = _run(
        engine,
        weekly_hours=WeeklyHours(20),
        full_time_weekly_hours=WeeklyHours(40),
    )
    assert half == full * Decimal("0.5")


def test_seniority_months_increases_gross(engine: PayrollEngine) -> None:
    """60 months seniority unlocks increments and raises period gross."""
    base = _run(engine)
    with_seniority = _run(engine, seniority_months=SeniorityMonths(60))
    assert with_seniority > base


def test_roles_forwarded(engine: PayrollEngine) -> None:
    """Passing roles does not crash; result is a positive amount."""
    gross = _run(engine, roles=frozenset({"caposquadra"}))
    assert gross > Decimal(0)


def test_employment_dates_select_the_year_runs(engine: PayrollEngine) -> None:
    """Employed 1 March to 31 May: three regular runs and no tredicesima."""
    year = engine.calculate_year(
        YearInput(
            year=2026,
            employment=Employment(
                ccnl_slug=_CCNL,
                level_code="C3",
                employment_period=EmploymentPeriod(date(2026, 3, 1), date(2026, 5, 31)),
            ),
            employer=_EMPLOYER,
        )
    )
    assert [r.run.run_id for r in year.period_results if r.run] == [
        "2026-03-regular",
        "2026-04-regular",
        "2026-05-regular",
    ]
