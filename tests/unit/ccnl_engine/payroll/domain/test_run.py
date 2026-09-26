"""Unit tests for PayrollRun domain type."""

from __future__ import annotations

import pytest

from ccnl_engine.payroll.domain.run import (
    PayrollRun,
    PayrollRunId,
    RunKind,
    run_identifier,
)


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

    def test_run_id_computed_not_settable(self) -> None:
        """run_id is computed from year/month/run_kind; not a constructor arg."""
        run = PayrollRun(run_kind=RunKind.REGULAR, month=1, year=2026)
        assert run.run_id == "2026-01-regular"

    def test_string_run_kind_is_normalized_to_enum(self) -> None:
        """Passing a plain string run_kind is normalized to a RunKind member."""
        run = PayrollRun(run_kind="thirteenth", month=12, year=2026)  # type: ignore[arg-type]
        assert run.run_kind == RunKind.THIRTEENTH

    def test_invalid_run_kind_raises(self) -> None:
        """An unrecognised run_kind string raises ValueError at construction."""
        with pytest.raises(ValueError, match="run_kind"):
            PayrollRun(run_kind="monthly", month=1, year=2026)  # type: ignore[arg-type]

    def test_frozen(self) -> None:
        """PayrollRun is immutable: attribute assignment raises AttributeError."""
        run = PayrollRun.regular(2026, 1)
        with pytest.raises(AttributeError):
            run.month = 2  # type: ignore[misc]

    def test_month_zero_raises(self) -> None:
        """month=0 raises ValueError."""
        with pytest.raises(ValueError, match="month"):
            PayrollRun(run_kind=RunKind.REGULAR, month=0, year=2026)

    def test_month_thirteen_raises(self) -> None:
        """month=13 raises ValueError."""
        with pytest.raises(ValueError, match="month"):
            PayrollRun(run_kind=RunKind.REGULAR, month=13, year=2026)

    def test_year_too_old_raises(self) -> None:
        """Year < 1970 raises ValueError."""
        with pytest.raises(ValueError, match="year"):
            PayrollRun(run_kind=RunKind.REGULAR, month=1, year=1969)

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


class TestPayrollRunId:
    """Typed run identifier: parse, format and order."""

    def test_round_trips_the_run_id_text(self) -> None:
        """str() of the identifier is the run_id of the run."""
        run = PayrollRun.fourteenth(2026, 6)

        assert run.identifier == PayrollRunId(2026, 6, RunKind.FOURTEENTH)
        assert str(run.identifier) == run.run_id
        assert PayrollRunId.parse(run.run_id) == run.identifier

    @pytest.mark.parametrize(
        ("text", "match"),
        [
            ("2026_01", "must look like"),
            ("2026-13-regular", "month must be 1-12"),
            ("1969-01-regular", "year must be >= 1970"),
            ("2026-01-bonus", "run_kind must be one of"),
        ],
    )
    def test_parse_rejects_a_malformed_id(self, text: str, match: str) -> None:
        """Only the engine's run id text is accepted."""
        with pytest.raises(ValueError, match=match):
            PayrollRunId.parse(text)

    def test_orders_regular_before_extra_months_and_termination(self) -> None:
        """Payment order inside a month."""
        keys = [
            PayrollRunId(2026, 12, kind).order_key
            for kind in (RunKind.REGULAR, RunKind.THIRTEENTH, RunKind.TERMINATION)
        ]

        assert keys == sorted(keys)
        assert PayrollRunId(2026, 11, RunKind.TERMINATION).order_key < keys[0]

    def test_bare_period_closes_its_regular_run(self) -> None:
        """Without a run, a period closes the regular run of its month."""
        assert run_identifier(None, 2026, 3) == PayrollRunId.parse("2026-03-regular")
        run = PayrollRun.thirteenth(2026, 12)
        assert run_identifier(run, 2026, 12) == run.identifier
