"""The seniority of a run: required, missing, and the reason it records."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.assurance.models_decision import CalculationStatus
from ccnl_engine.payroll.employment.inputs_seniority import (
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.payroll.employment.services_seniority import (
    FACT,
    INCREMENTS_APPLIED,
    NOT_APPLICABLE_BY_CONTRACT,
    REASONS,
    REQUIRED_FACT_MISSING,
    ZERO_CONFIRMED,
    RunSeniority,
    seniority_months_at,
)

_FACT = SeniorityFact(30, date(2026, 6, 1), SenioritySource.PAYSLIP)
_ZERO = Decimal("0.00")


def _run(
    *,
    fact: SeniorityFact | None = _FACT,
    increments: bool = True,
    gated: tuple[str, ...] = (),
    amount: Decimal = _ZERO,
) -> RunSeniority:
    return RunSeniority(
        fact=fact,
        months=None if fact is None else fact.months,
        increments=increments,
        gated=gated,
        amount=amount,
        source=None,
    )


@pytest.mark.parametrize(
    ("run", "reason"),
    [
        (_run(fact=None), REQUIRED_FACT_MISSING),
        (_run(fact=None, increments=False, gated=("PREMIO",)), REQUIRED_FACT_MISSING),
        (_run(fact=None, increments=False), NOT_APPLICABLE_BY_CONTRACT),
        (_run(increments=False, gated=("PREMIO",)), NOT_APPLICABLE_BY_CONTRACT),
        (_run(), ZERO_CONFIRMED),
        (_run(amount=Decimal("56.66")), INCREMENTS_APPLIED),
    ],
    ids=[
        "unknown-with-increments",
        "unknown-with-gated-allowance",
        "unknown-without-either",
        "known-gated-allowance-only",
        "known-zero",
        "known-increments",
    ],
)
def test_reason(run: RunSeniority, reason: str) -> None:
    """Every run records one of the four reasons."""
    assert run.reason == reason
    assert run.reason in REASONS


def test_missing_fact_issue_names_the_public_field() -> None:
    """The issue is incomplete and names ``seniority`` and the allowances."""
    issue = _run(fact=None, gated=("PREMIO_5YR",)).issue()

    assert issue is not None
    assert issue.fact == FACT == "seniority"
    assert issue.code == "seniority_unknown"
    assert issue.status is CalculationStatus.INCOMPLETE
    assert "PREMIO_5YR" in issue.message


@pytest.mark.parametrize(
    "run",
    [_run(), _run(fact=None, increments=False)],
    ids=["known", "not-required"],
)
def test_no_issue_when_the_fact_is_not_missing(run: RunSeniority) -> None:
    """A known or unneeded seniority raises no issue."""
    assert run.issue() is None


def test_months_at_run() -> None:
    """The fact is aged to the competence date; unknown stays unknown."""
    assert seniority_months_at(_FACT, date(2026, 7, 1)) == 31
    assert seniority_months_at(None, date(2026, 7, 1)) is None
