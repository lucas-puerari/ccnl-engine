"""The bundle values a caller-supplied value of a work event is compared with."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.event.facade import (
    AbsenceEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
)
from ccnl_engine.working_time.models import TimeSupplementKind, WorkKind
from ccnl_engine.working_time.supplement.models import SupplementWork
from ccnl_engine.working_time.supplement.policies import work_of

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.agreement.validity.rules import TimeSeries
    from ccnl_engine.event.facade import WorkEvent
    from ccnl_engine.working_time.models import TimeSupplements

__all__ = ["NOT_IN_BUNDLE", "bundle_value"]


_SHIFT_WORKS = frozenset({SupplementWork.DAY_SHIFT, SupplementWork.NIGHT_SHIFT})
#: Bundle value of a rule the bundle does not hold.
NOT_IN_BUNDLE = "not_in_bundle"


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
