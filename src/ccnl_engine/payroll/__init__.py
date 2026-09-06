"""Payroll computation bounded context."""

from ccnl_engine.payroll.domain.payslip import Payslip as Payslip
from ccnl_engine.payroll.service.orchestrator import compute as compute

__all__ = ["Payslip", "compute"]
