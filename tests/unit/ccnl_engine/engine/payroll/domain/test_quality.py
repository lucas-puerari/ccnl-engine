"""Tests for payroll quality metadata types."""

from __future__ import annotations

import pytest

from ccnl_engine.engine.payroll.domain.quality import (
    ConfidenceLevel,
    CoverageStatus,
    PayrollWarning,
)


class TestCoverageStatus:
    """CoverageStatus is a StrEnum with PARTIAL and COMPLETE values."""

    def test_values(self) -> None:
        """Enum values match the expected strings."""
        assert CoverageStatus.PARTIAL.value == "partial"
        assert CoverageStatus.COMPLETE.value == "complete"

    def test_is_str(self) -> None:
        """CoverageStatus members are str instances."""
        assert isinstance(CoverageStatus.PARTIAL, str)

    def test_comparison_with_str(self) -> None:
        """StrEnum members compare equal to their string values."""
        assert str(CoverageStatus.PARTIAL) == "partial"
        assert str(CoverageStatus.COMPLETE) == "complete"


class TestConfidenceLevel:
    """ConfidenceLevel is a StrEnum with LOW, MEDIUM, and HIGH values."""

    def test_values(self) -> None:
        """Enum values match the expected strings."""
        assert ConfidenceLevel.LOW.value == "low"
        assert ConfidenceLevel.MEDIUM.value == "medium"
        assert ConfidenceLevel.HIGH.value == "high"

    def test_is_str(self) -> None:
        """ConfidenceLevel members are str instances."""
        assert isinstance(ConfidenceLevel.HIGH, str)

    def test_comparison_with_str(self) -> None:
        """StrEnum members compare equal to their string values."""
        assert str(ConfidenceLevel.LOW) == "low"
        assert str(ConfidenceLevel.MEDIUM) == "medium"
        assert str(ConfidenceLevel.HIGH) == "high"


class TestPayrollWarning:
    """PayrollWarning is a frozen dataclass with code, message, and path."""

    def test_required_fields(self) -> None:
        """``code`` and ``message`` are required; path defaults to None."""
        w = PayrollWarning(code="missing_schema", message="Schema not found")
        assert w.code == "missing_schema"
        assert w.message == "Schema not found"
        assert w.path is None

    def test_with_path(self) -> None:
        """``path`` can be set to a non-None string."""
        w = PayrollWarning(code="c", message="m", path="overtime.weekday")
        assert w.path == "overtime.weekday"

    def test_frozen(self) -> None:
        """Assigning to a frozen instance raises FrozenInstanceError."""
        w = PayrollWarning(code="c", message="m")
        with pytest.raises(Exception, match="cannot assign"):
            w.code = "other"  # type: ignore[misc]

    def test_equality(self) -> None:
        """Two PayrollWarning instances with identical fields are equal."""
        a = PayrollWarning(code="x", message="y")
        b = PayrollWarning(code="x", message="y")
        assert a == b

    def test_inequality(self) -> None:
        """PayrollWarning instances with different fields are not equal."""
        a = PayrollWarning(code="x", message="y")
        b = PayrollWarning(code="x", message="z")
        assert a != b
