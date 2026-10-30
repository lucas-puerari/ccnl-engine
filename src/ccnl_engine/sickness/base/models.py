"""The INPS daily base a sickness regime computes its indemnity on."""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["DailyBaseKind", "RegimeDailyBase"]


class DailyBaseKind(StrEnum):
    """Which pay the INPS daily base of a regime averages.

    Attributes:
        MONTH_BEFORE: The pay of the month immediately before the illness
            (INPS circ. 134368/1981 point 11): the general rule.
        LAST_CONTRIBUTIONS: The pay of the last daily contributions of the
            sector, the 13th and the bonuses included (spettacolo: the last
            40, art. 13 D.Lgs. C.P.S. 708/1947 as amended by art. 66 D.L.
            73/2021).
    """

    MONTH_BEFORE = "month_before"
    LAST_CONTRIBUTIONS = "last_contributions"


class RegimeDailyBase(BaseModel):
    """The daily base of a sickness regime.

    Attributes:
        kind: Which pay the base averages.
        fixed_term_ceiling: Most the daily base of a fixed-term worker can
            reach (spettacolo: 100 EUR from 26 May 2021, art. 66 c. 3 D.L.
            73/2021); ``None`` without one.
        provenance: Where the rule is read from.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: DailyBaseKind = DailyBaseKind.MONTH_BEFORE
    fixed_term_ceiling: Decimal | None = Field(default=None, gt=Decimal(0))
    provenance: RuleProvenance | None = None
