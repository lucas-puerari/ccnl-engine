"""A second-level element validates its fields when it is built."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.compensation.second_level.inputs import (
    SecondLevelAgreement,
    SecondLevelElement,
    check_second_level_elements,
)
from ccnl_engine.errors import InvalidInputError

_DAY = date(2026, 1, 1)


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"monthly": Decimal(0)}, "SecondLevelElement.monthly"),
        ({"agreement": "national"}, "SecondLevelElement.agreement"),
        ({"valid_until": date(2025, 12, 31)}, "SecondLevelElement.valid_until"),
        ({"levels": "4"}, "SecondLevelElement.levels"),
        ({"levels": ("",)}, "SecondLevelElement.levels[0]"),
        ({"extra_months": "yes"}, "SecondLevelElement.extra_months"),
    ],
)
def test_an_invalid_field_is_named(changes: dict[str, object], field: str) -> None:
    """Each invalid value raises InvalidInputError at its field."""
    fields: dict[str, object] = {
        "code": "premio",
        "monthly": Decimal(10),
        "agreement": "company",
        "valid_from": _DAY,
    } | changes
    with pytest.raises(InvalidInputError) as raised:
        SecondLevelElement(**fields)  # type: ignore[arg-type]
    assert raised.value.field == field


def test_the_agreement_is_parsed_and_the_levels_kept_as_a_tuple() -> None:
    """A string agreement becomes the enum; a list of levels a tuple."""
    element = SecondLevelElement(
        "premio",
        Decimal(10),
        "territorial",  # type: ignore[arg-type]
        _DAY,
        levels=["4", "5"],  # type: ignore[arg-type]
    )
    assert element.agreement is SecondLevelAgreement.TERRITORIAL
    assert element.levels == ("4", "5")
    assert element.applies_to("4", _DAY)
    assert not element.applies_to("3", _DAY)
    assert not element.applies_to("4", date(2025, 12, 31))


def test_the_elements_are_a_sequence_of_elements() -> None:
    """Anything but a tuple or a list of elements is rejected."""
    with pytest.raises(InvalidInputError):
        check_second_level_elements("premio", "EmployerProfile.second_level_elements")
    with pytest.raises(InvalidInputError):
        check_second_level_elements(["premio"], "EmployerProfile.second_level_elements")
