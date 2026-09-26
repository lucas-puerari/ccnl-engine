"""Tests for capability enforcement in the period-first pipeline.

Verifies that calculate_period always returns a CapabilityReport, that it
correctly classifies gaps against the 2026 catalog, and that the report's
status and confidence reflect the set of gaps found.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.capability_catalog import (
    CapabilityGapKind,
    CapabilityReport,
)
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodState,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026


def _req(month: int = 1) -> PeriodCalculationRequest:
    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=PeriodId(year=_YEAR, month=month),
        payment_date=date(_YEAR, month, 28),
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=PeriodState.zero(),
    )


class TestCapabilityReportPresent:
    """calculate_period always populates capability_report on the result."""

    def test_result_has_capability_report(self) -> None:
        """The result exposes a CapabilityReport instance."""
        result = calculate_period(_req())
        assert isinstance(result.capability_report, CapabilityReport)

    def test_report_catalog_year_matches_period(self) -> None:
        """capability_report.catalog_year equals the period year."""
        result = calculate_period(_req(month=6))
        assert result.capability_report.catalog_year == _YEAR


class TestCapabilityReportGaps:
    """Gaps reflect unimplemented features declared in the 2026 catalog."""

    def test_report_has_feature_absent_gaps(self) -> None:
        """Features declared computed but absent from the pipeline produce gaps."""
        result = calculate_period(_req())
        report = result.capability_report
        absent_gaps = [
            g for g in report.gaps if g.kind == CapabilityGapKind.FEATURE_ABSENT
        ]
        assert len(absent_gaps) > 0

    def test_known_unimplemented_features_in_gaps(self) -> None:
        """Inail is partially_computed in catalog but absent from the pipeline."""
        result = calculate_period(_req())
        absent_features = {
            g.feature
            for g in result.capability_report.gaps
            if g.kind == CapabilityGapKind.FEATURE_ABSENT
        }
        assert "inail" in absent_features
        assert "bilateral_funds" not in absent_features

    def test_implemented_features_not_in_gaps(self) -> None:
        """Features present in _OBSERVED do not produce FEATURE_ABSENT gaps."""
        result = calculate_period(_req())
        absent_features = {
            g.feature
            for g in result.capability_report.gaps
            if g.kind == CapabilityGapKind.FEATURE_ABSENT
        }
        assert "base_salary" not in absent_features
        assert "irpef" not in absent_features
        assert "overtime" not in absent_features
        assert "night_work" not in absent_features
        assert "holiday_work" not in absent_features


class TestCapabilityReportStatus:
    """Report status and confidence reflect gap severity."""

    def test_status_is_incomplete(self) -> None:
        """The 2026 pipeline is incomplete (many features absent)."""
        result = calculate_period(_req())
        assert result.capability_report.status == "incomplete"

    def test_confidence_is_low(self) -> None:
        """Low confidence when status is incomplete."""
        result = calculate_period(_req())
        assert result.capability_report.confidence == "low"


class TestCapabilityReportImmutable:
    """CapabilityReport embedded in the result is frozen."""

    def test_report_is_frozen(self) -> None:
        """Assigning to capability_report raises FrozenInstanceError."""
        result = calculate_period(_req())
        with pytest.raises(FrozenInstanceError):
            result.capability_report = CapabilityReport.empty(_YEAR)  # type: ignore[misc]


class TestCapabilityReportDeterminism:
    """Two identical requests produce identical capability reports."""

    def test_same_request_same_report(self) -> None:
        """capability_report is deterministic for identical requests."""
        req = _req(month=3)
        first = calculate_period(req)
        second = calculate_period(req)
        assert first.capability_report == second.capability_report
