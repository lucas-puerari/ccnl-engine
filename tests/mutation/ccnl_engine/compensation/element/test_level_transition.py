"""The time-limited junior level and its mandatory promotion."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import cast

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.services import _resolve_chain
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.compensation.entry.transition import transitioned_level
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.fact.services import level_start_issue
from ccnl_engine.employment.inputs import Apprentice, Permanent
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.period.context.services import RunContext


def _chain(month: date, started_on: date | None) -> MonthlyPayChain:
    ccnl = load_ccnl("logistica-trasporto-confetra")
    chain, _ = _resolve_chain(
        ccnl,
        ccnl.level_by_code("6J"),
        Permanent(),
        month,
        seniority_months=None,
        roles=frozenset(),
        worker_category=None,
        hired_on=date(2025, 6, 1),
        level_started_on=started_on,
    )
    return chain


def test_junior_pay_and_cutoff() -> None:
    """2025: 1464.53 + 7.58 = 1472.11; 2026: 1648.74 + 8.26 = 1657.00."""
    junior = _chain(date(2025, 11, 1), date(2025, 6, 1))
    assert junior.base == Decimal("1464.53")
    assert sum((value for _, value in junior.allowances), Decimal()) == Decimal("7.58")
    promoted = _chain(date(2026, 1, 1), date(2025, 6, 1))
    assert promoted.base == Decimal("1648.74")
    assert sum((value for _, value in promoted.allowances), Decimal()) == Decimal(
        "8.26"
    )


def test_twelve_month_promotion_and_missing_start() -> None:
    """A 2024 level start pays 1615.71; unknown start blocks 1464.53."""
    assert _chain(date(2025, 6, 1), date(2024, 1, 1)).base == Decimal("1615.71")
    assert _chain(date(2025, 6, 1), None).base == Decimal("1464.53")
    ccnl = load_ccnl("logistica-trasporto-confetra")

    def context(month: date, level: str) -> RunContext:
        return cast(
            "RunContext",
            SimpleNamespace(
                contract=SimpleNamespace(
                    level=ccnl.level_by_code(level),
                    tctx=SimpleNamespace(competence=month),
                ),
                request=SimpleNamespace(level_started_on=None),
            ),
        )

    issue = level_start_issue(context(date(2025, 6, 1), "6J"))
    assert issue is not None
    assert issue.fact == "level_started_on"
    assert level_start_issue(context(date(2026, 1, 1), "6J")) is None
    assert level_start_issue(context(date(2025, 6, 1), "6")) is None


def test_period_uses_promoted_level_without_entry_date() -> None:
    """January 2026 gross: level 6 minimum 1648.74 + EDR 8.26 = 1657.00."""
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 25),
            employment=Employment(
                ccnl_id="logistica-trasporto-confetra",
                level_code="6J",
                contract_type=Permanent(),
                category=WorkerCategory.OPERAIO,
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="F205"),
        )
    )
    assert result.period_gross == Decimal("1657.00")
    assert all(issue.code != "entry_level_start_unknown" for issue in result.issues)


def test_unsupported_apprentice_and_cutoff() -> None:
    """The 2025 apprentice cannot receive 1464.53 without the 24-month rule."""
    ccnl = load_ccnl("logistica-trasporto-confetra")
    junior = ccnl.level_by_code("6J")
    apprentice = Apprentice(months_elapsed=6)
    with pytest.raises(InvalidInputError, match="apprenticeship"):
        transitioned_level(ccnl, junior, apprentice, date(2025, 11, 1), None)
    assert (
        transitioned_level(ccnl, junior, apprentice, date(2026, 1, 1), None).code == "6"
    )


def test_transition_without_months_and_invalid_targets() -> None:
    """The cutoff is independent of tenure; invalid transition targets fail loading."""
    ccnl = load_ccnl("logistica-trasporto-confetra")
    junior = ccnl.level_by_code("6J")
    by_cutoff = junior.model_copy(update={"transition_after_months": None})
    assert (
        transitioned_level(ccnl, by_cutoff, Permanent(), date(2025, 11, 1), None).code
        == "6J"
    )
    for changes, message in (
        ({"transition_to": None}, "without a target"),
        ({"transition_to": "unknown"}, "invalid transition target"),
        ({"transition_to": "6J"}, "invalid transition target"),
    ):
        invalid_level = junior.model_copy(update=changes)
        invalid = ccnl.model_copy(update={"levels": (invalid_level, *ccnl.levels[1:])})
        with pytest.raises(ValueError, match=message):
            invalid._assert_level_transitions()
