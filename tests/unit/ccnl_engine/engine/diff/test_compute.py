"""Unit tests for diff_ccnl().

Uses in-memory CCNL objects (no file I/O, no source_hash) to test every
code path of the diff walker independently of the knowledge-base loader.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from ccnl_engine.engine.contract.domain.ccnl import CCNL
from ccnl_engine.engine.contract.domain.validity import TimeSeries, ValidityPeriod
from ccnl_engine.engine.diff.compute import diff_ccnl
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


def _ccnl_with_salary(level_salary_a: str, level_salary_b: str) -> CCNL:
    """CCNL whose level-4 base_salary changes at 2025-01-01.

    Returns:
        A validated CCNL with two salary tranches on level 4.
    """
    data = make_ccnl_dict()
    data["levels"][2]["base_salary"] = _two_period_series(
        level_salary_a, "2025-01-01", level_salary_b
    )
    return CCNL.model_validate(data)


# ---------------------------------------------------------------------------
# period_at (smoke-test the new TimeSeries method via diff_ccnl)
# ---------------------------------------------------------------------------


class TestPeriodAt:
    """TimeSeries.period_at() returns the right period or None."""

    def test_before_series_start_returns_none(self) -> None:
        """period_at before series start returns None."""
        ts = TimeSeries(
            periods=[
                ValidityPeriod(
                    valid_from=date(2025, 1, 1),
                    valid_until=None,
                    value=Decimal(100),
                )
            ]
        )
        assert ts.period_at(date(2024, 12, 31)) is None

    def test_at_series_start_returns_period(self) -> None:
        """period_at on the first valid_from date returns that period."""
        ts = TimeSeries(
            periods=[
                ValidityPeriod(
                    valid_from=date(2025, 1, 1),
                    valid_until=None,
                    value=Decimal(100),
                )
            ]
        )
        p = ts.period_at(date(2025, 1, 1))
        assert p is not None
        assert p.value == Decimal(100)

    def test_at_boundary_returns_second_period(self) -> None:
        """period_at exactly at valid_until boundary returns the next period."""
        ts = TimeSeries(
            periods=[
                ValidityPeriod(
                    valid_from=date(2025, 1, 1),
                    valid_until=date(2026, 1, 1),
                    value=Decimal(100),
                ),
                ValidityPeriod(
                    valid_from=date(2026, 1, 1),
                    valid_until=None,
                    value=Decimal(110),
                ),
            ]
        )
        p = ts.period_at(date(2026, 1, 1))
        assert p is not None
        assert p.value == Decimal(110)

    def test_open_ended_period_matches_far_future(self) -> None:
        """An open-ended period is returned for any date after valid_from."""
        ts = TimeSeries(
            periods=[
                ValidityPeriod(
                    valid_from=date(2020, 1, 1),
                    valid_until=None,
                    value=Decimal(999),
                )
            ]
        )
        p = ts.period_at(date(2099, 12, 31))
        assert p is not None
        assert p.value == Decimal(999)


# ---------------------------------------------------------------------------
# diff_ccnl — argument validation
# ---------------------------------------------------------------------------


class TestDiffCcnlValidation:
    """diff_ccnl raises ValueError for invalid date pairs."""

    def test_to_before_from_raises(self) -> None:
        """to_date <= from_date raises ValueError."""
        ccnl = CCNL.model_validate(make_ccnl_dict())
        with pytest.raises(ValueError, match="to_date"):
            diff_ccnl(ccnl, date(2026, 1, 1), date(2025, 1, 1))

    def test_equal_dates_raise(self) -> None:
        """to_date == from_date raises ValueError."""
        ccnl = CCNL.model_validate(make_ccnl_dict())
        with pytest.raises(ValueError, match="to_date"):
            diff_ccnl(ccnl, date(2026, 1, 1), date(2026, 1, 1))


# ---------------------------------------------------------------------------
# diff_ccnl — no changes detected
# ---------------------------------------------------------------------------


class TestDiffCcnlNoChanges:
    """diff_ccnl returns an empty diff when nothing changed."""

    def test_no_changes_same_period(self) -> None:
        """Single-period CCNL produces no changes for any date range."""
        ccnl = CCNL.model_validate(make_ccnl_dict())
        result = diff_ccnl(ccnl, date(2022, 1, 1), date(2026, 1, 1))
        assert result.changes == ()
        assert result.affected_rules == 0

    def test_metadata(self) -> None:
        """Basic metadata fields are populated correctly."""
        ccnl = CCNL.model_validate(make_ccnl_dict())
        from_d = date(2022, 1, 1)
        to_d = date(2026, 1, 1)
        result = diff_ccnl(ccnl, from_d, to_d)
        assert result.ccnl_id == "test"
        assert result.from_date == from_d
        assert result.to_date == to_d
        assert result.affected_scenarios == 0
        assert result.regression_status == "not_run"


# ---------------------------------------------------------------------------
# diff_ccnl — salary changes detected
# ---------------------------------------------------------------------------


class TestDiffCcnlSalaryChange:
    """diff_ccnl detects base_salary tranche changes."""

    def test_single_level_salary_change(self) -> None:
        """One level salary change produces exactly one RuleChange."""
        ccnl = _ccnl_with_salary("1000.00", "1100.00")
        result = diff_ccnl(ccnl, date(2024, 6, 1), date(2025, 6, 1))
        salary_changes = [c for c in result.changes if "base_salary" in c.path]
        assert len(salary_changes) == 1
        ch = salary_changes[0]
        assert ch.from_value == Decimal("1000.00")
        assert ch.to_value == Decimal("1100.00")
        assert ch.effective_date == date(2025, 1, 1)
        assert ch.unit == "EUR/month"

    def test_path_and_label_content(self) -> None:
        """Path contains level code and label is human-readable."""
        ccnl = _ccnl_with_salary("1000.00", "1200.00")
        result = diff_ccnl(ccnl, date(2024, 6, 1), date(2025, 6, 1))
        ch = next(c for c in result.changes if "base_salary" in c.path)
        assert "4" in ch.path
        assert "Level 4" in ch.label
        assert "base salary" in ch.label

    def test_unchanged_levels_not_reported(self) -> None:
        """Levels whose salary is unchanged are not included in the diff."""
        ccnl = _ccnl_with_salary("1000.00", "1100.00")
        result = diff_ccnl(ccnl, date(2024, 6, 1), date(2025, 6, 1))
        # Only level "4" has two periods; levels "2" and "3" are unchanged
        level2_changes = [c for c in result.changes if "[2]" in c.path]
        level3_changes = [c for c in result.changes if "[3]" in c.path]
        assert level2_changes == []
        assert level3_changes == []


# ---------------------------------------------------------------------------
# diff_ccnl — no value before series start
# ---------------------------------------------------------------------------


class TestDiffCcnlNewRule:
    """diff_ccnl handles from_date before series start (from_value=None)."""

    def test_new_rule_from_value_is_none(self) -> None:
        """When from_date precedes series start, from_value is None."""
        data = make_ccnl_dict()
        # Override level "4" salary to start on 2025-01-01
        data["levels"][2]["base_salary"] = {
            "periods": [_period("2025-01-01", None, "1100.00")]
        }
        ccnl = CCNL.model_validate(data)
        result = diff_ccnl(ccnl, date(2024, 1, 1), date(2025, 6, 1))
        salary_changes = [c for c in result.changes if "[4].base_salary" in c.path]
        assert len(salary_changes) == 1
        assert salary_changes[0].from_value is None
        assert salary_changes[0].to_value == Decimal("1100.00")


# ---------------------------------------------------------------------------
# diff_ccnl — seniority increment changes
# ---------------------------------------------------------------------------


class TestDiffCcnlSeniorityChange:
    """diff_ccnl detects seniority increment changes."""

    def test_seniority_change_detected(self) -> None:
        """A changed seniority amount is included in the diff."""
        data = make_ccnl_dict()
        data["parameters"]["seniority_increments"]["amount_by_level"] = {
            "4": _two_period_series("20.00", "2025-01-01", "22.00")
        }
        ccnl = CCNL.model_validate(data)
        result = diff_ccnl(ccnl, date(2024, 1, 1), date(2025, 6, 1))
        seniority_changes = [
            c for c in result.changes if "seniority_increments" in c.path
        ]
        assert len(seniority_changes) == 1
        assert seniority_changes[0].from_value == Decimal("20.00")
        assert seniority_changes[0].to_value == Decimal("22.00")


# ---------------------------------------------------------------------------
# diff_ccnl — employer fund rate changes
# ---------------------------------------------------------------------------


class TestDiffCcnlEmployerFundChange:
    """diff_ccnl detects employer-fund rate changes."""

    def test_employer_fund_rate_change(self) -> None:
        """A changed fund rate is included in the diff."""
        data = make_ccnl_dict()
        data["parameters"]["employer_funds"] = [
            {
                "code": "FNCS",
                "description": "Test fund",
                "rate": _two_period_series("0.0050", "2025-01-01", "0.0060"),
                "provenance": TEST_PROV,
            }
        ]
        ccnl = CCNL.model_validate(data)
        result = diff_ccnl(ccnl, date(2024, 1, 1), date(2025, 6, 1))
        fund_changes = [c for c in result.changes if "employer_funds" in c.path]
        assert len(fund_changes) == 1
        assert fund_changes[0].unit == "%"
        assert fund_changes[0].from_value == Decimal("0.0050")
        assert fund_changes[0].to_value == Decimal("0.0060")


# ---------------------------------------------------------------------------
# diff_ccnl — ruleset verification_status
# ---------------------------------------------------------------------------


class TestDiffCcnlVerificationStatus:
    """verification_status is inherited from the CCNL ruleset (or defaults)."""

    def test_no_ruleset_defaults_to_unverified(self) -> None:
        """CCNLs without a ruleset block use 'unverified'."""
        ccnl = CCNL.model_validate(make_ccnl_dict())
        result = diff_ccnl(ccnl, date(2022, 1, 1), date(2026, 1, 1))
        assert result.verification_status == "unverified"

    def test_ruleset_verification_status_propagated(self) -> None:
        """verification_status from ruleset is propagated to the diff."""
        data = make_ccnl_dict()
        data["schema_version"] = "0.5"
        data["ruleset"] = {
            "id": "ccnl/test",
            "version": "2026.1",
            "effective_from": "2026-01-01",
            "effective_until": None,
            "published_at": "2026-09-01",
            "source": "https://example.com",
            "source_hash": "a" * 64,
            "verification_status": "verified",
        }
        ccnl = CCNL.model_validate(data)
        result = diff_ccnl(ccnl, date(2024, 1, 1), date(2026, 6, 1))
        assert result.verification_status == "verified"


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
# diff_ccnl — overtime band rate changes (R8)
# ---------------------------------------------------------------------------


class TestDiffCcnlOvertimeBandChange:
    """diff_ccnl detects overtime/supplement band rate changes (R8)."""

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
