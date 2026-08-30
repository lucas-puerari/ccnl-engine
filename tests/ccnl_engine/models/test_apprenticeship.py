"""Tests for apprenticeship rule models.

Each class targets a specific validator branch to satisfy 100 % branch coverage.
"""

import pytest
from pydantic import TypeAdapter, ValidationError

from ccnl_engine.models.apprenticeship import (
    Apprenticeship,
    ApprenticeshipPercentage,
    ApprenticeshipUnderClassification,
)

_ta: TypeAdapter[Apprenticeship] = TypeAdapter(Apprenticeship)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _pct_period(
    months_from: int,
    months_until: int | None,
    pct: str = "0.80",
) -> dict[str, object]:
    return {"months_from": months_from, "months_until": months_until, "percentage": pct}


def _uc_period(
    months_from: int,
    months_until: int | None,
    pay_level: str = "3",
) -> dict[str, object]:
    return {
        "months_from": months_from,
        "months_until": months_until,
        "pay_level_code": pay_level,
    }


# ---------------------------------------------------------------------------
# ApprenticeshipPeriod bounds validator
# ---------------------------------------------------------------------------


class TestApprenticeshipPeriodBounds:
    """Validate months_until > months_from when months_until is set."""

    def test_open_ended_accepted(self) -> None:
        """months_until=None is always accepted."""
        data = {
            "type": "percentage",
            "destination_level": "4",
            "periods": [_pct_period(0, None)],
        }
        emp = _ta.validate_python(data)
        assert isinstance(emp, ApprenticeshipPercentage)

    def test_months_until_equal_raises(self) -> None:
        """months_until == months_from must raise ValidationError."""
        data = {
            "type": "percentage",
            "destination_level": "4",
            "periods": [_pct_period(0, 0)],
        }
        with pytest.raises(ValidationError):
            _ta.validate_python(data)

    def test_months_until_less_raises(self) -> None:
        """months_until < months_from must raise ValidationError."""
        data = {
            "type": "percentage",
            "destination_level": "4",
            "periods": [_pct_period(12, 6)],
        }
        with pytest.raises(ValidationError):
            _ta.validate_python(data)


# ---------------------------------------------------------------------------
# ApprenticeshipPercentage validators
# ---------------------------------------------------------------------------


class TestApprenticeshipPercentage:
    """Unit tests for ApprenticeshipPercentage validators."""

    def test_empty_periods_raises(self) -> None:
        """Empty periods list must raise ValidationError."""
        data = {"type": "percentage", "destination_level": "4", "periods": []}
        with pytest.raises(ValidationError):
            _ta.validate_python(data)

    def test_non_last_open_ended_raises(self) -> None:
        """Non-last period with months_until=None must raise ValidationError."""
        data = {
            "type": "percentage",
            "destination_level": "4",
            "periods": [_pct_period(0, None), _pct_period(12, None)],
        }
        with pytest.raises(ValidationError):
            _ta.validate_python(data)

    def test_gap_raises(self) -> None:
        """A gap between consecutive periods must raise ValidationError."""
        data = {
            "type": "percentage",
            "destination_level": "4",
            "periods": [_pct_period(0, 12), _pct_period(24, None)],  # gap 12-24
        }
        with pytest.raises(ValidationError):
            _ta.validate_python(data)

    def test_closed_last_period_raises(self) -> None:
        """Last period with months_until not None must raise ValidationError."""
        data = {
            "type": "percentage",
            "destination_level": "4",
            "periods": [_pct_period(0, 36)],
        }
        with pytest.raises(ValidationError):
            _ta.validate_python(data)

    def test_single_period_valid(self) -> None:
        """A single open-ended period is valid."""
        data = {
            "type": "percentage",
            "destination_level": "4",
            "periods": [_pct_period(0, None)],
        }
        emp = _ta.validate_python(data)
        assert isinstance(emp, ApprenticeshipPercentage)

    def test_two_contiguous_periods_valid(self) -> None:
        """Two contiguous periods with an open-ended last are valid."""
        data = {
            "type": "percentage",
            "destination_level": "4",
            "periods": [_pct_period(0, 18, "0.80"), _pct_period(18, None, "0.90")],
        }
        emp = _ta.validate_python(data)
        assert isinstance(emp, ApprenticeshipPercentage)
        assert len(emp.periods) == 2


# ---------------------------------------------------------------------------
# ApprenticeshipUnderClassification validators
# ---------------------------------------------------------------------------


class TestApprenticeshipUnderClassification:
    """Unit tests for ApprenticeshipUnderClassification validators."""

    def test_empty_periods_raises(self) -> None:
        """Empty periods list must raise ValidationError."""
        data = {
            "type": "under_classification",
            "destination_level": "4",
            "periods": [],
        }
        with pytest.raises(ValidationError):
            _ta.validate_python(data)

    def test_non_last_open_ended_raises(self) -> None:
        """Non-last period with months_until=None must raise ValidationError."""
        data = {
            "type": "under_classification",
            "destination_level": "4",
            "periods": [_uc_period(0, None, "5"), _uc_period(18, None, "4")],
        }
        with pytest.raises(ValidationError):
            _ta.validate_python(data)

    def test_gap_raises(self) -> None:
        """A gap between consecutive periods must raise ValidationError."""
        data = {
            "type": "under_classification",
            "destination_level": "4",
            "periods": [_uc_period(0, 12, "5"), _uc_period(24, None, "4")],
        }
        with pytest.raises(ValidationError):
            _ta.validate_python(data)

    def test_closed_last_period_raises(self) -> None:
        """Last period with months_until not None must raise ValidationError."""
        data = {
            "type": "under_classification",
            "destination_level": "4",
            "periods": [_uc_period(0, 36, "5")],
        }
        with pytest.raises(ValidationError):
            _ta.validate_python(data)

    def test_single_period_valid(self) -> None:
        """A single open-ended period is valid."""
        data = {
            "type": "under_classification",
            "destination_level": "4",
            "periods": [_uc_period(0, None, "5")],
        }
        emp = _ta.validate_python(data)
        assert isinstance(emp, ApprenticeshipUnderClassification)

    def test_two_contiguous_periods_valid(self) -> None:
        """Two contiguous periods with an open-ended last are valid."""
        data = {
            "type": "under_classification",
            "destination_level": "4",
            "periods": [_uc_period(0, 18, "5"), _uc_period(18, None, "4")],
        }
        emp = _ta.validate_python(data)
        assert isinstance(emp, ApprenticeshipUnderClassification)
        assert len(emp.periods) == 2

    def test_uc_period_bounds_raises(self) -> None:
        """months_until <= months_from must raise for UnderClassificationPeriod."""
        data = {
            "type": "under_classification",
            "destination_level": "4",
            "periods": [_uc_period(12, 6, "5")],
        }
        with pytest.raises(ValidationError):
            _ta.validate_python(data)
