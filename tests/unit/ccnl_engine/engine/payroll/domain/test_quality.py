"""Tests for payroll quality metadata types."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from ccnl_engine.engine.payroll.domain.quality import (
    ConfidenceLevel,
    CoverageStatus,
    Limitation,
    LimitationIntegrationStatus,
    LimitationSeverity,
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


def _make_limitation() -> Limitation:
    return Limitation(
        code="simplification_0",
        affected_component="maternity_leave",
        applicability_predicate="always",
        severity=LimitationSeverity.MEDIUM,
        impact_axis=("gross", "net"),
        integration_status=LimitationIntegrationStatus.NOT_INTEGRATED,
        remediation="Statutory rate used; actual fund return may differ.",
        source="CCNL coverage note",
    )


class TestLimitationSeverity:
    """LimitationSeverity is a StrEnum with HIGH, MEDIUM, LOW values."""

    def test_values(self) -> None:
        """Enum values match the expected strings."""
        assert LimitationSeverity.HIGH.value == "high"
        assert LimitationSeverity.MEDIUM.value == "medium"
        assert LimitationSeverity.LOW.value == "low"

    def test_is_str(self) -> None:
        """LimitationSeverity members are str instances."""
        assert isinstance(LimitationSeverity.HIGH, str)


class TestLimitationIntegrationStatus:
    """LimitationIntegrationStatus is a StrEnum with three values."""

    def test_values(self) -> None:
        """Enum values match the expected strings."""
        assert LimitationIntegrationStatus.NOT_INTEGRATED.value == "not_integrated"
        assert (
            LimitationIntegrationStatus.PARTIALLY_INTEGRATED.value
            == "partially_integrated"
        )
        assert LimitationIntegrationStatus.INTEGRATED.value == "integrated"

    def test_is_str(self) -> None:
        """LimitationIntegrationStatus members are str instances."""
        assert isinstance(LimitationIntegrationStatus.NOT_INTEGRATED, str)


class TestLimitation:
    """Limitation is a frozen dataclass with to_dict / from_dict round-trip."""

    def test_fields_stored(self) -> None:
        """All fields are stored correctly on construction."""
        lim = _make_limitation()
        assert lim.code == "simplification_0"
        assert lim.affected_component == "maternity_leave"
        assert lim.applicability_predicate == "always"
        assert lim.severity == LimitationSeverity.MEDIUM
        assert lim.impact_axis == ("gross", "net")
        assert lim.integration_status == LimitationIntegrationStatus.NOT_INTEGRATED
        assert "Statutory" in lim.remediation
        assert lim.source == "CCNL coverage note"

    def test_source_defaults_to_empty_string(self) -> None:
        """The source field defaults to an empty string."""
        lim = Limitation(
            code="x",
            affected_component="general",
            applicability_predicate="always",
            severity=LimitationSeverity.LOW,
            impact_axis=(),
            integration_status=LimitationIntegrationStatus.INTEGRATED,
            remediation="desc",
        )
        assert not lim.source

    def test_to_dict_roundtrip(self) -> None:
        """to_dict() followed by from_dict() returns an equal instance."""
        lim = _make_limitation()
        d = lim.to_dict()
        restored = Limitation.from_dict(d)
        assert restored == lim

    def test_to_dict_keys(self) -> None:
        """to_dict() contains all eight expected keys."""
        d = _make_limitation().to_dict()
        assert set(d.keys()) == {
            "code",
            "affected_component",
            "applicability_predicate",
            "severity",
            "impact_axis",
            "integration_status",
            "remediation",
            "source",
        }

    def test_to_dict_impact_axis_is_list(self) -> None:
        """to_dict() serialises impact_axis as a list."""
        d = _make_limitation().to_dict()
        assert isinstance(d["impact_axis"], list)

    def test_from_dict_empty_impact_axis(self) -> None:
        """from_dict() handles a missing/empty impact_axis gracefully."""
        d = _make_limitation().to_dict()
        d["impact_axis"] = []
        lim = Limitation.from_dict(d)
        assert lim.impact_axis == ()

    def test_from_dict_non_list_impact_axis_becomes_empty(self) -> None:
        """from_dict() normalises a non-list impact_axis to empty tuple."""
        d = _make_limitation().to_dict()
        d["impact_axis"] = "gross"
        lim = Limitation.from_dict(d)
        assert lim.impact_axis == ()

    def test_frozen(self) -> None:
        """Assigning to a frozen instance raises FrozenInstanceError."""
        lim = _make_limitation()
        with pytest.raises(FrozenInstanceError):
            lim.code = "other"  # type: ignore[misc]
