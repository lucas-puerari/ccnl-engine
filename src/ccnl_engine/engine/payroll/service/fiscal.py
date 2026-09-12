"""Annual contributions, tax and deduction coordination."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

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
    relevant_deductions: Decimal,
    rules: YearRules,
) -> tuple[Decimal, frozenset[FiscalSimplification]]:
    """Return (trattamento_integrativo, fiscal_simplifications) for the scenario.

    When the tax data file carries trattamento integrativo parameters, the
    bonus is computed and the three unmodelled simplifications are returned.
    Otherwise, all four ``FiscalSimplification`` members are returned and the
    bonus is zero.

    Args:
        gross_annual: RAL (proxy for reddito complessivo di riferimento).
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
            FiscalSimplification.NO_DETRAZIONI_ART15,
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
            sfs.discard(FiscalSimplification.NO_ADDIZIONALE_REGIONALE)
        else:
            # Jurisdiction provided but not found in the bundle: mark as
            # not_computed (unknown) rather than verified-zero, so the scope
            # exposes a warning instead of silently attesting a zero tax.
            sfs.add(FiscalSimplification.ADDIZIONALE_REGIONALE_UNKNOWN)
            sfs.discard(FiscalSimplification.NO_ADDIZIONALE_REGIONALE)
    else:
        sfs.add(FiscalSimplification.NO_ADDIZIONALE_REGIONALE)

    if surtax is not None and comune_belfiore is not None:
        entry_com = surtax.comunale.get(comune_belfiore)
        if entry_com is not None:
            addizionale_comunale = _irpef.surtax_from_brackets(
                taxable_income, entry_com.brackets, entry_com.exemption_threshold
            )
            sfs.discard(FiscalSimplification.NO_ADDIZIONALE_COMUNALE)
        else:
            # Unknown belfiore code: not_computed, not verified-zero.
            sfs.add(FiscalSimplification.ADDIZIONALE_COMUNALE_UNKNOWN)
            sfs.discard(FiscalSimplification.NO_ADDIZIONALE_COMUNALE)
    else:
        sfs.add(FiscalSimplification.NO_ADDIZIONALE_COMUNALE)

    return addizionale_regionale, addizionale_comunale, frozenset(sfs)


def _run_wr_family_deductions(
    scenario: PayrollScenario,
    gross_annual: Decimal,
    irpef_gross: Decimal,
    work_income_deduction: Decimal,
    year: int,
    *,
    employer_withholds_irpef: bool,
) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal]:
    """Compute Art. 12 TUIR family deductions when ``scenario.family`` is set.

    Family deductions reduce the IRPEF actually withheld by the employer; they
    are NOT informational-only (unlike all other work-rules features).  The total is
    subtracted from ``irpef_gross - work_income_deduction`` (floored at zero)
    to obtain ``irpef_net``.

    Args:
        scenario: The payroll scenario.
        gross_annual: Annual gross pay (proxy for reddito complessivo).
        irpef_gross: IRPEF before any deductions.
        work_income_deduction: Art. 13 work-income deduction.
        year: Fiscal year for loading rules.
        employer_withholds_irpef: When ``False``, deductions are still computed
            but ``irpef_net`` is zero regardless.

    Returns:
        A 5-tuple of (spouse_deduction, children_deduction, other_deduction,
        total_deduction, unused_deduction).  All amounts are annual.
        ``unused_deduction`` is the portion that exceeded the available
        IRPEF (incapienza — not refundable).
    """
    family = scenario.family
    if family is None or not family.has_any_dependent:
        return _ZERO, _ZERO, _ZERO, _ZERO, _ZERO
    rules = load_family_deduction_rules(year)
    spouse, children, other, total = compute_family_deductions(
        family, gross_annual, rules
    )
    if not employer_withholds_irpef:
        # Deductions computed but irpef_net is always zero here.
        return spouse, children, other, total, total
    available = money(max(_ZERO, irpef_gross - work_income_deduction))
    unused = money(max(_ZERO, total - available))
    return spouse, children, other, total, unused


def _run_wr_art15_deductions(
    scenario: PayrollScenario,
    irpef_gross: Decimal,
    work_income_deduction: Decimal,
    fam_total: Decimal,
    year: int,
    *,
    employer_withholds_irpef: bool,
) -> tuple[Decimal, Decimal]:
    """Compute Art. 15 TUIR deductions when ``scenario.art15_deductions`` is set.

    Art. 15 deductions are a flat 19 % credit on eligible expenditure up to
    statutory ceilings.  They reduce the IRPEF actually withheld by the
    employer and are NOT informational-only (unlike most work-rules features).

    Art. 1 c. 3-4 L. 199/2025 sterilizzazione does NOT apply here: the
    EUR 440 clawback is specific to Art. 12 + Art. 13 TUIR.

    Args:
        scenario: The payroll scenario.
        irpef_gross: IRPEF before any deductions.
        work_income_deduction: Art. 13 work-income deduction (post-sterilizzazione).
        fam_total: Art. 12 family deductions total (post-sterilizzazione).
        year: Fiscal year for loading rules.
        employer_withholds_irpef: When ``False``, deductions are still computed
            but ``irpef_net`` is zero regardless.

    Returns:
        A 2-tuple of (art15_total, art15_unused).  Both amounts are annual.
        ``art15_unused`` is the portion that exceeded available IRPEF
        (incapienza — not refundable).
    """
    art15 = scenario.art15_deductions
    if art15 is None or not art15.has_any_onere:
        return _ZERO, _ZERO
    rules = load_art15_deduction_rules(year)
    total = compute_art15_deductions(art15, rules)
    if not employer_withholds_irpef:
        # Deductions computed but irpef_net is always zero here.
        return total, total
    available = money(max(_ZERO, irpef_gross - work_income_deduction - fam_total))
    unused = money(max(_ZERO, total - available))
    return total, unused


