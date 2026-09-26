"""Period amount computation: salary chain, domestic INPS, and gross-to-tax amounts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._domestic_contributions import (
    compute_domestic_breakdown,
)
from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.application._run_decisions import (
    family_deduction_decision,
    pdr_decision,
)
from ccnl_engine.payroll.application._withholding_plan import slot_share
from ccnl_engine.payroll.domain.contributions import (
    ContributionBreakdown,
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
from ccnl_engine.payroll.service.fiscal_surtax import SurtaxOutcome, compute_surtax
from ccnl_engine.payroll.service.irpef import DAYS_IN_YEAR
from ccnl_engine.payroll.service.rounding import money
from ccnl_engine.payroll.service.seniority import _resolve_seniority_count
from ccnl_engine.payroll.service.tax_computation import compute_tax
from ccnl_engine.payroll.service.types import MonthlyPayChain

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.category import WorkerCategory
    from ccnl_engine.engine.contract.domain.ccnl import CCNL
    from ccnl_engine.engine.contract.domain.compensation import Level
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.family import FamilyDeductionRules
    from ccnl_engine.engine.tax.domain.rules import YearRules
    from ccnl_engine.engine.tax.domain.variable_pay import PdRRules
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.payroll.domain.schedule import WithholdingSchedule
    from ccnl_engine.payroll.domain.tax_year_state import TaxYearState


@dataclass(frozen=True)
class _PeriodAmounts:
    """Computed monetary amounts passed to pay-item and ledger builders.

    Does not include period_gross, period_net or period_employer_cost — those
    are derived from the ledger after all entries are posted.  ``surtax``
    carries the annual surtax decisions and issues behind ``period_surtax``;
    ``decisions`` holds every tax decision of the run, the surtax ones last.
    ``projected_taxable`` is the annual taxable income the IRPEF of the run
    was computed on; ``None`` when not recorded.
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
    surtax: SurtaxOutcome = field(default_factory=SurtaxOutcome)
    decisions: tuple[CalculationDecision, ...] = ()
    projected_taxable: Decimal | None = None


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


def _compute_amounts(
    monthly_gross: Decimal,
    event_inps_base: Decimal,
    event_tfr_base: Decimal,
    event_irpef_base: Decimal,
    event_substitute_base: Decimal,
    opening: TaxYearState,
    withholding_schedule: WithholdingSchedule,
    upcoming_gross: Decimal,
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
    eligible_work_days: int = DAYS_IN_YEAR,
    recovery_plan: RecoveryPlan | None = None,
) -> tuple[_PeriodAmounts, ContributionBreakdown, TaxComputation, RecoveryPlan | None]:
    """Resolve all monetary amounts for the period from gross, events and YTD state.

    The annual taxable income is projected as the opening YTD taxable, plus
    this run, plus ``upcoming_gross`` for the withholding slots still to
    come (net of employee INPS at the current rate).  On the last slot
    ``upcoming_gross`` is zero, so the projection equals the final taxable
    income and the conguaglio settles on it.  ``eligible_work_days`` are
    the days of employment in the tax year the deductions are proportioned
    to.  ``recovery_plan`` is the installment recovery opened in this tax
    year, if one is running.

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
        breakdown = compute_domestic_breakdown(
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

    # The run enters with its actual employee INPS (IVS ceiling and 1%
    # addizionale included); only the slots still to come are projected at
    # the current rate, so the last slot settles on the final taxable income.
    period_taxable = money(monthly_gross - inps_employee + effective_irpef_base)
    upcoming_inps = money(upcoming_gross * employee_rate_for_irpef)
    taxable = opening.earnings.taxable + period_taxable + upcoming_gross - upcoming_inps

    fam_ded = _ZERO
    family_rules = None if family_composition is None else family_deduction_rules
    if family_composition is not None and family_rules is not None:
        _, _, _, fam_ded = compute_family_deductions(
            family_composition, taxable, family_rules
        )

    # Net credit = recognized minus already recovered; prevents re-recovering credits
    # that have already been clawed back in previous periods (D.L. 3/2020, art. 1 c. 3).
    net_credit_ytd = opening.trattamento.recognized - opening.trattamento.recovered
    tax = compute_tax(
        taxable,
        rules,
        opening_irpef_withheld=opening.tax.irpef,
        opening_tratt_ytd=net_credit_ytd,
        withholding_schedule=withholding_schedule,
        slots_closed=opening.tax_withholding_periods_closed,
        family_deductions=fam_ded,
        recovery_plan=recovery_plan,
        eligible_work_days=eligible_work_days,
    )
    tax_comp, next_recovery_plan = tax.computation, tax.recovery_plan
    period_irpef = tax_comp.ordinary_tax
    period_tratt = tax_comp.trattamento_integrativo

    ig = next((c.amount for c in tax_comp.components if c.name == "irpef_gross"), _ZERO)
    surtax = (
        compute_surtax(
            taxable,
            surtax_rules,
            regione=regione,
            comune_belfiore=comune_belfiore,
            irpef_due=ig,
        )
        if surtax_rules is not None
        else SurtaxOutcome()
    )
    period_surtax = slot_share(surtax.total, withholding_schedule)

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
            projected_taxable=taxable,
            surtax=surtax,
            decisions=tuple(
                d
                for d in (
                    family_deduction_decision(fam_ded, family_rules),
                    pdr_decision(
                        event_substitute_base,
                        pdr_eligible,
                        period_substitute_tax,
                        pdr_rules,
                        rules.year,
                    ),
                    *tax.decisions,
                    *surtax.decisions,
                )
                if d is not None
            ),
        ),
        breakdown,
        tax_comp,
        next_recovery_plan,
    )
