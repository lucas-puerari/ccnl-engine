"""Tests for PayrollResult.to_dict / to_json / from_dict / from_json."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from ccnl_engine import (
    Employee,
    Employer,
    Employment,
    FiscalSimplification,
    PayrollScenario,
    Permanent,
    compute,
)
from ccnl_engine.engine.metadata.domain.rules import VerificationStatus
from ccnl_engine.engine.payroll.domain.payroll_result import PayrollResult
from ccnl_engine.engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.engine.provenance.domain.extraction import (
    ExtractionMethod,
    ExtractionTrace,
)
from ccnl_engine.engine.provenance.domain.source import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)


def _rule_provenance() -> RuleProvenance:
    """Build a representative RuleProvenance for serialisation tests.

    Returns:
        A :class:`RuleProvenance` with sample location and extraction data.
    """
    return RuleProvenance(
        location=SourceLocation(
            source_document=SourceDocument(
                document_id="doc",
                title="Document",
                kind=SourceKind.TABELLA_RETRIBUTIVA,
                url="https://example.com",
                pages=["12"],
                published_on=date(2025, 1, 1),
            ),
            page="12",
            section="Tabella 1",
        ),
        extraction=ExtractionTrace(
            method=ExtractionMethod.MANUAL,
            extraction_timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            verification_status=VerificationStatus.UNVERIFIED,
            effective_from=date(2025, 1, 1),
        ),
        note="test provenance",
    )


@pytest.fixture(scope="module")
def payroll() -> PayrollResult:
    """Return a representative PayrollResult via a real compute() call.

    Returns:
        A PayrollResult for CCNL Commercio level 4, 2026, permanent full-time.
    """
    return compute(
        PayrollScenario(
            employee=Employee(level_code="4"),
            employment=Employment(
                ccnl="commercio-confcommercio.json",
                contract=Permanent(),
                employer=Employer(num_employees=50),
                calculation_date=date(2026, 1, 1),
            ),
        )
    ).result


@pytest.fixture(scope="module")
def payroll_domestic() -> PayrollResult:
    """Return a PayrollResult for lavoro domestico (employer_withholds_irpef=False).

    Returns:
        A PayrollResult for CCNL Lavoro Domestico level C, 2026, full-time 40h.
    """
    return compute(
        PayrollScenario(
            employee=Employee(level_code="C", weekly_hours=Decimal(40)),
            employment=Employment(
                ccnl="lavoro-domestico-non-convivente.json",
                contract=Permanent(),
                employer=Employer(num_employees=1),
                calculation_date=date(2026, 1, 1),
            ),
        )
    ).result


class TestToDict:
    """Unit tests for PayrollResult.to_dict()."""

    def test_decimal_fields_are_strings(self, payroll: PayrollResult) -> None:
        """Decimal fields are serialised as strings."""
        d = payroll.to_dict()
        assert isinstance(d["net_annual"], str)
        assert isinstance(d["gross_monthly"], str)

    def test_date_is_iso_string(self, payroll: PayrollResult) -> None:
        """The as_of date is serialised as an ISO-8601 string."""
        d = payroll.to_dict()
        assert d["as_of"] == "2026-01-01"

    def test_fiscal_simplifications_is_sorted_list(
        self, payroll: PayrollResult
    ) -> None:
        """fiscal_simplifications is a sorted list of valid enum value strings."""
        d = payroll.to_dict()
        flist = d["fiscal_simplifications"]
        assert isinstance(flist, list)
        assert flist == sorted(flist)
        for v in flist:
            FiscalSimplification(v)  # raises ValueError if invalid

    def test_none_field_preserved(self, payroll: PayrollResult) -> None:
        """None values are preserved as None."""
        d = payroll.to_dict()
        assert d["apprenticeship_pct"] is None
        assert d["apprenticeship_under_level_code"] is None

    def test_bool_field_preserved(
        self, payroll: PayrollResult, payroll_domestic: PayrollResult
    ) -> None:
        """Bool fields keep their Python bool type."""
        assert payroll.to_dict()["employer_withholds_irpef"] is True
        assert payroll_domestic.to_dict()["employer_withholds_irpef"] is False

    def test_int_fields_preserved(self, payroll: PayrollResult) -> None:
        """Integer fields remain int."""
        d = payroll.to_dict()
        assert isinstance(d["year"], int)
        assert isinstance(d["seniority_count"], int)


class TestToJson:
    """Unit tests for PayrollResult.to_json()."""

    def test_returns_valid_json(self, payroll: PayrollResult) -> None:
        """to_json() returns a parseable JSON string with the expected keys."""
        raw = payroll.to_json()
        parsed = json.loads(raw)
        assert isinstance(parsed, dict)
        assert "net_annual" in parsed


class TestFromDict:
    """Unit tests for PayrollResult.from_dict()."""

    def test_round_trip_standard(self, payroll: PayrollResult) -> None:
        """from_dict(to_dict(p)) == p for a standard permanent payroll."""
        assert PayrollResult.from_dict(payroll.to_dict()) == payroll

    def test_round_trip_domestic(self, payroll_domestic: PayrollResult) -> None:
        """Round-trip for domestic payroll: withholds=False, ti>0."""
        assert PayrollResult.from_dict(payroll_domestic.to_dict()) == payroll_domestic

    def test_decimal_fields_restored(self, payroll: PayrollResult) -> None:
        """Decimal fields come back as Decimal with the same value."""
        restored = PayrollResult.from_dict(payroll.to_dict())
        assert isinstance(restored.net_annual, Decimal)
        assert restored.net_annual == payroll.net_annual

    def test_date_field_restored(self, payroll: PayrollResult) -> None:
        """The as_of field comes back as a date object."""
        restored = PayrollResult.from_dict(payroll.to_dict())
        assert isinstance(restored.as_of, date)
        assert restored.as_of == payroll.as_of

    def test_frozenset_field_restored(self, payroll: PayrollResult) -> None:
        """fiscal_simplifications comes back as a frozenset."""
        restored = PayrollResult.from_dict(payroll.to_dict())
        assert isinstance(restored.fiscal_simplifications, frozenset)
        assert restored.fiscal_simplifications == payroll.fiscal_simplifications

    def test_none_decimal_field_restored(self, payroll: PayrollResult) -> None:
        """apprenticeship_pct (Decimal | None) is restored as None for permanent."""
        assert payroll.apprenticeship_pct is None
        restored = PayrollResult.from_dict(payroll.to_dict())
        assert restored.apprenticeship_pct is None

    def test_optional_decimal_coerced_when_present(
        self, payroll: PayrollResult
    ) -> None:
        """apprenticeship_pct is coerced to Decimal when a non-None value is given."""
        d = payroll.to_dict()
        d["apprenticeship_pct"] = "0.80"
        restored = PayrollResult.from_dict(d)
        assert restored.apprenticeship_pct == Decimal("0.80")

    def test_missing_key_raises(self, payroll: PayrollResult) -> None:
        """ValueError is raised when a required field is absent."""
        d = payroll.to_dict()
        del d["net_annual"]
        with pytest.raises(ValueError, match="Missing field"):
            PayrollResult.from_dict(d)

    def test_provenance_round_trip(self, payroll: PayrollResult) -> None:
        """RuleProvenance entries in the provenance tuple survive the round-trip."""
        prov = _rule_provenance()
        d = payroll.to_dict()
        d["provenance"] = [prov.model_dump(mode="json")]
        restored = PayrollResult.from_dict(d)
        assert restored.provenance == (prov,)
        assert isinstance(restored.provenance[0], RuleProvenance)
        assert restored.provenance[0].location.page == "12"

    def test_empty_provenance_round_trip(self, payroll: PayrollResult) -> None:
        """An empty provenance tuple round-trips to an empty tuple."""
        restored = PayrollResult.from_dict(payroll.to_dict())
        assert restored.provenance == payroll.provenance
        assert isinstance(restored.provenance, tuple)


class TestFromJson:
    """Unit tests for PayrollResult.from_json()."""

    def test_round_trip(self, payroll: PayrollResult) -> None:
        """from_json(to_json(p)) == p."""
        assert PayrollResult.from_json(payroll.to_json()) == payroll

    def test_invalid_json_raises(self) -> None:
        """JSONDecodeError is raised for unparseable input."""
        with pytest.raises(json.JSONDecodeError):
            PayrollResult.from_json("not json")
