"""Surtax models: addizionale regionale e comunale IRPEF."""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.engine.metadata import RulesetIdentity
from ccnl_engine.engine.primitives import Bracket
from ccnl_engine.engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.engine.provenance.domain.extraction import ExtractionTrace
from ccnl_engine.engine.provenance.domain.source import SourceDocument

#: One marginal bracket in a surtax rate schedule.
#: Shares the same structure as :class:`~ccnl_engine.engine.tax.models.IrpefBracket`
#: so the same bracket-sum computation can be reused.
SurtaxBracket = Bracket


def _validate_surtax_brackets(brackets: list[SurtaxBracket], label: str) -> None:
    """Validate that *brackets* form a well-ordered marginal rate schedule.

    Rules (mirrors ``YearRulesRaw._check_irpef_brackets``):
    - The list must not be empty.
    - Only the last bracket may have ``up_to=None``.
    - ``up_to`` values in non-final brackets must be strictly ascending.

    Raises:
        ValueError: If any rule is violated.
    """
    if not brackets:
        msg = f"{label}.brackets must not be empty"
        raise ValueError(msg)
    for i, b in enumerate(brackets[:-1]):
        if b.up_to is None:
            msg = (
                f"{label}: only the last bracket may have up_to=None "
                f"(bracket {i} of {len(brackets)} is not the last)"
            )
            raise ValueError(msg)
        next_b = brackets[i + 1]
        if next_b.up_to is not None and next_b.up_to <= b.up_to:
            msg = (
                f"{label}: brackets must have strictly ascending up_to; "
                f"bracket {i} up_to={b.up_to} >= bracket {i + 1} up_to={next_b.up_to}"
            )
            raise ValueError(msg)
    if brackets[-1].up_to is not None:
        msg = (
            f"{label}: last bracket must be unbounded (up_to=None), "
            f"got up_to={brackets[-1].up_to}"
        )
        raise ValueError(msg)


class RegionaleEntry(BaseModel):
    """Addizionale regionale IRPEF for one region/autonomous province.

    ``brackets`` always has at least one element. Regions with a single
    flat rate have exactly one bracket with ``up_to=None``.
    """

    model_config = ConfigDict(extra="forbid")

    brackets: list[SurtaxBracket]
    """Marginal rate brackets, ascending by ``up_to`` with the last entry unbounded."""

    notes: str = ""
    """Free-form note (e.g. reference to the regional law)."""
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_brackets(self) -> Self:
        _validate_surtax_brackets(self.brackets, "RegionaleEntry")
        return self


class ComunaleEntry(BaseModel):
    """Addizionale comunale IRPEF for one municipality.

    Municipalities with a simple flat rate have exactly one bracket with
    ``up_to=None`` and ``exemption_threshold=0``. Municipalities with income
    brackets or an exemption threshold will have multiple brackets and/or
    ``exemption_threshold > 0``.
    """

    model_config = ConfigDict(extra="forbid")

    nome: str
    """Italian municipality name (e.g. ``"Roma"``)."""

    brackets: list[SurtaxBracket]
    """Marginal rate brackets, ascending by ``up_to`` with the last entry unbounded."""

    exemption_threshold: Decimal = Decimal(0)
    """Exemption threshold: if taxable income ≤ threshold, the surtax is zero."""
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check_brackets(self) -> Self:
        _validate_surtax_brackets(self.brackets, "ComunaleEntry")
        return self


class RegionaleRaw(BaseModel):
    """Raw deserialization model for a regionale surtax data file."""

    model_config = ConfigDict(extra="forbid")
    year: int
    ruleset: RulesetIdentity | None = None
    notes: list[str] = Field(default_factory=list)
    rates: dict[str, RegionaleEntry]
    sources: list[SourceDocument] = Field(default_factory=list)
    extraction: ExtractionTrace | None = None


class ComunaleRaw(BaseModel):
    """Raw deserialization model for a comunale surtax data file."""

    model_config = ConfigDict(extra="forbid")
    year: int
    ruleset: RulesetIdentity | None = None
    notes: list[str] = []
    rates: dict[str, ComunaleEntry]
    sources: list[SourceDocument] = []
    extraction: ExtractionTrace | None = None


class SurtaxRules(BaseModel):
    """Bundled addizionale regionale and comunale rates for one fiscal year.

    Loaded via :func:`~ccnl_engine.knowledge.load_surtax_rules`.

    Attributes:
        year: Fiscal year these rates apply to.
        ruleset: Identity and provenance of this surtax ruleset.
        regionale: Per-region surtax data, keyed by Italian region name
            (e.g. ``"Lombardia"``).
        comunale: Per-municipality surtax data, keyed by *codice catastale*
            (belfiore code, e.g. ``"H501"`` for Rome).
    """

    model_config = ConfigDict(extra="forbid")

    year: int
    ruleset: RulesetIdentity | None = None
    regionale: dict[str, RegionaleEntry]
    comunale: dict[str, ComunaleEntry]
