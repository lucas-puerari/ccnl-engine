"""Unit tests for Art15Deductions domain model."""

from __future__ import annotations

import dataclasses
from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions

_D = Decimal


class TestArt15DeductionsDefaults:
    """Art15Deductions — default construction."""

    def test_default_mortgage_interest_is_zero(self) -> None:
        """Default instance has zero mortgage_interest."""
        d = Art15Deductions()
        assert d.mortgage_interest == _D("0")

    def test_has_any_onere_false_by_default(self) -> None:
        """has_any_onere is False when mortgage_interest is zero."""
        assert not Art15Deductions().has_any_onere

    def test_has_any_onere_true_when_nonzero(self) -> None:
        """has_any_onere is True when mortgage_interest > 0."""
        d = Art15Deductions(mortgage_interest=_D("1"))
        assert d.has_any_onere


class TestArt15DeductionsValidation:
    """Art15Deductions — input validation."""

    def test_negative_mortgage_interest_raises(self) -> None:
        """Negative mortgage_interest raises ValueError."""
        with pytest.raises(ValueError, match="mortgage_interest must be >= 0"):
            Art15Deductions(mortgage_interest=_D("-0.01"))

    def test_zero_mortgage_interest_is_valid(self) -> None:
        """Zero is a valid mortgage_interest value."""
        d = Art15Deductions(mortgage_interest=_D("0"))
        assert d.mortgage_interest == _D("0")

    def test_positive_mortgage_interest_is_valid(self) -> None:
        """Positive value is accepted."""
        d = Art15Deductions(mortgage_interest=_D("3000"))
        assert d.mortgage_interest == _D("3000")


class TestArt15DeductionsFrozen:
    """Art15Deductions — immutability."""

    def test_is_frozen(self) -> None:
        """Modifying a field raises FrozenInstanceError."""
        d = Art15Deductions(mortgage_interest=_D("1000"))
        with pytest.raises(dataclasses.FrozenInstanceError):
            d.mortgage_interest = _D("2000")  # type: ignore[misc]
