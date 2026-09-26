"""State-transition reconciliation invariants (I11, I16, I18, I19).

These invariants verify that the closing PeriodState advances correctly
from the opening state, that YTD credit and cap fields stay within their
bounds, and that recoveries carried from an earlier tax year advance by
the installment the run posts.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._carried_recovery import carried_item_id
from ccnl_engine.payroll.application._reconcile_types import (
    ReconciliationViolation,
    _sum_account,
)
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.run import run_identifier

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodCalculationResult, PeriodState
    from ccnl_engine.payroll.domain.run import PayrollRunId

_ZERO = Decimal(0)


def _run_id(result: PeriodCalculationResult) -> PayrollRunId:
    """Return the run identifier the calculation closed.

    Returns:
        The identifier of ``result.run``, or of the regular run of the
        period without a run.
    """
    return run_identifier(result.run, result.period_id.year, result.period_id.month)


def check_i11(
    result: PeriodCalculationResult,
    opening: PeriodState,
) -> list[ReconciliationViolation]:
    """I11: closing state correctly advances from opening.

    Returns:
        Violations for any YTD field that does not advance as expected.
    """
    violations: list[ReconciliationViolation] = []
    run_id = _run_id(result)
    run_kind = run_id.kind

    expected_regular = opening.ytd.regular_periods_closed + (
        1 if run_kind == "regular" else 0
    )
    if result.closing_state.ytd.regular_periods_closed != expected_regular:
        violations.append(
            ReconciliationViolation(
                invariant_id="I11",
                message="regular_periods_closed not correctly incremented",
                expected=Decimal(expected_regular),
                actual=Decimal(result.closing_state.ytd.regular_periods_closed),
            )
        )

    expected_tax = opening.ytd.tax_withholding_periods_closed + (
        1 if run_kind.consumes_withholding_slot else 0
    )
    if result.closing_state.ytd.tax_withholding_periods_closed != expected_tax:
        violations.append(
            ReconciliationViolation(
                invariant_id="I11",
                message="tax_withholding_periods_closed not correctly incremented",
                expected=Decimal(expected_tax),
                actual=Decimal(result.closing_state.ytd.tax_withholding_periods_closed),
            )
        )

    if run_id not in result.closing_state.ytd.closed_run_ids:
        violations.append(
            ReconciliationViolation(
                invariant_id="I11",
                message=f"run_id '{run_id}' not added to closed_run_ids",
            )
        )

    expected_gross = opening.ytd.earnings.gross + _sum_account(
        result, AccountKind.CASH_EARNINGS
    )
    if result.closing_state.ytd.earnings.gross != expected_gross:
        violations.append(
            ReconciliationViolation(
                invariant_id="I11",
                message="gross_ytd not correctly accumulated from ledger",
                expected=expected_gross,
                actual=result.closing_state.ytd.earnings.gross,
            )
        )
    expected_inps = opening.ytd.earnings.inps_employee + _sum_account(
        result, AccountKind.EMPLOYEE_CONTRIBUTIONS
    )
    if result.closing_state.ytd.earnings.inps_employee != expected_inps:
        violations.append(
            ReconciliationViolation(
                invariant_id="I11",
                message="inps_employee_ytd not correctly accumulated from ledger",
                expected=expected_inps,
                actual=result.closing_state.ytd.earnings.inps_employee,
            )
        )
    return violations


def check_i16(
    result: PeriodCalculationResult,
) -> list[ReconciliationViolation]:
    """I16: each credit account recovers between zero and what it recognized.

    Checks the trattamento integrativo and the somma esente accounts.

    Returns:
        One violation per account that breaches the constraint.
    """
    ytd = result.closing_state.ytd
    return [
        ReconciliationViolation(
            invariant_id="I16",
            message=(
                f"{name} recovered outside [0, recognized]: "
                f"recovered={account.recovered}, recognized={account.recognized}"
            ),
            expected=account.recognized,
            actual=account.recovered,
        )
        for name, account in (
            ("trattamento", ytd.trattamento),
            ("somma_esente", ytd.somma_esente),
        )
        if account.recovered < _ZERO or account.recovered > account.recognized
    ]


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
    used = result.closing_state.ytd.work_time_regime.used
    expected = opening.ytd.work_time_regime.used + sum(
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


def check_i19(
    result: PeriodCalculationResult,
    opening: PeriodState,
) -> list[ReconciliationViolation]:
    """I19: recoveries carried from an earlier tax year advance by one step.

    Every recovery opened before the tax year of the run must post its next
    installment as a negative ``CREDITS`` entry, and the closing state must
    carry it one installment further, or no more after its last one.

    Returns:
        Violations for a missing or wrong installment and for carried
        recoveries that do not advance as expected.
    """
    tax_year = result.closing_state.tax_year
    if tax_year is None:
        return []
    carried = opening.obligations.carried_into(tax_year)
    run_id = str(_run_id(result))
    posted = {e.entry_id: e.amount for e in result.ledger_entries}
    violations = [
        ReconciliationViolation(
            invariant_id="I19",
            message=(
                f"carried recovery of {o.tax_year} did not post its installment "
                f"{o.plan.next_installment}"
            ),
            expected=-o.plan.next_installment,
            actual=posted.get(carried_item_id(o, run_id)),
        )
        for o in carried
        if posted.get(carried_item_id(o, run_id)) != -o.plan.next_installment
    ]
    expected = tuple(a for a in (o.advanced() for o in carried) if a is not None)
    if result.closing_state.obligations.carried_into(tax_year) != expected:
        violations.append(
            ReconciliationViolation(
                invariant_id="I19",
                message="carried recoveries not advanced by one installment",
            )
        )
    return violations
