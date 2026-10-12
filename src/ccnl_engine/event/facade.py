"""Variable work events for the period-first payroll engine.

Each event type carries the data needed to compute its gross amount and
accounting treatment (INPS, IRPEF, TFR bases).  Events are passed on
:class:`~ccnl_engine.period.requests.PeriodCalculationRequest` and
processed in ``calculate_period``.
"""

from __future__ import annotations

from ccnl_engine.absence.inputs import (
    AbsenceEvent,
    SickLeaveEvent,
)
from ccnl_engine.event.types import WORK_EVENT_TYPES, WorkEvent
from ccnl_engine.sickness.models import SicknessEpisode
from ccnl_engine.termination.inputs import TerminationTFREvent
from ccnl_engine.variable_pay.inputs import (
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    FringeEvent,
    TravelAllowanceEvent,
    WelfareEvent,
)
from ccnl_engine.working_time.inputs import (
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    OvertimeKind,
    ShiftWorkEvent,
)

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
    "TravelAllowanceEvent",
    "WelfareEvent",
    "WorkEvent",
]
