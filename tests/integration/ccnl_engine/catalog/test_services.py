"""Catalog use cases: list the contracts of a repository and inspect a ruleset."""

from __future__ import annotations

import pytest

from ccnl_engine.agreement.metadata.review.models import ReviewIndependence
from ccnl_engine.catalog.models import ccnl_axes
from ccnl_engine.catalog.services import (
    inspect_ruleset,
    list_contracts,
    list_levels,
)
from ccnl_engine.errors import DataIntegrityError, UnknownCcnlError
from ccnl_engine.period.repositories import (
    BundledKnowledgeRepository,
)
from ccnl_engine.provenance.ruleset.assurance.models import (
    AssuranceAxes,
    RulesetKind,
)
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


def test_the_axes_keep_each_kind_of_evidence_apart() -> None:
    """Metalmeccanico is source-checked and externally compared, not signed.

    A reviewed CCNL without a verified case (Chimica) is source-checked only; no CCNL
    of the bundle has a human sign-off, every review is an AI review.
    """
    repo = BundledKnowledgeRepository()

    assert inspect_ruleset(repo, _METALMECCANICO).axes == AssuranceAxes(
        source_checked=True, externally_compared=True, human_signed_off=False
    )
    chimica = inspect_ruleset(repo, "chimica-farmaceutica-federchimica")
    assert chimica.axes == AssuranceAxes(
        source_checked=True, externally_compared=False, human_signed_off=False
    )
    assert not any(
        inspect_ruleset(repo, s.ccnl_id).axes.human_signed_off  # type: ignore[union-attr]
        for s in list_contracts(repo)
    )


def test_a_human_review_independent_of_the_extraction_signs_off() -> None:
    """Only ``independence`` ``human`` sets the sign-off, not the reviewer kind."""
    ccnl = BundledKnowledgeRepository().load_ccnl(_METALMECCANICO)
    last = ccnl.verification.reviews[-1]
    signed = last.model_copy(update={"independence": ReviewIndependence.HUMAN})
    verification = ccnl.verification.model_copy(
        update={"reviews": (*ccnl.verification.reviews[:-1], signed)}
    )

    assert not ccnl_axes(ccnl).human_signed_off
    assert ccnl_axes(
        ccnl.model_copy(update={"verification": verification})
    ).human_signed_off


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
