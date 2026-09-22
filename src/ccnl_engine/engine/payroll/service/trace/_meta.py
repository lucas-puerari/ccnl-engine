"""Static step metadata and the _step() helper."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from decimal import Decimal

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
    TraceCategory.ULTERIORE_DETRAZIONE: {
        "source": "Art. 1 c. 6 L. 207/2024",
    },
    TraceCategory.STERILIZZAZIONE_CLAWBACK: {
        "source": "Art. 1 c. 3-4 L. 199/2025",
    },
    TraceCategory.BILATERAL_EMPLOYEE: {
        "rounding": _ROUNDING,
    },
    TraceCategory.IRPEF_NET: {
        "formula": (
            "IRPEF_lorda - detrazione_lavoro - ulteriore_detrazione"
            " - detrazioni_familiari - detrazioni_Art15 + clawback_sterilizzazione"
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
    TraceCategory.SOMMA_ESENTE: {
        "source": "L. 207/2024",
        "rounding": _ROUNDING,
    },
    TraceCategory.NET: {
        "formula": (
            "lordo_annuale - contributi_INPS_dipendente - IRPEF_netta"
            " - addizionale_regionale - addizionale_comunale"
            " + trattamento_integrativo + somma_esente"
            " - fondi_bilaterali_dipendente"
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
