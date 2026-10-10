"""Tests for employment contract type models."""

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.employment.inputs import (
    Apprentice,
    FixedTerm,
    Permanent,
)


class TestPermanent:
    """Unit tests for the Permanent employment type."""

    def test_valid(self) -> None:
        """Permanent carries its discriminator."""
        assert Permanent().type == "permanent"

    def test_discriminator_is_not_an_argument(self) -> None:
        """The discriminator is fixed by the class, not passed."""
        with pytest.raises(TypeError):
            Permanent(type="fixed_term")  # type: ignore[call-arg]


class TestFixedTerm:
    """Unit tests for the FixedTerm employment type."""

    def test_valid(self) -> None:
        """FixedTerm carries its discriminator."""
        assert FixedTerm().type == "fixed_term"


class TestApprentice:
    """Unit tests for the Apprentice employment type."""

    def test_valid(self) -> None:
        """Apprentice is created with months_elapsed."""
        emp = Apprentice(months_elapsed=12)
        assert emp.type == "apprentice"
        assert emp.months_elapsed == 12
        assert emp.track is None

    def test_missing_months_elapsed_raises(self) -> None:
        """months_elapsed is required."""
        with pytest.raises(TypeError):
            Apprentice()  # type: ignore[call-arg]

    @pytest.mark.parametrize("months", [-1, True, 1.5, "12"], ids=repr)
    def test_months_elapsed_must_be_a_non_negative_int(self, months: object) -> None:
        """A negative count, a bool, a float or a string is rejected."""
        with pytest.raises(InvalidInputError) as raised:
            Apprentice(months_elapsed=months)  # type: ignore[arg-type]
        assert raised.value.field == "Apprentice.months_elapsed"

    @pytest.mark.parametrize("track", ["", " ", 3], ids=repr)
    def test_track_must_be_a_non_blank_string(self, track: object) -> None:
        """A blank track or one that is not a string is rejected."""
        with pytest.raises(InvalidInputError) as raised:
            Apprentice(months_elapsed=0, track=track)  # type: ignore[arg-type]
        assert raised.value.field == "Apprentice.track"
