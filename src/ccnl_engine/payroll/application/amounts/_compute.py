"""Amounts of one run: contributions, taxable, IRPEF and surtax in sequence."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.amounts._contributions import (
    run_contributions,
    tfr_accrual,
)
from ccnl_engine.payroll.application.amounts._irpef import withhold_irpef
from ccnl_engine.payroll.application.amounts._surtax import run_surtax
from ccnl_engine.payroll.application.amounts._taxable import (
    pdr_split,
    taxable_income,
)
from ccnl_engine.payroll.application.amounts._types import _PeriodAmounts
from ccnl_engine.payroll.application.period._run_decisions import (
    family_deduction_decision,
    pdr_decision,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.amounts._irpef import _Irpef
    from ccnl_engine.payroll.application.amounts._taxable import _PdrSplit
    from ccnl_engine.payroll.application.amounts._types import _AmountsInput
    from ccnl_engine.payroll.domain.contributions import ContributionBreakdown
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
    from ccnl_engine.payroll.domain.tax import TaxComputation
    from ccnl_engine.payroll.service.fiscal_surtax import SurtaxOutcome


def _decisions(
    inp: _AmountsInput, pdr: _PdrSplit, irpef: _Irpef, surtax: SurtaxOutcome
) -> tuple[CalculationDecision, ...]:
    """Return the tax decisions of the run, the surtax ones last.

    Returns:
        Family deductions, PdR, IRPEF and surtax decisions, when taken.
    """
    return tuple(
        d
        for d in (
            family_deduction_decision(irpef.family_deductions, irpef.family_rules),
            pdr_decision(
                inp.event_substitute_base,
                pdr.eligible,
                pdr.substitute_tax,
                inp.pdr_rules,
                inp.rules.year,
            ),
            *irpef.tax.decisions,
            *surtax.decisions,
        )
        if d is not None
    )


def _compute_amounts(
    inp: _AmountsInput,
) -> tuple[_PeriodAmounts, ContributionBreakdown, TaxComputation, RecoveryPlan | None]:
    """Resolve all monetary amounts for the period from gross, events and YTD state.

    The annual taxable income is projected as the opening YTD taxable, plus
    this run, plus ``upcoming_gross`` for the withholding slots still to
    come (net of employee INPS at the current rate).  On the last slot
    ``upcoming_gross`` is zero, so the projection equals the final taxable
    income and the conguaglio settles on it.

    Returns:
        ``(_PeriodAmounts, ContributionBreakdown, TaxComputation, RecoveryPlan | None)``
        with all rounded monetary quantities, the per-component INPS breakdown,
        the per-rule IRPEF computation, and the updated recovery plan (if any).
    """
    breakdown, employee_rate = run_contributions(inp)
    tfr = tfr_accrual(inp)
    pdr = pdr_split(inp)
    taxable = taxable_income(inp, breakdown.employee, employee_rate, pdr)
    irpef = withhold_irpef(inp, taxable, breakdown.employee)
    tax_comp = irpef.tax.computation
    surtax, period_surtax = run_surtax(inp, taxable.projected, irpef.tax.irpef_net)
    amounts = _PeriodAmounts(
        monthly_gross=inp.monthly_gross,
        inps_employee=breakdown.employee,
        inps_employer=breakdown.employer,
        tfr=tfr,
        period_irpef=tax_comp.ordinary_tax,
        period_tratt=tax_comp.trattamento_integrativo,
        period_surtax=period_surtax,
        period_taxable=taxable.period,
        period_substitute_tax=pdr.substitute_tax,
        pdr_eligible=pdr.eligible,
        projected_taxable=taxable.projected,
        surtax=surtax,
        ulteriore=irpef.tax.ulteriore,
        decisions=_decisions(inp, pdr, irpef, surtax),
    )
    return amounts, breakdown, tax_comp, irpef.tax.recovery_plan
