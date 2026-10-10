"""Work events of a payroll period.

Each event goes in :attr:`ccnl_engine.PeriodFacts.events`.
"""

from __future__ import annotations

from ccnl_engine.payroll.event.facade import (
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    OvertimeKind,
    ShiftWorkEvent,
    SickLeaveEvent,
    SicknessEpisode,
    TerminationTFREvent,
    WelfareEvent,
    WorkEvent,
)
from ccnl_engine.payroll.period.models_payroll import PeriodId

__all__ = [
    "AbsenceEvent",
    "ArrearsEvent",
    "BilateralFundEvent",
    "BonusEvent",
    "FringeEvent",
    "HolidayWorkEvent",
    "NightShiftEvent",
    "OvertimeEvent",
    "OvertimeKind",
    "PeriodId",
    "ShiftWorkEvent",
    "SickLeaveEvent",
    "SicknessEpisode",
    "TerminationTFREvent",
    "WelfareEvent",
    "WorkEvent",
]
