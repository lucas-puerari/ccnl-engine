"""IRPEF and surtax withheld up to the pay available, the rest carried.

A run can owe more IRPEF and surtax than the pay it leaves after the
contributions and the other deductions, e.g. when unpaid absences take most
of the monthly pay.  The withholding agent withholds what the pay covers and
takes the rest on the next runs of the tax year: the cumulative method of the
conguaglio settles the tax on the whole year (art. 23 c. 3 DPR 600/1973,
in force for 2026; art. 33 c. 4 D.Lgs. 33/2025 from 1 January 2027, see
:mod:`~ccnl_engine.payroll.withholding.rules_law`).
The credit recoveries of the run (``CREDIT_RECOVERIES`` lines) are taken
first, then the IRPEF and the surtax from what is left.  The carried
amount is withheld in full on the next run, before any new share.  A
credit recovery the pay cannot cover, e.g. the residual of a recovery
settled at once on the last run of the employment (AdE circ. 29/E/2020
par. 6 and 4/E/2025 par. 1.2), is carried in the same way: the run posts
one ``credit_recovery_shortfall`` line that gives back the part not
withheld (``CREDIT_RECOVERY_SHORTFALL``), or withholds a part carried in
(``CREDIT_RECOVERIES``).

What is still not withheld on the last withholding slot "deve essere
comunicato all'interessato che deve provvedere al versamento entro il 15
gennaio dell'anno successivo" (art. 23 c. 3).  The engine reports it as a
provisional issue.  When the worker asked in writing to defer it, the IRPEF
part is withheld on the payslips of the next year instead
(:mod:`~ccnl_engine.payroll.withholding.services_deferral`).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.assurance.models_decision import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.ledger.models import AccountKind
from ccnl_engine.payroll.period.services_shared import _sum_ledger
from ccnl_engine.payroll.state.models_ytd_account import WithholdingShortfall
from ccnl_engine.payroll.withholding.rules_law import (
    WithholdingTopic,
    withholding_rule,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.amount.types import _PeriodAmounts
    from ccnl_engine.payroll.employment.inputs_fact import EmploymentPeriod
    from ccnl_engine.payroll.ledger.models import LedgerEntry
    from ccnl_engine.tax.annual.models import YearRules

__all__ = [
    "CappedWithholding",
    "cap_withholding",
    "ends_in_year",
    "run_net",
    "unrecovered_issue",
]

_ZERO = Decimal(0)
CAPABILITY = "withholding_shortfall"


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
        Cash earnings, TFR settled, credits paid, IRPEF and surtax refunded
        and credit
        recoveries given back, less the credits recovered, the employee
        contributions, bilateral and pension fund contributions, deductions
        and every tax withheld.
    """
    return (
        _sum_ledger(entries, AccountKind.CASH_EARNINGS)
        + _sum_ledger(entries, AccountKind.TFR_SETTLEMENT)
        + _sum_ledger(entries, AccountKind.CREDITS)
        + _sum_ledger(entries, AccountKind.TAX_REFUNDS)
        + _sum_ledger(entries, AccountKind.SURTAX_REFUNDS)
        + _sum_ledger(entries, AccountKind.CREDIT_RECOVERY_SHORTFALL)
        - _sum_ledger(entries, AccountKind.CREDIT_RECOVERIES)
        - _sum_ledger(entries, AccountKind.EMPLOYEE_CONTRIBUTIONS)
        - _sum_ledger(entries, AccountKind.BILATERAL_FUND_EMPLOYEE)
        - _sum_ledger(entries, AccountKind.PENSION_FUND_EMPLOYEE)
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
        shortfall: IRPEF, surtax and credit recoveries carried after the run.
        decisions: One decision when the run carried a shortfall in or out.
        issues: A provisional issue when a shortfall is left after the last
            withholding slot.
        recovery_adjustment: Amount of the ``credit_recovery_shortfall``
            line: positive for a recovery of the run not withheld, negative
            for a recovery carried in and withheld; zero without one.
    """

    amounts: _PeriodAmounts
    shortfall: WithholdingShortfall
    decisions: tuple[CalculationDecision, ...] = ()
    issues: tuple[CalculationIssue, ...] = ()
    recovery_adjustment: Decimal = _ZERO


def unrecovered_issue(
    shortfall: WithholdingShortfall, tax_year: int
) -> CalculationIssue:
    """Return the provisional issue of a shortfall left after the last slot.

    Args:
        shortfall: What the tax year leaves not withheld.
        tax_year: Tax year of the conguaglio, whose rule the issue cites.

    Returns:
        The ``withholding_shortfall_unrecovered`` issue.
    """
    law = withholding_rule(WithholdingTopic.CONGUAGLIO, tax_year)
    return CalculationIssue(
        code="withholding_shortfall_unrecovered",
        message=(
            f"withholding_shortfall: {shortfall.irpef} IRPEF, "
            f"{shortfall.surtax} surtax and {shortfall.credit_recovery} credit "
            "recovery of the tax year were not withheld for lack of pay; "
            f"{law.citation} requires the amount to be "
            "communicated to the worker, who pays it by 15 January of the "
            "next year unless a written deferral is agreed"
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
    """Cap the credit recoveries, IRPEF and surtax of a run at the pay left.

    Args:
        amounts: Amounts of the run; their IRPEF and surtax already include
            ``carried_in``.
        entries: Every ledger entry of the run, built from ``amounts``.
        carried_in: Shortfall the run opened with.
        last_slot: Whether no later run of the tax year withholds: the run
            closes the last withholding slot or ends the employment.
        rules: Year rules, whose version the decision records.

    Returns:
        The capped amounts, the shortfall carried after the run and the
        adjustment of the credit recoveries.  A refund (negative IRPEF) is
        never capped.
    """
    irpef_due = max(_ZERO, amounts.period_irpef)
    surtax_due = amounts.period_surtax
    run_recovery = _sum_ledger(entries, AccountKind.CREDIT_RECOVERIES)
    recovery_due = run_recovery + carried_in.credit_recovery
    available = max(_ZERO, run_net(entries) + irpef_due + surtax_due + run_recovery)
    recovered = min(recovery_due, available)
    irpef = min(irpef_due, available - recovered)
    surtax = min(surtax_due, available - recovered - irpef)
    shortfall = WithholdingShortfall(
        irpef=irpef_due - irpef,
        surtax=surtax_due - surtax,
        credit_recovery=recovery_due - recovered,
    )
    capped = (
        amounts
        if shortfall.irpef == _ZERO and shortfall.surtax == _ZERO
        else replace(
            amounts,
            period_irpef=amounts.period_irpef - shortfall.irpef,
            period_surtax=surtax,
        )
    )
    adjustment = run_recovery - recovered
    if carried_in.total == _ZERO and shortfall.total == _ZERO:
        return CappedWithholding(capped, shortfall)
    law = withholding_rule(WithholdingTopic.CONGUAGLIO, rules.year)
    decision = CalculationDecision(
        capability=CAPABILITY,
        status=CalculationStatus.FINAL,
        reason_code=("withholding_capped" if shortfall.total else "shortfall_withheld"),
        rule=law.rule,
        rule_version=(
            str(rules.year) if rules.ruleset is None else rules.ruleset.version
        ),
        inputs={
            "pay_available": available,
            "irpef_due": irpef_due,
            "surtax_due": surtax_due,
            "credit_recovery_due": recovery_due,
            "carried_in": carried_in.total,
        },
        source=law.source,
        amount=shortfall.total,
    )
    issues = (
        (unrecovered_issue(shortfall, rules.year),)
        if last_slot and shortfall.total
        else ()
    )
    return CappedWithholding(capped, shortfall, (decision,), issues, adjustment)
