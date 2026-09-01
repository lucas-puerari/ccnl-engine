"""Tests for employment contract type models."""

import pytest
from pydantic import TypeAdapter, ValidationError

from ccnl_engine.models.employment import Apprentice, Employment, FixedTerm, Permanent

_ta: TypeAdapter[Employment] = TypeAdapter(Employment)


class TestPermanent:
    """Unit tests for the Permanent employment type."""

    def test_valid(self) -> None:
        """Permanent is created correctly from its discriminator."""
        emp = _ta.validate_python({"type": "permanent"})
        assert isinstance(emp, Permanent)

    def test_wrong_discriminator_raises(self) -> None:
        """An unknown type discriminator must raise ValidationError."""
        with pytest.raises(ValidationError):
            _ta.validate_python({"type": "unknown"})


class TestFixedTerm:
    """Unit tests for the FixedTerm employment type."""

    def test_valid(self) -> None:
        """FixedTerm is created correctly from its discriminator."""
        emp = _ta.validate_python({"type": "fixed_term"})
        assert isinstance(emp, FixedTerm)


class TestApprentice:
    """Unit tests for the Apprentice employment type."""

    def test_valid(self) -> None:
        """Apprentice is created with months_elapsed."""
        emp = _ta.validate_python({"type": "apprentice", "months_elapsed": 12})
        assert isinstance(emp, Apprentice)
        assert emp.months_elapsed == 12

    def test_missing_months_elapsed_raises(self) -> None:
        """Missing months_elapsed must raise ValidationError."""
        with pytest.raises(ValidationError):
            _ta.validate_python({"type": "apprentice"})

    def test_negative_months_elapsed_raises(self) -> None:
        """Negative months_elapsed must raise ValidationError (Field ge=0)."""
        with pytest.raises(ValidationError):
            _ta.validate_python({"type": "apprentice", "months_elapsed": -1})
