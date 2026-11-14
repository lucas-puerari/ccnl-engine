"""Rate of the part-time supplementary hours past a yearly share.

Federmeccanica (CCNL 5 February 2021, p. 58): 10% until the supplementary
hours exceed 50% of the agreed annual part-time hours, 20% on the excess;
Logistica Confetra art. 56: 18% up to 30% of the agreed annual hours, 40% on
the excess.  The supplementary hours worked earlier in the year and the
agreed annual hours are facts of the timesheet
(``OvertimeEvent.supplementary_hours_before`` and ``agreed_annual_hours``);
without them only the base band applies and the run carries the CCNL
limitation of the clause.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.provenance.source.rule.models import RuleProvenance
from ccnl_engine.working_time.event_kinds import OvertimeKind

if TYPE_CHECKING:
    from ccnl_engine.event.facade import OvertimeEvent

__all__ = [
    "SUPPLEMENTARY_VARIANT",
    "ExcessRate",
    "SupplementaryExcess",
    "excess_rate",
]

#: Variant of the CCNL limitation a run carries when the excess is unknown.
SUPPLEMENTARY_VARIANT = "part_time_supplementary_rate"
_ZERO = Decimal(0)


class SupplementaryExcess(BaseModel):
    """The rate of the supplementary hours past a share of the annual hours.

    Attributes:
        share: Share of the agreed annual part-time hours past which the
            supplementary hours of the year take ``rate``.
        rate: Premium of each supplementary hour past the share, in place
            of the base band, from its decorrenza.
        provenance: Source of the clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    share: Decimal = Field(gt=0, le=1)
    rate: TimeSeries
    provenance: RuleProvenance


@dataclass(frozen=True)
class ExcessRate:
    """The supplementary hours of an event past the yearly share.

    Attributes:
        hours: Hours of the event past the share.
        threshold: Supplementary hours of the year at which the share ends.
        rate: Premium of those hours.
        unknown: Whether a fact the split needs is missing.
    """

    hours: Decimal = _ZERO
    threshold: Decimal = _ZERO
    rate: Decimal = _ZERO
    unknown: bool = False


def excess_rate(
    event: OvertimeEvent, rule: SupplementaryExcess | None
) -> ExcessRate | None:
    """Return the hours of ``event`` past the yearly share of ``rule``.

    Returns:
        ``None`` for an event that is not supplementary work or a CCNL
        without the clause in force on its day; otherwise the excess,
        ``unknown`` when the earlier hours or the annual hours are missing.
    """
    if rule is None or event.kind is not OvertimeKind.SUPPLEMENTARY:
        return None
    period = rule.rate.period_at(event.event_date)
    if period is None or period.is_gap:
        return None
    rate = rule.rate.value_at(event.event_date)
    before, annual = event.supplementary_hours_before, event.agreed_annual_hours
    if before is None or annual is None:
        return ExcessRate(rate=rate, unknown=True)
    threshold = annual * rule.share
    past = max(before + event.hours - max(before, threshold), _ZERO)
    return ExcessRate(hours=past, threshold=threshold, rate=rate)
