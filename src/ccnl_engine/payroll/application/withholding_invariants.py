"""Withholding invariants: contribution ceiling and annual IRPEF.

Implemented invariants:
    contribution_ceiling: when the IVS massimale applies to the worker, the
        IVS base of the run fits in the headroom the YTD INPS base leaves
        (``max(0, massimale - opening inps_base)``).  The YTD INPS base
        itself is not capped: it measures the headroom, so it can exceed
        the massimale.
    irpef_annual_reconciliation: on the run that closes the last
        withholding slot of the tax year, the IRPEF withheld YTD plus the
        IRPEF the pay could not cover (still carried as a shortfall) and
        the ulteriore detrazione deferred to installments equals
        the net annual IRPEF of the tax computation, rebuilt from its
        components (gross IRPEF less the deductions, floored at zero),
        within one cent;
        and the taxable income that computation used equals the final
        taxable income YTD, within two cents of rounding (the projection
        rounds the employee INPS of the run on the total rate, the ledger
        per component).
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._reconcile_types import (
    InvariantCode,
    ReconciliationViolation,
)
from ccnl_engine.payroll.application.state_invariants import run_id_of
from ccnl_engine.payroll.domain.obligations import ULTERIORE_RECOVERY

if TYPE_CHECKING:
    from ccnl_engine.payroll.application._reconcile_types import RunFacts
    from ccnl_engine.payroll.domain.period import PeriodCalculationResult, PeriodState
    from ccnl_engine.payroll.domain.tax import TaxComputation

__all__: list[str] = []

_ZERO = Decimal(0)
_CENT = Decimal("0.01")
_TAXABLE_TOLERANCE = Decimal("0.02")
_IVS_COMPONENTS = frozenset({"ivs_employee", "ivs_employer"})
#: Tax computation components that lower the gross IRPEF.  The
#: sterilizzazione is recorded as a negative amount, so it adds back.
_DEDUCTIONS = frozenset({
    "work_deduction",
    "family_deductions",
    "ulteriore_detrazione",
    "sterilizzazione_detrazioni",
})


def check_contribution_ceiling(
    result: PeriodCalculationResult, opening: PeriodState, facts: RunFacts
) -> list[ReconciliationViolation]:
    """Check that the IVS base of the run stays within the massimale headroom.

    Returns:
        One violation per IVS component whose base exceeds the headroom;
        nothing when the ceiling does not apply.
    """
    ceiling = facts.ivs_ceiling
    if ceiling is None:
        return []
    headroom = max(_ZERO, ceiling - opening.ytd.earnings.inps_base)
    return [
        ReconciliationViolation(
            invariant_id=InvariantCode.CONTRIBUTION_CEILING,
            message=(
                f"{c.name} base {c.base} exceeds the massimale headroom {headroom}"
            ),
            expected=headroom,
            actual=c.base,
        )
        for c in result.contribution_breakdown.components
        if c.name in _IVS_COMPONENTS and c.base > headroom
    ]


def net_annual_irpef(computation: TaxComputation) -> Decimal:
    """Return the net annual IRPEF the components of ``computation`` give.

    Returns:
        ``max(0, irpef_gross - deductions)``, zero without ``irpef_gross``.
    """
    gross = _ZERO
    deductions = _ZERO
    for component in computation.components:
        if component.name == "irpef_gross":
            gross += component.amount
        elif component.name in _DEDUCTIONS:
            deductions += component.amount
    return max(_ZERO, gross - deductions)


def _closes_last_slot(result: PeriodCalculationResult, opening: PeriodState) -> bool:
    slots = result.closing_state.ytd.withholding_slots
    return (
        slots is not None
        and run_id_of(result).kind.consumes_withholding_slot
        and opening.ytd.tax_withholding_periods_closed + 1 == slots
    )


def check_irpef_annual_reconciliation(
    result: PeriodCalculationResult, opening: PeriodState, facts: RunFacts
) -> list[ReconciliationViolation]:
    """Check that the last withholding slot settles the IRPEF of the year.

    Returns:
        Violations when, on the run closing the last slot, the IRPEF
        withheld YTD plus the IRPEF shortfall still carried differs from
        the net annual IRPEF by more than a cent, or the taxable income of
        the tax computation differs from the final taxable income YTD by
        more than two cents.
    """
    if not _closes_last_slot(result, opening):
        return []
    violations: list[ReconciliationViolation] = []
    due = net_annual_irpef(result.tax_computation)
    ytd = result.closing_state.ytd
    deferred = result.closing_state.obligations.recovery_of(
        ytd.tax_year or 0, ULTERIORE_RECOVERY
    )
    withheld = (
        ytd.tax.irpef
        + ytd.shortfall.irpef
        + (_ZERO if deferred is None else deferred.residual)
    )
    if abs(withheld - due) > _CENT:
        violations.append(
            ReconciliationViolation(
                invariant_id=InvariantCode.IRPEF_ANNUAL_RECONCILIATION,
                message=(
                    "IRPEF withheld YTD and shortfall differ from the net annual IRPEF"
                ),
                expected=due,
                actual=withheld,
            )
        )
    projected = facts.projected_taxable
    final = result.closing_state.ytd.earnings.taxable
    if projected is not None and abs(projected - final) > _TAXABLE_TOLERANCE:
        violations.append(
            ReconciliationViolation(
                invariant_id=InvariantCode.IRPEF_ANNUAL_RECONCILIATION,
                message="IRPEF settled on a taxable income other than the final one",
                expected=final,
                actual=projected,
            )
        )
    return violations
