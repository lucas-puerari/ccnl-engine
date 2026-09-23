"""Unit tests for PayrollRun domain type."""

from __future__ import annotations

import pytest

from ccnl_engine.payroll.domain.run import PayrollRun


class TestPayrollRun:
    """PayrollRun stores run identity, kind, month, and year."""

    def test_regular_factory(self) -> None:
        """regular() produces a deterministic run_id and run_kind='regular'."""
        run = PayrollRun.regular(2026, 3)
        assert run.run_id == "2026-03-regular"
        assert run.run_kind == "regular"
        assert run.month == 3
        assert run.year == 2026

    def test_thirteenth_factory(self) -> None:
        """thirteenth() produces run_kind='thirteenth' paid in the given month."""
        run = PayrollRun.thirteenth(2026, 12)
        assert run.run_id == "2026-12-thirteenth"
        assert run.run_kind == "thirteenth"
        assert run.month == 12

    def test_fourteenth_factory(self) -> None:
        """fourteenth() produces run_kind='fourteenth' paid in the given month."""
        run = PayrollRun.fourteenth(2026, 6)
        assert run.run_id == "2026-06-fourteenth"
        assert run.run_kind == "fourteenth"
        assert run.month == 6

    def test_frozen(self) -> None:
        """PayrollRun is immutable: attribute assignment raises AttributeError."""
        run = PayrollRun.regular(2026, 1)
        with pytest.raises(AttributeError):
            run.month = 2  # type: ignore[misc]

    def test_month_zero_raises(self) -> None:
        """month=0 raises ValueError."""
        with pytest.raises(ValueError, match="month"):
            PayrollRun(run_id="x", run_kind="regular", month=0, year=2026)

    def test_month_thirteen_raises(self) -> None:
        """month=13 raises ValueError."""
        with pytest.raises(ValueError, match="month"):
            PayrollRun(run_id="x", run_kind="regular", month=13, year=2026)

    def test_year_too_old_raises(self) -> None:
        """Year < 1970 raises ValueError."""
        with pytest.raises(ValueError, match="year"):
            PayrollRun(run_id="x", run_kind="regular", month=1, year=1969)

    def test_empty_run_id_raises(self) -> None:
        """Empty run_id raises ValueError."""
        with pytest.raises(ValueError, match="run_id"):
            PayrollRun(run_id="", run_kind="regular", month=1, year=2026)

    def test_equality(self) -> None:
        """Two PayrollRun instances with the same fields are equal."""
        a = PayrollRun.regular(2026, 1)
        b = PayrollRun.regular(2026, 1)
        assert a == b

    def test_inequality_different_kind(self) -> None:
        """PayrollRun instances with different run_kind are not equal."""
        a = PayrollRun.regular(2026, 12)
        b = PayrollRun.thirteenth(2026, 12)
        assert a != b
