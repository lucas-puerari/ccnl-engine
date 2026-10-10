"""Unit tests for diff_ccnl() on allowances, tiers, apprentices and overtime.

Uses in-memory CCNL objects (no file I/O, no source_hash) to test the diff
walker on allowance, tiered seniority, per-category, apprentice amount and
overtime band changes.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from ccnl_engine.comparison.ruleset.services import diff_ccnl
from ccnl_engine.contract.identity.facade import CCNL
from tests.helpers import TEST_PROV, make_ccnl_dict

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _period(
    valid_from: str,
    valid_until: str | None,
    value: str,
) -> dict[str, Any]:
    return {
        "valid_from": valid_from,
        "valid_until": valid_until,
        "value": value,
        "provenance": TEST_PROV,
    }


def _two_period_series(
    value_a: str,
    boundary: str,
    value_b: str,
) -> dict[str, Any]:
    """TimeSeries with two periods split at *boundary*, each with provenance.

    Returns:
        A dict suitable for passing as a TimeSeries in CCNL.model_validate().
    """
    return {
        "periods": [
            _period("2020-01-01", boundary, value_a),
            _period(boundary, None, value_b),
        ]
    }


# ---------------------------------------------------------------------------
# diff_ccnl — allowance changes
# ---------------------------------------------------------------------------


class TestDiffCcnlAllowanceChange:
    """diff_ccnl detects fixed_allowance changes."""

    def test_allowance_change_detected(self) -> None:
        """A changing allowance monthly value appears in the diff."""
        data = make_ccnl_dict()
        data["levels"][0]["fixed_allowances"] = [
            {
                "code": "EVR",
                "description": "EVR",
                "monthly": _two_period_series("10.00", "2025-01-01", "12.00"),
                "provenance": TEST_PROV,
            }
        ]
        ccnl = CCNL.model_validate(data)
        result = diff_ccnl(ccnl, date(2024, 1, 1), date(2025, 6, 1))
        allowance_changes = [c for c in result.changes if "fixed_allowances" in c.path]
        assert len(allowance_changes) == 1
        assert allowance_changes[0].from_value == Decimal("10.00")
        assert allowance_changes[0].to_value == Decimal("12.00")
        assert "EVR" in allowance_changes[0].path
        assert "EVR" in allowance_changes[0].label

    def test_unchanged_allowance_not_reported(self) -> None:
        """An allowance whose value does not change is not in the diff."""
        data = make_ccnl_dict()
        data["levels"][0]["fixed_allowances"] = [
            {
                "code": "EVR",
                "description": "EVR",
                "monthly": {"periods": [_period("2020-01-01", None, "10.00")]},
                "provenance": TEST_PROV,
            }
        ]
        ccnl = CCNL.model_validate(data)
        result = diff_ccnl(ccnl, date(2024, 1, 1), date(2025, 6, 1))
        assert result.changes == ()


# ---------------------------------------------------------------------------
# diff_ccnl — tiered seniority
# ---------------------------------------------------------------------------


class TestDiffCcnlTieredSeniority:
    """diff_ccnl walks seniority tiers correctly."""

    def test_tier_amount_change_detected(self) -> None:
        """A changed amount inside a seniority tier is detected."""
        data = make_ccnl_dict(app_type="")
        data["parameters"]["seniority_increments"] = {
            "cadence_months": 24,
            "maximum_count": 3,  # must equal sum of tier maximum_count values
            "amount_by_level": {},
            "provenance": TEST_PROV,
            "tiers": [
                {
                    "cadence_months": 24,
                    "maximum_count": 3,
                    "amount_by_level": {
                        "4": _two_period_series("10.00", "2025-01-01", "12.00")
                    },
                },
            ],
        }
        ccnl = CCNL.model_validate(data)
        result = diff_ccnl(ccnl, date(2024, 1, 1), date(2025, 6, 1))
        tier_changes = [c for c in result.changes if "tiers[0]" in c.path]
        assert len(tier_changes) == 1
        assert tier_changes[0].from_value == Decimal("10.00")
        assert tier_changes[0].to_value == Decimal("12.00")
        assert "tier 1" in tier_changes[0].label


# ---------------------------------------------------------------------------
# diff_ccnl — amount_by_level_by_category
# ---------------------------------------------------------------------------


class TestDiffCcnlAmountByCategory:
    """diff_ccnl walks amount_by_level_by_category."""

    def test_category_seniority_change_detected(self) -> None:
        """A changed amount in amount_by_level_by_category is detected."""
        data = make_ccnl_dict()
        data["parameters"]["seniority_increments"] = {
            "cadence_months": 36,
            "maximum_count": 10,
            "amount_by_level": {
                "4": {"periods": [_period("2020-01-01", None, "20.00")]}
            },
            "provenance": TEST_PROV,
            "amount_by_level_by_category": {
                "operaio": {"4": _two_period_series("5.00", "2025-01-01", "6.00")}
            },
        }
        ccnl = CCNL.model_validate(data)
        result = diff_ccnl(ccnl, date(2024, 1, 1), date(2025, 6, 1))
        cat_changes = [
            c for c in result.changes if "amount_by_level_by_category" in c.path
        ]
        assert len(cat_changes) == 1
        assert cat_changes[0].from_value == Decimal("5.00")
        assert cat_changes[0].to_value == Decimal("6.00")
        assert "operaio" in cat_changes[0].label


# ---------------------------------------------------------------------------
# diff_ccnl — apprentice_amount
# ---------------------------------------------------------------------------


class TestDiffCcnlApprenticeAmount:
    """diff_ccnl detects apprentice_amount changes."""

    def test_apprentice_amount_change_detected(self) -> None:
        """A changing apprentice_amount is detected."""
        data = make_ccnl_dict()
        data["parameters"]["seniority_increments"]["apprentice_amount"] = (
            _two_period_series("5.00", "2025-01-01", "6.00")
        )
        ccnl = CCNL.model_validate(data)
        result = diff_ccnl(ccnl, date(2024, 1, 1), date(2025, 6, 1))
        app_changes = [c for c in result.changes if "apprentice_amount" in c.path]
        assert len(app_changes) == 1
        assert app_changes[0].from_value == Decimal("5.00")
        assert app_changes[0].to_value == Decimal("6.00")


# ---------------------------------------------------------------------------
# diff_ccnl — overtime band rate changes
# ---------------------------------------------------------------------------


class TestDiffCcnlOvertimeBandChange:
    """diff_ccnl detects overtime/supplement band rate changes."""

    @staticmethod
    def _make_band(code: str, rate_series: dict[str, Any]) -> dict[str, Any]:
        return {
            "code": code,
            "description": f"Band {code}",
            "kind": "percentage",
            "rate": rate_series,
            "applies_to_kinds": ["weekday"],
            "provenance": TEST_PROV,
        }

    def test_overtime_band_rate_change_detected(self) -> None:
        """A changing overtime band rate is included in the diff."""
        data = make_ccnl_dict()
        data["work_rules"] = {
            "time_supplements": {
                "overtime_bands": [
                    self._make_band(
                        "OT_DIURNO",
                        _two_period_series("0.15", "2026-08-01", "0.30"),
                    )
                ]
            }
        }
        ccnl = CCNL.model_validate(data)
        result = diff_ccnl(ccnl, date(2026, 7, 1), date(2026, 9, 1))
        band_changes = [c for c in result.changes if "overtime_bands" in c.path]
        assert len(band_changes) == 1
        ch = band_changes[0]
        assert ch.from_value == Decimal("0.15")
        assert ch.to_value == Decimal("0.30")
        assert ch.effective_date == date(2026, 8, 1)
        assert ch.unit == "%"
        assert "OT_DIURNO" in ch.path
        assert "OT_DIURNO" in ch.label

    def test_overtime_band_unchanged_not_reported(self) -> None:
        """An unchanged overtime band rate does not appear in the diff."""
        data = make_ccnl_dict()
        data["work_rules"] = {
            "time_supplements": {
                "overtime_bands": [
                    self._make_band(
                        "OT_DIURNO",
                        {"periods": [_period("2020-01-01", None, "0.25")]},
                    )
                ]
            }
        }
        ccnl = CCNL.model_validate(data)
        result = diff_ccnl(ccnl, date(2026, 7, 1), date(2026, 9, 1))
        band_changes = [c for c in result.changes if "overtime_bands" in c.path]
        assert band_changes == []

    def test_no_time_supplements_produces_no_band_changes(self) -> None:
        """A CCNL with no time_supplements block produces no band changes."""
        ccnl = CCNL.model_validate(make_ccnl_dict())
        result = diff_ccnl(ccnl, date(2024, 1, 1), date(2026, 1, 1))
        band_changes = [c for c in result.changes if "overtime_bands" in c.path]
        assert band_changes == []

    def test_only_rate_changes_not_salary_changes(self) -> None:
        """Isolated band rate change: salary unchanged, diff has only the band."""
        data = make_ccnl_dict()
        data["work_rules"] = {
            "time_supplements": {
                "overtime_bands": [
                    self._make_band(
                        "OT_NOTTE",
                        _two_period_series("0.35", "2026-08-01", "0.40"),
                    )
                ]
            }
        }
        ccnl = CCNL.model_validate(data)
        result = diff_ccnl(ccnl, date(2026, 7, 1), date(2026, 9, 1))
        assert result.affected_rules == 1
        assert "overtime_bands[OT_NOTTE]" in result.changes[0].path
