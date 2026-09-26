"""IRPEF and surtax withheld up to the pay available, the rest carried.

A run can owe more IRPEF and surtax than the pay it leaves after the
contributions and the other deductions, e.g. when unpaid absences take most
of the monthly pay.  The withholding agent withholds what the pay covers and
takes the rest on the next runs of the tax year: the cumulative method of the
conguaglio settles the tax on the whole year (art. 33 c. 4 D.Lgs. 33/2025,
ex art. 23 c. 3 DPR 600/1973, in force from 1 January 2026 by art. 243).
IRPEF is withheld first and the surtax from what is left.  The carried
amount is withheld in full on the next run, before any new share.

What is still not withheld on the last withholding slot "deve essere
comunicato all'interessato che deve provvedere al versamento entro il 15
gennaio dell'anno successivo" (art. 33 c. 4).  The engine reports it as a
provisional issue; the written request of the worker to defer it on the
next pay periods, with interest at 0.50 per cent a month, is not modelled.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _sum_ledger
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.ytd_accounts import WithholdingShortfall

if TYPE_CHECKING:
    from ccnl_engine.engine.tax.domain.ruleset import YearRules
    from ccnl_engine.payroll.application._period_amounts import _PeriodAmounts
    from ccnl_engine.payroll.domain.employment import EmploymentPeriod
    from ccnl_engine.payroll.domain.ledger import LedgerEntry

__all__ = ["CappedWithholding", "cap_withholding", "ends_in_year", "run_net"]

_ZERO = Decimal(0)
CAPABILITY = "withholding_shortfall"
_RULE = "dlgs33-2025-art33-c4"


def ends_in_year(period: EmploymentPeriod | None, tax_year: int) -> bool:
    """Whether the employment ends within ``tax_year``.

    Returns:
        ``True`` when ``period`` has an end date in ``tax_year`` or before:
        no payslip of a later year follows the conguaglio.
    """
    return (
        period is not None
        and period.ended_on is not None
        and period.ended_on.year <= tax_year
    )


def run_net(entries: tuple[LedgerEntry, ...]) -> Decimal:
    """Return the net pay of the ledger ``entries`` of a run.

    Returns:
        Cash earnings, TFR settled and credits, less the employee
        contributions, bilateral fund, deductions and every tax withheld.
    """
    return (
        _sum_ledger(entries, AccountKind.CASH_EARNINGS)
        + _sum_ledger(entries, AccountKind.TFR_SETTLEMENT)
        + _sum_ledger(entries, AccountKind.CREDITS)
        - _sum_ledger(entries, AccountKind.EMPLOYEE_CONTRIBUTIONS)
        - _sum_ledger(entries, AccountKind.BILATERAL_FUND_EMPLOYEE)
        - _sum_ledger(entries, AccountKind.EMPLOYEE_DEDUCTIONS)
        - _sum_ledger(entries, AccountKind.SUBSTITUTE_TAX)
        - _sum_ledger(entries, AccountKind.ORDINARY_TAX)
        - _sum_ledger(entries, AccountKind.SURTAX)
        - _sum_ledger(entries, AccountKind.SEPARATE_TAX)
    )


@dataclass(frozen=True)
class CappedWithholding:
    """Withholding of a run after the cap on the pay available.

    Attributes:
        amounts: The amounts of the run with IRPEF and surtax capped; the
            same object when nothing was capped.
        shortfall: IRPEF and surtax carried after the run.
        decisions: One decision when the run carried a shortfall in or out.
        issues: A provisional issue when a shortfall is left after the last
            withholding slot.
    """

    amounts: _PeriodAmounts
    shortfall: WithholdingShortfall
    decisions: tuple[CalculationDecision, ...] = ()
    issues: tuple[CalculationIssue, ...] = ()


def _unrecovered_issue(shortfall: WithholdingShortfall) -> CalculationIssue:
    return CalculationIssue(
        code="withholding_shortfall_unrecovered",
        message=(
            f"withholding_shortfall: {shortfall.irpef} IRPEF and "
            f"{shortfall.surtax} surtax of the tax year were not withheld "
            "for lack of pay; art. 33 c. 4 D.Lgs. 33/2025 requires the "
            "amount to be communicated to the worker, who pays it by 15 "
            "January of the next year unless a written deferral is agreed"
        ),
        status=CalculationStatus.PROVISIONAL,
    )


def cap_withholding(
    amounts: _PeriodAmounts,
    entries: tuple[LedgerEntry, ...],
    carried_in: WithholdingShortfall,
    *,
    last_slot: bool,
    rules: YearRules,
) -> CappedWithholding:
    """Cap the IRPEF and surtax of a run at the pay it leaves.

    Args:
        amounts: Amounts of the run; their IRPEF and surtax already include
            ``carried_in``.
        entries: Every ledger entry of the run, built from ``amounts``.
        carried_in: Shortfall the run opened with.
        last_slot: Whether the run closes the last withholding slot.
        rules: Year rules, whose version the decision records.

    Returns:
        The capped amounts and the shortfall carried after the run.  A
        refund (negative IRPEF) is never capped.
    """
    irpef_due = max(_ZERO, amounts.period_irpef)
    surtax_due = amounts.period_surtax
    available = max(_ZERO, run_net(entries) + irpef_due + surtax_due)
    irpef = min(irpef_due, available)
    surtax = min(surtax_due, available - irpef)
    shortfall = WithholdingShortfall(
        irpef=irpef_due - irpef, surtax=surtax_due - surtax
    )
    capped = (
        amounts
        if shortfall.total == _ZERO
        else replace(
            amounts,
            period_irpef=amounts.period_irpef - shortfall.irpef,
            period_surtax=surtax,
        )
    )
    if carried_in.total == _ZERO and shortfall.total == _ZERO:
        return CappedWithholding(capped, shortfall)
    decision = CalculationDecision(
        capability=CAPABILITY,
        status=CalculationStatus.FINAL,
        reason_code=("withholding_capped" if shortfall.total else "shortfall_withheld"),
        rule=_RULE,
        rule_version=(
            str(rules.year) if rules.ruleset is None else rules.ruleset.version
        ),
        inputs={
            "pay_available": available,
            "irpef_due": irpef_due,
            "surtax_due": surtax_due,
            "carried_in": carried_in.total,
        },
        amount=shortfall.total,
    )
    issues = (_unrecovered_issue(shortfall),) if last_slot and shortfall.total else ()
    return CappedWithholding(capped, shortfall, (decision,), issues)
