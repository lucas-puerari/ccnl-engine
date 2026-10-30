"""Contract family models: the catalog and the family of one CCNL."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.agreement.family.models import FamilyAssignment, FamilyCatalog


def _family(family_id: str, groups: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": family_id,
        "name": family_id.title(),
        "description": "What the family covers.",
        "criteria": "The activity of the employer.",
        "groups": groups or ["G01"],
    }


def _catalog(*families: dict[str, Any]) -> FamilyCatalog:
    return FamilyCatalog.model_validate({"schema_version": 1, "families": families})


def test_the_catalog_keys_its_families_by_id() -> None:
    """``by_id`` finds each family under its id."""
    catalog = _catalog(_family("commercio"), _family("edilizia", ["G11", "G13"]))

    assert catalog.by_id["edilizia"].groups == ("G11", "G13")
    assert list(catalog.by_id) == ["commercio", "edilizia"]


@pytest.mark.parametrize(
    ("families", "match"),
    [
        ((_family("b"), _family("a")), "sorted and unique"),
        ((_family("a"), _family("a")), "sorted and unique"),
        ((_family("Commercio"),), "lower-case words"),
        ((_family("a", ["G18"]),), "work groups G01-G17"),
        ((_family("a", ["G02", "G01"]),), "sorted and unique"),
        ((), "at least 1"),
    ],
)
def test_a_malformed_catalog_is_rejected(
    families: tuple[dict[str, Any], ...], match: str
) -> None:
    """Ids and groups must be well formed, sorted and unique."""
    with pytest.raises(ValidationError, match=match):
        _catalog(*families)


def test_an_assignment_lists_the_main_family_first() -> None:
    """``ids`` is the main family followed by the related ones."""
    assignment = FamilyAssignment(
        id="tessile-moda", reason="Craft textiles.", related=("chimica",)
    )

    assert assignment.ids == ("tessile-moda", "chimica")


@pytest.mark.parametrize(
    "related",
    [("b", "a"), ("a", "a"), ("main",)],
)
def test_related_families_are_sorted_unique_and_distinct(
    related: tuple[str, ...],
) -> None:
    """The related families never repeat each other or the main family."""
    with pytest.raises(ValidationError, match=r"family\.related"):
        FamilyAssignment(id="main", reason="A reason.", related=related)


def test_an_assignment_needs_a_reason() -> None:
    """An empty reason is rejected: every assignment is motivated."""
    with pytest.raises(ValidationError, match="at least 1 character"):
        FamilyAssignment(id="commercio", reason="")
