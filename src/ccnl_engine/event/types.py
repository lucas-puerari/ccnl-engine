"""WorkEvent union type — the discriminated union of all payroll event types."""

from __future__ import annotations

from ccnl_engine.absence.inputs import (
    AbsenceEvent,
    SickLeaveEvent,
)
from ccnl_engine.absence.insured.extraordinary.inputs import ExtraordinaryLeaveEvent
from ccnl_engine.absence.insured.inputs import (
    MaternityLeaveEvent,
    PaternityLeaveEvent,
    WorkInjuryEvent,
)
from ccnl_engine.absence.insured.parental.inputs import ParentalLeaveEvent
from ccnl_engine.absence.insured.permit.inputs import DisabilityPermitEvent
from ccnl_engine.absence.insured.rest.inputs import NursingRestEvent
from ccnl_engine.leave.inputs import LeaveTakenEvent
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
    ShiftWorkEvent,
)
from ccnl_engine.working_time.standby.inputs import StandbyEvent

__all__ = ["WORK_EVENT_TYPES", "WorkEvent"]

WorkEvent = (
    OvertimeEvent
    | NightShiftEvent
    | HolidayWorkEvent
    | ShiftWorkEvent
    | StandbyEvent
    | AbsenceEvent
    | SickLeaveEvent
    | SicknessEpisode
    | MaternityLeaveEvent
    | PaternityLeaveEvent
    | ParentalLeaveEvent
    | DisabilityPermitEvent
    | NursingRestEvent
    | ExtraordinaryLeaveEvent
    | WorkInjuryEvent
    | BonusEvent
    | FringeEvent
    | TravelAllowanceEvent
    | WelfareEvent
    | ArrearsEvent
    | BilateralFundEvent
    | TerminationTFREvent
    | LeaveTakenEvent
)

#: The classes of :data:`WorkEvent`, for ``isinstance`` checks.
WORK_EVENT_TYPES: tuple[type[WorkEvent], ...] = (
    OvertimeEvent,
    NightShiftEvent,
    HolidayWorkEvent,
    ShiftWorkEvent,
    StandbyEvent,
    AbsenceEvent,
    SickLeaveEvent,
    SicknessEpisode,
    MaternityLeaveEvent,
    PaternityLeaveEvent,
    ParentalLeaveEvent,
    DisabilityPermitEvent,
    NursingRestEvent,
    ExtraordinaryLeaveEvent,
    WorkInjuryEvent,
    BonusEvent,
    FringeEvent,
    TravelAllowanceEvent,
    WelfareEvent,
    ArrearsEvent,
    BilateralFundEvent,
    TerminationTFREvent,
    LeaveTakenEvent,
)
