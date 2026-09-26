"""State-transition reconciliation invariants (I11, I16, I18).

These invariants verify that the closing PeriodState advances correctly
from the opening state, and that YTD credit and cap fields stay within their
bounds.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._reconcile_types import (
    ReconciliationViolation,
    _sum_account,
)
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.run import RunKind

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodCalculationResult, PeriodState

_ZERO = Decimal(0)


def check_i11(
    result: PeriodCalculationResult,
    opening: PeriodState,
) -> list[ReconciliationViolation]:
    """I11: closing state correctly advances from opening.

    Returns:
        Violations for any YTD field that does not advance as expected.
    """
    violations: list[ReconciliationViolation] = []
    run_kind = result.run.run_kind if result.run is not None else RunKind.REGULAR
    run_id = (
        result.run.run_id
        if result.run is not None
        else f"{result.period_id.year}_{result.period_id.month:02d}"
    )

    expected_regular = opening.regular_periods_closed + (
        1 if run_kind == "regular" else 0
    )
    if result.closing_state.regular_periods_closed != expected_regular:
        violations.append(
            ReconciliationViolation(
                invariant_id="I11",
                message="regular_periods_closed not correctly incremented",
                expected=Decimal(expected_regular),
                actual=Decimal(result.closing_state.regular_periods_closed),
            )
        )

    expected_tax = opening.tax_withholding_periods_closed + (
        1 if run_kind.consumes_withholding_slot else 0
    )
    if result.closing_state.tax_withholding_periods_closed != expected_tax:
        violations.append(
            ReconciliationViolation(
                invariant_id="I11",
                message="tax_withholding_periods_closed not correctly incremented",
                expected=Decimal(expected_tax),
                actual=Decimal(result.closing_state.tax_withholding_periods_closed),
            )
        )

    if run_id not in result.closing_state.closed_run_ids:
        violations.append(
            ReconciliationViolation(
                invariant_id="I11",
                message=f"run_id {run_id!r} not added to closed_run_ids",
            )
        )

    expected_gross = opening.earnings.gross + _sum_account(
        result, AccountKind.CASH_EARNINGS
    )
    if result.closing_state.earnings.gross != expected_gross:
        violations.append(
            ReconciliationViolation(
                invariant_id="I11",
                message="gross_ytd not correctly accumulated from ledger",
                expected=expected_gross,
                actual=result.closing_state.earnings.gross,
            )
        )
    expected_inps = opening.earnings.inps_employee + _sum_account(
        result, AccountKind.EMPLOYEE_CONTRIBUTIONS
    )
    if result.closing_state.earnings.inps_employee != expected_inps:
        violations.append(
            ReconciliationViolation(
                invariant_id="I11",
                message="inps_employee_ytd not correctly accumulated from ledger",
                expected=expected_inps,
                actual=result.closing_state.earnings.inps_employee,
            )
        )
    return violations


def check_i16(
    result: PeriodCalculationResult,
) -> list[ReconciliationViolation]:
    """I16: credit_recovered_ytd is between zero and credit_recognized_ytd.

    Returns:
        A violation when the constraint is breached.
    """
    recovered = result.closing_state.trattamento.recovered
    recognized = result.closing_state.trattamento.recognized
    if recovered < _ZERO or recovered > recognized:
        return [
            ReconciliationViolation(
                invariant_id="I16",
                message=(
                    "credit_recovered_ytd outside [0, credit_recognized_ytd]: "
                    f"recovered={recovered}, recognized={recognized}"
                ),
                expected=recognized,
                actual=recovered,
            )
        ]
    return []


def check_i18(
    result: PeriodCalculationResult,
    opening: PeriodState,
) -> list[ReconciliationViolation]:
    """I18: the work-time regime cap account advances by the eligible amounts.

    The closing ``work_time_regime.used`` must equal the opening value plus
    the ``eligible_amount`` of every capped regime decision of the run, and
    must not exceed the ``annual_cap`` those decisions record.

    Returns:
        Violations for a wrong advance or a used amount above the cap.
    """
    capped = [d for d in result.decisions if "annual_cap" in d.inputs]
    used = result.closing_state.work_time_regime.used
    expected = opening.work_time_regime.used + sum(
        (Decimal(d.inputs["eligible_amount"]) for d in capped), _ZERO
    )
    violations: list[ReconciliationViolation] = []
    if used != expected:
        violations.append(
            ReconciliationViolation(
                invariant_id="I18",
                message="work_time_regime.used not advanced by the eligible amounts",
                expected=expected,
                actual=used,
            )
        )
    caps = {Decimal(d.inputs["annual_cap"]) for d in capped}
    violations.extend(
        ReconciliationViolation(
            invariant_id="I18",
            message=f"work_time_regime.used {used} exceeds the annual cap {cap}",
            expected=cap,
            actual=used,
        )
        for cap in sorted(caps)
        if used > cap
    )
    return violations
