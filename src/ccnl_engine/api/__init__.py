"""Public API types for ccnl-engine.

Re-exports the canonical request/result types used by
:class:`~ccnl_engine.engine.payroll.service.engine.PayrollEngine`.
"""

from ccnl_engine.api.requests import PayrollRequest, PayrollYearRequest
from ccnl_engine.api.results import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
    PayrollResult,
)

__all__ = [
    "CalculationDecision",
    "CalculationIssue",
    "CalculationStatus",
    "PayrollRequest",
    "PayrollResult",
    "PayrollYearRequest",
]
