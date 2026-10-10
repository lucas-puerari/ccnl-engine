"""Unit tests for extra-month entitlement and run count."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.calendar import WorkCalendar
from ccnl_engine.payroll.domain.extra_month_entitlement import ExtraMonthEntitlement
from ccnl_engine.payroll.domain.extra_month_schedule import ExtraMonthKind
from ccnl_engine.payroll.domain.schedule import PayrollRunCount, PayrollSchedule

_YEAR = 2026


class TestExtraMonthEntitlement:
    """ExtraMonthEntitlement keeps equivalent months as a validated Decimal."""

    def test_of_preserves_fraction(self) -> None:
        """of() converts through str and keeps the fractional part."""
        assert ExtraMonthEntitlement.of(Decimal("13.5")).value == Decimal("13.5")
        assert ExtraMonthEntitlement.of(14).value == Decimal(14)

    def test_non_decimal_rejected(self) -> None:
        """A float value is rejected instead of being coerced."""
        with pytest.raises(InvalidInputError, match="Decimal"):
            ExtraMonthEntitlement(13.5)  # type: ignore[arg-type]

    @pytest.mark.parametrize("value", [True, 13.5, "13"], ids=repr)
    def test_of_rejects_a_value_that_is_not_a_number(self, value: object) -> None:
        """A bool, a float or a string is not a CCNL months parameter."""
        with pytest.raises(InvalidInputError, match="an int or a Decimal"):
            ExtraMonthEntitlement.of(value)  # type: ignore[arg-type]

    @pytest.mark.parametrize("value", ["11.99", "NaN", "-Infinity"])
    def test_below_twelve_or_not_finite_rejected(self, value: str) -> None:
        """Below 12, or not a finite number, is rejected."""
        with pytest.raises(InvalidInputError, match=">= 12 and <= 14"):
            ExtraMonthEntitlement(Decimal(value))

    def test_above_fourteen_rejected(self) -> None:
        """Above 14 is rejected."""
        with pytest.raises(InvalidInputError, match=">= 12 and <= 14"):
            ExtraMonthEntitlement(Decimal("14.01"))


class TestCalendarEntitlement:
    """WorkCalendar exposes and accepts the entitlement."""

    def test_calendar_entitlement_sums_fractions(self) -> None:
        """Tredicesima plus half quattordicesima gives 13.5."""
        cal = WorkCalendar.from_additional_months(_YEAR, Decimal("13.5"))
        assert cal.entitlement == ExtraMonthEntitlement(Decimal("13.5"))

    def test_from_additional_months_accepts_entitlement(self) -> None:
        """The factory accepts an ExtraMonthEntitlement directly."""
        cal = WorkCalendar.from_additional_months(
            _YEAR, ExtraMonthEntitlement(Decimal(14))
        )
        assert [s.kind for s in cal.extra_months] == [
            ExtraMonthKind.THIRTEENTH,
            ExtraMonthKind.FOURTEENTH,
        ]

    def test_partial_tredicesima_rejected(self) -> None:
        """A value between 12 and 13 is rejected, not silently dropped."""
        with pytest.raises(InvalidInputError, match="partial tredicesima"):
            WorkCalendar.from_additional_months(_YEAR, Decimal("12.5"))


class TestPayrollRunCount:
    """PayrollRunCount is a positive int."""

    @pytest.mark.parametrize("value", [True, Decimal(14)])
    def test_non_int_rejected(self, value: object) -> None:
        """A bool or a Decimal is not a run count."""
        with pytest.raises(TypeError, match="int"):
            PayrollRunCount(value)  # type: ignore[arg-type]

    def test_zero_rejected(self) -> None:
        """At least one run."""
        with pytest.raises(ValueError, match=">= 1"):
            PayrollRunCount(0)

    def test_schedule_run_count(self) -> None:
        """PayrollSchedule reports its number of runs."""
        cal = WorkCalendar.from_additional_months(_YEAR, Decimal("13.5"))
        assert PayrollSchedule.from_calendar(cal).run_count == PayrollRunCount(14)
