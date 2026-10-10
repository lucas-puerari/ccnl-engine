"""Merged registry of the defaults of the public input fields."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from ccnl_engine.payroll.period.policies_default_event import EVENT_DEFAULTS
from ccnl_engine.payroll.period.policies_default_fact import FACT_DEFAULTS
from ccnl_engine.payroll.period.policies_default_request import (
    REQUEST_DEFAULTS,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.payroll.period.models_default import FieldDefault

__all__ = ["INPUT_DEFAULTS"]

#: Classification of every defaulted public input field, keyed ``Type.field``.
INPUT_DEFAULTS: Mapping[str, FieldDefault] = MappingProxyType({
    **REQUEST_DEFAULTS,
    **FACT_DEFAULTS,
    **EVENT_DEFAULTS,
})
