"""Integration tests: EmploymentFacts fields propagated through PayrollEngine.

Covers the public API path (PayrollEngine.calculate) for CCNLs that require
employment facts not previously exposed, e.g. domestic CCNLs which raise
MissingRequiredFactError without weekly_hours and contributable_hours.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine import EmploymentFacts, PayrollEngine, PayrollRequest, PayrollRun

_ENGINE = PayrollEngine.from_builtin_data()
_YEAR = 2026
_ZERO = Decimal(0)


def _request(
    *,
    ccnl: str,
    level: str,
    month: int = 6,
    employment_facts: EmploymentFacts | None = None,
) -> PayrollRequest:
    return PayrollRequest(
        run=PayrollRun.regular(_YEAR, month),
        payment_date=date(_YEAR, month, 28),
        ccnl_slug=ccnl,
        level_code=level,
        employment_facts=employment_facts or EmploymentFacts(),
    )


def test_employment_facts_default_fields() -> None:
    """Default EmploymentFacts must expose all new fields with None/empty defaults."""
    ef = EmploymentFacts()
    assert ef.weekly_hours is None
    assert ef.contributable_hours is None
    assert ef.full_time_weekly_hours is None
    assert ef.started_on is None
    assert ef.ended_on is None
    assert ef.seniority_months is None
    assert ef.roles == frozenset()
    assert ef.category is None


def test_domestic_ccnl_via_public_api_returns_result() -> None:
    """PayrollEngine.calculate with a domestic CCNL must succeed.

    Without weekly_hours and contributable_hours in EmploymentFacts, the facade
    formerly omitted them from PeriodCalculationRequest, causing the domestic
    INPS bracket resolver to raise MissingRequiredFactError.
    """
    ef = EmploymentFacts(
        weekly_hours=30,
        contributable_hours=Decimal(130),
    )
    req = _request(
        ccnl="lavoro-domestico-convivente.json",
        level="BS",
        employment_facts=ef,
    )
    result = _ENGINE.calculate(req)
    assert result.period_gross > _ZERO, (
        "Domestic CCNL must produce a positive period_gross via the public API."
    )
    assert result.contribution_breakdown.employee > _ZERO, (
        "Domestic CCNL must produce non-zero employee INPS contributions."
    )


def test_employment_facts_roles_and_seniority_are_accepted() -> None:
    """EmploymentFacts with roles and seniority_months must be accepted."""
    ef = EmploymentFacts(
        seniority_months=36,
        roles=frozenset({"caposquadra"}),
        category="operaio",
        started_on=date(2023, 1, 1),
    )
    req = _request(
        ccnl="metalmeccanico-federmeccanica.json",
        level="C3",
        employment_facts=ef,
    )
    result = _ENGINE.calculate(req)
    assert result.period_gross > _ZERO
