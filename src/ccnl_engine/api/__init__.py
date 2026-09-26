"""Public API types for ccnl-engine.

Re-exports the inputs and results of
:class:`~ccnl_engine.api.facade.PayrollEngine`.
"""

from ccnl_engine.payroll.application.calculate_year import YearResult
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.inputs import PeriodFacts, PeriodInput, YearInput
from ccnl_engine.payroll.domain.period import PeriodResult

__all__ = [
    "CalculationDecision",
    "CalculationIssue",
    "CalculationStatus",
    "PeriodFacts",
    "PeriodInput",
    "PeriodResult",
    "YearInput",
    "YearResult",
]
