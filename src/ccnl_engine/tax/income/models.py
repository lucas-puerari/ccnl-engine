"""IRPEF bracket and deduction rule models."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.primitives import Bracket
from ccnl_engine.provenance.source.models_chain import RuleProvenance

#: A single IRPEF marginal tax bracket (Art. 11 TUIR).
IrpefBracket = Bracket


class WorkDeductionMinimum(BaseModel):
    """Minimum of the Art. 13 co. 1 lett. a) TUIR deduction, by contract.

    Lett. a): "L'ammontare della detrazione effettivamente spettante non può
    essere inferiore a 690 euro. Per i rapporti di lavoro a tempo
    determinato, [...] non può essere inferiore a 1.380 euro".  The
    withholding agent proportions it to the days of work (istruzioni CU
    2026, punto 367); the tax return grants it whole (Allegato C to the
    730/2026 instructions, par. 19.9.1).  Defaults encode the 2026 values.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    open_ended: Decimal = Decimal(690)
    """Minimum for an open-ended employment, apprenticeship included (EUR)."""
    fixed_term: Decimal = Decimal(1380)
    """Minimum for a fixed-term employment (EUR)."""
    provenance: RuleProvenance | None = None
    """Source and status of the minimum."""


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
    minimum: WorkDeductionMinimum = Field(default_factory=WorkDeductionMinimum)
    """Minimum of the deduction up to detr_lo, proportioned in the withholding."""
    provenance: RuleProvenance | None = None
    """Source and status of the constants."""


class SterilizzazioneDetrazioniRules(BaseModel):
    """Reduction of art. 16-ter c. 5-bis TUIR for high-income earners.

    Inserted by L. 199/2025 art. 1 c. 4: for a reddito complessivo above
    ``threshold``, the deduction for these oneri is lowered by
    ``reduction`` EUR: the oneri detraibili al 19% under any tax provision
    except the spese sanitarie of art. 15 c. 1 lett. c) TUIR, the
    donations to political parties (D.L. 149/2013 art. 11) and the
    catastrophe insurance premiums (D.L. 34/2020 art. 119 c. 4).  The art.
    12 and art. 13 deductions and the ulteriore detrazione are outside its
    scope.  The payroll computes none of those oneri, so it does not apply
    the reduction; the block records the statutory parameters only.
    """

    model_config = ConfigDict(extra="forbid")

    threshold: Decimal
    reduction: Decimal
    provenance: RuleProvenance | None = None
