"""IRPEF bracket and deduction rule models."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from ccnl_engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.shared.domain.primitives import Bracket

#: A single IRPEF marginal tax bracket (Art. 11 TUIR).
IrpefBracket = Bracket


class DeductionBreakpoint(BaseModel):
    """A single breakpoint in a piecewise-linear deduction schedule.

    Reused for Art. 12 TUIR family deductions (spouse, children) whose
    schedules are tabulated as breakpoint lists in the tax data files.

    Note: Art. 13 TUIR work-income deduction uses statutory piecewise
    formulas in ``irpef.py`` and no longer stores breakpoints here.
    """

    model_config = ConfigDict(extra="forbid")

    income_up_to: Decimal | None
    deduction: Decimal
    provenance: RuleProvenance | None = None


class WorkDeductionRules(BaseModel):
    """Art. 13 co. 1 TUIR work-income deduction constants for a fiscal year.

    These values are statutory and sector-agnostic. They are versioned here
    so a future year can update the schedule without touching irpef.py.
    Defaults encode the 2026 values (circolare AdE 4/E/2025, p. 6).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    detr_flat: Decimal = Decimal(1955)
    """Flat deduction for reddito complessivo <= detr_lo (EUR)."""
    detr_a: Decimal = Decimal(1910)
    """Base coefficient for reddito complessivo > detr_lo (EUR)."""
    detr_b_coeff: Decimal = Decimal(1190)
    """Variable coefficient for detr_lo < RC <= detr_mid band (EUR)."""
    detr_b_span: Decimal = Decimal(13000)
    """Width of the middle band: detr_mid - detr_lo (EUR)."""
    detr_c_span: Decimal = Decimal(22000)
    """Width of the upper band: detr_high - detr_mid (EUR)."""
    detr_lo: Decimal = Decimal(15000)
    """Lower income threshold; flat deduction applies at or below (EUR)."""
    detr_mid: Decimal = Decimal(28000)
    """Mid income threshold; separates middle and upper bands (EUR)."""
    detr_high: Decimal = Decimal(50000)
    """Upper income threshold; deduction is zero above this (EUR)."""
    detr_increment: Decimal = Decimal(65)
    """Art. 13 co. 1 lett. b-bis EUR 65 increment (applies in increment range)."""
    increment_lo: Decimal = Decimal(25000)
    """Lower bound of the EUR 65 increment range (exclusive, EUR)."""
    increment_hi: Decimal = Decimal(35000)
    """Upper bound of the EUR 65 increment range (inclusive, EUR)."""
    seventy_five: Decimal = Decimal(75)
    """Trattamento integrativo corrective (Art. 1 co. 3 L. 207/2024, EUR)."""


class SterilizzazioneDetrazioniRules(BaseModel):
    """Sterilizzazione detrazioni for high-income earners.

    Per Art. 1 c. 3-4 L. 199/2025 (Legge di Bilancio 2026): for
    reddito complessivo exceeding ``threshold``, the Art. 15 TUIR
    oneri detraibili al 19 % (lett. a, b, d, e; not lett. c spese
    sanitarie) is reduced by ``reduction`` EUR. The reduction is the
    exact clawback of the tax benefit from the 35% to 33% IRPEF
    bracket change on the EUR 28 000-50 000 slice:
    2% x EUR 22 000 = EUR 440.
    """

    model_config = ConfigDict(extra="forbid")

    threshold: Decimal
    reduction: Decimal
    provenance: RuleProvenance | None = None
