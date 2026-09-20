"""Coordinate gross, fiscal and optional computations into a payroll result.

Re-exports all public names from the split modules for backwards compatibility.
"""

from __future__ import annotations

from ccnl_engine.engine.payroll.service.annual_service import (
    estimate_annual,
    estimate_period_effects,
)
from ccnl_engine.engine.payroll.service.coverage_evaluator import (
    _ivs_ceiling_warning as _ivs_ceiling_warning,  # noqa: PLC0414
)
from ccnl_engine.engine.payroll.service.period_service import (
    compute_period,
    compute_period_payroll,
    compute_year,
)
from ccnl_engine.engine.payroll.service.year_service import (
    compute_payroll_year,
    summarize_payroll_year,
)

__all__ = [
    "compute_payroll_year",
    "compute_period",
    "compute_period_payroll",
    "compute_year",
    "estimate_annual",
    "estimate_period_effects",
    "summarize_payroll_year",
]
