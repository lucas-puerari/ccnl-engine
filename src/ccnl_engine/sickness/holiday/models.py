"""The CCNL pay of a national holiday falling in a sickness."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["SicknessHoliday"]


class SicknessHoliday(BaseModel):
    """The share of the daily pay a holiday falling in a sickness reaches.

    Studi professionali art. 124: for the festività in a sickness the
    employer pays "un'indennità integrativa di quella a carico dell'INPS
    [...] in modo da raggiungere complessivamente il 100%".  On such a
    weekday holiday the integration target of the day rises to ``rate``;
    the INPS share of the day is netted as on any other sick day.

    Attributes:
        rate: Share of the daily pay the holiday reaches, INPS included.
        excluded_days: Codes of the national calendar (``MM-DD``,
            ``easter_monday``) the clause does not cover, e.g. ``10-04``,
            a holiday from 2026 that a text signed before does not list.
        provenance: The clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    rate: Decimal = Field(gt=Decimal(0), le=Decimal(1))
    excluded_days: tuple[str, ...] = ()
    provenance: RuleProvenance
