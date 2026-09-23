"""Backward-compatible re-export from ccnl_engine.payroll.service.seniority."""

from ccnl_engine.payroll.service.seniority import *  # noqa: F403
from ccnl_engine.payroll.service.seniority import (
    _resolve_seniority_count as _resolve_seniority_count,
)
from ccnl_engine.payroll.service.seniority import (
    _resolve_tier_amount as _resolve_tier_amount,
)
