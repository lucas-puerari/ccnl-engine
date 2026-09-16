"""Annual contributions, tax and deduction coordination."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.bilateral_funds import (
    BilateralFundInput,
    FlatMonthlyFund,
)
from ccnl_engine.engine.payroll.domain.employment import Apprentice, FixedTerm
from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.service import contributions as _contrib
from ccnl_engine.engine.payroll.service import irpef as _irpef
from ccnl_engine.engine.payroll.service.art15_deductions import (
    compute_art15_deductions,
)
from ccnl_engine.engine.payroll.service.family_deductions import (
    compute_family_deductions,
)
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.engine.tax.service.loaders import (
    load_art15_deduction_rules,
    load_family_deduction_rules,
)

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.contract.domain.ccnl import (
        CCNL,
        LevelCategory,
    )
    from ccnl_engine.engine.metadata import RulesetIdentity
    from ccnl_engine.engine.payroll.domain.employment import (
        Permanent,
    )
    from ccnl_engine.engine.payroll.domain.scenario import PayrollScenario
    from ccnl_engine.engine.payroll.service.gross import GrossPay
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.rules import DomesticInpsRates, YearRules

_ZERO = Decimal(0)


def _inps_domestic(
    dc: DomesticInpsRates,
    contract: Permanent | FixedTerm | Apprentice,
    gross_monthly: Decimal,
    weekly_hours: Decimal,
) -> tuple[Decimal, Decimal]:
    """Return (employee_annual, employer_annual) via the flat per-hour model.

    Returns:
        Rounded annual INPS contributions for both parties.
    """
    annual_rate = gross_monthly * Decimal(12) / (weekly_hours * Decimal(52))
    hourly_rate_for_bracket = money(annual_rate)
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
) -> tuple[Decimal, Decimal, Decimal]:
    """Return ``(employee, employer, additional)`` via the standard percentage model.

    The employee contribution includes the 1% additional IVS charge on
    earnings above the first pensionable band (Art. 3-ter D.L. 384/1992)
    when ``rules.inps.employee_additional_rate`` is configured.

    Returns:
        A 3-tuple of (employee INPS, employer INPS, employee 1% additional),
        all rounded to two decimal places.  The additional is returned
        separately so callers can include it in trace formulas without
        re-computing it.
    """
    rates = _contrib.resolve_rates(rules, contract, worker_category)
    employee_inps = _contrib.inps_contribution(
        contribution_base,
        rates.employee_rate,
        rates.employee_ivs_rate,
        rules,
        ivs_ceiling_applies=ivs_ceiling_applies,
    )
    additional = _contrib.inps_employee_additional(
        contribution_base,
        rules.inps,
        ivs_ceiling_applies=ivs_ceiling_applies,
    )
    employee_inps = money(employee_inps + additional)
    employer_inps = _contrib.inps_contribution(
        contribution_base,
        rates.employer_rate,
        rates.employer_ivs_rate,
        rules,
        ivs_ceiling_applies=ivs_ceiling_applies,
    )
    return employee_inps, employer_inps, additional


def _inps_contributions(
    rules: YearRules,
    contract: Permanent | FixedTerm | Apprentice,
    gross_monthly: Decimal,
    contribution_base: Decimal,
    worker_category: LevelCategory | None,
    *,
    weekly_hours: Decimal | None,
    ivs_ceiling_applies: bool,
) -> tuple[Decimal, Decimal, Decimal]:
    """Return (inps_employee_annual, inps_employer_annual, additional_annual).

    Routes to the flat per-hour domestic model when
    ``rules.domestic_contributions`` is set, otherwise uses the standard
    percentage model via
    :func:`~ccnl_engine.engine.payroll.service.contributions.resolve_rates`.
    The domestic model does not separate the 1% additional (the per-hour
    tariff is composite), so it returns zero for the additional component.

    Returns:
        A 3-tuple of (employee INPS, employer INPS, employee 1% additional),
        all rounded to two decimal places.

    Raises:
        ValueError: If the domestic model is active and ``weekly_hours`` is None.
    """
    if rules.domestic_contributions is not None:
        if weekly_hours is None:
            msg = "weekly_hours is required when rules.domestic_contributions is set"
            raise ValueError(msg)
        emp, er = _inps_domestic(
            rules.domestic_contributions,
            contract,
            gross_monthly,
            weekly_hours,
        )
        return emp, er, _ZERO
    return _inps_standard(
        rules,
        contract,
        contribution_base,
        worker_category,
        ivs_ceiling_applies=ivs_ceiling_applies,
    )


_TWELVE = Decimal(12)


def _compute_bilateral_funds(
    bilateral_funds: tuple[BilateralFundInput, ...],
    tfr_base: Decimal,
    gross_annual: Decimal,
) -> tuple[Decimal, Decimal]:
    """Return (bilateral_employee_annual, bilateral_employer_annual).

    Accumulates contributions from all funds in the tuple.

    - :class:`~ccnl_engine.engine.payroll.domain.bilateral_funds.FlatMonthlyFund`:
      annualised by multiplying the monthly amount by 12.
    - :class:`~ccnl_engine.engine.payroll.domain.bilateral_funds.RateFund`:
      rate applied to the selected annual base (``tfr_base`` or
      ``gross_annual``).

    Both returned amounts are rounded to two decimal places.

    Args:
        bilateral_funds: Scenario-level fund contributions.
        tfr_base: TFR computation base for rate funds that use it.
        gross_annual: Annual gross pay for rate funds that use it.

    Returns:
        A 2-tuple of (employee_annual, employer_annual).
    """
    employee_total = _ZERO
    employer_total = _ZERO
    for fund in bilateral_funds:
        if isinstance(fund, FlatMonthlyFund):
            employee_total += money(fund.employee_monthly * _TWELVE)
            employer_total += money(fund.employer_monthly * _TWELVE)
        else:
            # RateFund
            base = tfr_base if fund.base == "tfr_base" else gross_annual
            employee_total += money(base * fund.employee_rate)
            employer_total += money(base * fund.employer_rate)
    return money(employee_total), money(employer_total)


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
    relevant_deductions: Decimal,
    rules: YearRules,
) -> tuple[Decimal, frozenset[FiscalSimplification]]:
    """Return (trattamento_integrativo, fiscal_simplifications) for the scenario.

    When the tax data file carries trattamento integrativo parameters, the
    bonus is computed and the three unmodelled simplifications are returned.
    Otherwise, all four ``FiscalSimplification`` members are returned and the
    bonus is zero.

    Args:
        gross_annual: Reddito complessivo di riferimento (taxable income).
        irpef_gross: IRPEF lorda before deductions.
        work_income_deduction: Art. 13 co. 1 deduction.
        relevant_deductions: Sum of Art. 12 + Art. 13 + qualifying Art. 15
            deductions (used for the 15 000-28 000 requisito check).
        rules: Resolved tax rules for the year.

    Returns:
        Tuple of (ti_amount, fiscal_simplifications_frozenset).
    """
    ti_rules = rules.trattamento_integrativo
    if ti_rules is not None:
        trattamento_integrativo = _irpef.trattamento_integrativo(
            gross_annual,
            irpef_gross,
            work_income_deduction,
            relevant_deductions,
            ti_rules,
        )
        simplifications: frozenset[FiscalSimplification] = frozenset({
            FiscalSimplification.NO_ADDIZIONALE_REGIONALE,
            FiscalSimplification.NO_ADDIZIONALE_COMUNALE,
            FiscalSimplification.NO_DETRAZIONI_FAMILIARI,
            FiscalSimplification.NO_DETRAZIONI_ART15_MORTGAGE,
            FiscalSimplification.PARTIAL_DETRAZIONI_ART15,
            FiscalSimplification.NO_BILATERAL_FUNDS,
            FiscalSimplification.NO_ASSEGNO_UNICO,
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
    irpef_due: Decimal,
) -> tuple[Decimal, Decimal, frozenset[FiscalSimplification], bool, bool]:
    """Return amounts, simplifications and applied flags for addizionali.

    The return value is a 5-tuple:
    ``(regionale_amount, comunale_amount, simplifications, reg_applied,
    com_applied)``.

    ``reg_applied`` is ``True`` when the regionale entry was found in the bundle
    and used to compute a rate (even if the amount is zero due to an exemption
    threshold).  ``com_applied`` follows the same semantics for the comunale
    entry.  Both flags are ``False`` when ``irpef_due`` is zero (no-tax area)
    because no entry is consulted in that case.

    Addizionali are only due when the underlying IRPEF is positive. When
    ``irpef_due`` is zero (no-tax area or deductions fully offset IRPEF),
    both surtaxes are zero and the ``NO_ADDIZIONALE_*`` flags are set.

    When ``surtax`` is ``None`` or the relevant field is ``None``, the
    corresponding surtax is zero and its ``FiscalSimplification`` tag is
    added. Otherwise the surtax is computed from the bundled bracket table.

    Returns:
        5-tuple of (regionale_amount, comunale_amount, simplifications,
        reg_applied, com_applied).
    """
    sfs: set[FiscalSimplification] = set(existing)
    addizionale_regionale = _ZERO
    addizionale_comunale = _ZERO

    if irpef_due == _ZERO:
        sfs.add(FiscalSimplification.NO_ADDIZIONALE_REGIONALE)
        sfs.add(FiscalSimplification.NO_ADDIZIONALE_COMUNALE)
        return _ZERO, _ZERO, frozenset(sfs), False, False

    reg_applied = False
    if surtax is not None and regione is not None:
        entry = surtax.regionale.get(regione)
        if entry is not None:
            reg_applied = True
            addizionale_regionale = _irpef.surtax_from_brackets(
                taxable_income, entry.brackets
            )
            sfs.discard(FiscalSimplification.NO_ADDIZIONALE_REGIONALE)
            sfs.discard(FiscalSimplification.ADDIZIONALE_REGIONALE_UNKNOWN)
        else:
            # Jurisdiction provided but not found in the bundle: mark as
            # not_computed (unknown) rather than verified-zero, so the scope
            # exposes a warning instead of silently attesting a zero tax.
            sfs.add(FiscalSimplification.ADDIZIONALE_REGIONALE_UNKNOWN)
            sfs.discard(FiscalSimplification.NO_ADDIZIONALE_REGIONALE)
    else:
        sfs.add(FiscalSimplification.NO_ADDIZIONALE_REGIONALE)

    com_applied = False
    if surtax is not None and comune_belfiore is not None:
        entry_com = surtax.comunale.get(comune_belfiore)
        if entry_com is not None:
            com_applied = True
            addizionale_comunale = _irpef.surtax_from_brackets(
                taxable_income, entry_com.brackets, entry_com.exemption_threshold
            )
            sfs.discard(FiscalSimplification.NO_ADDIZIONALE_COMUNALE)
            sfs.discard(FiscalSimplification.ADDIZIONALE_COMUNALE_UNKNOWN)
        else:
            # Unknown codice catastale: not_computed, not verified-zero.
            sfs.add(FiscalSimplification.ADDIZIONALE_COMUNALE_UNKNOWN)
            sfs.discard(FiscalSimplification.NO_ADDIZIONALE_COMUNALE)
    else:
        sfs.add(FiscalSimplification.NO_ADDIZIONALE_COMUNALE)

    return (
        addizionale_regionale,
        addizionale_comunale,
        frozenset(sfs),
        reg_applied,
        com_applied,
    )


def _run_wr_family_deductions(
    scenario: PayrollScenario,
    reddito_complessivo: Decimal,
    irpef_gross: Decimal,
    work_income_deduction: Decimal,
    year: int,
    *,
    employer_withholds_irpef: bool,
) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal, RulesetIdentity | None]:
    """Compute Art. 12 TUIR family deductions when ``scenario.family`` is set.

    Family deductions reduce the IRPEF actually withheld by the employer; they
    are NOT informational-only (unlike all other work-rules features).  The total
    is subtracted from ``irpef_gross - work_income_deduction`` (floored at zero)
    to obtain ``irpef_net``.

    Args:
        scenario: The payroll scenario.
        reddito_complessivo: Taxable income (gross minus INPS employee
            contribution) used as the Art. 12 reddito complessivo reference.
        irpef_gross: IRPEF before any deductions.
        work_income_deduction: Art. 13 work-income deduction.
        year: Fiscal year for loading rules.
        employer_withholds_irpef: When ``False``, deductions are still computed
            but ``irpef_net`` is zero regardless.

    Returns:
        A 6-tuple of (spouse_deduction, children_deduction, other_deduction,
        total_deduction, unused_deduction, ruleset_identity).  All amounts are
        annual.  ``unused_deduction`` is the portion that exceeded the available
        IRPEF (incapienza — not refundable).  ``ruleset_identity`` is the
        :class:`~ccnl_engine.engine.metadata.RulesetIdentity` for the loaded
        rules, or ``None`` when the rules carry no identity.  When family
        deductions are not applicable (no dependents), all amounts are zero and
        the identity is ``None``.
    """
    family = scenario.family
    if family is None or not family.has_any_dependent:
        return _ZERO, _ZERO, _ZERO, _ZERO, _ZERO, None
    rules = load_family_deduction_rules(year)
    spouse, children, other, total = compute_family_deductions(
        family, reddito_complessivo, rules
    )
    if not employer_withholds_irpef:
        # Deductions computed but irpef_net is always zero here.
        return spouse, children, other, total, total, rules.ruleset
    available = money(max(_ZERO, irpef_gross - work_income_deduction))
    unused = money(max(_ZERO, total - available))
    return spouse, children, other, total, unused, rules.ruleset


def _run_wr_art15_deductions(
    scenario: PayrollScenario,
    irpef_gross: Decimal,
    work_income_deduction: Decimal,
    fam_total: Decimal,
    ulteriore_detrazione_lavoro: Decimal,
    year: int,
    *,
    employer_withholds_irpef: bool,
) -> tuple[Decimal, Decimal, RulesetIdentity | None]:
    """Compute Art. 15 TUIR deductions when ``scenario.art15_deductions`` is set.

    Art. 15 deductions are a flat 19 % credit on eligible expenditure up to
    statutory ceilings.  They reduce the IRPEF actually withheld by the
    employer and are NOT informational-only (unlike most work-rules features).

    The sterilizzazione (Art. 1 c. 3-4 L. 199/2025) is applied by the
    caller after this function returns.

    Args:
        scenario: The payroll scenario.
        irpef_gross: IRPEF before any deductions.
        work_income_deduction: Art. 13 work-income deduction.
        fam_total: Art. 12 family deductions total.
        ulteriore_detrazione_lavoro: Art. 1 c. 6 L. 207/2024 detrazione; reduces
            IRPEF capacity available to Art. 15 credits.
        year: Fiscal year for loading rules.
        employer_withholds_irpef: When ``False``, deductions are still computed
            but ``irpef_net`` is zero regardless.

    Returns:
        A 3-tuple of (art15_total, art15_unused, ruleset_identity).  Both
        amounts are annual.  ``art15_unused`` is the portion that exceeded
        available IRPEF (incapienza — not refundable).  ``ruleset_identity``
        is the :class:`~ccnl_engine.engine.metadata.RulesetIdentity` for the
        loaded rules, or ``None`` when the rules carry no identity.  When
        Art. 15 deductions are not applicable, all amounts are zero and the
        identity is ``None``.
    """
    art15 = scenario.art15_deductions
    if art15 is None or not art15.has_any_onere:
        return _ZERO, _ZERO, None
    rules = load_art15_deduction_rules(year)
    total = compute_art15_deductions(art15, rules)
    if not employer_withholds_irpef:
        # Deductions computed but irpef_net is always zero here.
        return total, total, rules.ruleset
    available = money(
        max(
            _ZERO,
            irpef_gross
            - work_income_deduction
            - fam_total
            - ulteriore_detrazione_lavoro,
        )
    )
    unused = money(max(_ZERO, total - available))
    return total, unused, rules.ruleset


@dataclass(frozen=True)
class FiscalPay:
    """Annual contributions, tax, deductions and net pay."""

    consumed_ruleset_ids: tuple[RulesetIdentity | None, ...]
    inps_employee_annual: Decimal
    inps_employer_annual: Decimal
    inps_employee_additional_annual: Decimal
    employer_funds_annual: Decimal
    tfr_annual: Decimal
    bilateral_employee_annual: Decimal
    bilateral_employer_annual: Decimal
    taxable_income: Decimal
    irpef_gross: Decimal
    work_income_deduction: Decimal
    fam_spouse: Decimal
    fam_children: Decimal
    fam_other: Decimal
    fam_total: Decimal
    fam_unused: Decimal
    art15_total: Decimal
    art15_unused: Decimal
    sterilizzazione_clawback: Decimal
    ulteriore_detrazione_lavoro: Decimal
    somma_esente: Decimal
    irpef_net: Decimal
    trattamento_integrativo: Decimal
    addizionale_regionale: Decimal
    addizionale_comunale: Decimal
    net_annual: Decimal
    net_monthly: Decimal
    employer_cost_annual: Decimal
    employer_withholds_irpef: bool
    fiscal_simplifications: frozenset[FiscalSimplification]


def _update_simplification_flags(
    sfs: frozenset[FiscalSimplification],
    *,
    has_any_dependent: bool,
    art15_total: Decimal,
    ud_rules_present: bool,
    se_rules_present: bool,
    has_bilateral_funds: bool,
) -> frozenset[FiscalSimplification]:
    """Return updated simplification flags after applying optional-feature presence.

    Discards flags for features that were actually computed; adds flags for
    features whose rules are absent from the loaded data file.

    Returns:
        Updated frozenset of active fiscal simplifications.
    """
    sfs_mut: set[FiscalSimplification] = set(sfs)
    if has_any_dependent:
        sfs_mut.discard(FiscalSimplification.NO_DETRAZIONI_FAMILIARI)
    if art15_total > _ZERO:
        sfs_mut.discard(FiscalSimplification.NO_DETRAZIONI_ART15_MORTGAGE)
    if not ud_rules_present:
        sfs_mut.add(FiscalSimplification.NO_ULTERIORE_DETRAZIONE_LAVORO)
    if se_rules_present:
        sfs_mut.discard(FiscalSimplification.NO_SOMMA_ESENTE)
    else:
        sfs_mut.add(FiscalSimplification.NO_SOMMA_ESENTE)
    if has_bilateral_funds:
        sfs_mut.discard(FiscalSimplification.NO_BILATERAL_FUNDS)
    return frozenset(sfs_mut)


def _collect_fiscal_rulesets(
    fam_ruleset: RulesetIdentity | None,
    art15_ruleset: RulesetIdentity | None,
    surtax_regional_ruleset: RulesetIdentity | None,
    surtax_municipal_ruleset: RulesetIdentity | None,
    *,
    family_consumed: bool,
    art15_consumed: bool,
    surtax_reg_consumed: bool,
    surtax_com_consumed: bool,
) -> tuple[RulesetIdentity | None, ...]:
    """Return the ordered tuple of optional-feature ruleset identities.

    Each slot is included when the feature was actually consumed; a ``None``
    entry means the feature ran but its ruleset identity was absent or
    incomplete (treated as unverified by the confidence aggregator).

    Returns:
        A tuple with at most four entries: family deductions, Art. 15,
        surtax regional and surtax municipal, each present only when the
        corresponding feature was consumed.
    """
    ids: list[RulesetIdentity | None] = []
    if fam_ruleset is not None or family_consumed:
        ids.append(fam_ruleset)
    if art15_ruleset is not None or art15_consumed:
        ids.append(art15_ruleset)
    if surtax_reg_consumed:
        ids.append(surtax_regional_ruleset)
    if surtax_com_consumed:
        ids.append(surtax_municipal_ruleset)
    return tuple(ids)


def compute_fiscal(
    scenario: PayrollScenario,
    ccnl: CCNL,
    rules: YearRules,
    surtax: SurtaxRules | None,
    gross: GrossPay,
    year: int,
) -> FiscalPay:
    """Apply the annual fiscal chain to resolved gross pay.

    Returns:
        Contributions, deductions, net pay and fiscal simplifications.
    """
    j = scenario.employee.jurisdiction
    ivs_ceiling_applies = scenario.employee.ivs_ceiling_applies

    inps_employee_annual, inps_employer_annual, inps_employee_additional_annual = (
        _inps_contributions(
            rules,
            scenario.employment.contract,
            gross.gross_monthly,
            gross.contribution_base,
            gross.worker_category,
            weekly_hours=scenario.employee.weekly_hours,
            ivs_ceiling_applies=ivs_ceiling_applies,
        )
    )
    employer_funds_annual = _employer_funds(
        ccnl,
        gross.worker_category,
        gross.contribution_base,
        scenario.employment.calculation_date,
    )
    tfr_annual = _contrib.tfr(gross.tfr_base, rules)
    bilateral_employee_annual, bilateral_employer_annual = _compute_bilateral_funds(
        scenario.bilateral_funds,
        gross.tfr_base,
        gross.gross_annual,
    )

    taxable_income = money(gross.gross_annual - inps_employee_annual)
    irpef_gross = _irpef.irpef_gross(taxable_income, rules)
    work_income_deduction = _irpef.work_income_deduction(taxable_income)
    employer_withholds_irpef = not ccnl.meta.withholding_exempt

    # Family deductions (Art. 12 TUIR): computed when scenario.family is set.
    # These are the only work-rules feature that mutates irpef_net / net_annual.
    # Trattamento integrativo eligibility (Art. 1 D.L. 3/2020) depends on the
    # sum of Art. 13 + Art. 12 + qualifying Art. 15 deductions, per the statute.
    (
        fam_spouse,
        fam_children,
        fam_other,
        fam_total,
        fam_unused,
        fam_ruleset,
    ) = _run_wr_family_deductions(
        scenario=scenario,
        reddito_complessivo=taxable_income,
        irpef_gross=irpef_gross,
        work_income_deduction=work_income_deduction,
        year=year,
        employer_withholds_irpef=employer_withholds_irpef,
    )

    # Ulteriore detrazione del lavoro dipendente (Art. 1 c. 6 L. 207/2024):
    # flat EUR 1 000 for taxable income in (20 000, 32 000].
    # Must be computed before Art. 15 so it can be deducted from available
    # IRPEF when computing art15_unused.
    ud_rules = rules.ulteriore_detrazione
    if ud_rules is not None:
        ulteriore_detrazione_lavoro = _irpef.ulteriore_detrazione_lavoro(
            taxable_income, ud_rules
        )
    else:
        ulteriore_detrazione_lavoro = _ZERO

    # Art. 15 TUIR deductions (interessi passivi mutuo prima casa, etc.).
    art15_total, art15_unused, art15_ruleset = _run_wr_art15_deductions(
        scenario=scenario,
        irpef_gross=irpef_gross,
        work_income_deduction=work_income_deduction,
        fam_total=fam_total,
        ulteriore_detrazione_lavoro=ulteriore_detrazione_lavoro,
        year=year,
        employer_withholds_irpef=employer_withholds_irpef,
    )

    # Sterilizzazione detrazioni (Art. 1 c. 3-4 L. 199/2025): for reddito
    # complessivo > EUR 200 000, reduce oneri detraibili al 19% (Art. 15 c. 1
    # lett. a, b, d, e TUIR; not spese sanitarie lett. c) by EUR 440.
    effective_art15 = _irpef.apply_sterilizzazione_detrazioni(
        art15_total,
        taxable_income,
        rules.sterilizzazione_detrazioni,
    )
    sterilizzazione_clawback = money(art15_total - effective_art15)
    if sterilizzazione_clawback > _ZERO and employer_withholds_irpef:
        art15_capacity = money(
            max(
                _ZERO,
                irpef_gross
                - work_income_deduction
                - fam_total
                - ulteriore_detrazione_lavoro,
            )
        )
        art15_unused = money(max(_ZERO, effective_art15 - art15_capacity))

    # irpef_fiscal: the tax actually owed after all deductions, regardless of
    # whether the employer is a sostituto d'imposta.  Used to gate addizionali
    # (only due when IRPEF is owed) and to derive irpef_net.
    # When the employer is not a sostituto d'imposta, irpef_net is zeroed;
    # irpef_gross and work_income_deduction remain as informational figures.
    irpef_fiscal = money(
        max(
            _ZERO,
            irpef_gross
            - work_income_deduction
            - fam_total
            + sterilizzazione_clawback
            - art15_total
            - ulteriore_detrazione_lavoro,
        )
    )
    irpef_net = irpef_fiscal if employer_withholds_irpef else _ZERO

    # Trattamento integrativo (Art. 1 D.L. 3/2020): computed when the tax
    # data file carries the required parameters.
    # relevant_deductions: Art. 12 + Art. 13 + qualifying Art. 15 (statute).
    # Only pre-2022 mortgage interest qualifies; later mortgages reduce
    # IRPEF but are excluded from the TI relevant-deductions sum.
    art15_pre_1993 = (
        art15_total
        if (
            scenario.art15_deductions is not None
            and scenario.art15_deductions.mortgage_pre_2022
        )
        else _ZERO
    )
    relevant_deductions = work_income_deduction + fam_total + art15_pre_1993
    trattamento_integrativo, fiscal_simplifications = _compute_ti(
        taxable_income,
        irpef_gross,
        work_income_deduction,
        relevant_deductions,
        rules,
    )

    # Somma esente (L. 207/2024): flat-rate net bonus for reddito complessivo
    # up to 20 000 EUR.  Added directly to net pay (not an IRPEF base change).
    se_rules = rules.somma_esente
    somma_esente_amount = (
        money(_irpef.somma_esente(taxable_income, se_rules))
        if se_rules is not None
        else _ZERO
    )

    fam = scenario.family
    has_any_dependent = fam is not None and fam.has_any_dependent
    fiscal_simplifications = _update_simplification_flags(
        fiscal_simplifications,
        has_any_dependent=has_any_dependent,
        art15_total=art15_total,
        ud_rules_present=ud_rules is not None,
        se_rules_present=se_rules is not None,
        has_bilateral_funds=bool(scenario.bilateral_funds),
    )

    # Addizionale regionale e comunale (Art. 50 TUIR; Art. 1 D.Lgs. 360/1998).
    regione = j.regione if j is not None else None
    comune_belfiore = j.comune_belfiore if j is not None else None
    (
        addizionale_regionale,
        addizionale_comunale,
        fiscal_simplifications,
        surtax_reg_consumed,
        surtax_com_consumed,
    ) = _compute_addizionali(
        taxable_income,
        surtax,
        fiscal_simplifications,
        regione=regione,
        comune_belfiore=comune_belfiore,
        irpef_due=irpef_fiscal,
    )

    if employer_withholds_irpef:
        net_annual = money(
            gross.gross_annual
            - inps_employee_annual
            - irpef_net
            - addizionale_regionale
            - addizionale_comunale
            + trattamento_integrativo
            + somma_esente_amount
            - bilateral_employee_annual
        )
    else:
        net_annual = money(
            gross.gross_annual - inps_employee_annual - bilateral_employee_annual
        )
    net_monthly = money(net_annual / gross.additional_months)
    employer_cost_annual = money(
        gross.gross_annual
        + inps_employer_annual
        + employer_funds_annual
        + bilateral_employer_annual
        + tfr_annual
    )

    consumed_ruleset_ids = _collect_fiscal_rulesets(
        fam_ruleset,
        art15_ruleset,
        surtax.regional_ruleset if surtax is not None else None,
        surtax.municipal_ruleset if surtax is not None else None,
        family_consumed=has_any_dependent,
        art15_consumed=scenario.art15_deductions is not None
        and scenario.art15_deductions.has_any_onere,
        surtax_reg_consumed=surtax_reg_consumed,
        surtax_com_consumed=surtax_com_consumed,
    )

    return FiscalPay(
        consumed_ruleset_ids=consumed_ruleset_ids,
        inps_employee_annual=inps_employee_annual,
        inps_employer_annual=inps_employer_annual,
        inps_employee_additional_annual=inps_employee_additional_annual,
        employer_funds_annual=employer_funds_annual,
        tfr_annual=tfr_annual,
        bilateral_employee_annual=bilateral_employee_annual,
        bilateral_employer_annual=bilateral_employer_annual,
        taxable_income=taxable_income,
        irpef_gross=irpef_gross,
        work_income_deduction=work_income_deduction,
        fam_spouse=fam_spouse,
        fam_children=fam_children,
        fam_other=fam_other,
        fam_total=fam_total,
        fam_unused=fam_unused,
        art15_total=art15_total,
        art15_unused=art15_unused,
        sterilizzazione_clawback=sterilizzazione_clawback,
        ulteriore_detrazione_lavoro=ulteriore_detrazione_lavoro,
        somma_esente=somma_esente_amount,
        irpef_net=irpef_net,
        trattamento_integrativo=trattamento_integrativo,
        addizionale_regionale=addizionale_regionale,
        addizionale_comunale=addizionale_comunale,
        net_annual=net_annual,
        net_monthly=net_monthly,
        employer_cost_annual=employer_cost_annual,
        employer_withholds_irpef=employer_withholds_irpef,
        fiscal_simplifications=fiscal_simplifications,
    )
