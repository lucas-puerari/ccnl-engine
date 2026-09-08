"""Gross-to-net and employer cost computation orchestrator."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.contract.service.loaders import load_ccnl
from ccnl_engine.engine.payroll.domain.calculation import (
    Calculation,
    CalculationTrace,
    InputSnapshot,
    TraceCategory,
    TraceStep,
)
from ccnl_engine.engine.payroll.domain.employee import (
    DestinationRalOverride,
    RalOverride,
)
from ccnl_engine.engine.payroll.domain.employment import Apprentice, FixedTerm
from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.domain.payroll_result import PayrollResult
from ccnl_engine.engine.payroll.service import contributions as _contrib
from ccnl_engine.engine.payroll.service import irpef as _irpef
from ccnl_engine.engine.payroll.service.apprenticeship import _apprentice_chain
from ccnl_engine.engine.payroll.service.chain import _level_chain
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.engine.payroll.service.seniority import _resolve_seniority_count
from ccnl_engine.engine.payroll.service.types import AnnualisedPay, MonthlyPayChain
from ccnl_engine.engine.surtax.service.loaders import load_surtax_rules
from ccnl_engine.engine.tax.service.loaders import load_year_rules
from ccnl_engine.knowledge.version import __version__ as knowledge_version
from ccnl_engine.version import __version__ as engine_version

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import date

    from ccnl_engine.engine.contract.domain.ccnl import (
        CCNL,
        Allowance,
        Level,
        LevelCategory,
        SeniorityIncrements,
        SupplementaryAllowance,
    )
    from ccnl_engine.engine.payroll.domain.employee import RalOverrideMode
    from ccnl_engine.engine.payroll.domain.employment import (
        Permanent,
    )
    from ccnl_engine.engine.payroll.domain.scenario import Employment, PayrollScenario
    from ccnl_engine.engine.provenance.domain.chain import RuleProvenance
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.rules import DomesticInpsRates, YearRules

_ZERO = Decimal(0)


def _resolve_tax_year(employment: Employment) -> int:
    """Return the tax year for rule loading.

    Uses the explicit override when set, otherwise falls back to the
    calendar year of the employment date.

    Returns:
        The integer year to use for ``load_year_rules`` and
        ``load_surtax_rules``.
    """
    if employment.tax_year is not None:
        return employment.tax_year
    return employment.date.year


def _resolve_worker_category(
    scenario: PayrollScenario,
    level: Level,
) -> LevelCategory | None:
    """Return the effective worker category.

    Prefers an explicit override from the scenario; falls back to the
    level's own category.

    Returns:
        The resolved :class:`~ccnl_engine.engine.contract.domain.ccnl\
.LevelCategory`, or ``None``.
    """
    if scenario.employee.category is not None:
        return scenario.employee.category
    return level.category


def _resolve_chain_and_apprenticeship(
    ccnl: CCNL,
    level: Level,
    contract: Permanent | FixedTerm | Apprentice,
    count: int,
    scenario: PayrollScenario,
    as_of: date,
    worker_category: LevelCategory | None,
    seniority_months_val: int | None,
    ral_override_mode: RalOverrideMode | None,
) -> tuple[MonthlyPayChain, Decimal | None, str | None, Decimal]:
    """Build the pay chain and resolve apprenticeship factors.

    Returns:
        A 4-tuple of:
        - ``chain_full_time``: the full-time monthly pay chain
        - ``apprenticeship_pct``: the percentage factor (``None`` when not
          a percentage-track apprentice)
        - ``under_level_code``: the under-classification level code (``None``
          when not an under-classification apprentice)
        - ``effective_factor``: the combined part-time and apprenticeship
          scaling factor used for ``chain.scaled(...)``

    Raises:
        ValueError: If DestinationRalOverride is used with an
            under-classification apprenticeship track (no percentage factor).
    """
    effective_factor = scenario.employee.part_time_pct
    apprenticeship_pct: Decimal | None = None
    under_level_code: str | None = None
    if isinstance(contract, Apprentice):
        chain_full_time, apprenticeship_pct, under_level_code = _apprentice_chain(
            ccnl,
            level,
            contract,
            count,
            scenario.employee.roles,
            as_of,
            worker_category=worker_category,
            seniority_months=seniority_months_val,
        )
        if apprenticeship_pct is not None:
            effective_factor *= apprenticeship_pct
        if (
            isinstance(ral_override_mode, DestinationRalOverride)
            and apprenticeship_pct is None
        ):
            msg = (
                "DestinationRalOverride requires a percentage-based "
                "apprenticeship track; the resolved track uses under-classification"
            )
            raise ValueError(msg)
    else:
        chain_full_time = _level_chain(
            ccnl,
            level,
            count,
            scenario.employee.roles,
            as_of,
            worker_category=worker_category,
            is_apprentice=False,
            seniority_months=seniority_months_val,
        )
    return chain_full_time, apprenticeship_pct, under_level_code, effective_factor


def _collect_provenance(
    level: Level,
    as_of: date,
    chain: MonthlyPayChain,
    seniority_increments: SeniorityIncrements,
) -> tuple[RuleProvenance, ...]:
    """Collect the provenance chain of the rules that produced a pay outcome.

    Every provenance-bearing item that actually contributed to the computed
    pay is gathered: the resolved level (plus any per-period base-salary
    override), each applied allowance, and the seniority-increment rule.
    Only non-``None`` entries are kept.

    Returns:
        An ordered tuple of the contributing :class:`RuleProvenance` objects.
    """
    out: list[RuleProvenance] = []

    def _add(prov: RuleProvenance | None) -> None:
        if prov is not None:
            out.append(prov)

    _add(level.provenance)
    for period in level.base_salary.periods:
        if period.valid_from <= as_of and (
            period.valid_until is None or as_of < period.valid_until
        ):
            _add(period.provenance)
            break
    for allowance, _ in chain.allowances:
        _add(allowance.provenance)
    _add(seniority_increments.provenance)
    return tuple(out)


def _extract_ral_override(
    scenario: PayrollScenario,
) -> RalOverrideMode | None:
    """Extract the RAL-override mode from the scenario's agreement.

    Returns:
        The ``ral_override`` from the :class:`~ccnl_engine.engine.payroll\
.domain.scenario.Agreement`, or ``None`` when no agreement is set.
    """
    agreement = scenario.employee.agreement
    return agreement.ral_override if agreement is not None else None


def _guard_ral_conflict(
    second_level_allowances: tuple[SupplementaryAllowance, ...],
    ral_override_mode: RalOverrideMode | None,
) -> None:
    """Raise if second-level allowances are combined with a RAL override.

    Raises:
        ValueError: When ``second_level_allowances`` is non-empty and a RAL
            override is also set.
    """
    if second_level_allowances and ral_override_mode is not None:
        msg = (
            "second_level_allowances cannot be combined with a RAL override: "
            "the negotiated figure already represents the full agreed salary"
        )
        raise ValueError(msg)


def _validate_ral_override(
    ral_override: RalOverrideMode | None,
    contract: Permanent | FixedTerm | Apprentice,
) -> bool:
    """Validate the RAL-override mode and return whether an override is active.

    Returns:
        True when a RAL override is set.

    Raises:
        ValueError: If ``DestinationRalOverride`` is used with a non-Apprentice
            contract type.
    """
    if isinstance(ral_override, DestinationRalOverride) and not isinstance(
        contract, Apprentice
    ):
        msg = "DestinationRalOverride is only valid for Apprentice employment"
        raise ValueError(msg)  # ruff: ignore[type-check-without-type-error]
    return ral_override is not None


def _override_gross(
    ral_override_mode: RalOverrideMode | None,
    apprenticeship_pct: Decimal | None,
    gross_annual: Decimal,
    gross_monthly: Decimal,
    additional_months: Decimal,
) -> tuple[Decimal, Decimal]:
    """Return (gross_annual, gross_monthly) after applying any RAL override.

    Returns:
        Tuple of (gross_annual, gross_monthly). Unchanged when no override is
        given.
    """
    if isinstance(ral_override_mode, RalOverride):
        # Actual agreed salary; taken as-is.
        gross_annual = money(ral_override_mode.value)
    elif isinstance(ral_override_mode, DestinationRalOverride):
        # Destination-level RAL; apprenticeship_pct is guaranteed non-None here.
        gross_annual = money(
            ral_override_mode.value * apprenticeship_pct  # type: ignore[operator]
        )
    else:
        return gross_annual, gross_monthly
    return gross_annual, money(gross_annual / additional_months)


def _scale_second_level(
    allowances: Sequence[SupplementaryAllowance],
    part_time_pct: Decimal,
    apprenticeship_pct: Decimal | None,
) -> tuple[list[tuple[Decimal, SupplementaryAllowance]], Decimal]:
    """Scale second-level allowances by part_time_pct and optionally apprenticeship_pct.

    Each item is multiplied by ``part_time_pct``; the apprenticeship percentage
    is applied on top only when ``apprenticeship_pct`` is not ``None`` and the
    item's ``apprenticeship_pct_relevant`` flag is ``True``.

    Returns:
        A tuple of (scaled pairs, monthly total) where scaled pairs are
        (scaled_monthly, allowance) items and monthly total is their rounded sum.
    """
    result: list[tuple[Decimal, SupplementaryAllowance]] = []
    total = _ZERO
    for sl in allowances:
        scaled = money(sl.monthly * part_time_pct)
        if apprenticeship_pct is not None and sl.apprenticeship_pct_relevant:
            scaled = money(scaled * apprenticeship_pct)
        result.append((scaled, sl))
        total += scaled
    return result, money(total)


def _annualise(
    chain: MonthlyPayChain,
    ad_personam: Decimal,
    additional_months: Decimal,
    second_level: Sequence[tuple[Decimal, SupplementaryAllowance]] = (),
) -> AnnualisedPay:
    """Annualise the monthly pay chain into gross and exclusion amounts.

    ``second_level`` carries already-scaled monthly amounts paired with their
    :class:`~ccnl_engine.engine.contract.domain.ccnl.SupplementaryAllowance`
    descriptors so that ``months_per_year``, ``contribution_relevant``, and
    ``tfr_relevant`` can be honoured just like CCNL-level allowances.

    Returns:
        An :class:`AnnualisedPay` with rounded gross and exclusion totals.
    """
    gross = (chain.base + chain.seniority + ad_personam) * additional_months
    excluded_contrib = _ZERO
    excluded_tfr = _ZERO

    # Normalise both allowance sequences to (monthly, item) so they can be
    # processed in a single loop.  chain.allowances stores (Allowance, monthly)
    # (reversed order compared to second_level).
    combined: list[tuple[Decimal, Allowance | SupplementaryAllowance]] = [
        (monthly, a) for a, monthly in chain.allowances
    ] + [(monthly, sl) for monthly, sl in second_level]

    for monthly, item in combined:
        months = (
            Decimal(item.months_per_year)
            if item.months_per_year is not None
            else additional_months
        )
        annual = monthly * months
        gross += annual
        if not item.contribution_relevant:
            excluded_contrib += annual
        if not item.tfr_relevant:
            excluded_tfr += annual

    return AnnualisedPay(
        gross=money(gross),
        excluded_from_contributions=money(excluded_contrib),
        excluded_from_tfr=money(excluded_tfr),
    )


def _inps_domestic(
    dc: DomesticInpsRates,
    contract: Permanent | FixedTerm | Apprentice,
    gross_monthly: Decimal,
    hourly_divisor: Decimal,
    weekly_hours: Decimal,
) -> tuple[Decimal, Decimal]:
    """Return (employee_annual, employer_annual) via the flat per-hour model.

    Returns:
        Rounded annual INPS contributions for both parties.
    """
    hourly_rate_for_bracket = money(gross_monthly / hourly_divisor)
    is_fixed_term = isinstance(contract, FixedTerm)
    emp_ph, er_ph = _contrib.resolve_domestic_inps_rate(
        dc,
        hourly_rate_for_bracket,
        weekly_hours,
        is_fixed_term=is_fixed_term,
    )
    annual_hours = weekly_hours * 52
    return money(emp_ph * annual_hours), money(er_ph * annual_hours)


def _inps_standard(
    rules: YearRules,
    contract: Permanent | FixedTerm | Apprentice,
    contribution_base: Decimal,
    worker_category: LevelCategory | None,
    *,
    ivs_ceiling_applies: bool,
) -> tuple[Decimal, Decimal]:
    """Return (employee_annual, employer_annual) via the standard percentage model.

    Returns:
        Rounded annual INPS contributions for both parties.
    """
    rates = _contrib.resolve_rates(rules, contract, worker_category)
    employee_inps = _contrib.inps_contribution(
        contribution_base,
        rates.employee_rate,
        rates.employee_ivs_rate,
        rules,
        ivs_ceiling_applies=ivs_ceiling_applies,
    )
    employer_inps = _contrib.inps_contribution(
        contribution_base,
        rates.employer_rate,
        rates.employer_ivs_rate,
        rules,
        ivs_ceiling_applies=ivs_ceiling_applies,
    )
    return employee_inps, employer_inps


def _inps_contributions(
    rules: YearRules,
    contract: Permanent | FixedTerm | Apprentice,
    gross_monthly: Decimal,
    hourly_divisor: Decimal,
    contribution_base: Decimal,
    worker_category: LevelCategory | None,
    *,
    weekly_hours: Decimal | None,
    ivs_ceiling_applies: bool,
) -> tuple[Decimal, Decimal]:
    """Return (inps_employee_annual, inps_employer_annual) for the employee.

    Routes to the flat per-hour domestic model when
    ``rules.domestic_contributions`` is set, otherwise uses the standard
    percentage model via
    :func:`~ccnl_engine.engine.payroll.service.contributions.resolve_rates`.

    Returns:
        A tuple of (employee annual INPS contribution, employer annual
        INPS contribution), both rounded to two decimal places.

    Raises:
        ValueError: If the domestic model is active and ``weekly_hours`` is None.
    """
    if rules.domestic_contributions is not None:
        if weekly_hours is None:
            msg = "weekly_hours is required when rules.domestic_contributions is set"
            raise ValueError(msg)
        return _inps_domestic(
            rules.domestic_contributions,
            contract,
            gross_monthly,
            hourly_divisor,
            weekly_hours,
        )
    return _inps_standard(
        rules,
        contract,
        contribution_base,
        worker_category,
        ivs_ceiling_applies=ivs_ceiling_applies,
    )


def _employer_funds(
    ccnl: CCNL,
    category: LevelCategory | None,
    contribution_base: Decimal,
    as_of: date,
) -> Decimal:
    total = _ZERO
    for fund in ccnl.parameters.employer_funds:
        if _contrib.fund_applies_to(fund, category):
            total += money(contribution_base * fund.rate.value_at(as_of))
    return money(total)


def _compute_ti(
    gross_annual: Decimal,
    irpef_gross: Decimal,
    work_income_deduction: Decimal,
    rules: YearRules,
) -> tuple[Decimal, frozenset[FiscalSimplification]]:
    """Return (trattamento_integrativo, fiscal_simplifications) for the scenario.

    When the tax data file carries trattamento integrativo parameters, the
    bonus is computed and the three unmodelled simplifications are returned.
    Otherwise, all four ``FiscalSimplification`` members are returned and the
    bonus is zero.

    Returns:
        Tuple of (ti_amount, fiscal_simplifications_frozenset).
    """
    ti_rules = rules.trattamento_integrativo
    if ti_rules is not None:
        trattamento_integrativo = _irpef.trattamento_integrativo(
            gross_annual, irpef_gross, work_income_deduction, ti_rules
        )
        simplifications: frozenset[FiscalSimplification] = frozenset({
            FiscalSimplification.NO_ADDIZIONALE_REGIONALE,
            FiscalSimplification.NO_ADDIZIONALE_COMUNALE,
            FiscalSimplification.NO_DETRAZIONI_FAMILIARI,
            FiscalSimplification.NO_STERILIZZAZIONE_DETRAZIONI,
        })
    else:
        trattamento_integrativo = _ZERO
        simplifications = frozenset(FiscalSimplification)
    return trattamento_integrativo, simplifications


def _compute_addizionali(
    taxable_income: Decimal,
    surtax: SurtaxRules | None,
    existing: frozenset[FiscalSimplification],
    *,
    regione: str | None,
    comune_belfiore: str | None,
) -> tuple[Decimal, Decimal, frozenset[FiscalSimplification]]:
    """Return (addizionale_regionale, addizionale_comunale, updated_simplifications).

    When ``surtax`` is ``None`` or the relevant field is ``None``, the
    corresponding surtax is zero and its ``FiscalSimplification`` tag is
    added. Otherwise the surtax is computed from the bundled bracket table.

    Returns:
        Tuple of (regionale_amount, comunale_amount, simplifications_frozenset).
    """
    sfs: set[FiscalSimplification] = set(existing)
    addizionale_regionale = _ZERO
    addizionale_comunale = _ZERO

    if surtax is not None and regione is not None:
        entry = surtax.regionale.get(regione)
        if entry is not None:
            addizionale_regionale = _irpef.surtax_from_brackets(
                taxable_income, entry.brackets
            )
        # If region name is not found, addizionale_regionale stays zero (no flag:
        # the caller intentionally passed a region; it is simply not in the
        # dataset, e.g. a non-deliberated rate or an unrecognised name).
        sfs.discard(FiscalSimplification.NO_ADDIZIONALE_REGIONALE)
    else:
        sfs.add(FiscalSimplification.NO_ADDIZIONALE_REGIONALE)

    if surtax is not None and comune_belfiore is not None:
        entry_com = surtax.comunale.get(comune_belfiore)
        if entry_com is not None:
            addizionale_comunale = _irpef.surtax_from_brackets(
                taxable_income, entry_com.brackets, entry_com.exemption_threshold
            )
        # Unrecognised belfiore code → zero, no flag (municipality has 0%).
        sfs.discard(FiscalSimplification.NO_ADDIZIONALE_COMUNALE)
    else:
        sfs.add(FiscalSimplification.NO_ADDIZIONALE_COMUNALE)

    return addizionale_regionale, addizionale_comunale, frozenset(sfs)


def _build_trace(
    ccnl_id: str,
    level: Level,
    chain: MonthlyPayChain,
    seniority_count: int,
    ad_personam: Decimal,
    scaled_second_level: list[tuple[Decimal, SupplementaryAllowance]],
    gross_monthly: Decimal,
) -> CalculationTrace:
    """Build the step-by-step gross computation trace, post-scaling.

    All amounts are taken from already-scaled values (part-time and
    apprenticeship percentages already applied), so the trace faithfully
    represents the actual contribution of each component.

    Returns:
        A :class:`CalculationTrace` whose non-GROSS steps sum to
        ``gross_monthly``.
    """
    steps: list[TraceStep] = [
        TraceStep(
            category=TraceCategory.BASE_SALARY,
            label="Base retributiva",
            amount=chain.base,
            detail=f"{level.code}@{ccnl_id}",
        ),
        TraceStep(
            category=TraceCategory.SENIORITY,
            label="Scatti di anzianità",
            amount=chain.seniority,
            detail=f"scatti={seniority_count}",
        ),
    ]

    for allowance, amount in chain.allowances:
        steps.append(
            TraceStep(
                category=TraceCategory.ALLOWANCE,
                label=allowance.description,
                amount=amount,
                detail=allowance.code,
            )
        )

    if ad_personam > _ZERO:
        steps.append(
            TraceStep(
                category=TraceCategory.AD_PERSONAM,
                label="Ad personam",
                amount=ad_personam,
            )
        )

    for scaled, sl in scaled_second_level:
        if scaled > _ZERO:
            steps.append(
                TraceStep(
                    category=TraceCategory.SECOND_LEVEL,
                    label=sl.description,
                    amount=scaled,
                    detail=sl.code,
                )
            )

    # When a negotiated RAL overrides the component sum (e.g. DestinationRalOverride
    # or a plain RalOverride), the gross_monthly differs from the sum of components.
    # A RAL_OVERRIDE step bridges the gap so the invariant always holds:
    #   sum(non-GROSS steps) == GROSS step amount
    component_sum = money(sum((s.amount for s in steps), _ZERO))
    ral_delta = money(gross_monthly - component_sum)
    if ral_delta != _ZERO:
        steps.append(
            TraceStep(
                category=TraceCategory.RAL_OVERRIDE,
                label="Rettifica RAL concordata",
                amount=ral_delta,
            )
        )

    steps.append(
        TraceStep(
            category=TraceCategory.GROSS,
            label="Lordo mensile",
            amount=gross_monthly,
        )
    )

    return CalculationTrace(steps=tuple(steps))


def compute(scenario: PayrollScenario) -> Calculation:
    """Compute gross-to-net salary and employer cost for a payroll scenario.

    Loads the CCNL, tax/INPS rules, and (when jurisdiction is set) surtax
    rules from the bundled knowledge base, then runs the full payroll
    computation chain.

    Args:
        scenario: The full payroll scenario — worker data and employment
            relationship — as a :class:`~ccnl_engine.engine.payroll.domain\
.scenario.PayrollScenario`.

    Returns:
        A :class:`~ccnl_engine.engine.payroll.domain.calculation.Calculation`
        whose ``result`` is the :class:`PayrollResult` with all gross, net,
        and cost figures, together with the engine version, the ruleset
        identities used and a serialisable snapshot of the inputs.

    """
    # Load rulesets from the knowledge base
    ccnl = load_ccnl(scenario.employment.ccnl)
    as_of = scenario.employment.date
    year = _resolve_tax_year(scenario.employment)
    rules = load_year_rules(
        year, ccnl.meta.tax_sector, scenario.employment.employer.num_employees
    )
    j = scenario.employee.jurisdiction
    needs_surtax = j is not None and (
        j.regione is not None or j.comune_belfiore is not None
    )
    surtax = load_surtax_rules(year) if needs_surtax else None

    # Resolve inputs
    contract = scenario.employment.contract
    second_level_allowances = scenario.employment.employer.second_level_allowances
    ral_override_mode = _extract_ral_override(scenario)
    _guard_ral_conflict(second_level_allowances, ral_override_mode)

    ral_override = _validate_ral_override(ral_override_mode, contract)

    level = ccnl.level_by_code(scenario.employee.level_code)
    worker_category = _resolve_worker_category(scenario, level)

    seniority_count_val = scenario.employee.seniority_count
    seniority_months_val = scenario.employee.seniority_months
    count = _resolve_seniority_count(
        ccnl.parameters.seniority_increments,
        scenario.employee.level_code,
        seniority_count_val,
        seniority_months_val,
        worker_category=worker_category,
    )
    additional_months = ccnl.parameters.additional_months.value_at(as_of)

    chain_full_time, apprenticeship_pct, under_level_code, effective_factor = (
        _resolve_chain_and_apprenticeship(
            ccnl,
            level,
            contract,
            count,
            scenario,
            as_of,
            worker_category,
            seniority_months_val,
            ral_override_mode,
        )
    )

    chain = (
        chain_full_time.scaled_selective(
            scenario.employee.part_time_pct, apprenticeship_pct
        )
        if apprenticeship_pct is not None
        else chain_full_time.scaled(effective_factor)
    )
    agreement = scenario.employee.agreement
    ad_personam = money(
        agreement.ad_personam_monthly if agreement is not None else _ZERO
    )
    scaled_second_level, second_level_monthly_total = _scale_second_level(
        second_level_allowances, scenario.employee.part_time_pct, apprenticeship_pct
    )

    gross_monthly = money(
        chain.base
        + chain.seniority
        + chain.allowances_total
        + ad_personam
        + second_level_monthly_total
    )
    annual = _annualise(chain, ad_personam, additional_months, scaled_second_level)
    gross_annual = annual.gross

    gross_annual, gross_monthly = _override_gross(
        ral_override_mode,
        apprenticeship_pct,
        gross_annual,
        gross_monthly,
        additional_months,
    )

    # The negotiated figure is the full RAL; CCNL exclusions don't apply to it.
    contribution_base = (
        gross_annual
        if ral_override
        else money(gross_annual - annual.excluded_from_contributions)
    )
    tfr_base = (
        gross_annual if ral_override else money(gross_annual - annual.excluded_from_tfr)
    )
    hourly_divisor = ccnl.parameters.hourly_divisor.value_at(as_of)

    ivs_ceiling_applies = scenario.employee.ivs_ceiling_applies

    inps_employee_annual, inps_employer_annual = _inps_contributions(
        rules,
        contract,
        gross_monthly,
        hourly_divisor,
        contribution_base,
        worker_category,
        weekly_hours=scenario.employee.weekly_hours,
        ivs_ceiling_applies=ivs_ceiling_applies,
    )
    employer_funds_annual = _employer_funds(
        ccnl, worker_category, contribution_base, as_of
    )
    tfr_annual = _contrib.tfr(tfr_base, rules)

    # Not modelled (scope of a separate fiscal layer): detrazioni per carichi
    # di famiglia (Art. 12 TUIR); sterilization of detrazioni for redditi
    # > EUR 200k (Art. 1 c. 3-4 L. 199/2025).
    taxable_income = money(gross_annual - inps_employee_annual)
    irpef_gross = _irpef.irpef_gross(taxable_income, rules)
    work_income_deduction = _irpef.work_income_deduction(gross_annual, rules)
    # When the employer is not a sostituto d'imposta, irpef_net is zeroed;
    # irpef_gross and work_income_deduction remain as informational figures.
    employer_withholds_irpef = not ccnl.meta.withholding_exempt
    irpef_net = (
        money(max(_ZERO, irpef_gross - work_income_deduction))
        if employer_withholds_irpef
        else _ZERO
    )

    # Trattamento integrativo (Art. 1 D.L. 3/2020): computed when the tax
    # data file carries the required parameters.
    trattamento_integrativo, fiscal_simplifications = _compute_ti(
        gross_annual, irpef_gross, work_income_deduction, rules
    )

    # Addizionale regionale e comunale (Art. 50 TUIR; Art. 1 D.Lgs. 360/1998).
    regione = j.regione if j is not None else None
    comune_belfiore = j.comune_belfiore if j is not None else None
    addizionale_regionale, addizionale_comunale, fiscal_simplifications = (
        _compute_addizionali(
            taxable_income,
            surtax,
            fiscal_simplifications,
            regione=regione,
            comune_belfiore=comune_belfiore,
        )
    )

    net_annual = money(
        gross_annual
        - inps_employee_annual
        - irpef_net
        - addizionale_regionale
        - addizionale_comunale
        + trattamento_integrativo
    )
    net_monthly = money(net_annual / additional_months)
    employer_cost_annual = money(
        gross_annual + inps_employer_annual + employer_funds_annual + tfr_annual
    )

    result = PayrollResult(
        ccnl_id=ccnl.meta.ccnl_id,
        level_code=scenario.employee.level_code,
        employment_type=contract.type,
        part_time_pct=scenario.employee.part_time_pct,
        as_of=as_of,
        year=as_of.year,
        seniority_count=count,
        base_monthly=chain.base,
        seniority_monthly=chain.seniority,
        allowances_monthly=chain.allowances_total,
        ad_personam_monthly=ad_personam,
        second_level_monthly=second_level_monthly_total,
        gross_monthly=gross_monthly,
        gross_annual=gross_annual,
        hourly_rate=money(gross_monthly / hourly_divisor),
        apprenticeship_pct=apprenticeship_pct,
        apprenticeship_under_level_code=under_level_code,
        inps_employee_annual=inps_employee_annual,
        inps_employer_annual=inps_employer_annual,
        employer_funds_annual=employer_funds_annual,
        tfr_annual=tfr_annual,
        taxable_income=taxable_income,
        irpef_gross=irpef_gross,
        work_income_deduction=work_income_deduction,
        irpef_net=irpef_net,
        employer_withholds_irpef=employer_withholds_irpef,
        addizionale_regionale_annual=addizionale_regionale,
        addizionale_comunale_annual=addizionale_comunale,
        trattamento_integrativo=trattamento_integrativo,
        fiscal_simplifications=fiscal_simplifications,
        net_annual=net_annual,
        net_monthly=net_monthly,
        employer_cost_annual=employer_cost_annual,
        provenance=_collect_provenance(
            level,
            as_of,
            chain,
            ccnl.parameters.seniority_increments,
        ),
    )

    snapshot = InputSnapshot.capture(
        scenario=scenario,
        ccnl_id=ccnl.meta.ccnl_id,
        tax_sector=ccnl.meta.tax_sector,
        year=rules.year,
        uses_surtax=surtax is not None,
    )

    return Calculation(
        engine_version=engine_version,
        ruleset_version=_ruleset_versions(ccnl, rules, surtax),
        input_snapshot=snapshot,
        result=result,
        trace=_build_trace(
            ccnl_id=ccnl.meta.ccnl_id,
            level=level,
            chain=chain,
            seniority_count=count,
            ad_personam=ad_personam,
            scaled_second_level=scaled_second_level,
            gross_monthly=gross_monthly,
        ),
    )


def _ruleset_versions(
    ccnl: CCNL,
    rules: YearRules,
    surtax: SurtaxRules | None,
) -> dict[str, str]:
    """Resolve the ``{kind: id@version}`` identities of the used rulesets.

    Rulesets without a recorded block fall back to the knowledge-base version.

    Returns:
        A mapping from ruleset kind to its ``id@version`` identity.
    """
    versions: dict[str, str] = {}
    if ccnl.ruleset is not None:
        versions["ccnl"] = str(ccnl.ruleset)
    else:
        versions["ccnl"] = f"{ccnl.meta.ccnl_id}@{knowledge_version}"
    if rules.ruleset is not None:
        versions["tax"] = str(rules.ruleset)
    else:
        versions["tax"] = f"tax/{rules.year}/{ccnl.meta.tax_sector}@{knowledge_version}"
    if rules.inps_ruleset is not None:
        versions["inps"] = str(rules.inps_ruleset)
    if surtax is not None:
        if surtax.ruleset is not None:
            versions["surtax"] = str(surtax.ruleset)
        else:
            versions["surtax"] = f"surtax/{surtax.year}@{knowledge_version}"
    return versions
