"""State-transition reconciliation invariants.

These invariants verify that the closing PeriodState advances correctly
from the opening state: the run counters, every YTD accumulator that the
ledger of the run determines, the credit accounts within their bounds, and
the recoveries carried from an earlier tax year.

The IRPEF withheld YTD is checked by ``irpef_withheld_continuity`` in
``ledger_invariants`` and the regime cap account by
``substitute_tax_plafond`` in ``decision_invariants``.  The INPS base and
the IRPEF taxable YTD are not derivable from the result without
recomputing the run, so they are not checked here.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._carried_recovery import carried_item_id
from ccnl_engine.payroll.application._reconcile_types import (
    InvariantCode,
    ReconciliationViolation,
    _sum_account,
)
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.run import run_identifier

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodResult, PeriodState
    from ccnl_engine.payroll.domain.run import PayrollRunId
    from ccnl_engine.payroll.domain.ytd_accounts import CreditAccount

_ZERO = Decimal(0)


def run_id_of(result: PeriodResult) -> PayrollRunId:
    """Return the run identifier the calculation closed.

    Returns:
        The identifier of ``result.run``, or of the regular run of the
        period without a run.
    """
    return run_identifier(result.run, result.period_id.year, result.period_id.month)


def _counter_violation(
    name: str, expected: int, actual: int
) -> ReconciliationViolation:
    return ReconciliationViolation(
        invariant_id=InvariantCode.RUN_COUNTERS_ADVANCE,
        message=f"{name} not correctly incremented",
        expected=Decimal(expected),
        actual=Decimal(actual),
    )


def check_run_counters(
    result: PeriodResult,
    opening: PeriodState,
) -> list[ReconciliationViolation]:
    """Check that the run counters and the closed run ids advance by the run.

    Returns:
        Violations for a counter that does not advance by one when the run
        counts for it, and for a run id missing from ``closed_run_ids``.
    """
    violations: list[ReconciliationViolation] = []
    run_id = run_id_of(result)
    closing = result.closing_state.ytd
    expected_regular = opening.ytd.regular_periods_closed + (
        1 if run_id.kind == "regular" else 0
    )
    if closing.regular_periods_closed != expected_regular:
        violations.append(
            _counter_violation(
                "regular_periods_closed",
                expected_regular,
                closing.regular_periods_closed,
            )
        )
    expected_slots = opening.ytd.tax_withholding_periods_closed + (
        1 if run_id.kind.consumes_withholding_slot else 0
    )
    if closing.tax_withholding_periods_closed != expected_slots:
        violations.append(
            _counter_violation(
                "tax_withholding_periods_closed",
                expected_slots,
                closing.tax_withholding_periods_closed,
            )
        )
    if run_id not in closing.closed_run_ids:
        violations.append(
            ReconciliationViolation(
                invariant_id=InvariantCode.RUN_COUNTERS_ADVANCE,
                message=f"run_id '{run_id}' not added to closed_run_ids",
            )
        )
    return violations


def _entry_total(result: PeriodResult, entry_ids: set[str]) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.entry_id in entry_ids), _ZERO
    )


def check_ytd_continuity(
    result: PeriodResult,
    opening: PeriodState,
) -> list[ReconciliationViolation]:
    """Check that each YTD accumulator closes at opening plus the run amount.

    Checked accumulators and the ledger amount of the run they advance by:

    - ``earnings.gross``: the CASH_EARNINGS total;
    - ``earnings.inps_employee``: the EMPLOYEE_CONTRIBUTIONS total;
    - ``tax.surtax``: the SURTAX total;
    - ``trattamento`` net credit: the ``tratt_integ_{run}`` entry;
    - ``somma_esente`` net credit: the ``somma_esente_{run}`` or
      ``somma_esente_recovery_{run}`` entry.

    Returns:
        One violation per accumulator that does not advance as expected.
    """
    run = str(run_id_of(result))
    op, closing = opening.ytd, result.closing_state.ytd
    checks: tuple[tuple[str, Decimal, Decimal, Decimal], ...] = (
        (
            "gross_ytd",
            op.earnings.gross,
            _sum_account(result, AccountKind.CASH_EARNINGS),
            closing.earnings.gross,
        ),
        (
            "inps_employee_ytd",
            op.earnings.inps_employee,
            _sum_account(result, AccountKind.EMPLOYEE_CONTRIBUTIONS),
            closing.earnings.inps_employee,
        ),
        (
            "surtax_ytd",
            op.tax.surtax,
            _sum_account(result, AccountKind.SURTAX),
            closing.tax.surtax,
        ),
        (
            "trattamento net credit",
            op.trattamento.net,
            _entry_total(result, {f"tratt_integ_{run}"}),
            closing.trattamento.net,
        ),
        (
            "somma_esente net credit",
            op.somma_esente.net,
            _entry_total(
                result, {f"somma_esente_{run}", f"somma_esente_recovery_{run}"}
            ),
            closing.somma_esente.net,
        ),
    )
    return [
        ReconciliationViolation(
            invariant_id=InvariantCode.YTD_CONTINUITY,
            message=f"{name} not correctly accumulated from ledger",
            expected=start + period,
            actual=end,
        )
        for name, start, period, end in checks
        if end != start + period
    ]


def _outside_bounds(account: CreditAccount) -> bool:
    return account.recovered < _ZERO or account.recovered > account.recognized


def check_credit_recovery_bounds(
    result: PeriodResult,
) -> list[ReconciliationViolation]:
    """Check that each credit account recovers within what it recognized.

    Checks the trattamento integrativo and the somma esente accounts.

    Returns:
        One violation per account that breaches the constraint.
    """
    ytd = result.closing_state.ytd
    return [
        ReconciliationViolation(
            invariant_id=InvariantCode.CREDIT_RECOVERY_BOUNDS,
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
        if _outside_bounds(account)
    ]


def check_carried_recovery_advance(
    result: PeriodResult,
    opening: PeriodState,
) -> list[ReconciliationViolation]:
    """Check that recoveries carried from an earlier year advance one step.

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
    run_id = str(run_id_of(result))
    posted = {e.entry_id: e.amount for e in result.ledger_entries}
    violations = [
        ReconciliationViolation(
            invariant_id=InvariantCode.CARRIED_RECOVERY_ADVANCE,
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
                invariant_id=InvariantCode.CARRIED_RECOVERY_ADVANCE,
                message="carried recoveries not advanced by one installment",
            )
        )
    return violations
