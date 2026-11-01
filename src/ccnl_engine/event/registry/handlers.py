"""Handler registry mapping each WorkEvent type to its handler function.

A companion test asserts that the registry covers every member of ``WorkEvent``,
providing the same exhaustiveness guarantee as the ``assert_never`` it replaces.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ccnl_engine.absence.insured.extraordinary.handlers import (
    _handle_extraordinary_leave,
)
from ccnl_engine.absence.insured.handlers import (
    _handle_maternity_leave,
    _handle_work_injury,
)
from ccnl_engine.absence.insured.parental.handlers import _handle_parental_leave
from ccnl_engine.absence.insured.parental.hourly.handlers import (
    _handle_hourly_parental,
)
from ccnl_engine.absence.insured.paternity.handlers import _handle_paternity_leave
from ccnl_engine.absence.insured.permit.handlers import _handle_disability_permit
from ccnl_engine.absence.insured.rest.handlers import _handle_nursing_rest
from ccnl_engine.compensation.board.handlers import _handle_board_lodging
from ccnl_engine.event.facade import (
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    BoardLodgingEvent,
    BonusEvent,
    DisabilityPermitEvent,
    ExtraordinaryLeaveEvent,
    FringeEvent,
    HolidayWorkEvent,
    HourlyParentalLeaveEvent,
    LeaveTakenEvent,
    MaternityLeaveEvent,
    NightShiftEvent,
    NoticeIndemnityEvent,
    NursingRestEvent,
    OvertimeEvent,
    ParentalLeaveEvent,
    PaternityLeaveEvent,
    ShiftWorkEvent,
    SickLeaveEvent,
    SicknessEpisode,
    StandbyEvent,
    TerminationTFREvent,
    TravelAllowanceEvent,
    WelfareEvent,
    WorkInjuryEvent,
)
from ccnl_engine.event.handlers import (
    EventEffect,
    _EventHandlerCtx,
)
from ccnl_engine.leave.handlers import _handle_leave_taken
from ccnl_engine.sickness.handlers import (
    _handle_sickness_episode,
)
from ccnl_engine.termination.handlers import (
    _handle_bilateral_fund,
    _handle_termination_tfr,
)
from ccnl_engine.termination.notice.handlers import _handle_notice_indemnity
from ccnl_engine.variable_pay.arrears.handlers import _handle_arrears
from ccnl_engine.variable_pay.benefit.handlers import (
    _handle_fringe,
    _handle_welfare,
)
from ccnl_engine.variable_pay.travel.handlers import _handle_travel_allowance
from ccnl_engine.working_time.handlers import _handle_standard
from ccnl_engine.working_time.standby.handlers import _handle_standby

__all__ = ["_HANDLER_REGISTRY", "EventEffect", "_EventHandlerCtx", "_EventHandlerFn"]

_EventHandlerFn = Callable[[Any, _EventHandlerCtx], EventEffect]

_HANDLER_REGISTRY: dict[type, _EventHandlerFn] = {
    OvertimeEvent: _handle_standard,
    NightShiftEvent: _handle_standard,
    HolidayWorkEvent: _handle_standard,
    ShiftWorkEvent: _handle_standard,
    StandbyEvent: _handle_standby,
    AbsenceEvent: _handle_standard,
    SickLeaveEvent: _handle_standard,
    BonusEvent: _handle_standard,
    WelfareEvent: _handle_welfare,
    FringeEvent: _handle_fringe,
    TravelAllowanceEvent: _handle_travel_allowance,
    ArrearsEvent: _handle_arrears,
    BilateralFundEvent: _handle_bilateral_fund,
    TerminationTFREvent: _handle_termination_tfr,
    SicknessEpisode: _handle_sickness_episode,
    LeaveTakenEvent: _handle_leave_taken,
    MaternityLeaveEvent: _handle_maternity_leave,
    PaternityLeaveEvent: _handle_paternity_leave,
    ParentalLeaveEvent: _handle_parental_leave,
    DisabilityPermitEvent: _handle_disability_permit,
    NursingRestEvent: _handle_nursing_rest,
    HourlyParentalLeaveEvent: _handle_hourly_parental,
    NoticeIndemnityEvent: _handle_notice_indemnity,
    ExtraordinaryLeaveEvent: _handle_extraordinary_leave,
    WorkInjuryEvent: _handle_work_injury,
    BoardLodgingEvent: _handle_board_lodging,
}
