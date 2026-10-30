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

from ccnl_engine.compensation.second_level.rules import (
    CAPABILITY as SECOND_LEVEL_CAPABILITY,
)
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
    LeaveTakenEvent,
    MaternityLeaveEvent,
    NightShiftEvent,
    OvertimeEvent,
    ParentalLeaveEvent,
    PaternityLeaveEvent,
    ShiftWorkEvent,
    SickLeaveEvent,
    SicknessEpisode,
    StandbyEvent,
    TerminationTFREvent,
    TravelAllowanceEvent,
    WelfareEvent,
    WorkInjuryEvent,
)
from ccnl_engine.event.standard.handlers import (
    _standard_event_gross,
)
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.period.decision.override.bundle.services import (
    NOT_IN_BUNDLE,
    _comparable,
    bundle_value,
)
from ccnl_engine.working_time.hourly.policies import HourlyTerms
from ccnl_engine.working_time.overtime.policies import CCNLOvertimeBands
from ccnl_engine.working_time.services import resolve_work_event
from ccnl_engine.working_time.supplement.models import SupplementWork

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.event.facade import WorkEvent

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
#: override replaces what a native capability computes.  A second-level
#: element is an amount of an agreement the bundle does not hold.
CALLER_SUPPLIED_CAPABILITIES = frozenset({
    *(
        rule.capability
        for rule in _RULES.values()
        if rule.reason_code not in {CALLER_DECLARED_AMOUNT, CALLER_OVERRIDE}
    ),
    *SECOND_LEVEL_CAPABILITY.values(),
})

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
    if isinstance(
        event,
        (
            SicknessEpisode,
            StandbyEvent,
            LeaveTakenEvent,
            MaternityLeaveEvent,
            PaternityLeaveEvent,
            ParentalLeaveEvent,
            WorkInjuryEvent,
        ),
    ):  # pragma: no cover
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
