"""Checks of a period calculation that reject what no payslip can carry.

The run must be able to close next in its tax year.  Unpaid absences are
validated against the pay of the run before the run is computed.  IRPEF
and surtax are withheld only up to the pay left, the rest carried to the
next runs; a run whose other deductions (contributions, substitute tax,
recovery installments) still exceed the pay left by the absences is
rejected after it.  Both are caller-facing errors, raised before the
reconciliation invariants, whose violations are engine errors.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.errors import InvalidInputError, OutOfScopeError
from ccnl_engine.payroll.application._period_utils import _sum_ledger
from ccnl_engine.payroll.application._reconcile_types import RunFacts
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.run import run_identifier

if TYPE_CHECKING:
    from ccnl_engine.engine.tax.domain.rules import YearRules
    from ccnl_engine.payroll.domain.accrual import ExtraMonthAccrual
    from ccnl_engine.payroll.domain.ledger import LedgerEntry
    from ccnl_engine.payroll.domain.period import (
        PeriodCalculationRequest,
        PeriodCalculationResult,
    )
    from ccnl_engine.payroll.domain.run import PayrollRunId

__all__ = [
    "check_absences_within_pay",
    "check_net_covered",
    "resolve_run_id",
    "run_facts",
]

_ZERO = Decimal(0)
_FEATURE = "absence"


def resolve_run_id(request: PeriodCalculationRequest) -> PayrollRunId:
    """Return the run identifier and raise if the run cannot close next.

    Returns:
        The identifier of the run of this period.

    Raises:
        InvalidInputError: When the run was already closed in the opening
            state, is of a later year, or comes before a closed run.
    """
    run_id = run_identifier(
        request.run, request.period_id.year, request.period_id.month
    )
    try:
        request.opening_state.ytd.check_next_run(run_id)
    except ValueError as exc:
        raise InvalidInputError(str(exc), feature="payroll_run") from exc
    return run_id


def check_absences_within_pay(
    entries: tuple[LedgerEntry, ...], period_pay: Decimal
) -> None:
    """Reject unpaid absences that deduct more than the pay of the run.

    Args:
        entries: Ledger entries of the events of the run.
        period_pay: Contractual pay of the run the absences are deducted
            from.

    Raises:
        InvalidInputError: When the EMPLOYEE_DEDUCTIONS of ``entries``
            exceed ``period_pay``.
    """
    deducted = _sum_ledger(entries, AccountKind.EMPLOYEE_DEDUCTIONS)
    if deducted > period_pay:
        msg = (
            f"unpaid absences deduct {deducted}, more than the pay of the "
            f"run ({period_pay}): check the absence hours and hourly rate"
        )
        raise InvalidInputError(msg, feature=_FEATURE)


def check_net_covered(result: PeriodCalculationResult) -> None:
    """Reject a run whose absences leave less pay than the deductions.

    IRPEF and surtax are already capped at the pay left, so a negative net
    here comes from the other deductions of the run.

    Raises:
        OutOfScopeError: When the net pay is negative and the run deducts
            unpaid absences: the contributions and other deductions due
            exceed the pay left, and carrying them forward is not
            modelled.  A negative net without absences is left to the
            ``net_pay_non_negative`` invariant.
    """
    if result.period_net >= _ZERO or result.unpaid_absence_deduction <= _ZERO:
        return
    msg = (
        f"unpaid absences of {result.unpaid_absence_deduction} leave a net "
        f"pay of {result.period_net}: the deductions other than IRPEF and "
        "surtax exceed the pay left, and carrying them to a later payslip "
        "is not modelled"
    )
    raise OutOfScopeError(
        msg,
        reason="withholding_shortfall",
        feature=_FEATURE,
        remediation="compute the withholdings of this payslip manually",
    )


def run_facts(
    request: PeriodCalculationRequest,
    year_rules: YearRules,
    *,
    ivs_ceiling_applies: bool,
    pdr_cap: Decimal,
    accrual: ExtraMonthAccrual | None,
    projected_taxable: Decimal | None,
) -> RunFacts:
    """Return the facts of the run the reconciliation invariants need.

    Returns:
        The employment, the massimale when it applies, the PdR limit, the
        ratei paid on the run and the taxable income its IRPEF used.
    """
    inps = year_rules.inps
    ceiling = inps.ceiling if inps is not None and ivs_ceiling_applies else None
    accruals = (() if accrual is None else (accrual,)) + tuple(
        request.extra_month_settlements
    )
    return RunFacts(
        employment_period=request.employment_period,
        ivs_ceiling=ceiling,
        pdr_cap=pdr_cap,
        accruals=accruals,
        projected_taxable=projected_taxable,
    )
