"""Unit tests for the WorkEvent domain types."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    BonusEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    SickLeaveEvent,
    WelfareEvent,
)

_DATE = date(2026, 1, 15)


class TestOvertimeEvent:
    """OvertimeEvent stores hours, rate, multiplier and is frozen."""

    def test_fields(self) -> None:
        """All fields are stored and retrievable."""
        evt = OvertimeEvent(
            event_date=_DATE,
            hours=Decimal(8),
            hourly_rate=Decimal("12.50"),
            multiplier=Decimal("1.25"),
        )
        assert evt.event_date == _DATE
        assert evt.hours == Decimal(8)
        assert evt.hourly_rate == Decimal("12.50")
        assert evt.multiplier == Decimal("1.25")

    def test_default_multiplier(self) -> None:
        """Multiplier defaults to 1.25."""
        evt = OvertimeEvent(event_date=_DATE, hours=Decimal(2), hourly_rate=Decimal(10))
        assert evt.multiplier == Decimal("1.25")

    def test_frozen(self) -> None:
        """OvertimeEvent is immutable."""
        evt = OvertimeEvent(event_date=_DATE, hours=Decimal(2), hourly_rate=Decimal(10))
        with pytest.raises(FrozenInstanceError):
            evt.hours = Decimal(4)  # type: ignore[misc]


class TestNightShiftEvent:
    """NightShiftEvent stores a flat supplement amount and is frozen."""

    def test_fields(self) -> None:
        """All fields are stored and retrievable."""
        evt = NightShiftEvent(event_date=_DATE, supplement_amount=Decimal("50.00"))
        assert evt.event_date == _DATE
        assert evt.supplement_amount == Decimal("50.00")

    def test_frozen(self) -> None:
        """NightShiftEvent is immutable."""
        evt = NightShiftEvent(event_date=_DATE, supplement_amount=Decimal(50))
        with pytest.raises(FrozenInstanceError):
            evt.supplement_amount = Decimal(100)  # type: ignore[misc]


class TestHolidayWorkEvent:
    """HolidayWorkEvent stores a flat supplement amount and is frozen."""

    def test_fields(self) -> None:
        """All fields are stored and retrievable."""
        evt = HolidayWorkEvent(event_date=_DATE, supplement_amount=Decimal("75.00"))
        assert evt.event_date == _DATE
        assert evt.supplement_amount == Decimal("75.00")

    def test_frozen(self) -> None:
        """HolidayWorkEvent is immutable."""
        evt = HolidayWorkEvent(event_date=_DATE, supplement_amount=Decimal(75))
        with pytest.raises(FrozenInstanceError):
            evt.supplement_amount = Decimal(100)  # type: ignore[misc]


class TestAbsenceEvent:
    """AbsenceEvent stores hours and hourly rate and is frozen."""

    def test_fields(self) -> None:
        """All fields are stored and retrievable."""
        evt = AbsenceEvent(
            event_date=_DATE, hours=Decimal(4), hourly_rate=Decimal("13.00")
        )
        assert evt.event_date == _DATE
        assert evt.hours == Decimal(4)
        assert evt.hourly_rate == Decimal("13.00")

    def test_frozen(self) -> None:
        """AbsenceEvent is immutable."""
        evt = AbsenceEvent(event_date=_DATE, hours=Decimal(4), hourly_rate=Decimal(13))
        with pytest.raises(FrozenInstanceError):
            evt.hours = Decimal(8)  # type: ignore[misc]


class TestSickLeaveEvent:
    """SickLeaveEvent stores employer-paid gross amount and is frozen."""

    def test_fields(self) -> None:
        """All fields are stored and retrievable."""
        evt = SickLeaveEvent(event_date=_DATE, amount=Decimal("200.00"))
        assert evt.event_date == _DATE
        assert evt.amount == Decimal("200.00")

    def test_frozen(self) -> None:
        """SickLeaveEvent is immutable."""
        evt = SickLeaveEvent(event_date=_DATE, amount=Decimal(200))
        with pytest.raises(FrozenInstanceError):
            evt.amount = Decimal(300)  # type: ignore[misc]


class TestBonusEvent:
    """BonusEvent stores a one-off gross amount and is frozen."""

    def test_fields(self) -> None:
        """All fields are stored and retrievable."""
        evt = BonusEvent(event_date=_DATE, amount=Decimal("1000.00"))
        assert evt.event_date == _DATE
        assert evt.amount == Decimal("1000.00")

    def test_frozen(self) -> None:
        """BonusEvent is immutable."""
        evt = BonusEvent(event_date=_DATE, amount=Decimal(1000))
        with pytest.raises(FrozenInstanceError):
            evt.amount = Decimal(2000)  # type: ignore[misc]


class TestFringeEvent:
    """FringeEvent stores amount and exempt threshold, and is frozen."""

    def test_fields(self) -> None:
        """All fields are stored and retrievable."""
        evt = FringeEvent(
            event_date=_DATE,
            amount=Decimal("500.00"),
            exempt_threshold=Decimal("258.23"),
        )
        assert evt.event_date == _DATE
        assert evt.amount == Decimal("500.00")
        assert evt.exempt_threshold == Decimal("258.23")

    def test_default_threshold(self) -> None:
        """Exempt threshold defaults to 258.23 (standard TUIR threshold)."""
        evt = FringeEvent(event_date=_DATE, amount=Decimal(100))
        assert evt.exempt_threshold == Decimal("258.23")

    def test_frozen(self) -> None:
        """FringeEvent is immutable."""
        evt = FringeEvent(event_date=_DATE, amount=Decimal(100))
        with pytest.raises(FrozenInstanceError):
            evt.amount = Decimal(200)  # type: ignore[misc]


class TestWelfareEvent:
    """WelfareEvent stores a gross amount and is frozen."""

    def test_fields(self) -> None:
        """All fields are stored and retrievable."""
        evt = WelfareEvent(event_date=_DATE, amount=Decimal("250.00"))
        assert evt.event_date == _DATE
        assert evt.amount == Decimal("250.00")

    def test_frozen(self) -> None:
        """WelfareEvent is immutable."""
        evt = WelfareEvent(event_date=_DATE, amount=Decimal(250))
        with pytest.raises(FrozenInstanceError):
            evt.amount = Decimal(500)  # type: ignore[misc]
