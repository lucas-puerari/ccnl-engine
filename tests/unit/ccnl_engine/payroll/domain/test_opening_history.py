"""Whether the opening state of a run holds the history of the employment."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.accrual_state import EmploymentAccrualState
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.obligations import (
    EmploymentObligations,
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.opening_history import (
    opening_gap,
    opening_state_issue,
)
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.run import PayrollRunId, RunKind
from ccnl_engine.payroll.domain.tax_cash_state import TaxCashState

_JUNE = PayrollRunId(2026, 6, RunKind.REGULAR)
_JANUARY = PayrollRunId(2026, 1, RunKind.REGULAR)
_ZERO = PeriodState.zero()


def _closed(*months: int) -> PeriodState:
    """Return a state that closed the regular runs of ``months`` of 2026.

    Returns:
        The state, bound to no tax year.
    """
    runs = tuple(PayrollRunId(2026, m, RunKind.REGULAR) for m in months)
    return PeriodState(accrual=EmploymentAccrualState(competence_runs=runs))


@pytest.mark.parametrize(
    ("opening", "run_id", "started_on"),
    [
        pytest.param(_ZERO, _JUNE, date(2026, 6, 15), id="first_run_of_a_hire"),
        pytest.param(
            _closed(1, 2, 3, 4, 5), _JUNE, date(2026, 1, 1), id="chained_from_may"
        ),
        pytest.param(
            _closed(3, 4, 5), _JUNE, date(2026, 3, 15), id="chained_from_the_hire"
        ),
        pytest.param(
            PeriodState(cash=TaxCashState(tax_year=2026)),
            _JANUARY,
            date(2020, 1, 1),
            id="january_after_close_tax_year",
        ),
        pytest.param(
            _ZERO,
            PayrollRunId(2026, 12, RunKind.REGULAR),
            date(2027, 2, 1),
            id="start_after_the_competence_year",
        ),
        pytest.param(
            _ZERO,
            PayrollRunId(2026, 12, RunKind.THIRTEENTH),
            date(2026, 12, 1),
            id="extra_month_of_the_hire_month",
        ),
    ],
)
def test_a_state_that_holds_the_history_has_no_gap(
    opening: PeriodState, run_id: PayrollRunId, started_on: date
) -> None:
    """The first run of a stated start, or a state of every earlier month."""
    assert opening_gap(opening, run_id, started_on) is None
    assert opening_state_issue(opening, run_id, started_on) is None


def test_a_state_built_by_hand_with_carried_obligations_is_a_statement() -> None:
    """Obligations carried into January state what the year before left."""
    plan = RecoveryPlan(
        kind="trattamento_integrativo",
        original_amount=Decimal(160),
        installment_amount=Decimal(20),
        installments_total=8,
        installments_posted=3,
    )
    obligations = EmploymentObligations(
        recoveries=(RecoveryObligation(tax_year=2025, plan=plan),)
    )
    carried = PeriodState(cash=TaxCashState(obligations=obligations))

    assert opening_gap(carried, _JANUARY, date(2020, 1, 1)) is None


@pytest.mark.parametrize(
    ("opening", "run_id", "started_on", "gap"),
    [
        pytest.param(
            _ZERO, _JUNE, date(2026, 1, 1), "months [1, 2, 3, 4, 5]", id="zero_in_june"
        ),
        pytest.param(
            _closed(3, 5), _JUNE, date(2026, 3, 15), "months [4]", id="broken_chain"
        ),
        pytest.param(_closed(1, 2), _JUNE, None, "months [3, 4, 5]", id="no_start"),
        pytest.param(
            _ZERO, _JANUARY, date(2020, 1, 1), "is 2020-01-01", id="cross_year"
        ),
        pytest.param(_ZERO, _JANUARY, None, "is not stated", id="january_no_start"),
        pytest.param(
            PeriodState(history_known=False),
            _JANUARY,
            date(2026, 1, 1),
            "descends from a run",
            id="tainted",
        ),
    ],
)
def test_a_state_that_misses_the_history_has_a_gap(
    opening: PeriodState, run_id: PayrollRunId, started_on: date | None, gap: str
) -> None:
    """A missing month, an unknown earlier year or an inherited gap."""
    found = opening_gap(opening, run_id, started_on)
    issue = opening_state_issue(opening, run_id, started_on)

    assert found is not None
    assert gap in found
    assert issue is not None
    assert issue.fact == "opening_state"
    assert issue.code == "opening_state_unknown"
    assert issue.status is CalculationStatus.INCOMPLETE
    assert found in issue.message
