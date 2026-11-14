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
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.absence.policies import absence_decision, resolve_absence
from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.errors import MissingRuleError
from ccnl_engine.event.facade import (
    AbsenceEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
)
from ccnl_engine.event.standard.handlers import _standard_event_gross
from ccnl_engine.working_time.overtime.hourly import HOURLY_RATE_DERIVED, hourly_paid
from ccnl_engine.working_time.overtime.policies import (
    band_decision,
    overtime_issues,
    resolve_overtime_rate,
)
from ccnl_engine.working_time.overtime.quota import EXEMPT_QUOTA_VARIANT, quota_premium
from ccnl_engine.working_time.overtime.supplementary import (
    SUPPLEMENTARY_VARIANT,
    excess_rate,
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
        limitations: Limitations of the CCNL the event's pay carries.
    """

    event: TimeWorkEvent
    decisions: tuple[CalculationDecision, ...] = ()
    issues: tuple[CalculationIssue, ...] = field(default=())
    limitations: tuple[str, ...] = ()


def _overtime(
    event: OvertimeEvent, bands: CCNLOvertimeBands, hourly: HourlyTerms
) -> WorkResolution:
    """Return an overtime event with its multiplier and hourly rate.

    Returns:
        The paid event, the band and hourly rate decisions and the issues.

    Raises:
        MissingRuleError: When banked hours have no percentage bank rule.
    """
    rate = resolve_overtime_rate(event, bands)
    if event.banked and (bands.bank_share is None or rate.hourly_amount is not None):
        msg = "No percentage overtime bank rule applies to these hours"
        raise MissingRuleError(
            msg,
            as_of=event.event_date,
            feature="overtime",
            remediation="Use an agreement with a verified overtime bank rule.",
        )
    paid, decisions = hourly_paid(event, rate, hourly)
    if event.banked:
        assert bands.bank_share is not None
        assert paid.multiplier is not None
        paid = replace(paid, multiplier=(paid.multiplier - 1) * bands.bank_share)
        if decisions:
            decisions[0] = replace(decisions[0], amount=_standard_event_gross(paid))
        decisions.append(
            CalculationDecision(
                capability="overtime",
                status=CalculationStatus.FINAL,
                reason_code="overtime_bank_premium",
                rule=f"{bands.ruleset}:work_rules.time_supplements.overtime_bank_share",
                rule_version=bands.version,
                inputs={"hours": event.hours, "premium_share": bands.bank_share},
                source=None
                if bands.bank_source is None
                else bands.bank_source.location,
                amount=_standard_event_gross(paid),
            )
        )
    else:
        band = band_decision(paid, rate, bands, _standard_event_gross(paid))
        decisions.extend(() if band is None else (band,))
        paid, limitations = _with_yearly_rules(event, paid, bands, decisions)
        return WorkResolution(
            paid, tuple(decisions), overtime_issues(event, rate), limitations
        )
    return WorkResolution(paid, tuple(decisions), overtime_issues(event, rate))


def _with_yearly_rules(
    event: OvertimeEvent,
    paid: OvertimeEvent,
    bands: CCNLOvertimeBands,
    decisions: list[CalculationDecision],
) -> tuple[OvertimeEvent, tuple[str, ...]]:
    """Apply the supplementary share and the exempt quota of the year.

    Returns:
        The paid event and the CCNL limitations of the missing facts; the
        decisions of the rules applied are appended to ``decisions``.
    """
    limitations: list[str] = []
    for step in (_with_supplementary_excess, _with_quota_premium):
        paid, extra, limitation = step(event, paid, bands)
        decisions.extend(() if extra is None else (extra,))
        limitations.extend(() if limitation is None else (limitation,))
    return paid, tuple(limitations)


def _with_supplementary_excess(
    event: OvertimeEvent, paid: OvertimeEvent, bands: CCNLOvertimeBands
) -> tuple[OvertimeEvent, CalculationDecision | None, str | None]:
    """Pay the supplementary hours past the yearly share at their rate.

    The hours within the share keep the base band; a multiplier the caller
    states is applied as given.

    Returns:
        As :func:`_with_quota_premium`.
    """
    excess = excess_rate(event, bands.supplementary_excess)
    if excess is None or event.multiplier is not None or paid.multiplier is None:
        return paid, None, None
    if excess.unknown:
        return paid, None, f"{bands.ccnl_id}/{SUPPLEMENTARY_VARIANT}"
    assert bands.supplementary_excess is not None
    base = paid.multiplier - 1
    multiplier = paid.multiplier + (excess.rate - base) * excess.hours / event.hours
    paid = replace(paid, multiplier=multiplier)
    return (
        paid,
        CalculationDecision(
            capability="overtime",
            status=CalculationStatus.FINAL,
            reason_code="part_time_supplementary_excess",
            rule=f"{bands.ruleset}:work_rules.time_supplements.supplementary_excess",
            rule_version=bands.version,
            inputs={
                "hours": event.hours,
                "threshold_hours": excess.threshold,
                "hours_past_threshold": excess.hours,
                "base_rate": base,
                "excess_rate": excess.rate,
            },
            source=bands.supplementary_excess.provenance.location,
            amount=_standard_event_gross(paid),
        ),
        None,
    )


def _with_quota_premium(
    event: OvertimeEvent, paid: OvertimeEvent, bands: CCNLOvertimeBands
) -> tuple[OvertimeEvent, CalculationDecision | None, str | None]:
    """Add the premium past the yearly exempt quota to ``paid``.

    A multiplier the caller states is applied as given.

    Returns:
        The event with the premium, its decision and no limitation; the
        event unchanged with the limitation of the CCNL when a fact the
        premium needs is missing; the event unchanged alone when the CCNL
        sets no such premium for it.
    """
    premium = quota_premium(event, bands.exempt_quota, bands.headcount)
    if premium is None or event.multiplier is not None or paid.multiplier is None:
        return paid, None, None
    if premium.unknown:
        return paid, None, f"{bands.ccnl_id}/{EXEMPT_QUOTA_VARIANT}"
    before, quota = event.exempt_quota_hours_before, premium.quota
    assert bands.exempt_quota is not None
    assert before is not None
    assert quota is not None
    paid = replace(paid, multiplier=paid.multiplier + premium.multiplier)
    return (
        paid,
        CalculationDecision(
            capability="overtime",
            status=CalculationStatus.FINAL,
            reason_code="overtime_exempt_quota_premium",
            rule=f"{bands.ruleset}:work_rules.time_supplements.overtime_exempt_quota",
            rule_version=bands.version,
            inputs={
                "hours_before": before,
                "hours": event.hours,
                "quota_hours": Decimal(quota),
                "hours_past_quota": premium.hours,
                "rate": premium.rate,
            },
            source=bands.exempt_quota.provenance.location,
            amount=_standard_event_gross(paid),
        ),
        None,
    )


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
