"""Tests for scenario/result serialisation helpers and JSON Schema generators."""

from __future__ import annotations

import json
from datetime import date
from typing import cast

import pytest

from ccnl_engine import (
    AnnualPayrollScenario,
    Employee,
    Employer,
    Employment,
    Permanent,
    estimate_annual,
    result_schema,
    scenario_schema,
)
from ccnl_engine.engine.payroll.domain.payroll_result import PayrollResult
from ccnl_engine.engine.payroll.service.schemas import _hint_to_schema


@pytest.fixture(scope="module")
def scenario() -> AnnualPayrollScenario:
    """Return a minimal AnnualPayrollScenario for serialisation tests.

    Returns:
        An :class:`AnnualPayrollScenario` for CCNL Commercio level 4, 2026.
    """
    return AnnualPayrollScenario(
        employee=Employee(level_code="4"),
        employment=Employment(
            ccnl="commercio-confcommercio.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 1, 1),
        ),
    )


@pytest.fixture(scope="module")
def result(scenario: AnnualPayrollScenario) -> PayrollResult:
    """Return a PayrollResult for the shared scenario.

    Returns:
        A :class:`PayrollResult` produced by :func:`estimate_annual`.
    """
    return estimate_annual(scenario).result


class TestAnnualPayrollScenarioSerialisation:
    """AnnualPayrollScenario.to_dict/from_dict/to_json/from_json round-trip."""

    def test_to_dict_returns_dict(self, scenario: AnnualPayrollScenario) -> None:
        """``to_dict()`` returns a plain dict."""
        assert isinstance(scenario.to_dict(), dict)

    def test_to_dict_contains_employment_type(
        self, scenario: AnnualPayrollScenario
    ) -> None:
        """The serialised dict includes the employment type discriminator."""
        d = scenario.to_dict()
        contract = cast("dict[str, object]", d["employment"])["contract"]
        assert cast("dict[str, object]", contract)["type"] == "permanent"

    def test_to_json_returns_str(self, scenario: AnnualPayrollScenario) -> None:
        """``to_json()`` returns a valid JSON string."""
        raw = scenario.to_json()
        assert isinstance(raw, str)
        parsed = json.loads(raw)
        assert isinstance(parsed, dict)

    def test_from_dict_roundtrip(self, scenario: AnnualPayrollScenario) -> None:
        """``from_dict(to_dict())`` reconstructs an equal scenario."""
        assert AnnualPayrollScenario.from_dict(scenario.to_dict()) == scenario

    def test_from_json_roundtrip(self, scenario: AnnualPayrollScenario) -> None:
        """``from_json(to_json())`` reconstructs an equal scenario."""
        assert AnnualPayrollScenario.from_json(scenario.to_json()) == scenario


class TestPayrollResultSchemaVersion:
    """PayrollResult includes schema_version in to_dict output."""

    def test_schema_version_field_exists(self, result: PayrollResult) -> None:
        """``result.schema_version`` is accessible on the instance."""
        assert result.schema_version == "1"

    def test_schema_version_in_to_dict(self, result: PayrollResult) -> None:
        """``to_dict()`` output includes ``schema_version``."""
        d = result.to_dict()
        assert d["schema_version"] == "1"

    def test_from_dict_roundtrip_with_schema_version(
        self, result: PayrollResult
    ) -> None:
        """``from_dict(to_dict())`` roundtrip succeeds with schema_version present."""
        restored = PayrollResult.from_dict(result.to_dict())
        assert restored.schema_version == "1"

    def test_from_dict_without_schema_version(self, result: PayrollResult) -> None:
        """``from_dict`` works on dicts missing schema_version (uses default)."""
        d = result.to_dict()
        d.pop("schema_version")
        restored = PayrollResult.from_dict(d)
        assert restored.schema_version == "1"


class TestScenarioSchema:
    """scenario_schema() returns a valid JSON Schema for AnnualPayrollScenario."""

    def test_returns_dict(self) -> None:
        """``scenario_schema()`` returns a dict."""
        assert isinstance(scenario_schema(), dict)

    def test_has_title(self) -> None:
        """The schema has a ``title`` key."""
        assert "title" in scenario_schema()

    def test_has_properties(self) -> None:
        """The schema has a ``properties`` section."""
        s = scenario_schema()
        assert "properties" in s

    def test_employee_present(self) -> None:
        """``employee`` is present in the schema properties."""
        props = cast("dict[str, object]", scenario_schema().get("properties", {}))
        assert "employee" in props

    def test_employment_present(self) -> None:
        """``employment`` is present in the schema properties."""
        props = cast("dict[str, object]", scenario_schema().get("properties", {}))
        assert "employment" in props


class TestResultSchema:
    """result_schema() returns a valid JSON Schema for PayrollResult."""

    def test_returns_dict(self) -> None:
        """``result_schema()`` returns a dict."""
        assert isinstance(result_schema(), dict)

    def test_has_schema_key(self) -> None:
        """The schema has a ``$schema`` declaration."""
        assert "$schema" in result_schema()

    def test_title_is_payroll_result(self) -> None:
        """The schema title is ``"PayrollResult"``."""
        assert result_schema()["title"] == "PayrollResult"

    def test_has_required(self) -> None:
        """The schema lists required fields."""
        required = cast("list[str]", result_schema().get("required", []))
        assert len(required) > 0

    def test_gross_annual_schema(self) -> None:
        """``gross_annual`` maps to ``{"type": "string"}`` (Decimal as str)."""
        props = cast("dict[str, object]", result_schema().get("properties", {}))
        assert props["gross_annual"] == {"type": "string"}

    def test_as_of_schema(self) -> None:
        """``as_of`` maps to date format schema."""
        props = cast("dict[str, object]", result_schema().get("properties", {}))
        assert props["as_of"] == {"type": "string", "format": "date"}

    def test_year_schema(self) -> None:
        """``year`` maps to integer schema."""
        props = cast("dict[str, object]", result_schema().get("properties", {}))
        assert props["year"] == {"type": "integer"}

    def test_employer_withholds_irpef_schema(self) -> None:
        """``employer_withholds_irpef`` maps to boolean schema."""
        props = cast("dict[str, object]", result_schema().get("properties", {}))
        assert props["employer_withholds_irpef"] == {"type": "boolean"}

    def test_schema_version_in_properties(self) -> None:
        """``schema_version`` is present in the result schema properties."""
        props = cast("dict[str, object]", result_schema().get("properties", {}))
        assert "schema_version" in props

    def test_no_additional_properties(self) -> None:
        """``additionalProperties`` is False (strict schema)."""
        assert result_schema()["additionalProperties"] is False

    def test_gross_annual_in_required(self) -> None:
        """``gross_annual`` is listed as a required field."""
        required = cast("list[str]", result_schema().get("required", []))
        assert "gross_annual" in required

    def test_schema_version_not_required(self) -> None:
        """``schema_version`` is not in required (it has a default)."""
        required = cast("list[str]", result_schema().get("required", []))
        assert "schema_version" not in required


class TestHintToSchema:
    """_hint_to_schema handles edge cases not exercised via result_schema."""

    def test_non_optional_union_falls_through(self) -> None:
        """A Union of two non-None types returns the fallback empty dict."""
        assert _hint_to_schema(int | str) == {}
