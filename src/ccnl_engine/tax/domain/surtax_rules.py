"""Surtax rules of a tax year: addizionale regionale e comunale IRPEF.

The tables map each jurisdiction, a region or a municipality, to its entry
(:mod:`~ccnl_engine.tax.domain.surtax_tables`); the payroll selects the
entries of the jurisdictions a request names.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.provenance.domain.extraction import ExtractionTrace
from ccnl_engine.provenance.domain.ruleset_identity import RulesetIdentity
from ccnl_engine.provenance.domain.source import SourceDocument
from ccnl_engine.tax.domain.surtax_tables import ComunaleEntry, RegionaleEntry


class RegionaleRaw(BaseModel):
    """Raw deserialization model for a regionale surtax data file."""

    model_config = ConfigDict(extra="forbid")
    year: int
    ruleset: RulesetIdentity | None = None
    notes: list[str] = Field(default_factory=list)
    rates: dict[str, RegionaleEntry]
    provenance: RuleProvenance | None = None
    """Source and status of the whole table; an entry may override it."""
    sources: list[SourceDocument] = Field(default_factory=list)
    extraction: ExtractionTrace | None = None


class ComunaleRaw(BaseModel):
    """Raw deserialization model for a comunale surtax data file."""

    model_config = ConfigDict(extra="forbid")
    year: int
    ruleset: RulesetIdentity | None = None
    notes: list[str] = []
    rates: dict[str, ComunaleEntry]
    provenance: RuleProvenance | None = None
    """Source and status of the whole table; an entry may override it."""
    sources: list[SourceDocument] = []
    extraction: ExtractionTrace | None = None
    rates_are_advance: bool = False
    """True when rates come from a prior year and represent the advance (acconto)."""
    advance_fraction: Decimal = Decimal("0.30")
    """Fraction of the bracket sum used as the current-year advance."""


class SurtaxRules(BaseModel):
    """Bundled addizionale regionale and comunale rates for one fiscal year.

    Loaded via :func:`~ccnl_engine.knowledge.load_surtax_rules`.

    Attributes:
        year: Fiscal year these rates apply to.
        regional_ruleset: Identity of the ``regionale-{year}.json`` data file.
        municipal_ruleset: Identity of the ``comunale-{year}.json`` data file.
        regionale: Per-region surtax data, keyed by Italian region name
            (e.g. ``"Lombardia"``).
        comunale: Per-municipality surtax data, keyed by *codice catastale*
            (e.g. ``"H501"`` for Rome).
        regional_provenance: Source and status of the regional table.
        municipal_provenance: Source and status of the municipal table.
    """

    model_config = ConfigDict(extra="forbid")

    year: int
    regional_ruleset: RulesetIdentity | None = None
    municipal_ruleset: RulesetIdentity | None = None
    regionale: dict[str, RegionaleEntry]
    comunale: dict[str, ComunaleEntry]
    regional_provenance: RuleProvenance | None = None
    municipal_provenance: RuleProvenance | None = None
    comunale_rates_are_advance: bool = False
    """True when comunale rates are from a prior year (advance only)."""
    comunale_advance_fraction: Decimal = Decimal("0.30")
    """Fraction of the bracket sum used as the current-year advance."""
