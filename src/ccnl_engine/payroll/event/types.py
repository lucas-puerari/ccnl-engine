"""WorkEvent union type — the discriminated union of all payroll event types."""

from __future__ import annotations

from ccnl_engine.payroll.event.inputs_absence_sickness import (
    AbsenceEvent,
    SickLeaveEvent,
)
from ccnl_engine.payroll.event.inputs_termination import TerminationTFREvent
from ccnl_engine.payroll.event.inputs_variable_pay import (
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    FringeEvent,
    WelfareEvent,
)
from ccnl_engine.payroll.event.inputs_work_time import (
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
)
from ccnl_engine.payroll.sickness.models import SicknessEpisode

__all__ = ["WORK_EVENT_TYPES", "WorkEvent"]

WorkEvent = (
    OvertimeEvent
    | NightShiftEvent
    | HolidayWorkEvent
    | ShiftWorkEvent
    | AbsenceEvent
    | SickLeaveEvent
    | SicknessEpisode
    | BonusEvent
    | FringeEvent
    | WelfareEvent
    | ArrearsEvent
    | BilateralFundEvent
    | TerminationTFREvent
)

#: The classes of :data:`WorkEvent`, for ``isinstance`` checks.
WORK_EVENT_TYPES: tuple[type[WorkEvent], ...] = (
    OvertimeEvent,
    NightShiftEvent,
    HolidayWorkEvent,
    ShiftWorkEvent,
    AbsenceEvent,
    SickLeaveEvent,
    SicknessEpisode,
    BonusEvent,
    FringeEvent,
    WelfareEvent,
    ArrearsEvent,
    BilateralFundEvent,
    TerminationTFREvent,
)
