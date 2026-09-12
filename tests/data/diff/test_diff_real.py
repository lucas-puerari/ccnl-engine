"""Data-level tests for diff_ccnl() against real bundled CCNL files.

Level 2 of the three-level architecture: loads real knowledge-base files
via load_ccnl() and verifies that diff_ccnl() correctly detects salary
tranche transitions already encoded in the TimeSeries data.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.engine.contract.service.loaders import load_ccnl
from ccnl_engine.engine.diff.service.compute import diff_ccnl


class TestDiffRealMetalmeccanico:
    """Diff checks against metalmeccanico-federmeccanica salary tranches."""

    def test_has_changes_across_renewal(self) -> None:
        """A date range spanning the 2026-06-01 tranche produces changes."""
        ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
        result = diff_ccnl(ccnl, date(2026, 1, 1), date(2026, 7, 1))
        assert result.affected_rules > 0, (
            "Expected salary changes between 2026-01 and 2026-07 but found none"
        )

    def test_same_period_produces_no_changes(self) -> None:
        """Dates within the same salary tranche produce no changes."""
        ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
        # Both dates fall in the same period (2026-06-01..next)
        result = diff_ccnl(ccnl, date(2026, 7, 1), date(2026, 9, 1))
        assert result.changes == (), (
            "Expected no changes for two dates in the same salary period"
        )

    def test_change_values_are_positive(self) -> None:
        """All detected changes have non-negative monetary values."""
        ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
        result = diff_ccnl(ccnl, date(2026, 1, 1), date(2026, 7, 1))
        for change in result.changes:
            if change.from_value is not None:
                assert change.from_value >= Decimal(0), (
                    f"Negative from_value on {change.path}"
                )
            if change.to_value is not None:
                assert change.to_value >= Decimal(0), (
                    f"Negative to_value on {change.path}"
                )

    def test_effective_date_within_range(self) -> None:
        """Effective dates fall within or at the boundary of the diff range."""
        from_d = date(2026, 1, 1)
        to_d = date(2026, 7, 1)
        ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
        result = diff_ccnl(ccnl, from_d, to_d)
        for change in result.changes:
            assert from_d <= change.effective_date <= to_d, (
                f"effective_date {change.effective_date} out of range for {change.path}"
            )

    def test_ccnl_id_correct(self) -> None:
        """The diff carries the correct CCNL id."""
        ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
        result = diff_ccnl(ccnl, date(2026, 1, 1), date(2026, 7, 1))
        assert result.ccnl_id == "metalmeccanico-federmeccanica"

    def test_all_salary_changes_are_increases(self) -> None:
        """For metalmeccanico, salary tranches are always increases."""
        ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
        result = diff_ccnl(ccnl, date(2026, 1, 1), date(2026, 7, 1))
        salary_changes = [c for c in result.changes if "base_salary" in c.path]
        for ch in salary_changes:
            if ch.from_value is not None and ch.to_value is not None:
                assert ch.to_value > ch.from_value, (
                    f"Expected increase on {ch.path}: {ch.from_value} → {ch.to_value}"
                )
