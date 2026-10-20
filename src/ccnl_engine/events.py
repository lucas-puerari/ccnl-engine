"""Work events of a payroll period.

Each event goes in :attr:`ccnl_engine.PeriodFacts.events`.
"""

from __future__ import annotations

from ccnl_engine.event.facade import (
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    FringeEvent,
    HolidayWorkEvent,
    HolidayWorkKind,
    LeaveBucket,
    LeaveTakenEvent,
    NightShiftEvent,
    OvertimeEvent,
    OvertimeKind,
    ShiftKind,
    ShiftWorkEvent,
    SickLeaveEvent,
    SicknessEpisode,
    StandbyEvent,
    StandbyKind,
    TerminationTFREvent,
    TravelAllowanceEvent,
    WelfareEvent,
    WorkEvent,
)
from ccnl_engine.run.types import PeriodId

__all__ = [
    "AbsenceEvent",
    "ArrearsEvent",
    "BilateralFundEvent",
    "BonusEvent",
    "FringeEvent",
    "HolidayWorkEvent",
    "HolidayWorkKind",
    "LeaveBucket",
    "LeaveTakenEvent",
    "NightShiftEvent",
    "OvertimeEvent",
    "OvertimeKind",
    "PeriodId",
    "ShiftKind",
    "ShiftWorkEvent",
    "SickLeaveEvent",
    "SicknessEpisode",
    "StandbyEvent",
    "StandbyKind",
    "TerminationTFREvent",
    "TravelAllowanceEvent",
    "WelfareEvent",
    "WorkEvent",
]
