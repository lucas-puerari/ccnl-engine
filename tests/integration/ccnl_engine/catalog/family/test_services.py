"""List the contract families and filter the contracts by family."""

from __future__ import annotations

import pytest

from ccnl_engine.catalog import list_families, search_ccnls
from ccnl_engine.catalog.family.services import of_family
from ccnl_engine.catalog.loaders import list_contracts
from ccnl_engine.errors import InvalidInputError

_CONSTRUCTION = {
    "edilizia-ance",
    "edilizia-ance-impiegati",
    "edilizia-artigianato-cna",
    "edilizia-cooperative-ancpl",
    "edilizia-pmi-confapi-aniem",
}


def test_the_families_are_listed_by_id() -> None:
    """``list_families`` returns the catalog, sorted by id."""
    ids = [family.id for family in list_families()]

    assert ids == sorted(ids)
    assert "edilizia" in ids


def test_a_family_filters_the_contracts() -> None:
    """Only the contracts whose main family matches are kept."""
    found = of_family(list_contracts(), "edilizia")

    assert {summary.ccnl_id for summary in found} == _CONSTRUCTION


def test_no_family_keeps_every_contract() -> None:
    """``None`` is no filter."""
    assert of_family(list_contracts(), None) == list_contracts()


def test_an_unknown_family_is_rejected() -> None:
    """A family the catalog does not hold is an input error, never empty."""
    with pytest.raises(InvalidInputError, match="not a contract family") as info:
        of_family(list_contracts(), "edile")

    assert info.value.field == "family"


def test_search_combines_text_and_family() -> None:
    """The search keeps the matches of the family only."""
    found = search_ccnls("artigianato", family="metalmeccanica")

    assert [summary.ccnl_id for summary in found] == ["metalmeccanico-artigianato"]
    assert {s.ccnl_id for s in search_ccnls("", family="edilizia")} == _CONSTRUCTION
