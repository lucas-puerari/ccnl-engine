"""Validation of what a caller passes to the engine facade.

A facade method may be called from an untyped caller (a JSON adapter, a
notebook): what it receives is checked here before any calculation, so a
value of the wrong type raises
:class:`~ccnl_engine.shared.domain.errors.InvalidInputError`, never an
``AttributeError``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.engine_mode import EngineMode
from ccnl_engine.payroll.domain.inputs import PeriodInput
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.year_input import YearInput
from ccnl_engine.shared.domain.validation import parse_enum, reject

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest

__all__ = ["closing_state", "parse_mode", "period_request", "year_request"]

_FEATURE = "payroll_engine"


def parse_mode(value: object) -> EngineMode:
    """Return the engine mode named ``value``.

    Args:
        value: An :class:`EngineMode` member or its value, ``"simulation"``
            or ``"operational"``; anything else is rejected.

    Returns:
        The mode.
    """
    return parse_enum(value, EngineMode, "PayrollEngine.mode", feature=_FEATURE)


def period_request(request: object) -> PeriodCalculationRequest:
    """Return the calculation request of a :class:`PeriodInput`.

    Returns:
        The request of the run; anything but a ``PeriodInput`` is rejected.
    """
    if not isinstance(request, PeriodInput):
        reject("request", "a PeriodInput", request, feature=_FEATURE)
    return request.calculation_request()


def year_request(request: object) -> YearInput:
    """Return ``request`` checked to be a :class:`YearInput`.

    Returns:
        The input; anything else is rejected.
    """
    if not isinstance(request, YearInput):
        reject("request", "a YearInput", request, feature=_FEATURE)
    return request


def closing_state(state: object) -> PeriodState:
    """Return ``state`` checked to be a :class:`PeriodState`.

    Returns:
        The state; anything else is rejected.
    """
    if not isinstance(state, PeriodState):
        reject("closing_state", "a PeriodState", state, feature=_FEATURE)
    return state
