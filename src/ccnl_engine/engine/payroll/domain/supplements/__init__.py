"""Layer 3 supplement input models."""

from ccnl_engine.engine.payroll.domain.supplements._inputs import (
    AbsenceDays,
    BonusInput,
    FringeBenefitInput,
    LeaveInput,
    SickInput,
    WelfareInput,
)
from ccnl_engine.engine.payroll.domain.supplements._overtime import (
    OvertimeHours,
    WeeklyOvertimeHours,
)

__all__ = [
    "AbsenceDays",
    "BonusInput",
    "FringeBenefitInput",
    "LeaveInput",
    "OvertimeHours",
    "SickInput",
    "WeeklyOvertimeHours",
    "WelfareInput",
]