@dataclass(frozen=True)
class FiscalPay:
    """Annual contributions, tax, deductions and net pay."""

    inps_employee_annual: Decimal
    inps_employer_annual: Decimal
    employer_funds_annual: Decimal
    tfr_annual: Decimal
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
    irpef_net: Decimal
    trattamento_integrativo: Decimal
    addizionale_regionale: Decimal
    addizionale_comunale: Decimal
    net_annual: Decimal
    net_monthly: Decimal
    employer_cost_annual: Decimal
    employer_withholds_irpef: bool
    fiscal_simplifications: frozenset[FiscalSimplification]


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

    inps_employee_annual, inps_employer_annual = _inps_contributions(
        rules,
        scenario.employment.contract,
        gross.gross_monthly,
        gross.hourly_divisor,
        gross.contribution_base,
        gross.worker_category,
        weekly_hours=scenario.employee.weekly_hours,
        ivs_ceiling_applies=ivs_ceiling_applies,
    )
    employer_funds_annual = _employer_funds(
        ccnl,
        gross.worker_category,
        gross.contribution_base,
        scenario.employment.calculation_date,
    )
    tfr_annual = _contrib.tfr(gross.tfr_base, rules)

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
    ) = _run_wr_family_deductions(
        scenario=scenario,
        gross_annual=gross.gross_annual,
        irpef_gross=irpef_gross,
        work_income_deduction=work_income_deduction,
        year=year,
        employer_withholds_irpef=employer_withholds_irpef,
    )

    # Sterilizzazione detrazioni (Art. 1 c. 3-4 L. 199/2025): for reddito
    # complessivo > EUR 200 000, reduce total Art. 12 + Art. 13 detrazioni
    # by EUR 440 (clawback of the 35% → 33% bracket benefit).
    # Save pre-sterilizzazione fam_total for the NO_DETRAZIONI_FAMILIARI check.
    fam_total_computed = fam_total
    work_income_deduction, fam_total = _irpef.apply_sterilizzazione_detrazioni(
        work_income_deduction,
        fam_total,
        gross.gross_annual,
        rules.sterilizzazione_detrazioni,
    )
    # Recompute unused after sterilizzazione (incapienza may change).
    if fam_total_computed != fam_total:
        available = money(max(_ZERO, irpef_gross - work_income_deduction))
        fam_unused = money(max(_ZERO, fam_total - available))

    # Art. 15 TUIR deductions (interessi passivi mutuo prima casa, etc.).
    # Sterilizzazione does NOT apply: EUR 440 clawback targets Art. 12 + Art. 13.
    art15_total, art15_unused = _run_wr_art15_deductions(
        scenario=scenario,
        irpef_gross=irpef_gross,
        work_income_deduction=work_income_deduction,
        fam_total=fam_total,
        year=year,
        employer_withholds_irpef=employer_withholds_irpef,
    )

    # When the employer is not a sostituto d'imposta, irpef_net is zeroed;
    # irpef_gross and work_income_deduction remain as informational figures.
    irpef_net = (
        money(max(_ZERO, irpef_gross - work_income_deduction - fam_total - art15_total))
        if employer_withholds_irpef
        else _ZERO
    )

    # Trattamento integrativo (Art. 1 D.L. 3/2020): computed when the tax
    # data file carries the required parameters.
    # relevant_deductions: Art. 12 + Art. 13 + qualifying Art. 15 (statute).
    relevant_deductions = work_income_deduction + fam_total + art15_total
    trattamento_integrativo, fiscal_simplifications = _compute_ti(
        gross.gross_annual,
        irpef_gross,
        work_income_deduction,
        relevant_deductions,
        rules,
    )

    # Remove NO_DETRAZIONI_FAMILIARI when family deductions were computed
    # (use pre-sterilizzazione total: deductions were still computed).
    # Remove NO_DETRAZIONI_ART15 when Art. 15 deductions were computed.
    sfs_mut: set[FiscalSimplification] = set(fiscal_simplifications)
    if fam_total_computed > _ZERO:
        sfs_mut.discard(FiscalSimplification.NO_DETRAZIONI_FAMILIARI)
    if art15_total > _ZERO:
        sfs_mut.discard(FiscalSimplification.NO_DETRAZIONI_ART15)
    fiscal_simplifications = frozenset(sfs_mut)

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
        gross.gross_annual
        - inps_employee_annual
        - irpef_net
        - addizionale_regionale
        - addizionale_comunale
        + trattamento_integrativo
    )
    net_monthly = money(net_annual / gross.additional_months)
    employer_cost_annual = money(
        gross.gross_annual + inps_employer_annual + employer_funds_annual + tfr_annual
    )

    return FiscalPay(
        inps_employee_annual=inps_employee_annual,
        inps_employer_annual=inps_employer_annual,
        employer_funds_annual=employer_funds_annual,
        tfr_annual=tfr_annual,
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
