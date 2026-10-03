"""State-transition reconciliation invariants.

These invariants verify that the closing PeriodState advances correctly
from the opening state: the competence run and the payment closed once,
the withholding counter, every YTD accumulator that the
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

from ccnl_engine.payroll.application.invariants._types import (
    InvariantCode,
    ReconciliationViolation,
    _sum_account,
)
from ccnl_engine.payroll.application.withholding._carried_recovery import (
    carried_item_id,
)
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.recovery_plan import InstallmentRun
from ccnl_engine.payroll.domain.run import run_identifier

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.credit_accounts import CreditAccount
    from ccnl_engine.payroll.domain.obligations import RecoveryObligation
    from ccnl_engine.payroll.domain.period import PeriodResult
    from ccnl_engine.payroll.domain.period_state import PeriodState
    from ccnl_engine.payroll.domain.run import PayrollRunId

_ZERO = Decimal(0)


def run_id_of(result: PeriodResult) -> PayrollRunId:
    """Return the run identifier the calculation closed.

    Returns:
        The identifier of ``result.run``, or of the regular run of the
        period without a run.
    """
    return run_identifier(result.run, result.period_id.year, result.period_id.month)


def check_run_counters(
    result: PeriodResult,
    opening: PeriodState,
) -> list[ReconciliationViolation]:
    """Check that the run closes its competence run and its payment once.

    Returns:
        Violations when the accrual state does not append exactly the run,
        or the tax cash state does not append exactly its payment.
    """
    violations: list[ReconciliationViolation] = []
    run_id = run_id_of(result)
    closing = result.closing_state
    if closing.accrual.competence_runs != (*opening.accrual.competence_runs, run_id):
        violations.append(
            ReconciliationViolation(
                invariant_id=InvariantCode.RUN_COUNTERS_ADVANCE,
                message=f"competence run '{run_id}' not closed once",
            )
        )
    payments = closing.cash.payments
    closed = [p.run_id for p in payments[len(opening.cash.payments) :]]
    if payments[: len(opening.cash.payments)] != opening.cash.payments or closed != [
        run_id
    ]:
        violations.append(
            ReconciliationViolation(
                invariant_id=InvariantCode.RUN_COUNTERS_ADVANCE,
                message=f"payment of run '{run_id}' not closed once",
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
    - ``tax.surtax``: the SURTAX total less the SURTAX_REFUNDS total;
    - ``trattamento`` net credit: the ``tratt_integ_{run}`` entry less the
      ``tratt_integ_recovery_{run}`` entry;
    - ``somma_esente`` net credit: the ``somma_esente_{run}`` entry less the
      ``somma_esente_recovery_{run}`` entry.

    Returns:
        One violation per accumulator that does not advance as expected.
    """
    run = str(run_id_of(result))
    op, closing = opening.cash, result.closing_state.cash
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
            _sum_account(result, AccountKind.SURTAX)
            - _sum_account(result, AccountKind.SURTAX_REFUNDS),
            closing.tax.surtax,
        ),
        (
            "trattamento net credit",
            op.trattamento.net,
            _entry_total(result, {f"tratt_integ_{run}"})
            - _entry_total(result, {f"tratt_integ_recovery_{run}"}),
            closing.trattamento.net,
        ),
        (
            "somma_esente net credit",
            op.somma_esente.net,
            _entry_total(result, {f"somma_esente_{run}"})
            - _entry_total(result, {f"somma_esente_recovery_{run}"}),
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
    ytd = result.closing_state.cash
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


def _expected_step(
    obligation: RecoveryObligation, posted: Decimal | None
) -> tuple[Decimal, RecoveryObligation | None]:
    """Return the amount ``obligation`` should post and what should remain.

    A run posts the next installment and advances the plan by one, or, on
    the last run of the employment, posts the whole residual and settles
    it.  The posted amount tells which one the run did.

    Returns:
        ``(expected_amount, expected_remaining)``.
    """
    if posted == obligation.plan.residual:
        return obligation.plan.residual, None
    step, after = obligation.post(InstallmentRun())
    return step.amount, after


def check_carried_recovery_advance(
    result: PeriodResult,
    opening: PeriodState,
) -> list[ReconciliationViolation]:
    """Check that recoveries carried from an earlier year advance one step.

    Every recovery opened before the tax year of the run must post its next
    installment as a ``CREDIT_RECOVERIES`` entry, and the closing state must
    carry it one installment further, or no more after its last one.  On
    the last run of the employment the recovery may instead post its whole
    residual and close.

    Returns:
        Violations for a missing or wrong installment and for carried
        recoveries that do not advance as expected.
    """
    tax_year = result.closing_state.tax_year
    if tax_year is None:
        return []
    carried = opening.cash.obligations.carried_into(tax_year)
    run_id = str(run_id_of(result))
    posted = {e.entry_id: e.amount for e in result.ledger_entries}
    violations: list[ReconciliationViolation] = []
    expected: list[RecoveryObligation] = []
    for o in carried:
        actual = posted.get(carried_item_id(o, run_id))
        amount, after = _expected_step(o, actual)
        if actual != amount:
            violations.append(
                ReconciliationViolation(
                    invariant_id=InvariantCode.CARRIED_RECOVERY_ADVANCE,
                    message=(
                        f"carried recovery of {o.tax_year} did not post its "
                        f"installment {amount}"
                    ),
                    expected=amount,
                    actual=actual,
                )
            )
        if after is not None:
            expected.append(after)
    if result.closing_state.cash.obligations.carried_into(tax_year) != tuple(expected):
        violations.append(
            ReconciliationViolation(
                invariant_id=InvariantCode.CARRIED_RECOVERY_ADVANCE,
                message="carried recoveries not advanced by one installment",
            )
        )
    return violations
