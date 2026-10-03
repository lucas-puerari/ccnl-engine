"""Validation of the engine mode a caller names."""

from __future__ import annotations

import pytest

from ccnl_engine.payroll.application.mode_input import parse_mode
from ccnl_engine.payroll.domain.engine_mode import EngineMode
from ccnl_engine.shared.domain.errors import InvalidInputError


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
