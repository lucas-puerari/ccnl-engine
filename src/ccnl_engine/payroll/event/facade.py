"""Variable work events for the period-first payroll engine.

Each event type carries the data needed to compute its gross amount and
accounting treatment (INPS, IRPEF, TFR bases).  Events are passed on
:class:`~ccnl_engine.payroll.period.requests.PeriodCalculationRequest` and
processed in ``calculate_period``.
"""

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
    OvertimeKind,
    ShiftWorkEvent,
)
from ccnl_engine.payroll.event.types import WORK_EVENT_TYPES, WorkEvent
from ccnl_engine.payroll.sickness.models import SicknessEpisode

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
