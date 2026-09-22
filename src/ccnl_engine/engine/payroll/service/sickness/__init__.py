"""Sick-leave (malattia ordinaria) computation service."""

from ccnl_engine.engine.payroll.service.sickness._compute import compute_sickness
from ccnl_engine.engine.payroll.service.sickness._helpers import (
    _bucket_days,
    _ccnl_tier_boundaries_in_period,
    _effective_integration_rate,
    _inps_boundaries_in_period,
    _tier_rate_segments,
)

__all__ = [
    "_bucket_days",
    "_ccnl_tier_boundaries_in_period",
    "_effective_integration_rate",
    "_inps_boundaries_in_period",
    "_tier_rate_segments",
    "compute_sickness",
]
