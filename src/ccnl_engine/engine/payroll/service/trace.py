"""Fiscal-chain trace builder for payroll computations.

Produces the ordered :class:`~ccnl_engine.engine.payroll.domain.calculation\
.TraceStep` list that records the annual derivation from gross to net.

The fiscal chain is a *derivation* — each step shows what is deducted from or
added to the running total — not a sum like the gross chain.  All amounts are
annual.  Steps with zero amounts are emitted unconditionally so the skeleton
stays stable across runs and diffs cleanly.

Each step carries three structured metadata fields:

- ``formula``: algebraic expression for the derivation (e.g.
  ``"lordo_annuale - contributi_INPS_dipendente"``).
- ``source``: normative or statutory reference (e.g. ``"Art. 11 TUIR"``).
- ``rounding``: rounding policy applied, only set when rounding is material
  (i.e. a rate multiplication or bracket calculation was involved); absent for
  pure additions/subtractions of already-rounded amounts.

The only structural fork is the ``employer_withholds_irpef`` flag: when
``False`` the IRPEF steps are labelled as informational (not actually
withheld).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Literal

from ccnl_engine.engine.payroll.domain.calculation import TraceCategory, TraceStep
from ccnl_engine.engine.payroll.service.rounding import MONETARY

_ANNUAL: Literal["annual"] = "annual"

# Standard rounding descriptor used for all money() applications.
# Derived from MONETARY so trace and implementation stay in sync.
_ROUNDING = str(MONETARY)

# Static per-category metadata: formula, source, rounding.
# Only categories with at least one populated field are listed.
# Populated in _step() via lookup; call sites may override individual fields.
_STEP_META: dict[TraceCategory, dict[str, str]] = {
    TraceCategory.CONTRIBUTION_BASE: {
        "formula": "lordo_annuale - voci_escluse_contributi",
        "source": "Art. 12 D.Lgs. 314/1997",
    },
    TraceCategory.INPS_EMPLOYEE: {
        "formula": "base_imponibile_INPS * aliquota_dipendente",
        "source": "L. 335/1995 Art. 1 c. 18",
        "rounding": _ROUNDING,
    },
    TraceCategory.TAXABLE_INCOME: {
        "formula": "lordo_annuale - contributi_INPS_dipendente",
    },
    TraceCategory.IRPEF_GROSS: {
        "formula": "applicazione_scaglioni_Art_11_TUIR",
        "source": "Art. 11 TUIR",
        "rounding": _ROUNDING,
    },
    TraceCategory.WORK_DEDUCTION: {
        "source": "Art. 13 TUIR",
        "rounding": _ROUNDING,
    },
    TraceCategory.FAMILY_DEDUCTION: {
        "source": "Art. 12 TUIR",
        "rounding": _ROUNDING,
    },
    TraceCategory.ART15_DEDUCTION: {
        "source": "Art. 15 TUIR",
        "rounding": _ROUNDING,
    },
    TraceCategory.IRPEF_NET: {
        "formula": (
            "IRPEF_lorda - detrazione_lavoro - detrazioni_familiari - detrazioni_Art15"
        ),
    },
    TraceCategory.ADDIZIONALE_REGIONALE: {
        "source": "Art. 50 TUIR",
        "rounding": _ROUNDING,
    },
    TraceCategory.ADDIZIONALE_COMUNALE: {
        "source": "Art. 1 D.Lgs. 360/1998",
        "rounding": _ROUNDING,
    },
    TraceCategory.TRATTAMENTO_INTEGRATIVO: {
        "source": "Art. 1 D.L. 3/2020",
        "rounding": _ROUNDING,
    },
    TraceCategory.NET: {
        "formula": (
            "lordo_annuale - contributi_INPS_dipendente - IRPEF_netta"
            " - addizionale_regionale - addizionale_comunale"
            " + trattamento_integrativo"
        ),
    },
    TraceCategory.INPS_EMPLOYER: {
        "formula": "base_imponibile_INPS * aliquota_datore",
        "source": "L. 335/1995 Art. 1 c. 18",
        "rounding": _ROUNDING,
    },
    TraceCategory.EMPLOYER_FUNDS: {
        "rounding": _ROUNDING,
    },
    TraceCategory.TFR: {
        # formula is built dynamically from the actual divisor; only source
        # and rounding are static.
        "source": "Art. 2120 c.c.",
        "rounding": _ROUNDING,
    },
}


def _step(
    category: TraceCategory,
    label: str,
    amount: Decimal,
    detail: str | None = None,
    formula: str | None = None,
    source: str | None = None,
    rounding: str | None = None,
) -> TraceStep:
    """Return an annual :class:`TraceStep`, applying static metadata.

    Looks up per-category defaults from :data:`_STEP_META` and fills in
    ``formula``, ``source``, and ``rounding`` unless an explicit override
    is passed.

    Returns:
        A :class:`TraceStep` with ``period="annual"`` and structured metadata.
    """
    meta = _STEP_META.get(category, {})
    return TraceStep(
        category=category,
        label=label,
        amount=amount,
        detail=detail,
        period=_ANNUAL,
        formula=formula if formula is not None else meta.get("formula"),
        source=source if source is not None else meta.get("source"),
        rounding=rounding if rounding is not None else meta.get("rounding"),
    )


_DEFAULT_TFR_DIVISOR = Decimal("13.5")


def build_fiscal_trace(
    *,
    gross_annual: Decimal,
    contribution_base: Decimal,
    inps_employee_annual: Decimal,
    inps_employer_annual: Decimal,
    employer_funds_annual: Decimal,
    tfr_annual: Decimal,
    taxable_income: Decimal,
    irpef_gross: Decimal,
    work_income_deduction: Decimal,
    family_deduction_annual: Decimal,
    art15_deduction_annual: Decimal,
    irpef_net: Decimal,
    addizionale_regionale_annual: Decimal,
    addizionale_comunale_annual: Decimal,
    trattamento_integrativo: Decimal,
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

    Returns:
        Ordered tuple of :class:`TraceStep` covering the full gross-to-net
        derivation, each annotated with ``formula``, ``source`` and
        ``rounding`` where applicable.
    """
    irpef_suffix = "" if employer_withholds_irpef else " (informativo)"

    # When the IVS ceiling applies, employee INPS is split across two bases.
    if ivs_ceiling_applies and ivs_ceiling is not None and inps_formula is None:
        inps_formula = (
            f"min(base_INPS, {ivs_ceiling}) * aliquota_IVS_dipendente"
            " + base_INPS * aliquota_non_IVS_dipendente"
        )
    tfr_formula = f"base_TFR ÷ {tfr_divisor}"
    # When deductions exceed IRPEF lorda, irpef_net is floored at zero.
    total_deductions = (
        work_income_deduction + family_deduction_annual + art15_deduction_annual
    )
    irpef_net_formula: str | None = None
    if (
        irpef_gross > Decimal(0)
        and irpef_net == Decimal(0)
        and (total_deductions >= irpef_gross)
    ):
        irpef_net_formula = (
            "max(0, IRPEF_lorda - detrazione_lavoro"
            " - detrazioni_familiari - detrazioni_Art15)"
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
            formula=inps_formula,
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
            TraceCategory.NET,
            "Netto annuale",
            net_annual,
        ),
        _step(
            TraceCategory.INPS_EMPLOYER,
            "Contributi INPS datore (informativo)",
            inps_employer_annual,
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
