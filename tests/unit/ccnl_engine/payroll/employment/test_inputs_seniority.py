"""Unit tests for the recognised seniority fact and its ageing."""

from __future__ import annotations

from datetime import date, datetime

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.employment.inputs_seniority import (
    SeniorityFact,
    SenioritySource,
)

_RECORDS = SenioritySource.EMPLOYER_RECORDS


class TestConstruction:
    """The fact holds a non-negative int, a date and a known source."""

    def test_accepts_zero_months(self) -> None:
        """A worker hired on the date has zero months of service."""
        fact = SeniorityFact(0, date(2026, 6, 1), _RECORDS)
        assert fact.months == 0

    def test_normalizes_a_source_string(self) -> None:
        """The string value of a source is accepted from untyped callers."""
        fact = SeniorityFact(12, date(2026, 6, 1), "payslip")  # type: ignore[arg-type]
        assert fact.source is SenioritySource.PAYSLIP

    @pytest.mark.parametrize(
        ("months", "message"),
        [
            pytest.param(
                -1, r"SeniorityFact\.months must be an int >= 0", id="negative"
            ),
            pytest.param(True, r"SeniorityFact\.months must be an int", id="bool"),
            pytest.param(1.5, r"SeniorityFact\.months must be an int", id="float"),
        ],
    )
    def test_rejects_invalid_months(self, months: object, message: str) -> None:
        """Months are a non-negative int, never coerced."""
        with pytest.raises(InvalidInputError, match=message):
            SeniorityFact(months, date(2026, 6, 1), _RECORDS)  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        "as_of",
        [
            pytest.param("2026-06-01", id="string"),
            pytest.param(datetime(2026, 6, 1, 9, 0), id="datetime"),  # noqa: DTZ001
        ],
    )
    def test_rejects_an_as_of_that_is_not_a_date(self, as_of: object) -> None:
        """The months are counted at a calendar date."""
        with pytest.raises(
            InvalidInputError, match=r"SeniorityFact\.as_of must be a date"
        ):
            SeniorityFact(0, as_of, _RECORDS)  # type: ignore[arg-type]

    def test_rejects_an_unknown_source(self) -> None:
        """The source is one of the known sources."""
        with pytest.raises(
            InvalidInputError, match=r"SeniorityFact\.source must be one"
        ):
            SeniorityFact(0, date(2026, 6, 1), "guess")  # type: ignore[arg-type]

    def test_since_starts_from_zero_months(self) -> None:
        """A recognised start date is zero months on that date."""
        fact = SeniorityFact.since(date(2024, 6, 15), SenioritySource.PAYSLIP)
        assert fact == SeniorityFact(0, date(2024, 6, 15), SenioritySource.PAYSLIP)


class TestMonthsAt:
    """A month is complete on the same day of the following month."""

    @pytest.mark.parametrize(
        ("day", "expected"),
        [
            pytest.param(date(2026, 6, 15), 24, id="anniversary"),
            pytest.param(date(2026, 6, 14), 23, id="day-before-anniversary"),
            pytest.param(date(2026, 6, 1), 23, id="first-of-anniversary-month"),
            pytest.param(date(2026, 7, 1), 24, id="first-of-next-month"),
            pytest.param(date(2024, 6, 15), 0, id="start"),
        ],
    )
    def test_ages_a_start_date(self, day: date, expected: int) -> None:
        """Service from 15 June 2024 completes 24 months on 15 June 2026."""
        fact = SeniorityFact.since(date(2024, 6, 15), _RECORDS)
        assert fact.months_at(day) == expected

    def test_counts_back_to_an_earlier_day(self) -> None:
        """Twelve months on 1 July are eleven on 1 June."""
        fact = SeniorityFact(12, date(2026, 7, 1), _RECORDS)
        assert fact.months_at(date(2026, 6, 1)) == 11

    def test_rejects_a_day_before_the_service(self) -> None:
        """No run can precede the recognised service."""
        fact = SeniorityFact.since(date(2026, 6, 15), _RECORDS)
        with pytest.raises(InvalidInputError, match="starts after 2026-06-01"):
            fact.months_at(date(2026, 6, 1))


class TestMonthsInMonth:
    """A run counts the months completed by the first day of its month."""

    @pytest.mark.parametrize(
        ("year", "month", "expected"),
        [
            pytest.param(2026, 6, 0, id="service-starts-within-the-month"),
            pytest.param(2026, 7, 0, id="first-month-after-the-start"),
            pytest.param(2026, 8, 1, id="one-month-complete"),
        ],
    )
    def test_counts_from_a_mid_month_start(
        self, year: int, month: int, expected: int
    ) -> None:
        """Service from 15 June: the hire month and July count zero months."""
        fact = SeniorityFact.since(date(2026, 6, 15), _RECORDS)
        assert fact.months_in_month(year, month) == expected

    def test_rejects_a_month_before_the_service(self) -> None:
        """Service from 1 July cannot be counted by a June run."""
        fact = SeniorityFact.since(date(2026, 7, 1), _RECORDS)
        with pytest.raises(InvalidInputError, match="starts after 2026-06-30"):
            fact.months_in_month(2026, 6)
