"""AnnualEstimate and PeriodPayroll — result types of compute().

Re-exports all public names from the split modules for backwards compatibility.
"""

from __future__ import annotations

from ccnl_engine.engine.payroll.domain.annual_result import (
    _SUB_OBJECT_DECODERS as _SUB_OBJECT_DECODERS,  # noqa: PLC0414
)
from ccnl_engine.engine.payroll.domain.annual_result import (
    AnnualEstimate,
)
from ccnl_engine.engine.payroll.domain.annual_result import (
    _decode_field as _decode_field,  # noqa: PLC0414
)
from ccnl_engine.engine.payroll.domain.components import (
    CalculationStatus,
    Contributions,
    Earnings,
    EligibilityStatus,
    EmployerCost,
    ScopeItem,
    SourceQuality,
    Taxes,
)
from ccnl_engine.engine.payroll.domain.components import (
    _coerce as _coerce,  # noqa: PLC0414
)
from ccnl_engine.engine.payroll.domain.components import (
    _coerce_scalar as _coerce_scalar,  # noqa: PLC0414
)
from ccnl_engine.engine.payroll.domain.components import (
    _coerce_scope_item as _coerce_scope_item,  # noqa: PLC0414
)
from ccnl_engine.engine.payroll.domain.components import (
    _has_default as _has_default,  # noqa: PLC0414
)
from ccnl_engine.engine.payroll.domain.components import (
    _serialise_dataclass as _serialise_dataclass,  # noqa: PLC0414
)
from ccnl_engine.engine.payroll.domain.components import (
    _serialise_value as _serialise_value,  # noqa: PLC0414
)
from ccnl_engine.engine.payroll.domain.components import (
    _unwrap_optional as _unwrap_optional,  # noqa: PLC0414
)
from ccnl_engine.engine.payroll.domain.coverage import Coverage
from ccnl_engine.engine.payroll.domain.period_result import PeriodPayroll

__all__ = [
    "AnnualEstimate",
    "CalculationStatus",
    "Contributions",
    "Coverage",
    "Earnings",
    "EligibilityStatus",
    "EmployerCost",
    "PeriodPayroll",
    "ScopeItem",
    "SourceQuality",
    "Taxes",
]
