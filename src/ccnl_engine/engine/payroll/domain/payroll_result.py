"""AnnualEstimate and PeriodPayroll — result types of compute().

Re-exports all public names from the split modules for backwards compatibility.
"""

from __future__ import annotations

from ccnl_engine.engine.payroll.domain.annual_result import (
    _SUB_OBJECT_DECODERS as _SUB_OBJECT_DECODERS,
)
from ccnl_engine.engine.payroll.domain.annual_result import (
    AnnualEstimate,
)
from ccnl_engine.engine.payroll.domain.annual_result import (
    _decode_field as _decode_field,
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
    _coerce as _coerce,
)
from ccnl_engine.engine.payroll.domain.components import (
    _coerce_scalar as _coerce_scalar,
)
from ccnl_engine.engine.payroll.domain.components import (
    _coerce_scope_item as _coerce_scope_item,
)
from ccnl_engine.engine.payroll.domain.components import (
    _has_default as _has_default,
)
from ccnl_engine.engine.payroll.domain.components import (
    _serialise_dataclass as _serialise_dataclass,
)
from ccnl_engine.engine.payroll.domain.components import (
    _serialise_value as _serialise_value,
)
from ccnl_engine.engine.payroll.domain.components import (
    _unwrap_optional as _unwrap_optional,
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
