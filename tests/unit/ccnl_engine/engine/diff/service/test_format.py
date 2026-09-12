"""Unit tests for format_diff()."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from ccnl_engine.engine.diff.domain.diff import RuleChange, RulesDiff
from ccnl_engine.engine.diff.service.format import format_diff


def _change(
    label: str = "Level C2 - base salary",
    from_value: str = "1850.00",
    to_value: str = "1920.00",
    effective_date: str = "2026-11-01",
    unit: str = "EUR/month",
) -> RuleChange:
    return RuleChange(
        path="levels[C2].base_salary",
        label=label,
        unit=unit,
        from_value=Decimal(from_value),
        to_value=Decimal(to_value),
        effective_date=date.fromisoformat(effective_date),
        provenance=None,
    )


def _diff(
    changes: tuple[RuleChange, ...] = (),
    affected_scenarios: int = 0,
    regression_status: str = "not_run",
    verification_status: str = "verified",
) -> RulesDiff:
    return RulesDiff(
        ccnl_id="test",
        from_date=date(2026, 1, 1),
        to_date=date(2026, 12, 1),
        changes=changes,
        affected_rules=len(changes),
        affected_scenarios=affected_scenarios,
        regression_status=regression_status,  # type: ignore[arg-type]
        verification_status=verification_status,
        generated_at=datetime(2026, 9, 1, 0, 0, tzinfo=UTC),
    )


class TestFormatDiffNoChanges:
    """format_diff with no changes."""

    def test_empty_diff_shows_no_changes(self) -> None:
        """An empty diff reports (no changes detected)."""
        output = format_diff(_diff())
        assert "Changed:" in output
        assert "(no changes detected)" in output

    def test_empty_diff_shows_affected_rules_zero(self) -> None:
        """Affected rules is 0 for an empty diff."""
        output = format_diff(_diff())
        assert "Affected rules:" in output
        assert "  0" in output

    def test_empty_diff_omits_scenarios_when_not_run(self) -> None:
        """Affected scenarios and regression tests are omitted when not run."""
        output = format_diff(_diff())
        assert "Affected scenarios:" not in output
        assert "Regression tests:" not in output

    def test_verification_status_shown(self) -> None:
        """Verification status is always shown."""
        output = format_diff(_diff(verification_status="verified"))
        assert "Verification:" in output
        assert "verified" in output


class TestFormatDiffWithChanges:
    """format_diff with one or more changes."""

    def test_single_change_label_and_values(self) -> None:
        """Label and from/to values are shown for a salary change."""
        c = _change(label="Level C2 - base salary")
        output = format_diff(_diff(changes=(c,)))
        assert "Level C2 - base salary" in output
        assert "€1,850.00" in output
        assert "€1,920.00" in output
        assert "->" in output

    def test_effective_date_shown(self) -> None:
        """Effective date is listed under 'Effective:'."""
        c = _change(effective_date="2026-11-01")
        output = format_diff(_diff(changes=(c,)))
        assert "Effective:" in output
        assert "2026-11-01" in output

    def test_affected_rules_count(self) -> None:
        """Affected rules count equals number of changes."""
        changes = (_change(), _change(label="Parameter - hourly divisor"))
        output = format_diff(_diff(changes=changes))
        assert "Affected rules:" in output
        assert "  2" in output

    def test_multiple_effective_dates_deduplicated(self) -> None:
        """When all changes share an effective date, it appears once."""
        changes = (
            _change(effective_date="2026-11-01"),
            _change(label="Level C3 - base salary", effective_date="2026-11-01"),
        )
        output = format_diff(_diff(changes=changes))
        assert output.count("2026-11-01") == 1

    def test_two_distinct_effective_dates_both_shown(self) -> None:
        """Two different effective dates are both listed under Effective:."""
        changes = (
            _change(effective_date="2026-07-01"),
            _change(label="Level C3 - base salary", effective_date="2026-11-01"),
        )
        output = format_diff(_diff(changes=changes))
        assert "2026-07-01" in output
        assert "2026-11-01" in output

    def test_new_rule_shows_new_label(self) -> None:
        """from_value=None renders as '(new)' in the output."""
        c = RuleChange(
            path="levels[C2].base_salary",
            label="Level C2 - base salary",
            unit="EUR/month",
            from_value=None,
            to_value=Decimal("1920.00"),
            effective_date=date(2026, 11, 1),
            provenance=None,
        )
        output = format_diff(_diff(changes=(c,)))
        assert "(new)" in output
        assert "€1,920.00" in output

    def test_removed_rule_shows_removed_label(self) -> None:
        """to_value=None renders as '(removed)' in the output."""
        c = RuleChange(
            path="levels[C2].base_salary",
            label="Level C2 - base salary",
            unit="EUR/month",
            from_value=Decimal("1850.00"),
            to_value=None,
            effective_date=date(2026, 11, 1),
            provenance=None,
        )
        output = format_diff(_diff(changes=(c,)))
        assert "(removed)" in output


class TestFormatDiffWithScenarios:
    """format_diff shows scenario impact when computed."""

    def test_scenarios_shown_when_nonzero(self) -> None:
        """Affected scenarios section appears when count > 0."""
        d = _diff(
            changes=(_change(),),
            affected_scenarios=27,
            regression_status="passed",
        )
        output = format_diff(d)
        assert "Affected scenarios:" in output
        assert "  27" in output
        assert "Regression tests:" in output
        assert "passed" in output

    def test_scenarios_shown_when_status_is_not_not_run(self) -> None:
        """Even 0 scenarios is shown if regression_status != 'not_run'."""
        d = _diff(
            changes=(_change(),),
            affected_scenarios=0,
            regression_status="passed",
        )
        output = format_diff(d)
        assert "Affected scenarios:" in output
        assert "  0" in output

    def test_scenarios_omitted_when_both_zero_and_not_run(self) -> None:
        """Sections omitted when affected_scenarios=0 and status='not_run'."""
        d = _diff(changes=(_change(),))
        output = format_diff(d)
        assert "Affected scenarios:" not in output
        assert "Regression tests:" not in output


class TestFormatDiffPercentageUnit:
    """format_diff formats % values distinctly from EUR values."""

    def test_percentage_value_format(self) -> None:
        """Percentage values are not prefixed with €."""
        c = RuleChange(
            path="parameters.employer_funds[FNCS].rate",
            label="Employer fund FNCS - rate",
            unit="%",
            from_value=Decimal("0.0050"),
            to_value=Decimal("0.0060"),
            effective_date=date(2026, 1, 1),
            provenance=None,
        )
        output = format_diff(_diff(changes=(c,)))
        assert "€" not in output.split("Changed:")[1].split("Effective:")[0]
        assert "0.0050" in output
        assert "0.0060" in output

    def test_other_unit_format(self) -> None:
        """Non-EUR/non-% units render as '<value> <unit>'."""
        c = RuleChange(
            path="parameters.hourly_divisor",
            label="Parameter - hourly divisor",
            unit="hours",
            from_value=Decimal(168),
            to_value=Decimal(173),
            effective_date=date(2026, 1, 1),
            provenance=None,
        )
        output = format_diff(_diff(changes=(c,)))
        assert "168 hours" in output
        assert "173 hours" in output
