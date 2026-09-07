"""Surtax models: addizionale regionale e comunale IRPEF."""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from ccnl_engine.engine.primitives import Bracket

#: One marginal bracket in a surtax rate schedule.
#: Shares the same structure as :class:`~ccnl_engine.engine.tax.models.IrpefBracket`
#: so the same bracket-sum computation can be reused.
SurtaxBracket = Bracket


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

    @model_validator(mode="after")
    def _check_brackets(self) -> Self:
        if not self.brackets:
            msg = "RegionaleEntry.brackets must not be empty"
            raise ValueError(msg)
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

    @model_validator(mode="after")
    def _check_brackets(self) -> Self:
        if not self.brackets:
            msg = "ComunaleEntry.brackets must not be empty"
            raise ValueError(msg)
        return self


class RegionaleRaw(BaseModel):
    """Raw deserialization model for a regionale surtax data file."""

    model_config = ConfigDict(extra="forbid")
    year: int
    notes: list[str] = []
    rates: dict[str, RegionaleEntry]


class ComunaleRaw(BaseModel):
    """Raw deserialization model for a comunale surtax data file."""

    model_config = ConfigDict(extra="forbid")
    year: int
    notes: list[str] = []
    rates: dict[str, ComunaleEntry]


class SurtaxRules(BaseModel):
    """Bundled addizionale regionale and comunale rates for one fiscal year.

    Loaded via :func:`~ccnl_engine.knowledge.load_surtax_rules`.

    Attributes:
        year: Fiscal year these rates apply to.
        regionale: Per-region surtax data, keyed by Italian region name
            (e.g. ``"Lombardia"``).
        comunale: Per-municipality surtax data, keyed by *codice catastale*
            (belfiore code, e.g. ``"H501"`` for Rome).
    """

    model_config = ConfigDict(extra="forbid")

    year: int
    regionale: dict[str, RegionaleEntry]
    comunale: dict[str, ComunaleEntry]
