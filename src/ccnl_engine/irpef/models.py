"""IRPEF bracket and deduction rule models."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from ccnl_engine.provenance.source.rule.models import RuleProvenance
from ccnl_engine.types import Bracket

#: A single IRPEF marginal tax bracket (Art. 11 TUIR).
IrpefBracket = Bracket


class WorkDeductionMinimum(BaseModel):
    """Minimum of the Art. 13 co. 1 lett. a) TUIR deduction, by contract.

    Lett. a): "L'ammontare della detrazione effettivamente spettante non può
    essere inferiore a 690 euro. Per i rapporti di lavoro a tempo
    determinato, [...] non può essere inferiore a 1.380 euro".  The
    withholding agent proportions it to the days of work (istruzioni CU
    2026, punto 367); the tax return grants it whole (Allegato C to the
    730/2026 instructions, par. 19.9.1).  The bundle states it for each year.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    open_ended: Decimal
    """Minimum for an open-ended employment, apprenticeship included (EUR)."""
    fixed_term: Decimal
    """Minimum for a fixed-term employment (EUR)."""
    provenance: RuleProvenance | None = None
    """Source and status of the minimum."""


class WorkDeductionRules(BaseModel):
    """Art. 13 co. 1 TUIR work-income deduction constants for a fiscal year.

    These values are statutory and sector-agnostic: one bundle file per
    year states them (``irpef/work_deduction/<year>.json``), every field
    required, so a year cannot fall back on the values of another.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    detr_flat: Decimal
    """Flat deduction for reddito complessivo <= detr_lo (EUR)."""
    detr_a: Decimal
    """Base coefficient for reddito complessivo > detr_lo (EUR)."""
    detr_b_coeff: Decimal
    """Variable coefficient for detr_lo < RC <= detr_mid band (EUR)."""
    detr_b_span: Decimal
    """Width of the middle band: detr_mid - detr_lo (EUR)."""
    detr_c_span: Decimal
    """Width of the upper band: detr_high - detr_mid (EUR)."""
    detr_lo: Decimal
    """Lower income threshold; flat deduction applies at or below (EUR)."""
    detr_mid: Decimal
    """Mid income threshold; separates middle and upper bands (EUR)."""
    detr_high: Decimal
    """Upper income threshold; deduction is zero above this (EUR)."""
    detr_increment: Decimal
    """Art. 13 co. 1 lett. b-bis EUR 65 increment (applies in increment range)."""
    increment_lo: Decimal
    """Lower bound of the EUR 65 increment range (exclusive, EUR)."""
    increment_hi: Decimal
    """Upper bound of the EUR 65 increment range (inclusive, EUR)."""
    seventy_five: Decimal
    """Trattamento integrativo corrective (Art. 1 co. 3 L. 207/2024, EUR)."""
    minimum: WorkDeductionMinimum
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
