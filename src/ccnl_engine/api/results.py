"""Canonical result types for the period-first payroll engine."""

from __future__ import annotations

from ccnl_engine.payroll.domain.period import PeriodCalculationResult

__all__ = ["PayrollResult"]

# PayrollResult is currently a structural alias for PeriodCalculationResult.
# Future PRs will extend it with run-identity fields (run_id, run_kind).
PayrollResult = PeriodCalculationResult
