"""build_fiscal_trace — builds the annual gross-to-net derivation trace."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.engine.payroll.domain.calculation import TraceCategory, TraceStep
from ccnl_engine.engine.payroll.service.trace._meta import _step

_DEFAULT_TFR_DIVISOR = Decimal("13.5")


def build_fiscal_trace(
    *,
    gross_annual: Decimal,
    contribution_base: Decimal,
    inps_employee_annual: Decimal,
    inps_employer_annual: Decimal,
    inps_employee_additional_annual: Decimal = Decimal(0),
    employer_funds_annual: Decimal,
    tfr_annual: Decimal,
    taxable_income: Decimal,
    irpef_gross: Decimal,
    work_income_deduction: Decimal,
    ulteriore_detrazione_lavoro: Decimal,
    family_deduction_annual: Decimal,
    art15_deduction_annual: Decimal,
    sterilizzazione_clawback: Decimal,
    bilateral_employee_annual: Decimal,
    irpef_net: Decimal,
    addizionale_regionale_annual: Decimal,
    addizionale_comunale_annual: Decimal,
    trattamento_integrativo: Decimal,
    somma_esente: Decimal,
    net_annual: Decimal,
    employer_withholds_irpef: bool,
    inps_formula: str | None = None,
    tfr_divisor: Decimal = _DEFAULT_TFR_DIVISOR,
    ivs_ceiling_applies: bool = False,
    ivs_ceiling: Decimal | None = None,
) -> tuple[TraceStep, ...]:
    """Build the ordered fiscal-chain trace from pre-computed annual amounts.

    All step amounts are annual figures.  Steps are emitted unconditionally
    — including zeros — so the skeleton is stable across scenarios and diffs
    cleanly between engine versions.

    Each step is annotated with a normative ``source``, an algebraic
    ``formula``, and a ``rounding`` descriptor when rounding is material.
    Pure derivations leave ``rounding`` unset.

    The only structural fork is ``employer_withholds_irpef``: when ``False``,
    IRPEF and deduction steps are labelled as informational.

    ``inps_formula`` is a shared override used for the domestic flat-hour
    model (``tariffa_oraria_INPS * ore_annuali_contratto``), where the same
    description applies to both employee and employer.  For the standard
    percentage model the employee and employer formulas are built separately:
    the employee formula includes the 1% additional IVS charge when
    ``inps_employee_additional_annual > 0``, while the employer formula uses
    the employer rate with its own IVS split (no addizionale).

    Returns:
        Ordered tuple of :class:`TraceStep` covering the full gross-to-net
        derivation, each annotated with ``formula``, ``source`` and
        ``rounding`` where applicable.
    """
    irpef_suffix = "" if employer_withholds_irpef else " (informativo)"

    # Domestic override: same per-hour formula for both employee and employer.
    # Standard model: build separate formulas when the IVS ceiling applies or
    # when the 1% employee additional is present.
    has_additional = inps_employee_additional_annual > Decimal(0)
    employee_inps_formula: str | None = inps_formula
    employer_inps_formula: str | None = inps_formula
    if inps_formula is None:
        if ivs_ceiling_applies and ivs_ceiling is not None:
            # Employee: IVS-capped base + uncapped non-IVS + optional addizionale.
            additional_term = (
                f" + max(0, min(base_INPS, {ivs_ceiling})"
                f" - soglia_addizionale_1pct) * 0.01"
                if has_additional
                else ""
            )
            employee_inps_formula = (
                f"min(base_INPS, {ivs_ceiling}) * aliquota_IVS_dipendente"
                f" + base_INPS * aliquota_non_IVS_dipendente"
                f"{additional_term}"
            )
            # Employer: same IVS split but with employer rates, no addizionale.
            employer_inps_formula = (
                f"min(base_INPS, {ivs_ceiling}) * aliquota_IVS_datore"
                " + base_INPS * aliquota_non_IVS_datore"
            )
        elif has_additional:
            # No ceiling, but the 1% additional applies.
            employee_inps_formula = (
                "base_imponibile_INPS * aliquota_dipendente"
                " + max(0, base_imponibile_INPS - soglia_addizionale_1pct) * 0.01"
            )
            # Employer: static meta default (None) is sufficient.
    tfr_formula = f"base_TFR ÷ {tfr_divisor}"
    # When employer doesn't withhold IRPEF, the NET formula reflects only
    # the employee INPS deduction; IRPEF and addizionali are informational.
    net_formula: str | None = None
    if not employer_withholds_irpef:
        net_formula = (
            "lordo_annuale - contributi_INPS_dipendente"
            " [esenzione ritenute: IRPEF e addizionali non trattenute]"
        )
    # When deductions exceed IRPEF lorda, irpef_net is floored at zero.
    total_deductions = (
        work_income_deduction
        + ulteriore_detrazione_lavoro
        + family_deduction_annual
        + art15_deduction_annual
        - sterilizzazione_clawback
    )
    irpef_net_formula: str | None = None
    if (
        irpef_gross > Decimal(0)
        and irpef_net == Decimal(0)
        and (total_deductions >= irpef_gross)
    ):
        irpef_net_formula = (
            "max(0, IRPEF_lorda - detrazione_lavoro - ulteriore_detrazione"
            " - detrazioni_familiari - detrazioni_Art15 + clawback_sterilizzazione)"
            " [incapienza: floored at 0]"
        )

    steps: list[TraceStep] = [
        _step(
            TraceCategory.GROSS,
            "Lordo annuale",
            gross_annual,
        ),
        _step(
            TraceCategory.CONTRIBUTION_BASE,
            "Base imponibile INPS",
            contribution_base,
        ),
        _step(
            TraceCategory.INPS_EMPLOYEE,
            "Contributi INPS dipendente",
            inps_employee_annual,
            formula=employee_inps_formula,
        ),
        _step(
            TraceCategory.TAXABLE_INCOME,
            "Imponibile IRPEF",
            taxable_income,
        ),
        _step(
            TraceCategory.IRPEF_GROSS,
            f"IRPEF lorda (Art. 11 TUIR){irpef_suffix}",
            irpef_gross,
        ),
        _step(
            TraceCategory.WORK_DEDUCTION,
            f"Detrazione lavoro dipendente (Art. 13 TUIR){irpef_suffix}",
            work_income_deduction,
        ),
        _step(
            TraceCategory.ULTERIORE_DETRAZIONE,
            f"Ulteriore detrazione lavoro dipendente{irpef_suffix}",
            ulteriore_detrazione_lavoro,
        ),
        _step(
            TraceCategory.FAMILY_DEDUCTION,
            f"Detrazioni carichi familiari (Art. 12 TUIR){irpef_suffix}",
            family_deduction_annual,
        ),
        _step(
            TraceCategory.ART15_DEDUCTION,
            f"Detrazioni Art. 15 TUIR{irpef_suffix}",
            art15_deduction_annual,
        ),
        _step(
            TraceCategory.STERILIZZAZIONE_CLAWBACK,
            f"Sterilizzazione detrazioni{irpef_suffix}",
            sterilizzazione_clawback,
        ),
        _step(
            TraceCategory.IRPEF_NET,
            "IRPEF netta",
            irpef_net,
            formula=irpef_net_formula,
        ),
        _step(
            TraceCategory.ADDIZIONALE_REGIONALE,
            "Addizionale regionale IRPEF",
            addizionale_regionale_annual,
        ),
        _step(
            TraceCategory.ADDIZIONALE_COMUNALE,
            "Addizionale comunale IRPEF",
            addizionale_comunale_annual,
        ),
        _step(
            TraceCategory.TRATTAMENTO_INTEGRATIVO,
            "Trattamento integrativo (Art. 1 D.L. 3/2020)",
            trattamento_integrativo,
        ),
        _step(
            TraceCategory.SOMMA_ESENTE,
            "Somma esente (L. 207/2024)",
            somma_esente,
        ),
        _step(
            TraceCategory.BILATERAL_EMPLOYEE,
            "Fondi bilaterali dipendente",
            bilateral_employee_annual,
        ),
        _step(
            TraceCategory.NET,
            "Netto annuale",
            net_annual,
            formula=net_formula,
        ),
        _step(
            TraceCategory.INPS_EMPLOYER,
            "Contributi INPS datore (informativo)",
            inps_employer_annual,
            formula=employer_inps_formula,
        ),
        _step(
            TraceCategory.EMPLOYER_FUNDS,
            "Fondi contrattuali datore (informativo)",
            employer_funds_annual,
        ),
        _step(
            TraceCategory.TFR,
            "Accantonamento TFR (informativo)",
            tfr_annual,
            formula=tfr_formula,
        ),
    ]

    return tuple(steps)
