"""Ordinary contribution of the solidarity fund of the CCNL on one run.

The decree of each bilateral fund of D.Lgs. 148/2015 art. 26 charges its
ordinary contribution on the INPS taxable pay of "tutti i lavoratori
dipendenti con contratto a tempo indeterminato, compresi i dirigenti"
(INPS circ. 90/2015 for the credito fund).  An apprenticeship is a
permanent contract (D.Lgs. 81/2015 art. 41 c. 1), so apprentices owe it;
a fixed-term worker does not.  The worker's share is a social contribution
withheld from the pay, like the INPS employee rate.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ccnl_engine.payroll.amount.policies_rounding import money
from ccnl_engine.payroll.contribution.results import ContributionComponent
from ccnl_engine.payroll.employment.inputs import FixedTerm
from ccnl_engine.payroll.period.services_shared import _ZERO

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.amount.types import _AmountsInput
    from ccnl_engine.payroll.contribution.results import ContributionBreakdown

__all__ = ["EMPLOYEE_COMPONENT", "EMPLOYER_COMPONENT", "with_solidarity_fund"]

#: Component of the worker's share of the fund contribution.
EMPLOYEE_COMPONENT = "solidarity_fund_employee"
#: Component of the employer's share of the fund contribution.
EMPLOYER_COMPONENT = "solidarity_fund_employer"
_BASES = ("non_ivs_employer", "ivs_employer")


def _base(breakdown: ContributionBreakdown) -> Decimal:
    """Return the INPS taxable base of the run, uncapped by the massimale.

    Returns:
        The base of the non-IVS employer component, else of the IVS one,
        else zero.
    """
    bases = {c.name: c.base for c in breakdown.components}
    return next((bases[name] for name in _BASES if name in bases), _ZERO)


def with_solidarity_fund(
    inp: _AmountsInput, breakdown: ContributionBreakdown
) -> tuple[ContributionBreakdown, Decimal]:
    """Return ``breakdown`` with the fund contribution of a permanent worker.

    Returns:
        The breakdown with the employee and employer components added to
        their totals, and the employee rate; ``breakdown`` and zero when
        the CCNL has no fund or the contract is a fixed term.
    """
    fund = inp.solidarity_fund
    if fund is None or isinstance(inp.contract_type, FixedTerm):
        return breakdown, _ZERO
    base = _base(breakdown)
    employee = money(base * fund.employee_rate)
    employer = money(base * fund.employer_rate)
    components = (
        ContributionComponent(EMPLOYEE_COMPONENT, base, fund.employee_rate, employee),
        ContributionComponent(EMPLOYER_COMPONENT, base, fund.employer_rate, employer),
    )
    added = replace(
        breakdown,
        employee=breakdown.employee + employee,
        employer=breakdown.employer + employer,
        components=(*breakdown.components, *components),
    )
    return added, fund.employee_rate
