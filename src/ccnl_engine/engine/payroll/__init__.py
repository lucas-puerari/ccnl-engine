"""Payroll computation bounded context."""

from ccnl_engine.engine.payroll.domain.payroll_result import (
    PayrollResult as PayrollResult,
)
from ccnl_engine.engine.payroll.service.orchestrator import compute as compute

__all__ = ["PayrollResult", "compute"]
