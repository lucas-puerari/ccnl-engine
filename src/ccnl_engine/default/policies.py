"""Merged registry of the defaults of the public input fields."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from ccnl_engine.default.employer.policies import EMPLOYER_DEFAULTS
from ccnl_engine.default.event.policies import EVENT_DEFAULTS
from ccnl_engine.default.fact.policies import FACT_DEFAULTS
from ccnl_engine.default.period.policies import PERIOD_DEFAULTS
from ccnl_engine.default.request.policies import (
    REQUEST_DEFAULTS,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine.default.models import FieldDefault

__all__ = ["INPUT_DEFAULTS"]

#: Classification of every defaulted public input field, keyed ``Type.field``.
INPUT_DEFAULTS: Mapping[str, FieldDefault] = MappingProxyType({
    **REQUEST_DEFAULTS,
    **EMPLOYER_DEFAULTS,
    **FACT_DEFAULTS,
    **PERIOD_DEFAULTS,
    **EVENT_DEFAULTS,
})
