"""Validation of the individual pay elements of an employment."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import pytest

from ccnl_engine.compensation.individual.inputs import (
    IndividualElement,
    check_individual_elements,
)
from ccnl_engine.employment.inputs import Employment, Permanent
from ccnl_engine.errors import InvalidInputError


def test_defaults_pay_every_month_and_enter_the_tfr() -> None:
    """A plain element: not absorbable, on the extra months, in the TFR."""
    element = IndividualElement("ad_personam", Decimal(50))

    assert (element.absorbable, element.extra_months, element.tfr_relevant) == (
        False,
        True,
        True,
    )


@pytest.mark.parametrize(
    ("fields", "path"),
    [
        ({"code": "Superminimo", "monthly": Decimal(1)}, "IndividualElement.code"),
        ({"code": "s", "monthly": Decimal(0)}, "IndividualElement.monthly"),
        ({"code": "s", "monthly": 10}, "IndividualElement.monthly"),
        (
            {"code": "s", "monthly": Decimal(1), "absorbable": "yes"},
            "IndividualElement.absorbable",
        ),
        (
            {"code": "s", "monthly": Decimal(1), "as_of": datetime(2026, 1, 1)},  # noqa: DTZ001
            "IndividualElement.as_of",
        ),
        (
            {"code": "s", "monthly": Decimal(1), "absorbable": True},
            "IndividualElement.as_of",
        ),
    ],
)
def test_an_invalid_element_is_rejected(fields: dict[str, object], path: str) -> None:
    """Each field is checked, and an absorbable element needs its date."""
    with pytest.raises(InvalidInputError) as raised:
        IndividualElement(**fields)  # type: ignore[arg-type]
    assert raised.value.field == path


def test_the_elements_are_a_sequence_of_elements_with_unique_codes() -> None:
    """A list is stored as a tuple; a duplicate code or a stray value fails."""
    element = IndividualElement("superminimo", Decimal(100))

    assert check_individual_elements([element], "p") == (element,)
    with pytest.raises(InvalidInputError, match="share a code"):
        check_individual_elements((element, element), "p")
    with pytest.raises(InvalidInputError):
        check_individual_elements(element, "p")
    with pytest.raises(InvalidInputError):
        check_individual_elements(("superminimo",), "p")


def test_the_employment_stores_its_elements() -> None:
    """``Employment.individual_elements`` accepts a list and keeps a tuple."""
    element = IndividualElement(
        "superminimo", Decimal(100), absorbable=True, as_of=date(2026, 1, 1)
    )
    employment = Employment(
        ccnl_id="commercio-confcommercio",
        level_code="4",
        contract_type=Permanent(),
        individual_elements=[element],  # type: ignore[arg-type]
    )

    assert employment.individual_elements == (element,)
