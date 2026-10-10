"""A provenance label never outruns the evidence its file records."""

from __future__ import annotations

from typing import Any

import pytest

from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.knowledge.validators import (
    has_citation,
    provenance_label_errors,
    verify_provenance_labels,
)

_CITED: dict[str, Any] = {
    "source_document": {"document_id": "d", "url": "https://example.org/d.pdf"},
    "section": "Art. 1 c. 2",
}
_NO_CITATION = "derived: no citation (http(s) url and section or page)"


def _derived(**extra: object) -> dict[str, Any]:
    return {"status": "derived", "location": _CITED, **extra}


@pytest.mark.parametrize(
    "location",
    [
        None,
        {"section": "Art. 1"},
        {"source_document": "d", "section": "Art. 1"},
        {"source_document": {"url": "unavailable"}, "section": "Art. 1"},
        {"source_document": {"url": "https://example.org"}, "section": ""},
    ],
)
def test_location_without_url_or_clause_is_no_citation(location: object) -> None:
    """A citation needs an http(s) document url and a section or page."""
    assert not has_citation(location)


def test_page_alone_locates_the_clause() -> None:
    """A page stands for the section of a paginated document."""
    location = {"source_document": {"url": "http://example.org"}, "page": "12"}
    assert has_citation(location)


def test_cited_derived_record_in_a_sourced_ruleset_holds() -> None:
    """Weak records are not checked; a cited derived one passes."""
    payload = {
        "ruleset": {"source_type": "official_primary"},
        "block": {"provenance": _derived()},
        "other": {"provenance": {"status": "assumed"}},
        "levels": [{"provenance": {"status": "missing"}}, "text"],
    }
    assert provenance_label_errors(payload) == []
    verify_provenance_labels(payload, "x.json")


def test_every_reason_is_listed_with_its_path() -> None:
    """Estimated ruleset, estimate wording and a missing citation all fail."""
    payload = {
        "ruleset": {"source_type": "estimated"},
        "irpef_brackets_provenance": _derived(note="Values estimated from 2025."),
        "levels": [{"provenance": {"status": "verified", "location": None}}],
    }
    estimated = "its ruleset declares source_type 'estimated'"
    assert provenance_label_errors(payload) == [
        f"irpef_brackets_provenance: derived: {estimated}",
        "irpef_brackets_provenance: derived: its note records an estimate",
        f"levels[0].provenance: verified: {estimated}",
        "levels[0].provenance: verified: no citation (http(s) url and section or page)",
    ]


def test_transformation_wording_counts_as_a_note() -> None:
    """An estimate recorded in the transformation fails like a note."""
    payload = {"block": {"provenance": _derived(transformation="An estimation.")}}
    assert provenance_label_errors(payload) == [
        "block.provenance: derived: its note records an estimate"
    ]


def test_regime_is_checked_on_its_source() -> None:
    """A regime records its status in ``source_status``, its location in ``source``."""
    payload = {
        "rinnovo": {"source_status": "derived", "source": _CITED},
        "notte": {"source_status": "derived", "source": {"section": "c. 10"}},
        "pdr": {"source_status": "assumed"},
    }
    assert provenance_label_errors(payload) == [f"notte: {_NO_CITATION}"]


def test_a_failing_label_does_not_load() -> None:
    """The loaders refuse a file whose label outruns its evidence."""
    payload = {"block": {"provenance": {"status": "derived", "location": None}}}
    with pytest.raises(DataIntegrityError, match=r"in 2026-x\.json: block"):
        verify_provenance_labels(payload, "2026-x.json")
