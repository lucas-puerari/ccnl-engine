"""Period amount computation: salary chain, domestic INPS, and gross-to-tax amounts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.errors import DataIntegrityError, MissingRequiredFactError
from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.domain.contributions import (
    ContributionBreakdown,
    ContributionComponent,
)
from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm, Permanent
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.tax import TaxComputation
from ccnl_engine.payroll.service.apprenticeship import _apprentice_chain
from ccnl_engine.payroll.service.chain import _level_chain
from ccnl_engine.payroll.service.contributions import (
    resolve_contributions,
    resolve_rates,
)
from ccnl_engine.payroll.service.family_deductions import compute_family_deductions
from ccnl_engine.payroll.service.fiscal_surtax import _compute_addizionali
from ccnl_engine.payroll.service.rounding import money
from ccnl_engine.payroll.service.seniority import _resolve_seniority_count
from ccnl_engine.payroll.service.tax_computation import resolve_tax_computation
from ccnl_engine.payroll.service.types import MonthlyPayChain

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.category import WorkerCategory
    from ccnl_engine.engine.contract.domain.ccnl import CCNL
    from ccnl_engine.engine.contract.domain.compensation import Level
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.contribution_rules import DomesticInpsRates
    from ccnl_engine.engine.tax.domain.family import FamilyDeductionRules
    from ccnl_engine.engine.tax.domain.rules import YearRules
    from ccnl_engine.engine.tax.domain.variable_pay import PdRRules
    from ccnl_engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.payroll.domain.period import PeriodState


@dataclass(frozen=True)
class _PeriodAmounts:
    """Computed monetary amounts passed to pay-item and ledger builders.

    Does not include period_gross, period_net or period_employer_cost — those
    are derived from the ledger after all entries are posted.
    """

    monthly_gross: Decimal
    inps_employee: Decimal
    inps_employer: Decimal
    tfr: Decimal
    period_irpef: Decimal
    period_tratt: Decimal
    period_surtax: Decimal
    period_taxable: Decimal
    period_substitute_tax: Decimal
    pdr_eligible: Decimal


def _resolve_chain(
    ccnl: CCNL,
    level: Level,
    contract_type: Permanent | FixedTerm | Apprentice,
    as_of: date,
    *,
    seniority_months: int | None = None,
    roles: frozenset[str] = frozenset(),
    worker_category: WorkerCategory | None = None,
    weekly_hours: int | None = None,
    full_time_weekly_hours: int | None = None,
) -> MonthlyPayChain:
    """Resolve the elementary pay chain for the period.

    Applies part-time scaling when ``weekly_hours < full_time_weekly_hours``.

    Returns:
        :class:`~ccnl_engine.payroll.service.types.MonthlyPayChain` with each
        component rounded and ready for pay-item emission.
    """
    count = (
        _resolve_seniority_count(
            ccnl.parameters.seniority_increments,
            level.code,
            None,
            seniority_months,
            worker_category=worker_category,
        )
        if seniority_months is not None
        else 0
    )
    if isinstance(contract_type, Apprentice):
        chain, pct, _ = _apprentice_chain(
            ccnl,
            level,
            contract_type,
            count,
            roles,
            as_of,
            worker_category=worker_category,
            seniority_months=seniority_months,
        )
        chain = chain.scaled(pct) if pct is not None else chain
    else:
        chain = _level_chain(
            ccnl,
            level,
            count,
            roles,
            as_of,
            is_apprentice=False,
            worker_category=worker_category,
            seniority_months=seniority_months,
        )
    # Both values are positive: WeeklyHours validates them on construction.
    if (
        full_time_weekly_hours is not None
        and weekly_hours is not None
        and weekly_hours < full_time_weekly_hours
    ):
        chain = chain.scaled_for_part_time(
            Decimal(weekly_hours) / Decimal(full_time_weekly_hours)
        )
    return chain


def _domestic_hourly_rate(
    ccnl: CCNL,
    year_rules: YearRules,
    monthly_gross: Decimal,
    as_of: date,
) -> Decimal | None:
    """Return the derived domestic hourly rate, or ``None`` for non-domestic CCNLs.

    Returns:
        Hourly rate in EUR for domestic CCNLs (``monthly_gross / hourly_divisor``),
        or ``None`` when the CCNL uses standard INPS rates.
    """
    if year_rules.domestic_contributions is None:
        return None
    hourly_divisor = Decimal(str(ccnl.parameters.hourly_divisor.value_at(as_of)))
    return money(monthly_gross / hourly_divisor) if monthly_gross > _ZERO else _ZERO


def _pick_domestic_per_hour(
    dc: DomesticInpsRates,
    weekly_hours: int,
    domestic_hourly_rate: Decimal,
    contract_type: Permanent | FixedTerm | Apprentice,
) -> tuple[Decimal, Decimal]:
    """Return (employee_per_hour, employer_per_hour) for a domestic CCNL bracket.

    Returns:
        ``(emp_ph, empr_ph)`` flat rates to multiply by contributable hours.
    """
    if weekly_hours > dc.weekly_hours_threshold:
        emp_ph = dc.hours_bracket.employee_per_hour
        empr_ph = (
            dc.hours_bracket.employer_per_hour_fixed_term
            if isinstance(contract_type, FixedTerm)
            else dc.hours_bracket.employer_per_hour
        )
    else:
        emp_ph = _ZERO
        empr_ph = _ZERO
        for wb in dc.wage_brackets:  # pragma: no branch
            if (  # pragma: no branch
                wb.hourly_rate_up_to is None
                or domestic_hourly_rate <= wb.hourly_rate_up_to
            ):
                emp_ph = wb.employee_per_hour
                empr_ph = (
                    wb.employer_per_hour_fixed_term
                    if isinstance(contract_type, FixedTerm)
                    else wb.employer_per_hour
                )
                break
    return emp_ph, empr_ph


def _compute_domestic_breakdown(
    rules: YearRules,
    weekly_hours: int | None,
    contributable_hours: Decimal | None,
    domestic_hourly_rate: Decimal | None,
    contract_type: Permanent | FixedTerm | Apprentice,
) -> ContributionBreakdown:
    """Compute domestic flat-rate INPS contributions.

    Returns:
        :class:`~ccnl_engine.payroll.domain.contributions.ContributionBreakdown`
        with employee and employer flat-rate contributions and per-component audit.

    Raises:
        MissingRequiredFactError: When ``weekly_hours`` or ``contributable_hours``
            is ``None``.
        DataIntegrityError: When ``domestic_contributions`` is unexpectedly absent.
    """
    dc = rules.domestic_contributions
    if dc is None:  # pragma: no cover
        msg = "YearRules has no domestic_contributions despite inps=None"
        raise DataIntegrityError(msg)
    if weekly_hours is None:
        msg = (
            "domestic CCNL requires weekly_hours in PeriodCalculationRequest "
            "to select the INPS contribution bracket"
        )
        raise MissingRequiredFactError(msg, feature="domestic_contributions")
    if contributable_hours is None:
        msg = (
            "domestic CCNL requires contributable_hours in "
            "PeriodCalculationRequest to compute INPS contributions"
        )
        raise MissingRequiredFactError(msg, feature="domestic_contributions")
    emp_ph, empr_ph = _pick_domestic_per_hour(
        dc, weekly_hours, domestic_hourly_rate or _ZERO, contract_type
    )
    employee_contribution = money(emp_ph * contributable_hours)
    employer_contribution = money(empr_ph * contributable_hours)
    return ContributionBreakdown(
        employee=employee_contribution,
        employer=employer_contribution,
        components=(
            ContributionComponent(
                name="domestic_employee_per_hour",
                base=contributable_hours,
                rate=emp_ph,
                amount=employee_contribution,
            ),
            ContributionComponent(
                name="domestic_employer_per_hour",
                base=contributable_hours,
                rate=empr_ph,
                amount=employer_contribution,
            ),
        ),
    )


def _compute_amounts(
    monthly_gross: Decimal,
    event_inps_base: Decimal,
    event_tfr_base: Decimal,
    event_irpef_base: Decimal,
    event_substitute_base: Decimal,
    opening: PeriodState,
    additional_months: int,
    rules: YearRules,
    contract_type: Permanent | FixedTerm | Apprentice,
    category: WorkerCategory | None,
    pdr_rules: PdRRules,
    surtax_rules: SurtaxRules | None = None,
    regione: str | None = None,
    comune_belfiore: str | None = None,
    family_composition: FamilyComposition | None = None,
    family_deduction_rules: FamilyDeductionRules | None = None,
    ivs_ceiling_applies: bool = True,
    weekly_hours: int | None = None,
    contributable_hours: Decimal | None = None,
    domestic_hourly_rate: Decimal | None = None,
) -> tuple[_PeriodAmounts, ContributionBreakdown, TaxComputation, RecoveryPlan | None]:
    """Resolve all monetary amounts for the period from gross, events and YTD state.

    Returns:
        ``(_PeriodAmounts, ContributionBreakdown, TaxComputation, RecoveryPlan | None)``
        with all rounded monetary quantities, the per-component INPS breakdown,
        the per-rule IRPEF computation, and the updated recovery plan (if any).
    """
    period_inps_base = monthly_gross + event_inps_base
    if rules.inps is not None:
        breakdown = resolve_contributions(
            period_inps_base,
            rules,
            contract_type,
            category,
            ytd_inps_base=opening.earnings.inps_base,
            ivs_ceiling_applies=ivs_ceiling_applies,
        )
        rates = resolve_rates(rules, contract_type, category)
        employee_rate_for_irpef = rates.employee_rate
    else:
        breakdown = _compute_domestic_breakdown(
            rules,
            weekly_hours,
            contributable_hours,
            domestic_hourly_rate,
            contract_type,
        )
        employee_rate_for_irpef = _ZERO
    inps_employee = breakdown.employee
    inps_employer = breakdown.employer

    period_tfr_base = monthly_gross + event_tfr_base
    tfr = money(period_tfr_base / rules.tfr.accrual_divisor)

    # PdR eligibility must be resolved before taxable, because any excess beyond the
    # annual cap (L. 199/2025, comma 9) returns to the ordinary IRPEF base.
    pdr_headroom = max(_ZERO, pdr_rules.max_amount - opening.fringe.pdr)
    pdr_eligible = min(event_substitute_base, pdr_headroom)
    pdr_excess = event_substitute_base - pdr_eligible
    period_substitute_tax = money(pdr_eligible * pdr_rules.flat_tax_rate)

    # Excess PdR beyond the cap is taxed ordinarily; add it back to the IRPEF base.
    effective_irpef_base = event_irpef_base + pdr_excess

    months_remaining = additional_months - opening.tax_withholding_periods_closed
    recurring_remaining = monthly_gross * months_remaining
    recurring_inps_remaining = money(recurring_remaining * employee_rate_for_irpef)
    recurring_taxable = recurring_remaining - recurring_inps_remaining
    event_inps_on_irpef = money(event_inps_base * employee_rate_for_irpef)
    event_taxable = effective_irpef_base - event_inps_on_irpef
    taxable = opening.earnings.taxable + recurring_taxable + event_taxable

    if family_composition is not None and family_deduction_rules is not None:
        _, _, _, fam_ded = compute_family_deductions(
            family_composition, taxable, family_deduction_rules
        )
    else:
        fam_ded = _ZERO

    # Net credit = recognized minus already recovered; prevents re-recovering credits
    # that have already been clawed back in previous periods (D.L. 3/2020, art. 1 c. 3).
    net_credit_ytd = opening.trattamento.recognized - opening.trattamento.recovered
    tax_comp, next_recovery_plan = resolve_tax_computation(
        taxable,
        rules,
        opening_irpef_withheld=opening.tax.irpef,
        opening_tratt_ytd=net_credit_ytd,
        months_closed=opening.tax_withholding_periods_closed,
        additional_months=additional_months,
        family_deductions=fam_ded,
        recovery_plan=opening.trattamento.plan,
    )
    period_irpef = tax_comp.ordinary_tax
    period_tratt = tax_comp.trattamento_integrativo

    ig = next((c.amount for c in tax_comp.components if c.name == "irpef_gross"), _ZERO)
    surtax_reg, surtax_com, _, _, _ = _compute_addizionali(
        taxable,
        surtax_rules,
        frozenset(),
        regione=regione,
        comune_belfiore=comune_belfiore,
        irpef_due=ig,
    )
    period_surtax_annual = surtax_reg + surtax_com
    period_surtax = money(period_surtax_annual / additional_months)

    period_taxable = money(monthly_gross - inps_employee + effective_irpef_base)

    return (
        _PeriodAmounts(
            monthly_gross=monthly_gross,
            inps_employee=inps_employee,
            inps_employer=inps_employer,
            tfr=tfr,
            period_irpef=period_irpef,
            period_tratt=period_tratt,
            period_surtax=period_surtax,
            period_taxable=period_taxable,
            period_substitute_tax=period_substitute_tax,
            pdr_eligible=pdr_eligible,
        ),
        breakdown,
        tax_comp,
        next_recovery_plan,
    )
