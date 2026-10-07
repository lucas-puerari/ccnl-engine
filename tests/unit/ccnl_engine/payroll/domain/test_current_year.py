"""CurrentYearTaxFacts: the income of the tax year beyond this employment."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.current_year import (
    CurrentYearTaxFacts,
    IncomeEstimateQuality,
)
from ccnl_engine.shared.domain.errors import InvalidInputError

_DAY = date(2026, 3, 1)


def _facts(**overrides: object) -> CurrentYearTaxFacts:
    fields: dict[str, object] = {
        "tax_year": 2026,
        "other_employment_income": Decimal(5000),
        "other_employment_inps_base": Decimal(5500),
        "other_income": Decimal(1500),
        "main_dwelling_income": Decimal(500),
        "estimated_on": _DAY,
        "quality": IncomeEstimateQuality.DECLARED,
    }
    fields.update(overrides)
    return CurrentYearTaxFacts(**fields)  # type: ignore[arg-type]


def test_external_income_excludes_the_main_dwelling() -> None:
    """5,000 + 1,500 - 500 (art. 12 c. 4-bis)."""
    assert _facts().external_income == Decimal(6000)


def test_employment_only_states_zero_other_income() -> None:
    """Declaring no other income is an explicit fact, not a default."""
    facts = CurrentYearTaxFacts.employment_only(2026, _DAY)
    assert facts.external_income == Decimal(0)
    assert facts.other_employment_inps_base == Decimal(0)
    assert facts.quality is IncomeEstimateQuality.DECLARED
    assert facts.tax_year == 2026


def test_quality_string_is_normalized() -> None:
    """The string value of a quality is accepted."""
    assert _facts(quality="estimated").quality is IncomeEstimateQuality.ESTIMATED


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("other_employment_income", Decimal(-1)),
        ("other_employment_inps_base", Decimal(-1)),
        ("other_employment_inps_base", None),
        ("other_income", Decimal("-0.01")),
        ("main_dwelling_income", Decimal(-1)),
        ("other_income", None),
        ("estimated_on", None),
        ("tax_year", 26),
        ("quality", "guessed"),
    ],
)
def test_invalid_field_raises(field: str, value: object) -> None:
    """Every amount is required and non-negative; the year has four digits."""
    with pytest.raises(InvalidInputError) as caught:
        _facts(**{field: value})
    assert caught.value.field == f"CurrentYearTaxFacts.{field}"


def test_main_dwelling_above_other_income_raises() -> None:
    """The excluded main dwelling income is part of the other income."""
    with pytest.raises(InvalidInputError) as caught:
        _facts(other_income=Decimal(100), main_dwelling_income=Decimal("100.01"))
    assert caught.value.field == "CurrentYearTaxFacts.main_dwelling_income"
