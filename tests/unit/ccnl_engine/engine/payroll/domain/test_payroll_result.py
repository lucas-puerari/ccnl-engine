"""Tests for AnnualEstimate.to_dict / to_json / from_dict / from_json."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from ccnl_engine import (
    AnnualEstimateInput,
    Employee,
    Employer,
    Employment,
    FiscalSimplification,
    PeriodPayrollInput,
    Permanent,
    TaxPeriod,
    estimate_annual,
    estimate_period_effects,
)
from ccnl_engine.engine.metadata.domain.rules import VerificationStatus
from ccnl_engine.engine.payroll.domain.payroll_result import (
    AnnualEstimate,
    Coverage,
    PeriodPayroll,
    _decode_field,
)
from ccnl_engine.engine.payroll.domain.supplements import OvertimeHours
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
        A :class:`RuleProvenance` with representative test data.
    """
    return RuleProvenance(
        location=SourceLocation(
            source_document=SourceDocument(
                document_id="doc",
                title="Document",
                kind=SourceKind.TABELLA_RETRIBUTIVA,
                url="https://example.com",
                pages=("12",),
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
def payroll() -> AnnualEstimate:
    """Return a representative AnnualEstimate via a real estimate_annual() call.

    Returns:
        An :class:`AnnualEstimate` for CCNL Commercio level 4, 2026.
    """
    return estimate_annual(
        AnnualEstimateInput(
            employee=Employee(level_code="4"),
            employment=Employment(
                ccnl="commercio-confcommercio.json",
                contract=Permanent(),
                employer=Employer(num_employees=50),
                as_of=date(2026, 1, 1),
            ),
        )
    ).result


@pytest.fixture(scope="module")
def payroll_domestic() -> AnnualEstimate:
    """Return an AnnualEstimate for lavoro domestico.

    Returns:
        An :class:`AnnualEstimate` where employer_withholds_irpef is False.
    """
    return estimate_annual(
        AnnualEstimateInput(
            employee=Employee(level_code="C", weekly_hours=Decimal(40)),
            employment=Employment(
                ccnl="lavoro-domestico-non-convivente.json",
                contract=Permanent(),
                employer=Employer(num_employees=1),
                as_of=date(2026, 1, 1),
            ),
        )
    ).result


class TestToDict:
    """Unit tests for AnnualEstimate.to_dict()."""

    def test_decimal_fields_are_strings(self, payroll: AnnualEstimate) -> None:
        """Decimal fields are serialised as strings."""
        d = payroll.to_dict()
        assert isinstance(d["net_annual"], str)
        assert isinstance(d["earnings"]["gross_monthly"], str)  # type: ignore[index]

    def test_date_is_iso_string(self, payroll: AnnualEstimate) -> None:
        """The as_of date is serialised as an ISO-8601 string."""
        d = payroll.to_dict()
        assert d["as_of"] == "2026-01-01"

    def test_fiscal_simplifications_is_sorted_list(
        self, payroll: AnnualEstimate
    ) -> None:
        """fiscal_simplifications is a sorted list of valid enum value strings."""
        d = payroll.to_dict()
        flist = d["taxes"]["fiscal_simplifications"]  # type: ignore[index]
        assert isinstance(flist, list)
        assert flist == sorted(flist)
        for v in flist:
            FiscalSimplification(v)

    def test_none_field_preserved(self, payroll: AnnualEstimate) -> None:
        """None values are preserved as None."""
        d = payroll.to_dict()
        assert d["earnings"]["apprenticeship_pct"] is None  # type: ignore[index]
        assert (
            d["earnings"]["apprenticeship_under_level_code"] is None  # type: ignore[index]
        )

    def test_bool_field_preserved(
        self, payroll: AnnualEstimate, payroll_domestic: AnnualEstimate
    ) -> None:
        """Bool fields keep their Python bool type."""
        taxes = payroll.to_dict()["taxes"]
        assert taxes["employer_withholds_irpef"] is True  # type: ignore[index]
        taxes_d = payroll_domestic.to_dict()["taxes"]
        assert taxes_d["employer_withholds_irpef"] is False  # type: ignore[index]

    def test_int_fields_preserved(self, payroll: AnnualEstimate) -> None:
        """Integer fields remain int."""
        d = payroll.to_dict()
        assert isinstance(d["year"], int)
        assert isinstance(d["earnings"]["seniority_count"], int)  # type: ignore[index]

    def test_sub_objects_present(self, payroll: AnnualEstimate) -> None:
        """to_dict output contains all sub-object keys."""
        d = payroll.to_dict()
        for key in ("earnings", "contributions", "taxes", "employer_cost", "coverage"):
            assert key in d
            assert isinstance(d[key], dict)


class TestToJson:
    """Unit tests for AnnualEstimate.to_json()."""

    def test_returns_valid_json(self, payroll: AnnualEstimate) -> None:
        """to_json() returns a parseable JSON string with the expected keys."""
        raw = payroll.to_json()
        parsed = json.loads(raw)
        assert isinstance(parsed, dict)
        assert "net_annual" in parsed


class TestFromDict:
    """Unit tests for AnnualEstimate.from_dict()."""

    def test_round_trip_standard(self, payroll: AnnualEstimate) -> None:
        """from_dict(to_dict(p)) == p for a standard permanent payroll."""
        assert AnnualEstimate.from_dict(payroll.to_dict()) == payroll

    def test_round_trip_domestic(self, payroll_domestic: AnnualEstimate) -> None:
        """Round-trip for domestic payroll: withholds=False, ti>0."""
        assert AnnualEstimate.from_dict(payroll_domestic.to_dict()) == payroll_domestic

    def test_decimal_fields_restored(self, payroll: AnnualEstimate) -> None:
        """Decimal fields come back as Decimal with the same value."""
        restored = AnnualEstimate.from_dict(payroll.to_dict())
        assert isinstance(restored.net_annual, Decimal)
        assert restored.net_annual == payroll.net_annual

    def test_date_field_restored(self, payroll: AnnualEstimate) -> None:
        """The as_of field comes back as a date object."""
        restored = AnnualEstimate.from_dict(payroll.to_dict())
        assert isinstance(restored.as_of, date)
        assert restored.as_of == payroll.as_of

    def test_frozenset_field_restored(self, payroll: AnnualEstimate) -> None:
        """fiscal_simplifications comes back as a frozenset."""
        restored = AnnualEstimate.from_dict(payroll.to_dict())
        assert isinstance(restored.taxes.fiscal_simplifications, frozenset)
        assert (
            restored.taxes.fiscal_simplifications
            == payroll.taxes.fiscal_simplifications
        )

    def test_none_decimal_field_restored(self, payroll: AnnualEstimate) -> None:
        """apprenticeship_pct (Decimal | None) is restored as None for permanent."""
        assert payroll.earnings.apprenticeship_pct is None
        restored = AnnualEstimate.from_dict(payroll.to_dict())
        assert restored.earnings.apprenticeship_pct is None

    def test_optional_decimal_coerced_when_present(
        self, payroll: AnnualEstimate
    ) -> None:
        """apprenticeship_pct is coerced to Decimal when a non-None value is given."""
        d = payroll.to_dict()
        d["earnings"]["apprenticeship_pct"] = "0.80"  # type: ignore[index]
        restored = AnnualEstimate.from_dict(d)
        assert restored.earnings.apprenticeship_pct == Decimal("0.80")

    def test_missing_key_raises(self, payroll: AnnualEstimate) -> None:
        """ValueError is raised when a required top-level field is absent."""
        d = payroll.to_dict()
        del d["net_annual"]
        with pytest.raises(ValueError, match="Missing field"):
            AnnualEstimate.from_dict(d)

    def test_provenance_round_trip(self, payroll: AnnualEstimate) -> None:
        """RuleProvenance entries in the provenance tuple survive the round-trip."""
        prov = _rule_provenance()
        d = payroll.to_dict()
        d["provenance"] = [prov.model_dump(mode="json")]
        restored = AnnualEstimate.from_dict(d)
        assert restored.provenance == (prov,)
        assert isinstance(restored.provenance[0], RuleProvenance)
        assert restored.provenance[0].location.page == "12"

    def test_empty_provenance_round_trip(self, payroll: AnnualEstimate) -> None:
        """An empty provenance tuple round-trips to an empty tuple."""
        restored = AnnualEstimate.from_dict(payroll.to_dict())
        assert restored.provenance == payroll.provenance
        assert isinstance(restored.provenance, tuple)


class TestFromJson:
    """Unit tests for AnnualEstimate.from_json()."""

    def test_round_trip(self, payroll: AnnualEstimate) -> None:
        """from_json(to_json(p)) == p."""
        assert AnnualEstimate.from_json(payroll.to_json()) == payroll

    def test_invalid_json_raises(self) -> None:
        """JSONDecodeError is raised for unparseable input."""
        with pytest.raises(json.JSONDecodeError):
            AnnualEstimate.from_json("not json")


class TestFromDictStrictValidation:
    """from_dict rejects extra keys, wrong primitive types, and invalid ScopeItem."""

    def test_extra_key_rejected(self, payroll: AnnualEstimate) -> None:
        """Extra keys not produced by to_dict must raise TypeError."""
        d = payroll.to_dict()
        d["unexpected_field"] = "value"
        with pytest.raises(TypeError, match="unexpected keys"):
            AnnualEstimate.from_dict(d)

    def test_employer_withholds_irpef_string_rejected(
        self, payroll: AnnualEstimate
    ) -> None:
        """String 'false' for employer_withholds_irpef must raise TypeError."""
        d = payroll.to_dict()
        d["taxes"]["employer_withholds_irpef"] = "false"  # type: ignore[index]
        with pytest.raises(TypeError, match="expected bool"):
            AnnualEstimate.from_dict(d)

    def test_year_string_rejected(self, payroll: AnnualEstimate) -> None:
        """String '2026' for year must raise TypeError."""
        d = payroll.to_dict()
        d["year"] = "2026"
        with pytest.raises(TypeError, match="expected int"):
            AnnualEstimate.from_dict(d)

    def test_level_code_int_rejected(self, payroll: AnnualEstimate) -> None:
        """Integer level_code must raise TypeError."""
        d = payroll.to_dict()
        d["level_code"] = 4
        with pytest.raises(TypeError, match="expected str"):
            AnnualEstimate.from_dict(d)

    def test_scope_item_invalid_status_rejected(self, payroll: AnnualEstimate) -> None:
        """ScopeItem with invalid calculation_status value raises ValueError."""
        d = payroll.to_dict()
        d["coverage"]["calculation_scope"] = [  # type: ignore[index]
            {
                "feature": "irpef",
                "calculation_status": "invalid_status",
                "eligibility_status": "engine_verified",
                "source_quality": "verified_primary",
            }
        ]
        with pytest.raises(ValueError, match=r"ScopeItem\.calculation_status"):
            AnnualEstimate.from_dict(d)

    def test_scope_item_non_str_feature_rejected(self, payroll: AnnualEstimate) -> None:
        """ScopeItem with integer feature raises TypeError."""
        d = payroll.to_dict()
        d["coverage"]["calculation_scope"] = [  # type: ignore[index]
            {
                "feature": 42,
                "calculation_status": "computed",
                "eligibility_status": "engine_verified",
                "source_quality": "verified_primary",
            }
        ]
        with pytest.raises(TypeError, match=r"ScopeItem\.feature"):
            AnnualEstimate.from_dict(d)

    def test_scope_item_invalid_eligibility_status_rejected(
        self, payroll: AnnualEstimate
    ) -> None:
        """ScopeItem with invalid eligibility_status value raises ValueError."""
        d = payroll.to_dict()
        d["coverage"]["calculation_scope"] = [  # type: ignore[index]
            {
                "feature": "irpef",
                "calculation_status": "computed",
                "eligibility_status": "bad_value",
                "source_quality": "verified_primary",
            }
        ]
        with pytest.raises(ValueError, match=r"ScopeItem\.eligibility_status"):
            AnnualEstimate.from_dict(d)

    def test_scope_item_invalid_source_quality_rejected(
        self, payroll: AnnualEstimate
    ) -> None:
        """ScopeItem with invalid source_quality value raises ValueError."""
        d = payroll.to_dict()
        d["coverage"]["calculation_scope"] = [  # type: ignore[index]
            {
                "feature": "irpef",
                "calculation_status": "computed",
                "eligibility_status": "engine_verified",
                "source_quality": "bad_value",
            }
        ]
        with pytest.raises(ValueError, match=r"ScopeItem\.source_quality"):
            AnnualEstimate.from_dict(d)

    def test_status_invalid_literal_rejected(self, payroll: AnnualEstimate) -> None:
        """Invalid status literal raises ValueError."""
        d = payroll.to_dict()
        d["coverage"]["status"] = "corrupted"  # type: ignore[index]
        with pytest.raises(ValueError, match="expected one of"):
            AnnualEstimate.from_dict(d)

    def test_confidence_invalid_literal_rejected(self, payroll: AnnualEstimate) -> None:
        """Invalid confidence literal raises ValueError."""
        d = payroll.to_dict()
        d["coverage"]["confidence"] = "certain"  # type: ignore[index]
        with pytest.raises(ValueError, match="expected one of"):
            AnnualEstimate.from_dict(d)

    def test_warnings_string_rejected(self, payroll: AnnualEstimate) -> None:
        """String for warnings tuple field raises TypeError."""
        d = payroll.to_dict()
        d["coverage"]["warnings"] = "single warning"  # type: ignore[index]
        with pytest.raises(TypeError, match="expected a JSON array"):
            AnnualEstimate.from_dict(d)


class TestSubObjectToDict:
    """Sub-object to_dict() methods serialize to plain dicts."""

    def test_earnings_to_dict(self, payroll: AnnualEstimate) -> None:
        """Earnings.to_dict() returns a dict with all fields."""
        d = payroll.earnings.to_dict()
        assert isinstance(d, dict)
        assert "gross_monthly" in d
        assert isinstance(d["gross_monthly"], str)

    def test_contributions_to_dict(self, payroll: AnnualEstimate) -> None:
        """Contributions.to_dict() returns a dict with all fields."""
        d = payroll.contributions.to_dict()
        assert isinstance(d, dict)
        assert "inps_employee_annual" in d

    def test_taxes_to_dict(self, payroll: AnnualEstimate) -> None:
        """Taxes.to_dict() returns a dict with all fields."""
        d = payroll.taxes.to_dict()
        assert isinstance(d, dict)
        assert "irpef_net" in d

    def test_employer_cost_to_dict(self, payroll: AnnualEstimate) -> None:
        """EmployerCost.to_dict() returns a dict with employer_cost_annual."""
        d = payroll.employer_cost.to_dict()
        assert isinstance(d, dict)
        assert "employer_cost_annual" in d

    def test_coverage_to_dict(self, payroll: AnnualEstimate) -> None:
        """Coverage.to_dict() returns a dict with status and confidence."""
        d = payroll.coverage.to_dict()
        assert isinstance(d, dict)
        assert "status" in d
        assert "confidence" in d


@pytest.fixture(scope="module")
def period_payroll() -> PeriodPayroll:
    """Return a PeriodPayroll via estimate_period_effects.

    Returns:
        A :class:`PeriodPayroll` for CCNL Commercio level 4 with overtime.
    """
    scenario = AnnualEstimateInput(
        employee=Employee(level_code="4"),
        employment=Employment(
            ccnl="commercio-confcommercio.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 1, 1),
        ),
    )
    calc = estimate_period_effects(
        scenario,
        PeriodPayrollInput(
            tax_period=TaxPeriod(
                start=date(2026, 1, 1),
                end=date(2026, 12, 31),
                eligible_work_days=365,
            ),
            time_supplements=OvertimeHours(weekday_hours=Decimal(8)),
        ),
    )
    assert isinstance(calc.result, PeriodPayroll)
    return calc.result


class TestPeriodPayrollSerde:
    """PeriodPayroll round-trips through from_dict / from_json."""

    def test_from_dict_round_trip(self, period_payroll: PeriodPayroll) -> None:
        """PeriodPayroll.from_dict(to_dict(p)) == p."""
        assert PeriodPayroll.from_dict(period_payroll.to_dict()) == period_payroll

    def test_from_json_round_trip(self, period_payroll: PeriodPayroll) -> None:
        """PeriodPayroll.from_json(to_json(p)) == p."""
        assert PeriodPayroll.from_json(period_payroll.to_json()) == period_payroll

    def test_from_dict_unexpected_key_raises(
        self, period_payroll: PeriodPayroll
    ) -> None:
        """PeriodPayroll.from_dict with extra key raises TypeError."""
        d = period_payroll.to_dict()
        d["unexpected"] = "bad"
        with pytest.raises(TypeError, match="unexpected keys"):
            PeriodPayroll.from_dict(d)

    def test_from_dict_missing_required_field_raises(
        self, period_payroll: PeriodPayroll
    ) -> None:
        """PeriodPayroll.from_dict raises ValueError for a missing required field."""
        d = period_payroll.to_dict()
        del d["net_annual"]
        with pytest.raises(ValueError, match="Missing field"):
            PeriodPayroll.from_dict(d)

    def test_from_dict_missing_optional_field_uses_default(
        self, period_payroll: PeriodPayroll
    ) -> None:
        """PeriodPayroll.from_dict with a missing optional field uses its default."""
        d = period_payroll.to_dict()
        del d["schema_version"]
        restored = PeriodPayroll.from_dict(d)
        assert restored.schema_version == "3"


class TestCoverageFromDictOptional:
    """Coverage.from_dict skips optional fields absent from the dict."""

    def test_from_dict_without_consumed_rulesets_uses_default(self) -> None:
        """Coverage.from_dict with no consumed_rulesets falls back to default."""
        minimal: dict[str, object] = {
            "status": "complete",
            "confidence": "high",
            "calculation_scope": [],
            "warnings": [],
        }
        cov = Coverage.from_dict(minimal)
        assert cov.consumed_rulesets == ()


class TestDecodeFieldBranches:
    """_decode_field covers extra_decoders miss and non-callable branches."""

    def test_extra_decoders_empty_falls_through_to_coerce(self) -> None:
        """extra_decoders empty (falsy) while raw is a dict: falls back to _coerce."""
        result = _decode_field("unknown", {"a": 1}, dict, extra_decoders={})
        assert result == {"a": 1}

    def test_extra_decoders_non_callable_falls_through_to_coerce(self) -> None:
        """extra_decoders[name] is not callable: falls back to _coerce."""
        result = _decode_field(
            "unknown",
            {"a": 1},
            dict,
            extra_decoders={"unknown": "not-callable"},
        )
        assert result == {"a": 1}
