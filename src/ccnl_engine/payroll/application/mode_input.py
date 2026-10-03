"""Validation of the engine mode a caller names."""

from __future__ import annotations

from ccnl_engine.payroll.domain.engine_mode import EngineMode
from ccnl_engine.shared.domain.errors import InvalidInputError

__all__ = ["parse_mode"]


def parse_mode(value: str) -> EngineMode:
    """Return the engine mode named ``value``.

    Args:
        value: An :class:`EngineMode` member or its value, ``"simulation"``
            or ``"operational"``.

    Returns:
        The mode.

    Raises:
        InvalidInputError: When ``value`` names no mode.
    """
    try:
        return EngineMode(value)
    except ValueError:
        allowed = ", ".join(repr(m.value) for m in EngineMode)
        msg = f"unknown engine mode {value!r}; expected one of {allowed}"
        raise InvalidInputError(msg, remediation=f"pass one of {allowed}") from None
