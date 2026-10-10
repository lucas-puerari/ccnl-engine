"""Foreign tax paid, one entry per State (art. 165 c. 3 TUIR)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.prior_year import ForeignTaxPaid, PriorYearTaxFacts


def _paid(
    country: str = "FR", income: str = "1000", tax: str = "100"
) -> ForeignTaxPaid:
    return ForeignTaxPaid(country, Decimal(income), Decimal(tax))


@pytest.mark.parametrize("country", ["IT", "fr", "FRA", "", 33])
def test_country_is_a_foreign_iso_code(country: object) -> None:
    """An ISO 3166-1 alpha-2 code of a State other than Italy."""
    with pytest.raises(InvalidInputError, match="country"):
        ForeignTaxPaid(country, Decimal(1), Decimal(0))  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("income", "tax", "field"),
    [
        (Decimal(0), Decimal(0), "income"),
        (Decimal(-1), Decimal(0), "income"),
        (Decimal(1), Decimal(-1), "tax"),
        (Decimal(1), Decimal("NaN"), "tax"),
        (1, Decimal(0), "income"),
    ],
)
def test_amounts_are_in_range(income: object, tax: object, field: str) -> None:
    """Positive income, non-negative tax, both finite Decimals."""
    with pytest.raises(InvalidInputError, match=field):
        ForeignTaxPaid("FR", income, tax)  # type: ignore[arg-type]


def test_zero_tax_is_accepted() -> None:
    """Income taxed abroad at zero gives no credit but is valid."""
    assert _paid(tax="0").tax == Decimal(0)


def test_facts_store_a_list_as_a_tuple() -> None:
    """A list of entries is accepted and stored as a tuple."""
    facts = PriorYearTaxFacts(foreign_taxes=[_paid(), _paid("DE")])  # type: ignore[arg-type]
    assert facts.foreign_taxes == (_paid(), _paid("DE"))


def test_facts_reject_two_entries_of_one_state() -> None:
    """The credit is per State: the entries of one State are summed first."""
    with pytest.raises(InvalidInputError, match="same State"):
        PriorYearTaxFacts(foreign_taxes=(_paid(), _paid(tax="5")))


def test_facts_reject_an_entry_of_another_type() -> None:
    """Each entry is a ForeignTaxPaid."""
    with pytest.raises(InvalidInputError, match="ForeignTaxPaid"):
        PriorYearTaxFacts(foreign_taxes=(("FR", 1, 1),))  # type: ignore[arg-type]


def test_facts_reject_a_value_that_is_not_a_sequence() -> None:
    """The entries come as a tuple or a list."""
    with pytest.raises(InvalidInputError, match="foreign_taxes"):
        PriorYearTaxFacts(foreign_taxes=_paid())  # type: ignore[arg-type]
