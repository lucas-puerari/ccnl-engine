"""Checks of a period calculation that reject what no payslip can carry.

The run must be able to close next in its competence year and its
payment in its tax year.  Unpaid absences are
validated against the pay of the run before the run is computed.  IRPEF
and surtax are withheld only up to the pay left, the rest carried to the
next runs; a run whose other deductions (contributions, substitute tax,
recovery installments) still exceed its pay, for example the INPS share
of a large fringe benefit on a part-time salary, is rejected after it.
Both are caller-facing errors, raised before the reconciliation
invariants, whose violations are engine errors.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _sum_ledger
from ccnl_engine.payroll.application.invariants._types import RunFacts
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.run import run_identifier
from ccnl_engine.shared.domain.errors import InvalidInputError, OutOfScopeError

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.accrual import ExtraMonthAccrual
    from ccnl_engine.payroll.domain.ledger import LedgerEntry
    from ccnl_engine.payroll.domain.period import PeriodResult
    from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
    from ccnl_engine.tax.domain.ruleset import YearRules

__all__ = [
    "check_absences_within_pay",
    "check_net_covered",
    "resolve_payment",
    "run_facts",
]

_ZERO = Decimal(0)
_FEATURE = "absence"


def resolve_payment(request: PeriodCalculationRequest) -> PaymentId:
    """Return the payment the run closes and raise if it cannot close next.

    A run already closed in the opening state, before a closed run of its
    competence year, or whose payment cannot close in the tax year of the
    opening state raises
    :class:`~ccnl_engine.shared.domain.errors.InvalidInputError`.

    Returns:
        The payment of this period: its run and payment date.
    """
    run_id = run_identifier(
        request.run, request.period_id.year, request.period_id.month
    )
    payment = PaymentId(run_id=run_id, payment_date=request.payment_date)
    request.opening_state.check_next(payment)
    return payment


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


def check_net_covered(result: PeriodResult) -> None:
    """Reject a run whose pay does not cover its deductions.

    IRPEF and surtax are already capped at the pay left and carried, so a
    negative net comes from the other deductions of the run: the employee
    INPS share, which the employer withholds "sulla retribuzione
    corrisposta al lavoratore stesso alla scadenza del periodo di paga cui
    il contributo si riferisce" (L. 218/1952 art. 19), a substitute tax or
    a recovery installment.  Carrying them to a later payslip, or
    collecting them from the worker, is not modelled.

    Raises:
        OutOfScopeError: When the net pay is negative, with reason
            ``negative_net``.
    """
    if result.period_net >= _ZERO:
        return
    absences = (
        f" after unpaid absences of {result.unpaid_absence_deduction}"
        if result.unpaid_absence_deduction > _ZERO
        else ""
    )
    msg = (
        f"the net pay of the run is {result.period_net}{absences}: the "
        "deductions other than IRPEF and surtax (employee contributions, "
        "substitute tax, recovery installments) exceed the pay of the run, "
        "and carrying them to a later payslip is not modelled"
    )
    raise OutOfScopeError(
        msg,
        reason="negative_net",
        feature="net_pay",
        remediation=(
            "compute the deductions of this payslip manually and agree with "
            "the worker how the uncovered amount is settled"
        ),
    )


def run_facts(
    request: PeriodCalculationRequest,
    year_rules: YearRules,
    *,
    ivs_ceiling_applies: bool,
    pdr_cap: Decimal,
    accruals: tuple[ExtraMonthAccrual, ...],
    projected_taxable: Decimal | None,
    withholding_agent: bool,
) -> RunFacts:
    """Return the facts of the run the reconciliation invariants need.

    Returns:
        The employment, the massimale when it applies, the PdR limit, the
        ratei paid on the run, the taxable income its IRPEF used and
        whether the employer withholds tax.
    """
    inps = year_rules.inps
    ceiling = inps.ceiling if inps is not None and ivs_ceiling_applies else None
    return RunFacts(
        employment_period=request.employment_period,
        ivs_ceiling=ceiling,
        pdr_cap=pdr_cap,
        accruals=accruals,
        projected_taxable=projected_taxable,
        withholding_agent=withholding_agent,
    )
