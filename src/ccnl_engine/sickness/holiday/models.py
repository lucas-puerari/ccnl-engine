"""The CCNL daily target for a national holiday during insured absence."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["SicknessHoliday"]


class SicknessHoliday(BaseModel):
    """The share of daily pay a holiday during sickness or injury reaches.

    Studi professionali art. 124: for the festività in a sickness the
    employer pays "un'indennità integrativa di quella a carico dell'INPS
    [...] in modo da raggiungere complessivamente il 100%".  On such a
    weekday holiday the integration target of the day rises to ``rate``;
    the insurer's share of the day is netted against the target.

    Attributes:
        rate: Share of the daily pay the holiday reaches, insurer included.
        gross_basis: Measure this target against the gross daily pay, without
            grossing up the insurer's share even if ordinary integration is net.
        excluded_days: Codes of the national calendar (``MM-DD``,
            ``easter_monday``) the clause does not cover, e.g. ``10-04``,
            a holiday from 2026 that a text signed before does not list.
        includes_patron_saint: Whether the clause covers the employer's local
            patron saint holiday when its date is stated.
        requires_legacy_section: Apply only to employers covered by a
            carried-forward section of the CCNL.
        provenance: The clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    rate: Decimal = Field(gt=Decimal(0), le=Decimal(1))
    gross_basis: bool = False
    excluded_days: tuple[str, ...] = ()
    includes_patron_saint: bool = False
    requires_legacy_section: bool = False
    provenance: RuleProvenance
