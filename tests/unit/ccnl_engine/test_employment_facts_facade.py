"""Integration tests: EmploymentFacts fields propagated through PayrollEngine.

Covers the public API path (PayrollEngine.calculate) for CCNLs that require
employment facts not previously exposed, e.g. domestic CCNLs which raise
MissingRequiredFactError without weekly_hours and contributable_hours.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmploymentFacts,
    InvalidInputError,
    PayrollEngine,
    PayrollRequest,
    PayrollRun,
)
from ccnl_engine.engine.contract.domain.category import WorkerCategory

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
        category=WorkerCategory.OPERAIO,
        started_on=date(2023, 1, 1),
    )
    req = _request(
        ccnl="metalmeccanico-federmeccanica.json",
        level="C3",
        employment_facts=ef,
    )
    result = _ENGINE.calculate(req)
    assert result.period_gross > _ZERO


def test_category_string_value_is_normalized() -> None:
    """A category given as its string value is stored as the enum member."""
    ef = EmploymentFacts(category="impiegato")  # type: ignore[arg-type]
    assert ef.category is WorkerCategory.IMPIEGATO


def test_unknown_category_is_rejected() -> None:
    """An unknown category string raises instead of being ignored."""
    with pytest.raises(InvalidInputError, match="unknown worker category"):
        EmploymentFacts(category="manager")  # type: ignore[arg-type]


def test_category_conflicting_with_level_is_rejected() -> None:
    """Commercio level Q is reserved to quadri, so impiegato is not admitted."""
    ef = EmploymentFacts(category=WorkerCategory.IMPIEGATO)
    with pytest.raises(InvalidInputError, match="not admitted"):
        _ENGINE.calculate(
            _request(
                ccnl="commercio-confcommercio.json", level="Q", employment_facts=ef
            )
        )


def test_declared_category_selects_artigianato_employer_rate() -> None:
    """Artigianato level 3 hosts operai and impiegati with different INPS rates.

    Bundled 2026 artigianato rules: employer rate 26.93% by default and
    24.71% for impiegati, applied to the same contribution base.
    """
    ccnl, level = "metalmeccanico-artigianato.json", "3"
    default = _ENGINE.calculate(_request(ccnl=ccnl, level=level))
    impiegato = _ENGINE.calculate(
        _request(
            ccnl=ccnl,
            level=level,
            employment_facts=EmploymentFacts(category=WorkerCategory.IMPIEGATO),
        )
    )
    base = default.period_gross
    assert impiegato.period_gross == base
    assert default.contribution_breakdown.employer == (
        base * Decimal("0.2693")
    ).quantize(Decimal("0.01"))
    assert impiegato.contribution_breakdown.employer == (
        base * Decimal("0.2471")
    ).quantize(Decimal("0.01"))
