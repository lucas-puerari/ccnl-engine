"""Unit tests for CalendarOverride validation against the standard calendar."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.calendar import (
    ExtraMonthKind,
    ExtraMonthSchedule,
    WorkCalendar,
)
from ccnl_engine.payroll.domain.calendar_override import (
    CalendarOverride,
    CalendarOverrideReason,
)

_YEAR = 2026
_PAYMENT_MONTH = CalendarOverrideReason.PAYMENT_MONTH
_MORE_FAVOURABLE = CalendarOverrideReason.MORE_FAVOURABLE_TREATMENT


def _override(
    calendar: WorkCalendar, reason: CalendarOverrideReason
) -> CalendarOverride:
    return CalendarOverride(calendar=calendar, reason=reason, note="test")


def _months(value: str, **payment_months: int) -> WorkCalendar:
    return WorkCalendar.from_additional_months(_YEAR, Decimal(value), **payment_months)


class TestConstruction:
    """The override carries a calendar, a known reason and a note."""

    def test_reason_values_are_stable(self) -> None:
        """Reasons serialize to their snake_case value."""
        assert _PAYMENT_MONTH == "payment_month"
        assert _MORE_FAVOURABLE == "more_favourable_treatment"

    def test_calendar_must_be_a_work_calendar(self) -> None:
        """A non-calendar value is rejected."""
        with pytest.raises(InvalidInputError, match="WorkCalendar"):
            CalendarOverride(
                calendar=14,  # type: ignore[arg-type]
                reason=_PAYMENT_MONTH,
                note="test",
            )

    def test_reason_must_be_an_override_reason(self) -> None:
        """A plain string is not a reason."""
        with pytest.raises(InvalidInputError, match="CalendarOverrideReason"):
            CalendarOverride(
                calendar=_months("13"),
                reason="payment_month",  # type: ignore[arg-type]
                note="test",
            )

    @pytest.mark.parametrize("note", ["", "   ", None])
    def test_note_must_not_be_blank(self, note: str | None) -> None:
        """The justification is mandatory."""
        with pytest.raises(InvalidInputError, match="note"):
            CalendarOverride(
                calendar=_months("13"),
                reason=_PAYMENT_MONTH,
                note=note,  # type: ignore[arg-type]
            )


class TestResolve:
    """resolve() accepts only overrides that keep the CCNL entitlement."""

    def test_year_mismatch_is_rejected(self) -> None:
        """The override must be for the payroll year."""
        override = _override(
            WorkCalendar.from_additional_months(2025, 13), _PAYMENT_MONTH
        )
        with pytest.raises(InvalidInputError, match="year 2025"):
            override.resolve(_months("13"))

    def test_payment_month_moves_the_quattordicesima(self) -> None:
        """Same entitlement paid in July is returned as the effective calendar."""
        july = _months("14", fourteenth_payment_month=7)
        assert _override(july, _PAYMENT_MONTH).resolve(_months("14")) is july

    @pytest.mark.parametrize(
        ("kind", "payment_month", "window_start"),
        [
            (ExtraMonthKind.FOURTEENTH, 7, 7),
            (ExtraMonthKind.FOURTEENTH, 6, 1),
            (ExtraMonthKind.THIRTEENTH, 11, 1),
        ],
    )
    def test_window_not_ending_at_payment_is_rejected(
        self, kind: ExtraMonthKind, payment_month: int, window_start: int
    ) -> None:
        """A window that does not end in the payment month pays less."""
        moved = ExtraMonthSchedule(
            kind,
            kind.value,
            payment_month=payment_month,
            accrual_window_start_month=window_start,
        )
        others = tuple(s for s in _months("14").extra_months if s.kind is not kind)
        calendar = WorkCalendar(year=_YEAR, extra_months=(*others, moved))
        override = _override(calendar, _PAYMENT_MONTH)
        with pytest.raises(InvalidInputError, match="must accrue over the 12 months"):
            override.resolve(_months("14"))

    @pytest.mark.parametrize("reason", list(CalendarOverrideReason))
    def test_dropping_an_extra_month_is_rejected(
        self, reason: CalendarOverrideReason
    ) -> None:
        """No reason may remove the quattordicesima the CCNL grants."""
        override = _override(_months("13"), reason)
        with pytest.raises(InvalidInputError, match="drops or lowers the fourteenth"):
            override.resolve(_months("14"))

    @pytest.mark.parametrize("reason", list(CalendarOverrideReason))
    def test_lowering_a_fraction_is_rejected(
        self, reason: CalendarOverrideReason
    ) -> None:
        """Half a quattordicesima is less than the full one the CCNL grants."""
        override = _override(_months("13.5"), reason)
        with pytest.raises(InvalidInputError, match="fraction 1"):
            override.resolve(_months("14"))

    def test_payment_month_cannot_add_an_extra_month(self) -> None:
        """Granting more needs the more-favourable reason."""
        override = _override(_months("14"), _PAYMENT_MONTH)
        with pytest.raises(InvalidInputError, match="more_favourable_treatment"):
            override.resolve(_months("13"))

    def test_more_favourable_adds_an_extra_month(self) -> None:
        """A company agreement may grant a quattordicesima."""
        fourteen = _months("14")
        assert _override(fourteen, _MORE_FAVOURABLE).resolve(_months("13")) is fourteen

    def test_more_favourable_raises_a_fraction(self) -> None:
        """A full quattordicesima is more than the half the CCNL grants."""
        fourteen = _months("14")
        assert (
            _override(fourteen, _MORE_FAVOURABLE).resolve(_months("13.5")) is fourteen
        )

    def test_more_favourable_must_grant_more(self) -> None:
        """An override equal to the CCNL entitlement is not more favourable."""
        override = _override(_months("13"), _MORE_FAVOURABLE)
        with pytest.raises(InvalidInputError, match="payment_month"):
            override.resolve(_months("13"))
