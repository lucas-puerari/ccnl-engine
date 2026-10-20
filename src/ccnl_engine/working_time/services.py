"""Values of a work-time event the caller leaves to the CCNL.

One resolution serves the event handler, which posts the event, and the
caller-supplied decisions, which report the amount the caller's values
produced: both read the same paid event.

- An overtime event takes its multiplier from the CCNL band
  (:mod:`~ccnl_engine.working_time.overtime.policies`) and, without
  ``hourly_rate``, the hourly base of the CCNL
  (:mod:`~ccnl_engine.working_time.hourly.policies`); a band paid in EUR
  per hour needs no hourly rate.
- A night, holiday or shift event without ``supplement_amount`` takes the
  CCNL band of its work (:mod:`~ccnl_engine.working_time.supplement.policies`).
- An absence without ``hourly_rate`` takes the quota of the CCNL absence
  rule (:mod:`~ccnl_engine.absence.policies`).

Each derived value records an engine decision; a value the caller states is
applied as given and reported by
:func:`~ccnl_engine.period.decision.override.services.caller_supplied_decisions`.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

from ccnl_engine.absence.policies import absence_decision, resolve_absence
from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.event.facade import (
    AbsenceEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
)
from ccnl_engine.event.standard.handlers import _standard_event_gross
from ccnl_engine.working_time.hourly.policies import BASE_PATH
from ccnl_engine.working_time.overtime.policies import (
    band_decision,
    overtime_issues,
    resolve_overtime_rate,
)
from ccnl_engine.working_time.supplement.policies import (
    resolve_supplement,
    supplement_decision,
    supplement_issue,
)

if TYPE_CHECKING:
    from ccnl_engine.decision.models import CalculationIssue
    from ccnl_engine.working_time.hourly.policies import HourlyTerms
    from ccnl_engine.working_time.overtime.policies import CCNLOvertimeBands

__all__ = ["HOURLY_RATE_DERIVED", "WorkResolution", "resolve_work_event"]

#: Reason of the decision of an overtime hourly rate derived from the CCNL.
HOURLY_RATE_DERIVED = "ccnl_hourly_rate_derived"

type TimeWorkEvent = (
    OvertimeEvent | NightShiftEvent | HolidayWorkEvent | ShiftWorkEvent | AbsenceEvent
)


@dataclass(frozen=True)
class WorkResolution:
    """A work-time event with every value it is paid with.

    Attributes:
        event: The event as paid: its rate, multiplier or amount filled in.
        decisions: Engine decisions of the derived values.
        issues: Issues the derived values raise.
    """

    event: TimeWorkEvent
    decisions: tuple[CalculationDecision, ...] = ()
    issues: tuple[CalculationIssue, ...] = field(default=())


def _overtime(
    event: OvertimeEvent, bands: CCNLOvertimeBands, hourly: HourlyTerms
) -> WorkResolution:
    """Return an overtime event with its multiplier and hourly rate.

    Returns:
        The paid event, the band and hourly rate decisions and the issues.
    """
    rate = resolve_overtime_rate(event, bands)
    paid = rate.paid(event)
    decisions: list[CalculationDecision] = []
    if paid.hourly_rate is None:
        base = hourly.base(event.event_date, "OvertimeEvent.hourly_rate", "overtime")
        paid = replace(paid, hourly_rate=base.rate)
        decisions.append(
            CalculationDecision(
                capability="overtime",
                status=CalculationStatus.FINAL,
                reason_code=HOURLY_RATE_DERIVED,
                rule=hourly.rule_of(BASE_PATH),
                rule_version=hourly.version,
                inputs={"hours": event.hours, **base.inputs()},
                source=hourly.base_source,
                amount=_standard_event_gross(paid),
            )
        )
    band = band_decision(paid, rate, bands, _standard_event_gross(paid))
    decisions.extend(() if band is None else (band,))
    return WorkResolution(paid, tuple(decisions), overtime_issues(paid, rate))


def resolve_work_event(
    event: TimeWorkEvent, bands: CCNLOvertimeBands, hourly: HourlyTerms
) -> WorkResolution:
    """Return ``event`` with every value it is paid with.

    Args:
        event: A work-time or absence event of the run.
        bands: Overtime bands of the CCNL for the worker's level.
        hourly: Hourly terms of the run.

    Returns:
        The paid event with the decisions and issues of the derived values;
        an event whose values are all the caller's comes back unchanged.
        A value left to a CCNL that does not set it for the event rejects
        the event with :class:`~ccnl_engine.errors.InvalidInputError`.
    """
    if isinstance(event, OvertimeEvent):
        return _overtime(event, bands, hourly)
    if isinstance(event, AbsenceEvent):
        if event.hourly_rate is not None:
            return WorkResolution(event)
        quota = resolve_absence(event, hourly)
        paid_absence = replace(event, hourly_rate=quota.hourly_rate)
        gross = _standard_event_gross(paid_absence)
        return WorkResolution(paid_absence, (absence_decision(quota, hourly, gross),))
    if event.supplement_amount is not None:
        return WorkResolution(event)
    pay = resolve_supplement(event, hourly)
    issue = supplement_issue(event, pay)
    return WorkResolution(
        replace(event, supplement_amount=pay.amount),
        (supplement_decision(event, pay, hourly),),
        () if issue is None else (issue,),
    )
