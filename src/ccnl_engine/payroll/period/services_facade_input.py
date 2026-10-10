"""Validation of what a caller passes to the engine facade.

A facade method may be called from an untyped caller (a JSON adapter, a
notebook): what it receives is checked here before any calculation, so a
value of the wrong type raises
:class:`~ccnl_engine.errors.InvalidInputError`, never an
``AttributeError``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.assurance.policies_engine_mode import EngineMode
from ccnl_engine.payroll.period.inputs import PeriodInput
from ccnl_engine.payroll.state.models import PeriodState
from ccnl_engine.payroll.state.services_opening_balance import OpeningBalances
from ccnl_engine.payroll.year.inputs_competence_plan import CompetenceYearPlan
from ccnl_engine.payroll.year.inputs_tax_plan import TaxYearPlan
from ccnl_engine.payroll.year.rules_close import close_tax_year
from ccnl_engine.validation import parse_enum, reject

if TYPE_CHECKING:
    from ccnl_engine.payroll.period.requests import PeriodCalculationRequest

__all__ = [
    "closing_state",
    "competence_plan",
    "next_tax_year",
    "opening_balances",
    "parse_mode",
    "period_request",
    "tax_year_plan",
]

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


def competence_plan(plan: object) -> CompetenceYearPlan:
    """Return ``plan`` checked to be a :class:`CompetenceYearPlan`.

    Returns:
        The plan; anything else is rejected.
    """
    if not isinstance(plan, CompetenceYearPlan):
        reject("plan", "a CompetenceYearPlan", plan, feature=_FEATURE)
    return plan


def opening_balances(balances: object) -> OpeningBalances:
    """Return ``balances`` checked to be :class:`OpeningBalances`.

    Returns:
        The balances; anything else is rejected.
    """
    if not isinstance(balances, OpeningBalances):
        reject("balances", "OpeningBalances", balances, feature=_FEATURE)
    return balances


def tax_year_plan(plan: object) -> TaxYearPlan:
    """Return ``plan`` checked to be a :class:`TaxYearPlan`.

    Returns:
        The plan; anything else is rejected.
    """
    if not isinstance(plan, TaxYearPlan):
        reject("plan", "a TaxYearPlan", plan, feature=_FEATURE)
    return plan


def closing_state(state: object) -> PeriodState:
    """Return ``state`` checked to be a :class:`PeriodState`.

    Returns:
        The state; anything else is rejected.
    """
    if not isinstance(state, PeriodState):
        reject("closing_state", "a PeriodState", state, feature=_FEATURE)
    return state


def next_tax_year(state: object) -> PeriodState:
    """Open the tax year after the one ``state`` closes.

    Returns:
        The opening state of the next tax year; anything but a
        :class:`PeriodState` is rejected.
    """
    return close_tax_year(closing_state(state))
