"""Fiscal chain: INPS contributions, IRPEF, addizionali, net pay."""

from ccnl_engine.engine.payroll.service.fiscal._compute import compute_fiscal
from ccnl_engine.engine.payroll.service.fiscal_result import FiscalPay

__all__ = ["FiscalPay", "compute_fiscal"]
