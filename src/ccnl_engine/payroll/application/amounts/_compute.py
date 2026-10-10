"""Amounts of one run: contributions, taxable, IRPEF and surtax in sequence."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.amounts._assistance import run_assistance
from ccnl_engine.payroll.application.amounts._contributions import (
    FIS_REDUCTION_UNKNOWN,
    run_contributions,
    tfr_accrual,
)
from ccnl_engine.payroll.application.amounts._irpef import (
    ulteriore_issues,
    withhold_irpef,
)
from ccnl_engine.payroll.application.amounts._pension import (
    CONVENTIONAL_BASE_UNKNOWN,
    ERC_UNKNOWN,
    YOUNG_MEMBER_UNKNOWN,
    conventional_base_unknown,
    run_pension,
)
from ccnl_engine.payroll.application.amounts._public_end_of_service import (
    end_of_service_issue,
    life_insurance_issue,
)
from ccnl_engine.payroll.application.amounts._surtax import run_surtax
from ccnl_engine.payroll.application.amounts._taxable import (
    pdr_split,
    taxable_income,
)
from ccnl_engine.payroll.application.amounts._types import _PeriodAmounts
from ccnl_engine.payroll.application.amounts._untaxed import untaxed_amounts
from ccnl_engine.payroll.application.period._run_decisions import pdr_decision

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.amounts._irpef import _Irpef
    from ccnl_engine.payroll.application.amounts._surtax import RunSurtax
    from ccnl_engine.payroll.application.amounts._taxable import _PdrSplit
    from ccnl_engine.payroll.application.amounts._types import _AmountsInput
    from ccnl_engine.payroll.domain.contributions import ContributionBreakdown
    from ccnl_engine.payroll.domain.decisions import (
        CalculationDecision,
        CalculationIssue,
    )
    from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
    from ccnl_engine.payroll.domain.tax import TaxComputation


def _decisions(
    inp: _AmountsInput, pdr: _PdrSplit, irpef: _Irpef, surtax: RunSurtax
) -> tuple[CalculationDecision, ...]:
    """Return the tax decisions of the run, the surtax ones last.

    Returns:
        Family deductions, PdR, IRPEF and surtax decisions, when taken.
    """
    return tuple(
        d
        for d in (
            None if irpef.family is None else irpef.family.decision(),
            pdr_decision(
                inp.event_substitute_base,
                pdr.eligible,
                pdr.substitute_tax,
                inp.pdr_rules,
                inp.rules.year,
            ),
            *irpef.tax.decisions,
            *surtax.all_decisions,
        )
        if d is not None
    )


def _issues(inp: _AmountsInput, irpef: _Irpef) -> tuple[CalculationIssue, ...]:
    family = () if irpef.family is None else irpef.family.issues()
    contractual = inp.contractual_fund.issue
    pension = inp.pension
    young = pension is not None and pension.young_member_unknown
    erc = pension is not None and pension.erc_unknown
    conventional = conventional_base_unknown(pension)
    public = end_of_service_issue(inp)
    life = life_insurance_issue(inp)
    fis = inp.rules.inps is not None and inp.rules.inps.fis_reduction_open
    return (
        family
        + ulteriore_issues(inp, irpef)
        + (() if contractual is None else (contractual,))
        + ((YOUNG_MEMBER_UNKNOWN,) if young else ())
        + ((ERC_UNKNOWN,) if erc else ())
        + ((CONVENTIONAL_BASE_UNKNOWN,) if conventional else ())
        + (() if public is None else (public,))
        + (() if life is None else (life,))
        + ((FIS_REDUCTION_UNKNOWN,) if fis else ())
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
        An employer that is not a withholding agent computes no tax: its
        amounts carry only contributions, TFR and taxable income.
    """
    breakdown, employee_rate = run_contributions(inp)
    tfr = tfr_accrual(inp, breakdown)
    pension = run_pension(inp)
    assistance = run_assistance(inp.assistance, inp.contributable_hours)
    if not inp.withholding_agent:
        untaxed, no_tax = untaxed_amounts(inp, breakdown, employee_rate, tfr, pension)
        return replace(untaxed, assistance=assistance), breakdown, no_tax, None
    pdr = pdr_split(inp)
    taxable = taxable_income(inp, breakdown.employee, employee_rate, pdr, pension)
    irpef = withhold_irpef(inp, taxable)
    tax_comp = irpef.tax.computation
    surtax = run_surtax(inp, taxable.projected, irpef.tax.irpef_net)
    amounts = _PeriodAmounts(
        monthly_gross=inp.monthly_gross,
        inps_employee=breakdown.employee,
        inps_employer=breakdown.employer,
        tfr=tfr,
        period_irpef=tax_comp.ordinary_tax,
        period_tratt=tax_comp.trattamento_integrativo,
        period_surtax=surtax.due,
        period_taxable=taxable.period,
        period_substitute_tax=pdr.substitute_tax,
        pdr_eligible=pdr.eligible,
        projected_taxable=taxable.projected,
        surtax=surtax,
        ulteriore=irpef.tax.ulteriore,
        decisions=_decisions(inp, pdr, irpef, surtax),
        pension=pension,
        issues=_issues(inp, irpef) + tfr.issues(),
        assistance=assistance,
    )
    return amounts, breakdown, tax_comp, irpef.tax.recovery_plan
