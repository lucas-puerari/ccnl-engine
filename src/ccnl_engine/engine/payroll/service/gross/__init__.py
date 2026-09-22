"""Contractual pay resolution, scaling and annualisation."""

from ccnl_engine.engine.payroll.service.gross._gross import GrossPay, compute_gross
from ccnl_engine.engine.payroll.service.gross._helpers import _scale_second_level

__all__ = ["GrossPay", "_scale_second_level", "compute_gross"]
