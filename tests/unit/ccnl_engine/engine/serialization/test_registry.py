"""Tests for the serialisation type registry."""

from __future__ import annotations

from ccnl_engine.engine.payroll.domain.annual_result import AnnualEstimate
from ccnl_engine.engine.payroll.domain.components import (
    Contributions,
    Earnings,
    EmployerCost,
    Taxes,
)
from ccnl_engine.engine.payroll.domain.coverage import Coverage
from ccnl_engine.engine.payroll.domain.period_result import PeriodPayroll
from ccnl_engine.engine.serialization.registry import result_types


class TestResultTypes:
    """result_types() returns a complete, correct registry."""

    def test_returns_dict(self) -> None:
        """result_types() returns a mapping."""
        reg = result_types()
        assert isinstance(reg, dict)

    def test_contains_expected_keys(self) -> None:
        """All expected public result types are registered."""
        reg = result_types()
        expected = {
            "AnnualEstimate",
            "PeriodPayroll",
            "Earnings",
            "Contributions",
            "Taxes",
            "EmployerCost",
            "Coverage",
        }
        assert expected == set(reg.keys())

    def test_maps_to_correct_classes(self) -> None:
        """Each key maps to its corresponding class."""
        reg = result_types()
        assert reg["AnnualEstimate"] is AnnualEstimate
        assert reg["PeriodPayroll"] is PeriodPayroll
        assert reg["Earnings"] is Earnings
        assert reg["Contributions"] is Contributions
        assert reg["Taxes"] is Taxes
        assert reg["EmployerCost"] is EmployerCost
        assert reg["Coverage"] is Coverage

    def test_is_cached(self) -> None:
        """Successive calls return the same dict object."""
        assert result_types() is result_types()
