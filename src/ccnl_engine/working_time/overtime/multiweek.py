"""Extra premium of the multi-week schedule hours past a threshold.

Federmeccanica art. 5 (ipotesi di rinnovo of 22 November 2025, p. 32):
"Ciascuna delle suddette maggiorazioni, a partire dalla 81esima ora, saranno
elevate nella misura onnicomprensiva dell'8%."  The 8% is read as 8 points
on each premium of the orario plurisettimanale (15% to 23%), as the
"maggiorazione aggiuntiva pari all'8%" of the quote esenti of art. 7.

The hours of the schedule worked earlier in its period (at most 12 months
from its activation) are a fact of the timesheet
(``OvertimeEvent.multiweek_hours_before``): without them a multi-week event
of a CCNL with the clause is paid its base band with a missing-fact issue.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.event.standard.handlers import _standard_event_gross
from ccnl_engine.provenance.source.rule.models import RuleProvenance
from ccnl_engine.working_time.event_kinds import OvertimeKind
from ccnl_engine.working_time.overtime.supplementary import missing_fact

if TYPE_CHECKING:
    from ccnl_engine.decision.models import CalculationIssue
    from ccnl_engine.event.facade import OvertimeEvent
    from ccnl_engine.working_time.overtime.models import CCNLOvertimeBands

__all__ = ["MULTIWEEK_UNKNOWN", "MultiweekExcess", "with_multiweek_premium"]

#: Issue of a multi-week event whose earlier hours are not stated.
MULTIWEEK_UNKNOWN = "overtime_multiweek_hours_unknown"
_KINDS = frozenset({
    OvertimeKind.MULTIWEEK,
    OvertimeKind.MULTIWEEK_SATURDAY,
    OvertimeKind.MULTIWEEK_SUDDEN,
    OvertimeKind.MULTIWEEK_SUDDEN_SATURDAY,
})
_ZERO = Decimal(0)


class MultiweekExcess(BaseModel):
    """The extra premium of the multi-week hours past a threshold.

    Attributes:
        rate: Points added to the premium of each hour past the threshold.
        threshold_hours: Hours of the schedule paid at the base premium.
        provenance: Source of the clause.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    rate: TimeSeries
    threshold_hours: int = Field(gt=0)
    provenance: RuleProvenance


def _past(event: OvertimeEvent, before: Decimal, threshold: int) -> Decimal:
    """Return the hours of ``event`` past ``threshold``.

    Returns:
        Zero up to the threshold, then the hours beyond it.
    """
    return max(before + event.hours - max(before, Decimal(threshold)), _ZERO)


def with_multiweek_premium(
    event: OvertimeEvent, paid: OvertimeEvent, bands: CCNLOvertimeBands
) -> tuple[OvertimeEvent, CalculationDecision | None, CalculationIssue | None]:
    """Add the premium past the multi-week threshold to ``paid``.

    A multiplier the caller states is applied as given.

    Returns:
        The event with the premium and its decision; the event unchanged
        with a missing-fact issue when the earlier hours are not stated;
        the event unchanged alone when the clause does not apply.
    """
    rule = bands.multiweek_excess
    if (
        rule is None
        or event.kind not in _KINDS
        or event.multiplier is not None
        or paid.multiplier is None
    ):
        return paid, None, None
    period = rule.rate.period_at(event.event_date)
    if period is None or period.is_gap:
        return paid, None, None
    before = event.multiweek_hours_before
    if before is None:
        return paid, None, missing_fact(MULTIWEEK_UNKNOWN, "multiweek_hours_before")
    rate = rule.rate.value_at(event.event_date)
    past = _past(event, before, rule.threshold_hours)
    paid = replace(paid, multiplier=paid.multiplier + rate * past / event.hours)
    return (
        paid,
        CalculationDecision(
            capability="overtime",
            status=CalculationStatus.FINAL,
            reason_code="overtime_multiweek_excess_premium",
            rule=f"{bands.ruleset}:work_rules.time_supplements.multiweek_excess",
            rule_version=bands.version,
            inputs={
                "hours_before": before,
                "hours": event.hours,
                "threshold_hours": Decimal(rule.threshold_hours),
                "hours_past_threshold": past,
                "rate": rate,
            },
            source=rule.provenance.location,
            amount=_standard_event_gross(paid),
        ),
        None,
    )
