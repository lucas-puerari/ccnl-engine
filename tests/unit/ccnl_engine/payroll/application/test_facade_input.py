"""Validation of the engine mode and of the arguments of the facade."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.application.facade_input import (
    closing_state,
    competence_plan,
    opening_balances,
    parse_mode,
    period_request,
    tax_year_plan,
)
from ccnl_engine.payroll.domain.engine_mode import EngineMode
from ccnl_engine.payroll.domain.period_state import PeriodState

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.mark.parametrize("mode", list(EngineMode))
def test_member_and_value_name_the_same_mode(mode: EngineMode) -> None:
    """A member or its string value both resolve."""
    assert parse_mode(mode) is mode
    assert parse_mode(mode.value) is mode


def test_unknown_mode_is_invalid_input() -> None:
    """A typo is a typed public error, not a bare ValueError."""
    with pytest.raises(InvalidInputError, match="'production'") as exc_info:
        parse_mode("production")

    assert "'simulation', 'operational'" in str(exc_info.value.remediation)


@pytest.mark.parametrize(
    ("check", "field"),
    [
        (period_request, "request"),
        (competence_plan, "plan"),
        (tax_year_plan, "plan"),
        (opening_balances, "balances"),
        (closing_state, "closing_state"),
    ],
)
@pytest.mark.parametrize("value", [None, {}, "2026-01-regular", object()], ids=repr)
def test_facade_arguments_of_the_wrong_type_are_invalid_input(
    check: Callable[[object], object], field: str, value: object
) -> None:
    """A dict, a string or ``None`` never reaches the calculation."""
    with pytest.raises(InvalidInputError) as raised:
        check(value)

    assert raised.value.field == field
    assert raised.value.feature == "payroll_engine"


def test_a_period_state_passes_as_closing_state() -> None:
    """The closing state is returned unchanged."""
    state = PeriodState.zero()
    assert closing_state(state) is state
