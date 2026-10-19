"""Decisions of the values a run takes from the caller in place of a rule.

Some events carry a rate or an amount the engine applies as given: the
overtime hourly rate and an explicit multiplier, the hourly rate of an
absence, a flat supplement, a separate tax rate, a sick pay amount or a
TFR payout or rate that overrides the engine.  Each such event records one
decision with origin
:attr:`~ccnl_engine.decision.models.DecisionOrigin.CALLER_SUPPLIED`: the
fields it took from the caller, their values and, where the bundle has a
comparable value (a CCNL band, the hourly divisor), that value for
comparison.  The amounts do not change.  A value the caller leaves out
and the engine derives from the CCNL (an overtime multiplier or hourly
rate, a supplement, an absence quota) is an engine decision of the handler,
not listed here: an event lists only the fields the caller stated.  A
fringe benefit records its own decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationStatus,
    DecisionOrigin,
)
from ccnl_engine.event.facade import (
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
    SickLeaveEvent,
    SicknessEpisode,
    StandbyEvent,
    TerminationTFREvent,
    TravelAllowanceEvent,
    WelfareEvent,
)
from ccnl_engine.event.standard.handlers import (
    _standard_event_gross,
)
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.working_time.hourly.policies import HourlyTerms
from ccnl_engine.working_time.models import (
    SupplementWork,
    TimeSupplementKind,
    WorkKind,
)
from ccnl_engine.working_time.overtime.policies import CCNLOvertimeBands
from ccnl_engine.working_time.services import resolve_work_event
from ccnl_engine.working_time.supplement.policies import work_of

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.agreement.validity.rules import TimeSeries
    from ccnl_engine.event.facade import WorkEvent
    from ccnl_engine.working_time.models import TimeSupplements

__all__ = [
    "CALLER_DECLARED_AMOUNT",
    "CALLER_OVERRIDE",
    "CALLER_SUPPLIED_AMOUNT",
    "CALLER_SUPPLIED_CAPABILITIES",
    "CALLER_SUPPLIED_RATE",
    "NOT_IN_BUNDLE",
    "bundle_value",
    "caller_supplied_decisions",
]

#: The caller gave a rate or a multiplier a rule would otherwise set.
CALLER_SUPPLIED_RATE = "caller_supplied_rate"
#: The caller gave an amount a rule would otherwise compute.
CALLER_SUPPLIED_AMOUNT = "caller_supplied_amount"
#: The caller declared the amount paid; no rule sets it.
CALLER_DECLARED_AMOUNT = "caller_declared_amount"
#: The caller overrode an amount a native capability computes.
CALLER_OVERRIDE = "caller_override"
NOT_IN_BUNDLE = "not_in_bundle"


@dataclass(frozen=True)
class _CallerRule:
    """Capability, reason and caller fields of one event type."""

    capability: str
    reason_code: str
    fields: tuple[str, ...]


_RULES: dict[type, _CallerRule] = {
    OvertimeEvent: _CallerRule(
        "overtime", CALLER_SUPPLIED_RATE, ("hourly_rate", "multiplier")
    ),
    NightShiftEvent: _CallerRule(
        "night_work", CALLER_SUPPLIED_AMOUNT, ("supplement_amount",)
    ),
    HolidayWorkEvent: _CallerRule(
        "holiday_work", CALLER_SUPPLIED_AMOUNT, ("supplement_amount",)
    ),
    ShiftWorkEvent: _CallerRule(
        "shift_work", CALLER_SUPPLIED_AMOUNT, ("supplement_amount",)
    ),
    AbsenceEvent: _CallerRule("absence", CALLER_SUPPLIED_RATE, ("hourly_rate",)),
    SickLeaveEvent: _CallerRule("sickness", CALLER_OVERRIDE, ("amount",)),
    BonusEvent: _CallerRule("bonus", CALLER_DECLARED_AMOUNT, ("amount",)),
    WelfareEvent: _CallerRule("welfare", CALLER_DECLARED_AMOUNT, ("amount",)),
    TravelAllowanceEvent: _CallerRule(
        "travel_allowance", CALLER_SUPPLIED_AMOUNT, ("daily_amount",)
    ),
    ArrearsEvent: _CallerRule(
        "contract_renewal_arrears", CALLER_SUPPLIED_RATE, ("separate_tax_rate",)
    ),
    BilateralFundEvent: _CallerRule(
        "bilateral_funds",
        CALLER_SUPPLIED_AMOUNT,
        ("employee_amount", "employer_amount"),
    ),
    TerminationTFREvent: _CallerRule(
        "termination_tfr", CALLER_OVERRIDE, ("amount", "separate_tax_rate")
    ),
}

#: Capabilities whose amounts can rest on a caller value that stands in for
#: a rule; a declared bonus or welfare amount is a fact, not a rule, and an
#: override replaces what a native capability computes.
CALLER_SUPPLIED_CAPABILITIES = frozenset(
    rule.capability
    for rule in _RULES.values()
    if rule.reason_code not in {CALLER_DECLARED_AMOUNT, CALLER_OVERRIDE}
)

_CASH_EVENTS = (
    OvertimeEvent,
    NightShiftEvent,
    HolidayWorkEvent,
    ShiftWorkEvent,
    AbsenceEvent,
    SickLeaveEvent,
    BonusEvent,
)

_WORK_EVENTS = (
    OvertimeEvent,
    NightShiftEvent,
    HolidayWorkEvent,
    ShiftWorkEvent,
    AbsenceEvent,
)
_SHIFT_WORKS = frozenset({SupplementWork.DAY_SHIFT, SupplementWork.NIGHT_SHIFT})


def bundle_value(series: TimeSeries, day: date) -> Decimal | str:
    """Return the value of ``series`` in force on ``day``.

    Returns:
        The value, or ``"not_in_bundle"`` before the series or in a gap.
    """
    period = series.period_at(day)
    if period is None or period.value is None:
        return NOT_IN_BUNDLE
    return period.value


def _band_inputs(
    ccnl: CCNL, event: OvertimeEvent, kind: WorkKind
) -> dict[str, Decimal | str]:
    """Return the CCNL overtime bands of an overtime event's work kind.

    A ``percentage`` band holds the supplement (``0.25`` for 25%), not the
    multiplier.

    Returns:
        One ``bundle_band[<code>]`` input per matching band, or a single
        ``bundle_band`` input ``"not_in_bundle"`` when the CCNL has none.
    """
    supplements = _supplements(ccnl)
    bands = () if supplements is None else supplements.overtime_bands
    inputs: dict[str, Decimal | str] = {
        f"bundle_band[{band.code}]": bundle_value(band.rate, event.event_date)
        for band in bands
        if kind in band.applies_to_kinds
    }
    if not inputs and kind is WorkKind.REST_DAY:
        # Rest-day overtime falls back on the holiday bands, as it is paid.
        return _band_inputs(ccnl, event, WorkKind.HOLIDAY)
    return inputs or {"bundle_band": NOT_IN_BUNDLE}


def _supplements(ccnl: CCNL) -> TimeSupplements | None:
    rules = ccnl.work_rules
    return None if rules is None else rules.time_supplements


def _supplement_inputs(
    ccnl: CCNL, event: NightShiftEvent | HolidayWorkEvent | ShiftWorkEvent
) -> dict[str, Decimal | str]:
    """Return the CCNL bands a supplement event stands in for.

    A night or holiday event compares with the supplement bands of its work,
    a shift event with those of its shift (of every shift without a kind)
    and with the per-shift allowances among the overtime bands.

    Returns:
        One ``bundle_band[<code>]`` input per matching band, or a single
        ``bundle_band`` input ``"not_in_bundle"`` when the CCNL has none.
    """
    supplements = _supplements(ccnl)
    day = event.event_date
    work = work_of(event)
    works = _SHIFT_WORKS if work is None else frozenset({work})
    inputs: dict[str, Decimal | str] = {
        f"bundle_band[{band.code}]": bundle_value(band.rate, day)
        for band in (() if supplements is None else supplements.supplement_bands)
        if band.work in works
    }
    if isinstance(event, ShiftWorkEvent):
        inputs.update(
            (f"bundle_band[{band.code}]", bundle_value(band.rate, day))
            for band in (() if supplements is None else supplements.overtime_bands)
            if band.kind is TimeSupplementKind.INDENNITA_PER_SHIFT
        )
    return inputs or {"bundle_band": NOT_IN_BUNDLE}


def _comparable(ccnl: CCNL, event: WorkEvent) -> dict[str, Decimal | str]:
    """Return the bundle values comparable with the caller's, when any.

    Returns:
        The bands of a supplement and the hourly divisor of an hourly rate;
        empty when the bundle has no comparable rule.
    """
    divisor = bundle_value(ccnl.parameters.hourly_divisor, event.event_date)
    if isinstance(event, OvertimeEvent):
        caller: dict[str, Decimal | str] = (
            {}
            if event.multiplier is None
            else {"caller_supplement": event.multiplier - 1}
        )
        return {
            **_band_inputs(ccnl, event, WorkKind(event.kind.value)),
            **caller,
            "bundle_hourly_divisor": divisor,
        }
    if isinstance(event, (NightShiftEvent, HolidayWorkEvent, ShiftWorkEvent)):
        return _supplement_inputs(ccnl, event)
    if isinstance(event, AbsenceEvent):
        return {"bundle_hourly_divisor": divisor}
    return {}


def _amount(event: WorkEvent) -> Decimal | None:
    """Return the amount the event posts from the caller's values.

    Returns:
        The gross of a standard event (negative for an absence), the total
        of a bilateral fund event, or the declared amount; ``None`` for a
        TFR settlement whose payout the engine computes.
    """
    if isinstance(event, BilateralFundEvent):
        return event.employee_amount + event.employer_amount
    if isinstance(event, TravelAllowanceEvent):
        return money((event.daily_amount or Decimal(0)) * event.days)
    if isinstance(event, _CASH_EVENTS):
        return _standard_event_gross(event)
    if isinstance(event, (SicknessEpisode, StandbyEvent)):  # pragma: no cover
        return Decimal(0)  # no caller rule: never asked
    return event.amount


def _value(value: object) -> Decimal | str:
    return value if isinstance(value, Decimal) else str(value)


def _decision(
    index: int,
    event: WorkEvent,
    rule: _CallerRule,
    ccnl: CCNL,
    level_code: str | None,
    hourly: HourlyTerms,
) -> CalculationDecision:
    fields = tuple(name for name in rule.fields if getattr(event, name) is not None)
    paid = event
    if isinstance(event, _WORK_EVENTS):
        bands = CCNLOvertimeBands.of(ccnl, event.event_date.year, level_code)
        paid = resolve_work_event(event, bands, hourly).event
    return CalculationDecision(
        capability=rule.capability,
        status=CalculationStatus.FINAL,
        reason_code=rule.reason_code,
        rule=f"request:events[{index}].{type(event).__name__}",
        rule_version="request",
        inputs={
            "fields": ",".join(fields),
            **{name: _value(getattr(event, name)) for name in fields},
            **_comparable(ccnl, event),
        },
        amount=_amount(paid),
        origin=DecisionOrigin.CALLER_SUPPLIED,
    )


def caller_supplied_decisions(
    events: tuple[WorkEvent, ...],
    ccnl: CCNL,
    level_code: str | None = None,
    hourly: HourlyTerms | None = None,
) -> tuple[CalculationDecision, ...]:
    """Return one caller-supplied decision per event that carries one.

    Args:
        events: Events of the run, in request order.
        ccnl: The applicable CCNL, source of the comparable bundle values.
        level_code: Level of the worker, selecting the bands of a level.
        hourly: Hourly terms of the run, which derive the values of an
            event the caller states in part (a multiplier without a rate).

    Returns:
        The decisions in event order; a fringe benefit has none.
    """
    terms = hourly or HourlyTerms()
    return tuple(
        _decision(index, event, rule, ccnl, level_code, terms)
        for index, event in enumerate(events)
        if (rule := _RULES.get(type(event))) is not None and _supplied(event, rule)
    )


def _supplied(event: WorkEvent, rule: _CallerRule) -> bool:
    """Return whether the event carries a caller's value of its rule.

    Returns:
        ``True`` when one field of the rule is stated: ``False`` for a
        travel allowance paid at the CCNL amount, or a work-time event
        whose values all come from the CCNL.
    """
    return any(getattr(event, name) is not None for name in rule.fields)
