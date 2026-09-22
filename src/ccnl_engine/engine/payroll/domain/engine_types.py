"""Public request/result type aliases for PayrollEngine.

Re-exports the underlying domain types under the new stable names
used by :class:`~ccnl_engine.engine.payroll.service.engine.PayrollEngine`.
"""

from __future__ import annotations

from ccnl_engine.engine.errors import CcnlEngineError as PayrollError
from ccnl_engine.engine.payroll.domain.period_payroll import (
    PayrollYearRequest as YearRequest,
)
from ccnl_engine.engine.payroll.domain.period_payroll import (
    PayrollYearResult as YearResult,
)
from ccnl_engine.engine.payroll.domain.period_payroll import (
    PeriodPayrollRequest as PeriodRequest,
)
from ccnl_engine.engine.payroll.domain.period_payroll import (
    PeriodPayrollResult as PeriodResult,
)

__all__ = [
    "PayrollError",
    "PeriodRequest",
    "PeriodResult",
    "YearRequest",
    "YearResult",
]
