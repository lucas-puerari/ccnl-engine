"""WorkEvent union type — the discriminated union of all payroll event types."""

from __future__ import annotations

from ccnl_engine.payroll.domain.events.absence_sickness import (
    AbsenceEvent,
    SickLeaveEvent,
    SicknessCaseEvent,
)
from ccnl_engine.payroll.domain.events.termination import TerminationTFREvent
from ccnl_engine.payroll.domain.events.variable_pay import (
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    FringeEvent,
    WelfareEvent,
)
from ccnl_engine.payroll.domain.events.work_time import (
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
)

__all__ = ["WorkEvent"]

WorkEvent = (
    OvertimeEvent
    | NightShiftEvent
    | HolidayWorkEvent
    | ShiftWorkEvent
    | AbsenceEvent
    | SickLeaveEvent
    | SicknessCaseEvent
    | BonusEvent
    | FringeEvent
    | WelfareEvent
    | ArrearsEvent
    | BilateralFundEvent
    | TerminationTFREvent
)
