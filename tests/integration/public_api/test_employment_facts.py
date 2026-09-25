"""Integration tests: EmploymentFacts fields wired through the pipeline."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import EmploymentFacts, PayrollEngine, PayrollRequest, PayrollRun


@pytest.fixture(scope="module")
def engine() -> PayrollEngine:
    """Shared engine instance for the module.

    Returns:
        A :class:`PayrollEngine` backed by the bundled knowledge data.
    """
    return PayrollEngine.bundled()


def _run(engine: PayrollEngine, **ef_kwargs: object) -> Decimal:
    ef = EmploymentFacts(**ef_kwargs)  # type: ignore[arg-type]
    result = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(2026, 1),
            payment_date=date(2026, 1, 28),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employment_facts=ef,
        )
    )
    return result.period_gross


def test_part_time_reduces_gross(engine: PayrollEngine) -> None:
    """Part-time fraction applied: half-time gross == half full-time gross."""
    full = _run(engine)
    half = _run(engine, weekly_hours=20, full_time_weekly_hours=40)
    assert half == full * Decimal("0.5")


def test_seniority_months_increases_gross(engine: PayrollEngine) -> None:
    """60 months seniority unlocks increments and raises period gross."""
    base = _run(engine)
    with_seniority = _run(engine, seniority_months=60)
    assert with_seniority > base


def test_roles_forwarded(engine: PayrollEngine) -> None:
    """Passing roles does not crash; result is a positive amount."""
    gross = _run(engine, roles=frozenset({"caposquadra"}))
    assert gross > Decimal(0)


def test_started_on_ended_on_forwarded(engine: PayrollEngine) -> None:
    """started_on and ended_on are accepted without error."""
    gross = _run(
        engine,
        started_on=date(2020, 1, 1),
        ended_on=date(2027, 12, 31),
    )
    assert gross > Decimal(0)
