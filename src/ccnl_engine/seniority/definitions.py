"""Promotion repricing and tier definitions for seniority increments."""

from collections.abc import Mapping
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.provenance.source.rule.models import RuleProvenance
from ccnl_engine.types import FrozenDict


class PromotionRepricing(BaseModel):
    """When the increments matured before a promotion take the new amounts.

    Attributes:
        at_next_increment: ``True`` when the CCNL reprices them at the new
            level only when the next increment matures (Turismo art. 158
            c. 6, FIPE art. 182 c. 5); ``False`` when they take the new
            amounts from the promotion (Federmeccanica art. 6: "il cui valore
            sarà ragguagliato agli importi previsti per la categoria di
            arrivo").
        provenance: Source of the clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    at_next_increment: bool
    provenance: RuleProvenance


class SeniorityTier(BaseModel):
    """One cadence tier in a multi-tier seniority ladder (*scatti di anzianità*).

    When a contract uses a single cadence throughout (e.g. 10 biennial scatti)
    use the flat ``cadence_months``/``maximum_count``/``amount_by_level`` fields
    on :class:`SeniorityIncrements` instead.

    When the cadence changes after a certain number of increments (e.g. 6
    biennial, then 1 dodecennial, then 3 quadrennial), populate
    ``SeniorityIncrements.tiers`` and leave ``amount_by_level`` empty.
    Tiers are consumed in order: the engine exhausts tier 1's full capacity
    (``cadence_months * maximum_count`` service months) before advancing to tier 2.

    ``amount_by_level`` is a read-only mapping; it is frozen after construction.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    cadence_months: int = Field(gt=0)
    maximum_count: int = Field(gt=0)
    amount_by_level: Mapping[str, TimeSeries]
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _freeze_dicts(self) -> Self:
        object.__setattr__(  # noqa: PLC2801
            self, "amount_by_level", FrozenDict(self.amount_by_level)
        )
        return self
