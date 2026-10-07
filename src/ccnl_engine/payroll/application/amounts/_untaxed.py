"""Amounts of a run whose employer is not a withholding agent.

See :mod:`~ccnl_engine.payroll.service.withholding_agent`: the employer
withholds no IRPEF, surtax or substitute tax and pays no tax credit.  The
taxable income is still tracked year to date, since the worker declares it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.application.amounts._taxable import _PdrSplit, taxable_income
from ccnl_engine.payroll.application.amounts._types import _PeriodAmounts
from ccnl_engine.payroll.domain.tax import TaxComputation
from ccnl_engine.payroll.service.withholding_agent import (
    not_withholding_agent_decision,
    not_withholding_agent_decisions,
)

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.application.amounts._contributions import TfrAccrual
    from ccnl_engine.payroll.application.amounts._types import _AmountsInput
    from ccnl_engine.payroll.domain.contributions import ContributionBreakdown
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.payroll.service.pension_fund import PensionContribution

#: No IRPEF computed: no withholding, credit or conguaglio.
_NO_TAX = TaxComputation(
    ordinary_tax=_ZERO,
    trattamento_integrativo=_ZERO,
    withholding_due=_ZERO,
    components=(),
)


def _decisions(inp: _AmountsInput) -> tuple[CalculationDecision, ...]:
    """Return the skipped payroll tax decisions, PdR included when paid.

    Returns:
        One decision per payroll tax capability and one for a PdR routed
        to the substitute tax, which stays ordinary income.
    """
    year = inp.rules.year
    decisions = not_withholding_agent_decisions(year)
    if not inp.event_substitute_base:
        return decisions
    pdr = not_withholding_agent_decision(
        "bonus_pdr",
        year,
        {"eligible_amount": _ZERO, "ordinary_amount": inp.event_substitute_base},
    )
    return (*decisions, pdr)


def untaxed_amounts(
    inp: _AmountsInput,
    breakdown: ContributionBreakdown,
    employee_rate: Decimal,
    tfr: TfrAccrual,
    pension: PensionContribution | None = None,
) -> tuple[_PeriodAmounts, TaxComputation]:
    """Return the amounts of a run that withholds no tax.

    A PdR routed to the substitute tax is ordinary taxable income, since
    no withholding agent applies the substitute rate.

    Returns:
        The amounts, with nil taxes and credits, and an empty tax computation.
    """
    ordinary_pdr = _PdrSplit(
        eligible=_ZERO, excess=inp.event_substitute_base, substitute_tax=_ZERO
    )
    taxable = taxable_income(
        inp, breakdown.employee, employee_rate, ordinary_pdr, pension
    )
    amounts = _PeriodAmounts(
        monthly_gross=inp.monthly_gross,
        inps_employee=breakdown.employee,
        inps_employer=breakdown.employer,
        tfr=tfr,
        period_irpef=_ZERO,
        period_tratt=_ZERO,
        period_surtax=_ZERO,
        period_taxable=taxable.period,
        period_substitute_tax=_ZERO,
        pdr_eligible=_ZERO,
        projected_taxable=taxable.projected,
        decisions=_decisions(inp),
        pension=pension,
        issues=tfr.issues(),
    )
    return amounts, _NO_TAX
