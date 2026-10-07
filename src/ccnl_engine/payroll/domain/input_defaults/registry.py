"""Merged registry of the defaults of the public input fields."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.input_defaults.event_fields import EVENT_DEFAULTS
from ccnl_engine.payroll.domain.input_defaults.fact_fields import FACT_DEFAULTS
from ccnl_engine.payroll.domain.input_defaults.request_fields import (
    REQUEST_DEFAULTS,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.payroll.domain.input_defaults.model import FieldDefault

__all__ = ["INPUT_DEFAULTS"]

#: Classification of every defaulted public input field, keyed ``Type.field``.
INPUT_DEFAULTS: Mapping[str, FieldDefault] = MappingProxyType({
    **REQUEST_DEFAULTS,
    **FACT_DEFAULTS,
    **EVENT_DEFAULTS,
})
