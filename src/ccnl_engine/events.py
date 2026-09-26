"""Stable public re-exports for variable work event types.

Import from here rather than ``ccnl_engine.payroll.domain.events``
to avoid coupling to the internal package layout.

Example::

    from ccnl_engine.events import OvertimeEvent, BonusEvent
"""

from ccnl_engine.payroll.domain.events import (
    AbsenceEvent as AbsenceEvent,
)
from ccnl_engine.payroll.domain.events import (
    ArrearsEvent as ArrearsEvent,
)
from ccnl_engine.payroll.domain.events import (
    BilateralFundEvent as BilateralFundEvent,
)
from ccnl_engine.payroll.domain.events import (
    BonusEvent as BonusEvent,
)
from ccnl_engine.payroll.domain.events import (
    FringeEvent as FringeEvent,
)
from ccnl_engine.payroll.domain.events import (
    HolidayWorkEvent as HolidayWorkEvent,
)
from ccnl_engine.payroll.domain.events import (
    NightShiftEvent as NightShiftEvent,
)
from ccnl_engine.payroll.domain.events import (
    OvertimeEvent as OvertimeEvent,
)
from ccnl_engine.payroll.domain.events import (
    ShiftWorkEvent as ShiftWorkEvent,
)
from ccnl_engine.payroll.domain.events import (
    SickLeaveEvent as SickLeaveEvent,
)
from ccnl_engine.payroll.domain.events import (
    SicknessCaseEvent as SicknessCaseEvent,
)
from ccnl_engine.payroll.domain.events import (
    TerminationTFREvent as TerminationTFREvent,
)
from ccnl_engine.payroll.domain.events import (
    WelfareEvent as WelfareEvent,
)
from ccnl_engine.payroll.domain.events import (
    WorkEvent as WorkEvent,
)

__all__ = [
    "AbsenceEvent",
    "ArrearsEvent",
    "BilateralFundEvent",
    "BonusEvent",
    "FringeEvent",
    "HolidayWorkEvent",
    "NightShiftEvent",
    "OvertimeEvent",
    "ShiftWorkEvent",
    "SickLeaveEvent",
    "SicknessCaseEvent",
    "TerminationTFREvent",
    "WelfareEvent",
    "WorkEvent",
]
