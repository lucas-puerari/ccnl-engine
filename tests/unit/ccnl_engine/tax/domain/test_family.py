"""Validation of the art. 12 TUIR rule models."""

from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine.tax.domain.family import (
    IncomeIncrease,
    SpouseDeductionRules,
    SpouseIncreaseRules,
)

_D = Decimal


def _band(above: int, up_to: int, amount: int = 10) -> IncomeIncrease:
    return IncomeIncrease(above=_D(above), up_to=_D(up_to), amount=_D(amount))


def _spouse(low: int, flat: int, phase_out: int) -> SpouseDeductionRules:
    return SpouseDeductionRules(
        dependent_income_threshold=_D("2840.51"),
        full_amount=_D(800),
        low_income_reduction=_D(110),
        low_income_limit=_D(low),
        flat_amount=_D(690),
        flat_income_limit=_D(flat),
        phase_out_limit=_D(phase_out),
    )


def test_spouse_limits_must_increase() -> None:
    """15,000 < 40,000 < 80,000; any other order is rejected."""
    assert _spouse(15000, 40000, 80000).flat_income_limit == _D(40000)
    with pytest.raises(ValidationError, match="must increase"):
        _spouse(40000, 15000, 80000)


def test_empty_band_is_rejected() -> None:
    """A band must be above its lower limit and not above a higher one."""
    with pytest.raises(ValidationError, match="empty"):
        _band(29200, 29200)


def test_overlapping_bands_are_rejected() -> None:
    """Two bands cannot cover the same income."""
    with pytest.raises(ValidationError, match="overlap"):
        SpouseIncreaseRules(bands=(_band(29000, 29300), _band(29200, 34700)))


def test_increase_of_the_band_containing_the_income() -> None:
    """Above the lower limit, up to the upper one; zero outside every band."""
    rules = SpouseIncreaseRules(
        bands=(_band(29200, 34700, 20), _band(29000, 29200, 10))
    )
    assert rules.increase(_D(29000)) == _D(0)
    assert rules.increase(_D("29000.01")) == _D(10)
    assert rules.increase(_D(29200)) == _D(10)
    assert rules.increase(_D("29200.01")) == _D(20)
    assert rules.increase(_D("34700.01")) == _D(0)
