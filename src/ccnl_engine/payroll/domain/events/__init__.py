"""Variable work events for the period-first payroll engine.

Each event type carries the data needed to compute its gross amount and
accounting treatment (INPS, IRPEF, TFR bases).  Events are passed on
:class:`~ccnl_engine.payroll.domain.period_request.PeriodCalculationRequest` and
processed in ``calculate_period``.
"""

from __future__ import annotations

from ccnl_engine.payroll.domain.events._union import WORK_EVENT_TYPES, WorkEvent
from ccnl_engine.payroll.domain.events.absence_sickness import (
    AbsenceEvent,
    SickLeaveEvent,
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
    OvertimeKind,
    ShiftWorkEvent,
)
from ccnl_engine.payroll.domain.sickness import SicknessEpisode

__all__ = [
    "WORK_EVENT_TYPES",
    "AbsenceEvent",
    "ArrearsEvent",
    "BilateralFundEvent",
    "BonusEvent",
    "FringeEvent",
    "HolidayWorkEvent",
    "NightShiftEvent",
    "OvertimeEvent",
    "OvertimeKind",
    "ShiftWorkEvent",
    "SickLeaveEvent",
    "SicknessEpisode",
    "TerminationTFREvent",
    "WelfareEvent",
    "WorkEvent",
]
