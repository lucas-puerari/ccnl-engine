"""Provenance status of a rule record and the checks that tie it to its data."""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from ccnl_engine.provenance.domain.chain import ProvenanceStatus, RuleProvenance
from ccnl_engine.provenance.domain.extraction import ExtractionMethod, ExtractionTrace
from ccnl_engine.provenance.domain.source import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)

_LOCATION = SourceLocation(
    source_document=SourceDocument(
        document_id="l-199-2025", title="L. 199/2025", kind=SourceKind.LEGGE
    ),
    section="art. 1 c. 2",
)


def _extraction(*, reviewed: bool) -> ExtractionTrace:
    return ExtractionTrace(
        method=ExtractionMethod.MANUAL,
        extraction_timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        effective_from=date(2026, 1, 1),
        verified_by="reviewer" if reviewed else None,
        verified_at=datetime(2026, 2, 1, tzinfo=UTC) if reviewed else None,
    )


class TestProvenanceStatus:
    """Statuses rank from the strongest to the weakest backing."""

    def test_rank_orders_statuses(self) -> None:
        """Verified is the strongest, missing the weakest."""
        ranks = [status.rank for status in ProvenanceStatus]
        assert ranks == [0, 1, 2, 3]

    def test_weakest_picks_the_highest_rank(self) -> None:
        """Combining derived and assumed gives assumed."""
        statuses = (ProvenanceStatus.DERIVED, ProvenanceStatus.ASSUMED)
        assert ProvenanceStatus.weakest(statuses) is ProvenanceStatus.ASSUMED


class TestRuleProvenance:
    """A record's status must agree with what it cites and who checked it."""

    def test_derived_with_location_is_accepted(self) -> None:
        """A derived record cites a location and needs no extraction."""
        record = RuleProvenance(status=ProvenanceStatus.DERIVED, location=_LOCATION)
        assert record.extraction is None
        assert record.transformation is None

    def test_assumed_without_location_is_accepted(self) -> None:
        """An assumed value may have no located clause."""
        record = RuleProvenance(status=ProvenanceStatus.ASSUMED, note="clause unknown")
        assert record.location is None

    def test_missing_without_location_is_accepted(self) -> None:
        """A missing record cites nothing."""
        record = RuleProvenance.model_validate({"status": "missing"})
        assert record.status is ProvenanceStatus.MISSING

    def test_verified_with_reviewer_is_accepted(self) -> None:
        """A verified record names the reviewer and the date."""
        record = RuleProvenance(
            status=ProvenanceStatus.VERIFIED,
            location=_LOCATION,
            extraction=_extraction(reviewed=True),
            transformation="percentages stored as fractions",
        )
        assert record.transformation == "percentages stored as fractions"

    @pytest.mark.parametrize("status", ["verified", "derived"])
    def test_located_status_requires_location(self, status: str) -> None:
        """Verified and derived values must point into a document."""
        with pytest.raises(ValidationError, match="requires a source location"):
            RuleProvenance(
                status=ProvenanceStatus(status), extraction=_extraction(reviewed=True)
            )

    def test_missing_cannot_cite_a_location(self) -> None:
        """A value with a cited location is not missing."""
        with pytest.raises(ValidationError, match="cannot cite a source location"):
            RuleProvenance(status=ProvenanceStatus.MISSING, location=_LOCATION)

    @pytest.mark.parametrize("reviewed", [False, None])
    def test_verified_requires_reviewer(self, *, reviewed: bool | None) -> None:
        """Nothing is verified without a named reviewer and a date."""
        extraction = None if reviewed is None else _extraction(reviewed=reviewed)
        with pytest.raises(ValidationError, match="verified_by and verified_at"):
            RuleProvenance(
                status=ProvenanceStatus.VERIFIED,
                location=_LOCATION,
                extraction=extraction,
            )

    def test_status_is_required(self) -> None:
        """A record without a status is rejected."""
        with pytest.raises(ValidationError, match="status"):
            RuleProvenance.model_validate({"location": None})
