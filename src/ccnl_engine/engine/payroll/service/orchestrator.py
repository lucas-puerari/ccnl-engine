"""Coordinate gross, fiscal and optional computations into a payroll result.

Re-exports all public names from the split modules for backwards compatibility.
"""

from __future__ import annotations

from ccnl_engine.engine.payroll.service.annual_service import (
    estimate_annual,
    estimate_period_effects,
)
from ccnl_engine.engine.payroll.service.coverage_evaluator import (
    _ivs_ceiling_warning as _ivs_ceiling_warning,
)

__all__ = [
    "estimate_annual",
    "estimate_period_effects",
]
