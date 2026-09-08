"""Unit tests for RuleChange and RulesDiff domain models."""

from __future__ import annotations

import dataclasses
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from ccnl_engine.engine.diff.domain.diff import RuleChange, RulesDiff


def _change(
    path: str = "levels[A1].base_salary",
    label: str = "Level A1 - base salary",
    unit: str = "EUR/month",
    from_value: str | None = "1850.00",
    to_value: str | None = "1920.00",
    effective_date: str = "2026-11-01",
) -> RuleChange:
    return RuleChange(
        path=path,
        label=label,
        unit=unit,
        from_value=Decimal(from_value) if from_value else None,
        to_value=Decimal(to_value) if to_value else None,
        effective_date=date.fromisoformat(effective_date),
        provenance=None,
    )


def _diff(
    changes: tuple[RuleChange, ...] = (),
    affected_scenarios: int = 0,
    regression_status: str = "not_run",
) -> RulesDiff:
    return RulesDiff(
        ccnl_id="test",
        from_date=date(2026, 1, 1),
        to_date=date(2026, 12, 1),
        changes=changes,
        affected_rules=len(changes),
        affected_scenarios=affected_scenarios,
        regression_status=regression_status,  # type: ignore[arg-type]
        verification_status="unverified",
        generated_at=datetime(2026, 9, 1, 0, 0, tzinfo=UTC),
    )


class TestRuleChange:
    """RuleChange construction and frozen semantics."""

    def test_basic_construction(self) -> None:
        """Fields are stored exactly as supplied."""
        c = _change()
        assert c.path == "levels[A1].base_salary"
        assert c.from_value == Decimal("1850.00")
        assert c.to_value == Decimal("1920.00")
        assert c.effective_date == date(2026, 11, 1)
        assert c.provenance is None

    def test_immutable(self) -> None:
        """RuleChange instances are frozen."""
        c = _change()
        with pytest.raises(dataclasses.FrozenInstanceError):
            c.path = "other"  # type: ignore[misc]

    def test_none_from_value_allowed(self) -> None:
        """from_value=None represents a newly introduced rule."""
        c = _change(from_value=None)
        assert c.from_value is None
        assert c.to_value is not None

    def test_none_to_value_allowed(self) -> None:
        """to_value=None represents a removed rule."""
        c = _change(to_value=None)
        assert c.to_value is None


class TestRulesDiff:
    """RulesDiff construction, defaults, and replace semantics."""

    def test_empty_diff(self) -> None:
        """A diff with no changes has affected_rules=0."""
        d = _diff()
        assert d.affected_rules == 0
        assert d.changes == ()
        assert d.affected_scenarios == 0
        assert d.regression_status == "not_run"

    def test_change_count_matches(self) -> None:
        """affected_rules equals the number of changes supplied."""
        changes = (_change(), _change(path="parameters.hourly_divisor"))
        d = _diff(changes=changes)
        assert d.affected_rules == 2
        assert len(d.changes) == 2

    def test_immutable(self) -> None:
        """RulesDiff instances are frozen."""
        d = _diff()
        with pytest.raises(dataclasses.FrozenInstanceError):
            d.ccnl_id = "other"  # type: ignore[misc]

    def test_replace_affected_scenarios(self) -> None:
        """dataclasses.replace() correctly updates affected_scenarios."""
        d = _diff()
        updated = dataclasses.replace(d, affected_scenarios=27)
        assert updated.affected_scenarios == 27
        assert d.affected_scenarios == 0  # original is unchanged

    def test_replace_regression_status(self) -> None:
        """dataclasses.replace() correctly updates regression_status."""
        d = _diff()
        updated = dataclasses.replace(d, regression_status="passed")
        assert updated.regression_status == "passed"
        assert d.regression_status == "not_run"

    def test_replace_both_impact_fields(self) -> None:
        """Both impact fields can be updated in a single replace call."""
        d = _diff(changes=(_change(),))
        updated = dataclasses.replace(
            d, affected_scenarios=5, regression_status="failed"
        )
        assert updated.affected_scenarios == 5
        assert updated.regression_status == "failed"
        assert updated.affected_rules == 1  # unchanged
