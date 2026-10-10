"""Handler registry mapping each WorkEvent type to its handler function.

A companion test asserts that the registry covers every member of ``WorkEvent``,
providing the same exhaustiveness guarantee as the ``assert_never`` it replaces.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ccnl_engine.payroll.event.facade import (
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    BonusEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
    SickLeaveEvent,
    SicknessEpisode,
    TerminationTFREvent,
    WelfareEvent,
)
from ccnl_engine.payroll.event.handlers_benefit import (
    _handle_fringe,
    _handle_welfare,
)
from ccnl_engine.payroll.event.handlers_context import (
    EventEffect,
    _EventHandlerCtx,
)
from ccnl_engine.payroll.event.handlers_variable_pay import _handle_arrears
from ccnl_engine.payroll.event.handlers_work_time import _handle_standard
from ccnl_engine.payroll.sickness.handlers import (
    _handle_sickness_episode,
)
from ccnl_engine.payroll.termination.handlers import (
    _handle_bilateral_fund,
    _handle_termination_tfr,
)

__all__ = ["_HANDLER_REGISTRY", "EventEffect", "_EventHandlerCtx", "_EventHandlerFn"]

_EventHandlerFn = Callable[[Any, _EventHandlerCtx], EventEffect]

_HANDLER_REGISTRY: dict[type, _EventHandlerFn] = {
    OvertimeEvent: _handle_standard,
    NightShiftEvent: _handle_standard,
    HolidayWorkEvent: _handle_standard,
    ShiftWorkEvent: _handle_standard,
    AbsenceEvent: _handle_standard,
    SickLeaveEvent: _handle_standard,
    BonusEvent: _handle_standard,
    WelfareEvent: _handle_welfare,
    FringeEvent: _handle_fringe,
    ArrearsEvent: _handle_arrears,
    BilateralFundEvent: _handle_bilateral_fund,
    TerminationTFREvent: _handle_termination_tfr,
    SicknessEpisode: _handle_sickness_episode,
}
