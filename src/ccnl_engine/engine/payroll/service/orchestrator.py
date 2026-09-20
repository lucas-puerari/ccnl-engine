"""Coordinate gross, fiscal and optional computations into a payroll result."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, assert_never

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.engine.io.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.engine.payroll.domain.employee import (
    SeniorityByCount,
    SeniorityByDate,
    SeniorityByMonths,
)
from ccnl_engine.engine.payroll.domain.ledger import Ledger
from ccnl_engine.engine.payroll.domain.payroll_result import (
    AnnualEstimate,
    Contributions,
    Coverage,
    Earnings,
    EmployerCost,
    PeriodPayroll,
    Taxes,
)
from ccnl_engine.engine.payroll.domain.period import PayrollPeriod, YTDState
from ccnl_engine.engine.payroll.domain.scenario import (
    AnnualEstimateInput,
    AnnualizedAssumption,
    PayrollScenario,
    PeriodPayrollInput,
)
from ccnl_engine.engine.payroll.service.assembly import (
    _collect_provenance,
    build_calculation,
)
from ccnl_engine.engine.payroll.service.fiscal import compute_fiscal
from ccnl_engine.engine.payroll.service.gross import compute_gross
from ccnl_engine.engine.payroll.service.ledger_builder import post_earnings
from ccnl_engine.engine.payroll.service.scope import (
    build_scope,
    compute_confidence,
    compute_result_status,
)
from ccnl_engine.engine.payroll.service.work_rules import compute_work_rules

if TYPE_CHECKING:
    from ccnl_engine.engine.metadata.domain.rules import RulesetIdentity
    from ccnl_engine.engine.payroll.domain.bundle import PayrollBundle
    from ccnl_engine.engine.payroll.domain.calculation import Calculation
    from ccnl_engine.engine.payroll.domain.scenario import Employment


_default_repo: BundledKnowledgeRepository = BundledKnowledgeRepository()

_IVS_CEILING_THRESHOLD = date(1996, 1, 1)


def _ivs_date_msg(hire_date: date) -> str | None:
    """Warning when an explicit hire date is on or after the IVS threshold.

    Returns:
        Warning string, or ``None`` when hire date is before the threshold.
    """
    if hire_date < _IVS_CEILING_THRESHOLD:
        return None
    return (
        f"hire date {hire_date} is on or after "
        f"{_IVS_CEILING_THRESHOLD}: contributions are overstated; "
        "consider setting ivs_ceiling_applies=True"
    )


def _ivs_months_msg(months: int, as_of: date) -> str | None:
    """Warning when implied hire date (from months of service) is post-threshold.

    Returns:
        Warning string, or ``None`` when the implied hire predates the threshold.
    """
    months_since_threshold = (as_of.year - _IVS_CEILING_THRESHOLD.year) * 12 + (
        as_of.month - _IVS_CEILING_THRESHOLD.month
    )
    if months > months_since_threshold:
        return None  # implied hire date is before the threshold
    return (
        f"seniority of {months} months implies hire on or after "
        f"{_IVS_CEILING_THRESHOLD}: contributions are overstated; "
        "consider setting ivs_ceiling_applies=True"
    )


def _ivs_ceiling_warning(
    scenario: PayrollScenario | AnnualEstimateInput,
    as_of: date,
    contribution_base: Decimal,
    ivs_ceiling: Decimal | None,
) -> str | None:
    """Return a warning when a post-1996 hire has ivs_ceiling_applies=False.

    Workers hired on or after 1996-01-01 are subject to the INPS IVS
    contribution ceiling.  When the ceiling is skipped, the engine uses a
    higher contribution base, so computed contributions are overstated.

    When ``ivs_ceiling`` is known and the contribution base does not exceed
    it, the ceiling would have no effect, so no warning is emitted.

    Covers all three seniority input types:

    - ``SeniorityByDate``: compare the explicit hire date to the threshold.
    - ``SeniorityByMonths``: derive an implied hire date from *as_of* and
      the stored months count; warn when the implied date is on or after
      the threshold.
    - ``SeniorityByCount``: hire date is unknowable; always warn so the
      caller can make an explicit choice.

    Returns:
        A warning string, or ``None`` when no warning is warranted.
    """
    if scenario.employee.ivs_ceiling_applies:
        return None
    if ivs_ceiling is not None and contribution_base <= ivs_ceiling:
        return None
    seniority = scenario.employee.seniority
    if seniority is None:
        # When seniority is absent we cannot determine whether the ceiling
        # applies.  Warn only when we know the ceiling exists and the base
        # already exceeds it (the prior guard handled base ≤ ceiling), so
        # the economic impact of the wrong decision is concrete.
        return (
            (
                "seniority is None: IVS ceiling applicability cannot be "
                "determined; if the worker was hired on or after "
                f"{_IVS_CEILING_THRESHOLD}, contributions are overstated. "
                "Set ivs_ceiling_applies=True to apply the IVS ceiling."
            )
            if ivs_ceiling is not None
            else None
        )
    if isinstance(seniority, SeniorityByDate):
        return _ivs_date_msg(seniority.value)
    if isinstance(seniority, SeniorityByMonths):
        return _ivs_months_msg(seniority.value, as_of)
    if isinstance(seniority, SeniorityByCount):
        return (
            "SeniorityByCount used without ivs_ceiling_applies: "
            f"if hired on or after {_IVS_CEILING_THRESHOLD}, "
            "contributions are overstated; "
            "consider setting ivs_ceiling_applies=True"
        )
    assert_never(seniority)  # pragma: no cover


def _resolve_tax_year(employment: Employment) -> int:
    """Return the tax year for rule loading.

    Uses the explicit override when set, otherwise falls back to the
    calendar year of the employment date.

    Returns:
        Integer year for ``load_year_rules`` and ``load_surtax_rules``.
    """
    if employment.tax_year is not None:
        return employment.tax_year
    return employment.as_of.year


def _build_earnings(gross: object, work: object) -> Earnings:
    """Build :class:`Earnings` from the gross and work-rules payloads.

    Returns:
        Earnings sub-object populated from *gross* and *work*.
    """
    from ccnl_engine.engine.payroll.service.gross import GrossPay  # noqa: PLC0415
    from ccnl_engine.engine.payroll.service.work_rules import (  # noqa: PLC0415
        WorkRulesPay,
    )

    g = gross
    w = work
    assert isinstance(g, GrossPay)
    assert isinstance(w, WorkRulesPay)
    return Earnings(
        seniority_count=g.count,
        base_monthly=g.chain.base,
        seniority_monthly=g.chain.seniority,
        allowances_monthly=g.chain.allowances_total,
        ad_personam_monthly=g.ad_personam,
        second_level_monthly=g.second_level_monthly_total,
        gross_monthly=g.gross_monthly,
        gross_annual=g.gross_annual,
        hourly_rate=w.hourly_rate,
        apprenticeship_pct=g.apprenticeship_pct,
        apprenticeship_under_level_code=g.under_level_code,
    )


def _build_contributions(fiscal: object) -> Contributions:
    """Build :class:`Contributions` from the fiscal payload.

    Returns:
        Contributions sub-object populated from *fiscal*.
    """
    from ccnl_engine.engine.payroll.service.fiscal import FiscalPay  # noqa: PLC0415

    f = fiscal
    assert isinstance(f, FiscalPay)
    return Contributions(
        inps_employee_annual=f.inps_employee_annual,
        inps_employer_annual=f.inps_employer_annual,
        inail_employer_annual=f.inail_employer_annual,
        inps_employer_exemption_annual=f.inps_employer_exemption_annual,
        maternity_inps_indemnity_annual=f.maternity_inps_indemnity_annual,
        workplace_injury_inail_indemnity_annual=f.workplace_injury_inail_indemnity_annual,
        termination_tfr_liquidation_annual=f.termination_tfr_liquidation_annual,
        employer_funds_annual=f.employer_funds_annual,
        tfr_annual=f.tfr_annual,
        bilateral_employee_annual=f.bilateral_employee_annual,
        bilateral_employer_annual=f.bilateral_employer_annual,
        health_fund_employee_annual=f.health_fund_employee_annual,
        health_fund_employer_annual=f.health_fund_employer_annual,
    )


def _build_taxes(fiscal: object) -> Taxes:
    """Build :class:`Taxes` from the fiscal payload.

    Returns:
        Taxes sub-object populated from *fiscal*.
    """
    from ccnl_engine.engine.payroll.service.fiscal import FiscalPay  # noqa: PLC0415

    f = fiscal
    assert isinstance(f, FiscalPay)
    return Taxes(
        taxable_income=f.taxable_income,
        irpef_gross=f.irpef_gross,
        work_income_deduction=f.work_income_deduction,
        ulteriore_detrazione_lavoro=f.ulteriore_detrazione_lavoro,
        somma_esente=f.somma_esente,
        irpef_net=f.irpef_net,
        employer_withholds_irpef=f.employer_withholds_irpef,
        addizionale_regionale_annual=f.addizionale_regionale,
        addizionale_comunale_annual=f.addizionale_comunale,
        trattamento_integrativo=f.trattamento_integrativo,
        fiscal_simplifications=f.fiscal_simplifications,
        family_deduction_spouse_annual=f.fam_spouse,
        family_deduction_children_annual=f.fam_children,
        family_deduction_other_annual=f.fam_other,
        family_deduction_annual=f.fam_total,
        unused_family_deduction_annual=f.fam_unused,
        art15_deduction_annual=f.art15_total,
        unused_art15_deduction_annual=f.art15_unused,
        sterilizzazione_clawback_annual=f.sterilizzazione_clawback,
        conguaglio_annual=f.conguaglio_annual,
        termination_residual_leave_payout_annual=f.termination_residual_leave_payout_annual,
        contract_renewal_arrears_annual=f.contract_renewal_arrears_annual,
        una_tantum_annual=f.una_tantum_annual,
        personal_withholdings_annual=f.personal_withholdings_annual,
        additional_irpef_base_annual=f.additional_irpef_base_annual,
        territorial_supplement_annual=f.territorial_supplement_annual,
        company_supplement_annual=f.company_supplement_annual,
    )


def _scenario_period(scenario: PayrollScenario) -> PeriodPayrollInput | None:
    """Build a PeriodPayrollInput from scenario period events.

    Returns:
        A :class:`PeriodPayrollInput` from *scenario*, or ``None`` when no
        period events are set.
    """
    fields = (
        scenario.time_supplements,
        scenario.absence_days,
        scenario.leave_input,
        scenario.sick_input,
        scenario.fringe_benefit_input,
        scenario.welfare_input,
        scenario.bonus_input,
    )
    if all(f is None for f in fields):
        return None
    from ccnl_engine.engine.payroll.domain.scenario import (  # noqa: PLC0415
        PeriodPayrollInput as _PayPeriod,
    )

    return _PayPeriod(
        time_supplements=scenario.time_supplements,
        absence_days=scenario.absence_days,
        leave_input=scenario.leave_input,
        sick_input=scenario.sick_input,
        fringe_benefit_input=scenario.fringe_benefit_input,
        welfare_input=scenario.welfare_input,
        bonus_input=scenario.bonus_input,
    )


_PERIOD_FIELD_NAMES = (
    "time_supplements",
    "absence_days",
    "leave_input",
    "sick_input",
    "fringe_benefit_input",
    "welfare_input",
    "bonus_input",
)


def _extract_injected_period(
    scenario: AnnualEstimateInput,
) -> PeriodPayrollInput | None:
    """Extract period fields injected onto an AnnualEstimateInput via model_copy.

    Returns:
        A :class:`PeriodPayrollInput` from the injected fields, or ``None``.
    """
    kwargs = {k: v for k in _PERIOD_FIELD_NAMES if (v := vars(scenario).get(k))}
    return PeriodPayrollInput(**kwargs) if kwargs else None


def compute(
    scenario: PayrollScenario | AnnualEstimateInput,
    bundle: PayrollBundle | None = None,
    *,
    _period: PeriodPayrollInput | None = None,
) -> Calculation:
    """Compute gross-to-net salary and employer cost for a payroll scenario.

    Loads the CCNL, tax/INPS rules, and (when jurisdiction is set) surtax
    rules from the bundled knowledge base, then runs the full payroll
    computation chain.

    When *bundle* is provided the three ruleset objects it carries are used
    directly, skipping rule loading.  This guarantees reproducibility across
    multiple calls (e.g. monthly payroll for a full year) and avoids repeated
    I/O even when the individual loaders are not yet cached.

    Args:
        scenario: The payroll scenario describing worker and employment.
            Accepts either :class:`PayrollScenario` or
            :class:`AnnualEstimateInput`; the latter is converted internally.
        bundle: Optional pre-loaded knowledge bundle.  When ``None``, rulesets
            are loaded (and cached) on demand.

    Returns:
        :class:`~ccnl_engine.engine.payroll.domain.calculation.Calculation`
        with all gross, net and cost figures plus a serialisable input snapshot.
    """
    if isinstance(scenario, AnnualEstimateInput):
        scenario = _annual_to_scenario(scenario, _period)
        _period = None
    if _period is None:
        _period = _scenario_period(scenario)
    as_of = scenario.employment.as_of
    year = _resolve_tax_year(scenario.employment)
    if bundle is not None:
        ccnl = bundle.ccnl
        rules = bundle.rules
        surtax = bundle.surtax
    else:
        ccnl = _default_repo.load_ccnl(scenario.employment.ccnl)
        rules = _default_repo.load_year_rules(
            year, ccnl.meta.tax_sector, scenario.employment.employer.num_employees
        )
        j = scenario.employee.jurisdiction
        needs_surtax = j is not None and (
            j.regione is not None or j.comune_belfiore is not None
        )
        surtax = _default_repo.load_surtax_rules(year) if needs_surtax else None

    gross = compute_gross(scenario, ccnl)
    ledger = Ledger()
    post_earnings(gross, as_of, ledger)
    work = compute_work_rules(scenario, ccnl, gross, year)
    fiscal = compute_fiscal(scenario, ccnl, rules, surtax, gross, year, work)
    calculation_scope = build_scope(scenario, fiscal, work, ccnl.coverage)
    provenance = _collect_provenance(
        gross.level,
        as_of,
        gross.chain,
        ccnl.parameters.seniority_increments,
        ccnl=ccnl,
        under_level_code=gross.under_level_code,
    )
    result_status = compute_result_status(calculation_scope)
    # Gather all RulesetIdentity records for rulesets actually consumed so
    # that compute_confidence can downgrade from "high" when any of them
    # has verification_status != "verified".  None entries mean "consumed
    # but identity absent" and are treated as unverified by compute_confidence.
    # Main rulesets (ccnl, tax rules) are always consumed; INPS rules are only
    # consumed for the standard percentage model, not the domestic forfait model.
    # Optional-feature rulesets are only added when the feature was used.
    main_rulesets: tuple[RulesetIdentity | None, ...] = (ccnl.ruleset, rules.ruleset)
    if rules.domestic_contributions is None:
        # Standard percentage model: INPS rules were consumed.
        main_rulesets = (*main_rulesets, rules.inps_ruleset)
    consumed_rulesets = (
        main_rulesets + tuple(work.consumed_ruleset_ids) + fiscal.consumed_ruleset_ids
    )
    ivs_ceiling = rules.inps.ceiling if rules.inps is not None else None
    # Domestic contracts use per-hour forfait rates; the IVS ceiling model
    # does not participate in that calculation, so no warning is warranted.
    ivs_warn = (
        None
        if rules.domestic_contributions is not None
        else _ivs_ceiling_warning(scenario, as_of, gross.contribution_base, ivs_ceiling)
    )
    result_warnings = (
        (*work.warnings, ivs_warn) if ivs_warn is not None else work.warnings
    )

    coverage = Coverage(
        status=result_status,
        confidence=compute_confidence(
            result_status, result_warnings, provenance, consumed_rulesets
        ),
        calculation_scope=calculation_scope,
        warnings=result_warnings,
        consumed_rulesets=consumed_rulesets,
    )
    base: dict[str, object] = {
        "ccnl_id": ccnl.meta.ccnl_id,
        "level_code": scenario.employee.level_code,
        "employment_type": scenario.employment.contract.type,
        "part_time_ratio": scenario.employee.part_time_ratio,
        "as_of": as_of,
        "year": as_of.year,
        "contract_effective_date": (
            p.valid_from
            if (p := gross.level.base_salary.period_at(as_of)) is not None
            else as_of  # pragma: no cover
        ),
        "tax_rule_year": year,
        "earnings": _build_earnings(gross, work),
        "contributions": _build_contributions(fiscal),
        "taxes": _build_taxes(fiscal),
        "employer_cost": EmployerCost(employer_cost_annual=fiscal.employer_cost_annual),
        "coverage": coverage,
        "provenance": provenance,
        "net_annual": fiscal.net_annual,
        "net_monthly": fiscal.net_monthly,
    }
    if _period is not None:
        result: AnnualEstimate = PeriodPayroll(
            **base,  # type: ignore[arg-type]
            pay_period=_period,
            base_monthly_full_time=work.base_monthly_full_time,
            overtime_supplement_monthly=work.overtime_supp,
            night_supplement_monthly=work.night_supp,
            holiday_supplement_monthly=work.holiday_supp,
            time_supplements_monthly=work.time_supplements_monthly,
            time_supplements_annual_projection=work.time_supplements_annual_projection,
            absence_deduction_monthly=work.absence_deduction_monthly,
            effective_gross_monthly=work.effective_gross_monthly,
            leave_accrued_days_monthly=work.leave_accrued_days_monthly,
            leave_taken_days_monthly=work.leave_taken_days_monthly,
            leave_balance_days=work.leave_balance_days,
            sick_days_monthly=work.sick_days_monthly,
            sick_carenza_days_monthly=work.sick_carenza_days_monthly,
            sick_inps_indemnity_monthly=work.sick_inps_indemnity_monthly,
            sick_company_integration_monthly=work.sick_company_integration_monthly,
            fringe_benefit_annual=work.fringe_benefit_annual,
            fringe_benefit_threshold_annual=work.fringe_benefit_threshold_annual,
            fringe_benefit_taxable_annual=work.fringe_benefit_taxable_annual,
            welfare_annual=work.welfare_annual,
            bonus_annual=work.bonus_annual,
            bonus_pdr_flat_tax_annual=work.bonus_pdr_flat_tax_annual,
            bonus_ordinary_taxable_annual=work.bonus_ordinary_taxable_annual,
        )
    else:
        result = AnnualEstimate(**base)  # type: ignore[arg-type]
    return build_calculation(
        scenario, ccnl, rules, surtax, gross, work, result, fiscal, ledger
    )


def _annual_to_scenario(
    scenario: AnnualEstimateInput,
    period: PeriodPayrollInput | None = None,
) -> PayrollScenario:
    """Build an internal PayrollScenario from an AnnualEstimateInput.

    Merges the structural fields from *scenario* with the period-specific
    events from *period* (when supplied).

    Returns:
        A :class:`PayrollScenario` ready for :func:`compute`.
    """
    if period is None:
        period = _extract_injected_period(scenario)
    if period is not None:
        return PayrollScenario(
            employee=scenario.employee,
            employment=scenario.employment,
            tax_basis=period.tax_period
            if period.tax_period is not None
            else AnnualizedAssumption(),
            family=scenario.family,
            art15_deductions=scenario.art15_deductions,
            bilateral_funds=scenario.bilateral_funds,
            time_supplements=period.time_supplements,
            absence_days=period.absence_days,
            leave_input=period.leave_input,
            sick_input=period.sick_input,
            fringe_benefit_input=period.fringe_benefit_input,
            welfare_input=period.welfare_input,
            bonus_input=period.bonus_input,
        )
    return PayrollScenario(
        employee=scenario.employee,
        employment=scenario.employment,
        family=scenario.family,
        art15_deductions=scenario.art15_deductions,
        bilateral_funds=scenario.bilateral_funds,
    )


def estimate_annual(
    scenario: AnnualEstimateInput,
    bundle: PayrollBundle | None = None,
) -> Calculation:
    """Estimate annual gross-to-net salary and employer cost.

    Computes annual payroll figures for the given scenario without any
    period-specific events (overtime, absences, sick leave, etc.).  All
    output figures are annual estimates based on the structural inputs only.

    Args:
        scenario: The annual payroll scenario describing the worker and the
            employment relationship.
        bundle: Optional pre-loaded knowledge bundle.  When ``None``, rulesets
            are loaded on demand.

    Returns:
        A :class:`~ccnl_engine.engine.payroll.domain.calculation.Calculation`
        with all gross, net and cost figures.
    """
    return compute(_annual_to_scenario(scenario), bundle)


def estimate_period_effects(
    scenario: AnnualEstimateInput,
    period: PeriodPayrollInput,
    bundle: PayrollBundle | None = None,
) -> Calculation:
    """Estimate the informational effect of period events on the annual figures.

    Merges the period-specific events from *period* (overtime hours, absences,
    sick leave, fringe benefits, bonuses) into the structural scenario and runs
    the computation chain.  The period events appear in dedicated result fields
    (e.g. ``overtime_supplement_monthly``, ``sick_days_monthly``) but do **not**
    flow into ``net_annual`` or ``employer_cost_annual`` in this version — those
    figures remain annualised estimates.

    Use :func:`estimate_annual` when you need the structural annual gross-to-net.
    Use this function only when you need the per-period breakdown fields alongside
    the annual figures.

    Args:
        scenario: The annual payroll scenario (structural fields only).
        period: The period-specific events to merge in.  Must include
            :attr:`~ccnl_engine.engine.payroll.domain.scenario\
.PeriodPayrollInput.tax_period` for fiscal pro-rata; the function raises
            :exc:`~ccnl_engine.engine.errors.InvalidInputError` when absent.
        bundle: Optional pre-loaded knowledge bundle.  When ``None``, rulesets
            are loaded on demand.

    Returns:
        A :class:`~ccnl_engine.engine.payroll.domain.calculation.Calculation`
        with annual figures plus informational period-event fields.

    Raises:
        InvalidInputError: When ``period.tax_period`` is ``None``.
    """
    if period.tax_period is None:
        msg = "period.tax_period is required for period payroll computation"
        raise InvalidInputError(
            msg,
            feature="tax_period",
            remediation=(
                "Set PeriodPayrollInput.tax_period to a TaxPeriod with "
                "the worker's employment start, end, and eligible_work_days "
                "in the tax year.  Never omit it: the engine does not "
                "silently apply 365/365 for period computations."
            ),
        )
    return compute(_annual_to_scenario(scenario, period), bundle, _period=period)


def _accrue_ytd(ytd: YTDState, calc: Calculation) -> YTDState:
    """Return a new YTDState with one month's contribution appended.

    The engine produces annualized figures; dividing by 12 gives the
    per-period share that accumulates in the YTD totals.

    Returns:
        A new :class:`~ccnl_engine.engine.payroll.domain.period.YTDState`
        with the monthly share of *calc* added to *ytd*.
    """
    twelve = Decimal(12)
    r = calc.result
    return YTDState(
        taxable_income=ytd.taxable_income + r.taxes.taxable_income / twelve,
        irpef_withheld=ytd.irpef_withheld + r.taxes.irpef_net / twelve,
        inps_employee=ytd.inps_employee + r.contributions.inps_employee_annual / twelve,
    )


def compute_period(
    scenario: AnnualEstimateInput,
    period: PayrollPeriod,
    bundle: PayrollBundle | None = None,
) -> Calculation:
    """Compute payroll for a single month of competence.

    Uses *period.year* and *period.month* as the reference date for all
    time-series lookups, overriding the ``as_of`` field in
    *scenario.employment*.  The period-specific events in *period.events*
    are merged into the scenario exactly as in :func:`estimate_period_effects`.

    The year-to-date state in *period.ytd* is stored in the period
    descriptor and is available for chaining across months; it does not
    alter the underlying annualized calculation in this version.

    Args:
        scenario: The annual payroll scenario (structural fields only).
        period: The month descriptor including YTD state and period events.
        bundle: Optional pre-loaded knowledge bundle.  When ``None``,
            rulesets are loaded on demand.

    Returns:
        A :class:`~ccnl_engine.engine.payroll.domain.calculation.Calculation`
        for the specified month.
    """
    updated = scenario.model_copy(
        update={
            "employment": scenario.employment.model_copy(
                update={"as_of": date(period.year, period.month, 1)}
            )
        }
    )
    return compute(
        _annual_to_scenario(updated, period.events), bundle, _period=period.events
    )


def compute_year(
    scenario: AnnualEstimateInput,
    year: int,
    *,
    bundle: PayrollBundle | None = None,
    month_events: list[PeriodPayrollInput] | None = None,
) -> list[Calculation]:
    """Compute payroll for all twelve months of *year*.

    Calls :func:`compute_period` for each month 1-12, threading the
    year-to-date progressive state forward from each period into the next.
    The *scenario.employment.as_of* date is overridden per month; all other
    structural fields are reused for every period.

    Args:
        scenario: The annual payroll scenario (structural fields only).
        year: The calendar year to compute (e.g. ``2026``).
        bundle: Optional pre-loaded knowledge bundle shared across all twelve
            calls.  When ``None``, rulesets are loaded on demand.
        month_events: List of exactly twelve :class:`~ccnl_engine.PeriodPayrollInput`
            instances, one per month January-December.  When ``None``, every
            month uses a default :class:`~ccnl_engine.PeriodPayrollInput` (no special
            events).

    Returns:
        A list of twelve
        :class:`~ccnl_engine.engine.payroll.domain.calculation.Calculation`
        instances, one per month in calendar order.

    Raises:
        InvalidInputError: When *month_events* is provided but does not
            contain exactly 12 entries.
    """
    events: list[PeriodPayrollInput] = (
        month_events
        if month_events is not None
        else [PeriodPayrollInput() for _ in range(12)]
    )
    if len(events) != 12:
        msg = f"month_events must have exactly 12 entries, got {len(events)}"
        raise InvalidInputError(msg, feature="payroll_period")
    results: list[Calculation] = []
    ytd = YTDState()
    for i, ev in enumerate(events):
        month = i + 1
        period = PayrollPeriod(year=year, month=month, events=ev, ytd=ytd)
        calc = compute_period(scenario, period, bundle)
        ytd = _accrue_ytd(ytd, calc)
        results.append(calc)
    return results
