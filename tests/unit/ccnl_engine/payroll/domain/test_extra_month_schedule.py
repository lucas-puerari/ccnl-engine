"""Unit tests for ExtraMonthSchedule fields and validation."""

from __future__ import annotations

import pytest

from ccnl_engine.payroll.domain.extra_month_schedule import (
    ExtraMonthKind,
    ExtraMonthSchedule,
)
from ccnl_engine.shared.domain.errors import InvalidInputError


class TestExtraMonthSchedule:
    """ExtraMonthSchedule stores name and payment month."""

    def test_stored_fields(self) -> None:
        """Name and payment_month are stored and retrievable."""
        s = ExtraMonthSchedule(
            kind=ExtraMonthKind.THIRTEENTH,
            name="tredicesima",
            payment_month=12,
        )
        assert s.name == "tredicesima"
        assert s.payment_month == 12

    def test_frozen(self) -> None:
        """ExtraMonthSchedule is immutable."""
        s = ExtraMonthSchedule(
            kind=ExtraMonthKind.THIRTEENTH,
            name="tredicesima",
            payment_month=12,
        )
        with pytest.raises(AttributeError):
            s.payment_month = 6  # type: ignore[misc]


class TestExtraMonthScheduleValidation:
    """ExtraMonthSchedule rejects invalid payment months."""

    def test_payment_month_zero_raises(self) -> None:
        """payment_month=0 raises ValueError."""
        with pytest.raises(InvalidInputError, match=">= 1 and <= 12"):
            ExtraMonthSchedule(
                kind=ExtraMonthKind.THIRTEENTH,
                name="tredicesima",
                payment_month=0,
            )

    def test_payment_month_13_raises(self) -> None:
        """payment_month=13 raises ValueError."""
        with pytest.raises(InvalidInputError, match=">= 1 and <= 12"):
            ExtraMonthSchedule(
                kind=ExtraMonthKind.THIRTEENTH,
                name="tredicesima",
                payment_month=13,
            )

    def test_payment_month_12_valid(self) -> None:
        """payment_month=12 is accepted."""
        s = ExtraMonthSchedule(
            kind=ExtraMonthKind.THIRTEENTH,
            name="tredicesima",
            payment_month=12,
        )
        assert s.payment_month == 12

    def test_kind_must_be_an_extra_month_kind(self) -> None:
        """The kind selects the run; its string value is not accepted."""
        with pytest.raises(InvalidInputError, match="an ExtraMonthKind") as raised:
            ExtraMonthSchedule(
                kind="thirteenth",  # type: ignore[arg-type]
                name="tredicesima",
                payment_month=12,
            )
        assert raised.value.field == "ExtraMonthSchedule.kind"

    def test_empty_name_raises(self) -> None:
        """Empty name raises ValueError."""
        with pytest.raises(InvalidInputError, match="non-blank"):
            ExtraMonthSchedule(
                kind=ExtraMonthKind.THIRTEENTH, name="", payment_month=12
            )
