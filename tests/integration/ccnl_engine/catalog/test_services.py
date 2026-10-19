"""Catalog use cases: list the contracts of a repository and inspect a ruleset."""

from __future__ import annotations

import pytest

from ccnl_engine.catalog.services import (
    inspect_ruleset,
    list_contracts,
    list_levels,
)
from ccnl_engine.errors import DataIntegrityError, UnknownCcnlError
from ccnl_engine.period.repositories import (
    BundledKnowledgeRepository,
)
from ccnl_engine.provenance.ruleset.assurance.models import RulesetKind
from tests.integration.ccnl_engine.catalog.builders import (
    AnonymousCcnlRepository,
)

_METALMECCANICO = "metalmeccanico-federmeccanica"


def test_every_listed_contract_can_be_inspected() -> None:
    """Listing and inspection agree on the tier of every contract."""
    repo = BundledKnowledgeRepository()
    for summary in list_contracts(repo):
        ruleset = inspect_ruleset(repo, summary.ccnl_id)
        assert ruleset.kind is RulesetKind.CCNL
        assert ruleset.readiness is summary.readiness


def test_slug_and_cnel_code_name_the_same_ruleset() -> None:
    """A CCNL is found by slug or by CNEL code."""
    repo = BundledKnowledgeRepository()
    by_slug = inspect_ruleset(repo, _METALMECCANICO)

    assert by_slug.id == f"ccnl/{_METALMECCANICO}"
    assert inspect_ruleset(repo, "C011") == by_slug


def test_a_filename_names_no_ccnl() -> None:
    """A slug with ``.json`` is a filename, not a CCNL id."""
    with pytest.raises(UnknownCcnlError):
        inspect_ruleset(BundledKnowledgeRepository(), f"{_METALMECCANICO}.json")


def test_levels_are_listed_in_the_order_of_the_data() -> None:
    """Every level of the CCNL, each code as ``Employment`` takes it."""
    repo = BundledKnowledgeRepository()
    levels = list_levels(repo, _METALMECCANICO)

    assert levels == list_levels(repo, "C011")
    assert len({level.code for level in levels}) == len(levels)
    assert "C3" in {level.code for level in levels}


def test_unknown_ccnl_is_a_typed_error() -> None:
    """An unknown id raises the public discovery error."""
    with pytest.raises(UnknownCcnlError):
        inspect_ruleset(BundledKnowledgeRepository(), "no-such-ccnl")


def test_a_ccnl_without_identity_is_a_data_integrity_error() -> None:
    """A ruleset nothing identifies cannot be inspected."""
    with pytest.raises(DataIntegrityError, match="no ruleset identity"):
        inspect_ruleset(AnonymousCcnlRepository(), _METALMECCANICO)
