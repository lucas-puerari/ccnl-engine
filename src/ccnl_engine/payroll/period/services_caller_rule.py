"""Decisions of the values a run takes from the caller in place of a rule.

Some events carry a rate or an amount the engine applies as given: the
overtime hourly rate and an explicit multiplier, the hourly rate of an
absence, a flat supplement, a separate tax rate, a sick pay amount that
overrides the engine.  Each such event records one decision with origin
:attr:`~ccnl_engine.payroll.assurance.models_decision.DecisionOrigin.CALLER_SUPPLIED`:
the fields it took from the caller, their values and, where the bundle has
a comparable value (a CCNL band, the hourly divisor), that value for
comparison.  The amounts do not change.  An
overtime multiplier derived from the CCNL band is an engine decision of the
handler, not listed here.  A fringe benefit records its own decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.working_time.models import TimeSupplementKind, WorkKind
from ccnl_engine.payroll.assurance.models_decision import (
    CalculationDecision,
    CalculationStatus,
    DecisionOrigin,
)
from ccnl_engine.payroll.event.facade import (
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
    TerminationTFREvent,
    WelfareEvent,
)
from ccnl_engine.payroll.event.handlers_standard import (
    _standard_event_gross,
)
from ccnl_engine.payroll.event.policies_overtime_rate import (
    CCNLOvertimeBands,
    resolve_overtime_rate,
)

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.contract.identity.facade import CCNL
    from ccnl_engine.contract.identity.rules_validity import TimeSeries
    from ccnl_engine.contract.working_time.models import OvertimeBand
    from ccnl_engine.payroll.event.facade import WorkEvent

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
    ArrearsEvent: _CallerRule(
        "contract_renewal_arrears", CALLER_SUPPLIED_RATE, ("separate_tax_rate",)
    ),
    BilateralFundEvent: _CallerRule(
        "bilateral_funds",
        CALLER_SUPPLIED_AMOUNT,
        ("employee_amount", "employer_amount"),
    ),
    TerminationTFREvent: _CallerRule(
        "termination_tfr", CALLER_SUPPLIED_RATE, ("separate_tax_rate",)
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

#: Work kind whose CCNL bands a supplement event stands in for; an
#: overtime event declares its own.
_BAND_KINDS: dict[type, WorkKind] = {
    NightShiftEvent: WorkKind.NIGHT,
    HolidayWorkEvent: WorkKind.HOLIDAY,
}


def bundle_value(series: TimeSeries, day: date) -> Decimal | str:
    """Return the value of ``series`` in force on ``day``.

    Returns:
        The value, or ``"not_in_bundle"`` before the series or in a gap.
    """
    period = series.period_at(day)
    if period is None or period.value is None:
        return NOT_IN_BUNDLE
    return period.value


def _stands_for(band: OvertimeBand, kind: WorkKind | None) -> bool:
    """Return whether ``band`` sets what an event of work ``kind`` pays.

    Returns:
        For a shift event (no work kind), whether the band is a per-shift
        allowance; otherwise whether it applies to ``kind``.
    """
    if kind is None:
        return band.kind is TimeSupplementKind.INDENNITA_PER_SHIFT
    return kind in band.applies_to_kinds


def _band_inputs(
    ccnl: CCNL, event: WorkEvent, kind: WorkKind | None
) -> dict[str, Decimal | str]:
    """Return the CCNL time-supplement bands a supplement event stands in for.

    Overtime, night and holiday events compare with the bands of their work
    kind, a shift event with the per-shift allowances.  A ``percentage``
    band holds the supplement (``0.25`` for 25%), not the multiplier.

    Returns:
        One ``bundle_band[<code>]`` input per matching band, or a single
        ``bundle_band`` input ``"not_in_bundle"`` when the CCNL has none.
    """
    rules = ccnl.work_rules
    supplements = None if rules is None else rules.time_supplements
    bands = () if supplements is None else supplements.overtime_bands
    inputs: dict[str, Decimal | str] = {
        f"bundle_band[{band.code}]": bundle_value(band.rate, event.event_date)
        for band in bands
        if _stands_for(band, kind)
    }
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
        return _band_inputs(ccnl, event, _BAND_KINDS.get(type(event)))
    if isinstance(event, AbsenceEvent):
        return {"bundle_hourly_divisor": divisor}
    return {}


def _amount(event: WorkEvent) -> Decimal:
    """Return the amount the event posts from the caller's values.

    Returns:
        The gross of a standard event (negative for an absence), the total
        of a bilateral fund event, or the declared amount.
    """
    if isinstance(event, BilateralFundEvent):
        return event.employee_amount + event.employer_amount
    if isinstance(event, _CASH_EVENTS):
        return _standard_event_gross(event)
    if isinstance(event, SicknessEpisode):  # pragma: no cover - no caller rule
        return Decimal(0)
    return event.amount


def _value(value: object) -> Decimal | str:
    return value if isinstance(value, Decimal) else str(value)


def _decision(
    index: int, event: WorkEvent, rule: _CallerRule, ccnl: CCNL
) -> CalculationDecision:
    fields, paid = rule.fields, event
    if isinstance(event, OvertimeEvent):
        bands = CCNLOvertimeBands.of(ccnl, event.event_date.year)
        paid = resolve_overtime_rate(event, bands).paid(event)
        fields = fields if event.multiplier is not None else ("hourly_rate",)
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
    events: tuple[WorkEvent, ...], ccnl: CCNL
) -> tuple[CalculationDecision, ...]:
    """Return one caller-supplied decision per event that carries one.

    Args:
        events: Events of the run, in request order.
        ccnl: The applicable CCNL, source of the comparable bundle values.

    Returns:
        The decisions in event order; a fringe benefit has none.
    """
    return tuple(
        _decision(index, event, rule, ccnl)
        for index, event in enumerate(events)
        if (rule := _RULES.get(type(event))) is not None
    )
