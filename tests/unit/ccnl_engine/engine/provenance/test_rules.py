"""Tests for the provenance domain models (source / extraction / chain)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from ccnl_engine.engine.metadata.domain.rules import VerificationStatus
from ccnl_engine.engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.engine.provenance.domain.extraction import (
    BackCalculationStep,
    ExtractionMethod,
    ExtractionTrace,
)
from ccnl_engine.engine.provenance.domain.source import (
    SourceAuthority,
    SourceDocument,
    SourceKind,
    SourceLocation,
)

_TS = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
_DATE = date(2026, 1, 1)

_DOC = SourceDocument(
    document_id="gazzetta-123",
    title="Gazzetta Ufficiale",
    kind=SourceKind.GAZZETTA,
    url="https://www.gazzettaufficiale.it",
    pages=["12-14"],
    published_on=date(2025, 11, 22),
)


class TestSourceDocument:
    """SourceDocument casts source-kind strings to the enum."""

    def test_kind_set(self) -> None:
        """SourceKind is stored as the enum value."""
        assert _DOC.kind == SourceKind.GAZZETTA
        assert _DOC.published_on == date(2025, 11, 22)

    def test_defaults(self) -> None:
        """Optional fields default to safe values."""
        doc = SourceDocument(document_id="d", title="T", kind=SourceKind.ALTRO)
        assert doc.url == "unavailable"
        assert doc.pages == []
        assert doc.jurisdiction == "it"

    @pytest.mark.parametrize(
        ("kind", "expected"),
        [
            (SourceKind.GAZZETTA, SourceAuthority.OFFICIAL),
            (SourceKind.CNEL, SourceAuthority.OFFICIAL),
            (SourceKind.INPS_CIRCOLARE, SourceAuthority.OFFICIAL),
            (SourceKind.LEGGE, SourceAuthority.OFFICIAL),
            (SourceKind.DPR, SourceAuthority.OFFICIAL),
            (SourceKind.DL, SourceAuthority.OFFICIAL),
            (SourceKind.DPR_DECRETO, SourceAuthority.OFFICIAL),
            (SourceKind.ASSOCIAZIONE, SourceAuthority.SECONDARY),
            (SourceKind.TABELLA_RETRIBUTIVA, SourceAuthority.SECONDARY),
            (SourceKind.RIVISTA, SourceAuthority.SECONDARY),
            (SourceKind.ALTRO, SourceAuthority.SECONDARY),
        ],
    )
    def test_authority_derived_from_kind(
        self, kind: SourceKind, expected: SourceAuthority
    ) -> None:
        """Authority is derived from kind without being stored."""
        doc = SourceDocument(document_id="d", title="T", kind=kind)
        assert doc.authority == expected


class TestSourceLocation:
    """SourceLocation nests the document and a page/section pointer."""

    def test_location(self) -> None:
        """Page and section are accessible; source_document is embedded."""
        loc = SourceLocation(source_document=_DOC, page="12", section="Art. 3")
        assert loc.page == "12"
        assert loc.section == "Art. 3"
        assert loc.source_document.document_id == "gazzetta-123"


class TestExtractionTrace:
    """ExtractionTrace validates method/back_calculation consistency."""

    def test_unverified_default(self) -> None:
        """verification_status defaults to UNVERIFIED."""
        trace = ExtractionTrace(
            method=ExtractionMethod.MANUAL,
            extraction_timestamp=_TS,
            effective_from=_DATE,
        )
        assert trace.verification_status is VerificationStatus.UNVERIFIED
        assert trace.verified_by is None
        assert trace.verified_at is None

    def test_verified_fields(self) -> None:
        """Explicit verification_status and timestamps are stored."""
        verified_at = datetime(2026, 1, 2, 0, 0, tzinfo=UTC)
        trace = ExtractionTrace(
            method=ExtractionMethod.MANUAL,
            extraction_timestamp=_TS,
            effective_from=_DATE,
            verified_by="curator@example.com",
            verified_at=verified_at,
            verification_status=VerificationStatus.VERIFIED,
        )
        assert trace.verification_status is VerificationStatus.VERIFIED
        assert trace.verified_by == "curator@example.com"
        assert trace.verified_at == verified_at

    def test_back_calculation_allowed_for_method(self) -> None:
        """back_calculation steps are accepted when method is BACK_CALCULATION."""
        trace = ExtractionTrace(
            method=ExtractionMethod.BACK_CALCULATION,
            extraction_timestamp=_TS,
            effective_from=_DATE,
            back_calculation=[
                BackCalculationStep(
                    description="conglobate seniority",
                    inputs={"floor": "100", "rate": "0.02"},
                    result=Decimal(102),
                )
            ],
        )
        assert trace.back_calculation is not None
        assert trace.back_calculation[0].result == Decimal(102)

    def test_back_calculation_without_method_raises(self) -> None:
        """back_calculation steps are rejected when method is not BACK_CALCULATION."""
        with pytest.raises(ValueError, match="back_calculation"):
            ExtractionTrace(
                method=ExtractionMethod.MANUAL,
                extraction_timestamp=_TS,
                effective_from=_DATE,
                back_calculation=[
                    BackCalculationStep(description="x", inputs={}, result=Decimal(1))
                ],
            )


class TestRuleProvenance:
    """RuleProvenance composes a location and an extraction trace."""

    def test_complete(self) -> None:
        """All fields are accessible on a fully-populated RuleProvenance."""
        prov = RuleProvenance(
            location=SourceLocation(source_document=_DOC, page="12", section="Art. 3"),
            extraction=ExtractionTrace(
                method=ExtractionMethod.MANUAL,
                extraction_timestamp=_TS,
                effective_from=_DATE,
            ),
            note="simplification",
        )
        assert prov.note == "simplification"
        assert prov.location.page == "12"
        assert prov.extraction.method == ExtractionMethod.MANUAL
