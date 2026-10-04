"""Work events of a payroll period.

Each event goes in :attr:`ccnl_engine.PeriodFacts.events`.
"""

from __future__ import annotations

from ccnl_engine.payroll.domain.events import (
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
from ccnl_engine.payroll.domain.period_payroll import PeriodId

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
