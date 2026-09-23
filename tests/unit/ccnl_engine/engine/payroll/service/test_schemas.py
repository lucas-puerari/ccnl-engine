"""Tests for scenario/result serialisation helpers and JSON Schema generators."""

from __future__ import annotations

import json
from datetime import date
from typing import Literal, cast

import pytest

from ccnl_engine import (
    AnnualEstimateInput,
    Employee,
    Employer,
    Employment,
    Permanent,
    result_schema,
    scenario_schema,
)
from ccnl_engine.engine.payroll.domain.payroll_result import AnnualEstimate
from ccnl_engine.engine.payroll.service.orchestrator import estimate_annual
from ccnl_engine.engine.payroll.service.schemas import _hint_to_schema


@pytest.fixture(scope="module")
def scenario() -> AnnualEstimateInput:
    """Return a minimal AnnualEstimateInput for serialisation tests.

    Returns:
        A minimal :class:`AnnualEstimateInput` for Commercio.
    """
    return AnnualEstimateInput(
        employee=Employee(level_code="4"),
        employment=Employment(
            ccnl="commercio-confcommercio.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 1, 1),
        ),
    )


@pytest.fixture(scope="module")
def result(scenario: AnnualEstimateInput) -> AnnualEstimate:
    """Return an AnnualEstimate for the shared scenario.

    Returns:
        The :class:`AnnualEstimate` produced by :func:`estimate_annual`.
    """
    return estimate_annual(scenario).result


class TestAnnualPayrollScenarioSerialisation:
    """AnnualEstimateInput Pydantic model_dump / model_validate round-trip."""

    def test_model_dump_returns_dict(self, scenario: AnnualEstimateInput) -> None:
        """``model_dump(mode='json')`` returns a plain dict."""
        assert isinstance(scenario.model_dump(mode="json"), dict)

    def test_model_dump_contains_employment_type(
        self, scenario: AnnualEstimateInput
    ) -> None:
        """The serialised dict includes the employment type discriminator."""
        d = scenario.model_dump(mode="json")
        contract = cast("dict[str, object]", d["employment"])["contract"]
        assert cast("dict[str, object]", contract)["type"] == "permanent"

    def test_model_dump_json_returns_str(self, scenario: AnnualEstimateInput) -> None:
        """``model_dump_json()`` returns a valid JSON string."""
        raw = scenario.model_dump_json()
        assert isinstance(raw, str)
        parsed = json.loads(raw)
        assert isinstance(parsed, dict)

    def test_model_validate_roundtrip(self, scenario: AnnualEstimateInput) -> None:
        """``model_validate(model_dump())`` reconstructs an equal scenario."""
        d = scenario.model_dump(mode="json")
        assert AnnualEstimateInput.model_validate(d) == scenario

    def test_model_validate_json_roundtrip(self, scenario: AnnualEstimateInput) -> None:
        """``model_validate_json(model_dump_json())`` reconstructs an equal scenario."""
        raw = scenario.model_dump_json()
        assert AnnualEstimateInput.model_validate_json(raw) == scenario


class TestPayrollResultSchemaVersion:
    """AnnualEstimate includes schema_version in to_dict output."""

    def test_schema_version_field_exists(self, result: AnnualEstimate) -> None:
        """``result.schema_version`` is accessible on the instance."""
        assert result.schema_version == "3"

    def test_schema_version_in_to_dict(self, result: AnnualEstimate) -> None:
        """``to_dict()`` output includes ``schema_version``."""
        d = result.to_dict()
        assert d["schema_version"] == "3"

    def test_from_dict_roundtrip_with_schema_version(
        self, result: AnnualEstimate
    ) -> None:
        """``from_dict(to_dict())`` roundtrip succeeds with schema_version present."""
        restored = AnnualEstimate.from_dict(result.to_dict())
        assert restored.schema_version == "3"

    def test_from_dict_without_schema_version(self, result: AnnualEstimate) -> None:
        """``from_dict`` works on dicts missing schema_version (uses default)."""
        d = result.to_dict()
        d.pop("schema_version")
        restored = AnnualEstimate.from_dict(d)
        assert restored.schema_version == "3"


class TestScenarioSchema:
    """scenario_schema() returns a valid JSON Schema for AnnualEstimateInput."""

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
    """result_schema() returns a valid JSON Schema for AnnualEstimate."""

    def test_returns_dict(self) -> None:
        """``result_schema()`` returns a dict."""
        assert isinstance(result_schema(), dict)

    def test_has_schema_key(self) -> None:
        """The schema has a ``$schema`` declaration."""
        assert "$schema" in result_schema()

    def test_title_is_annual_estimate(self) -> None:
        """The schema title is ``"AnnualEstimate"``."""
        assert result_schema()["title"] == "AnnualEstimate"

    def test_has_required(self) -> None:
        """The schema lists required fields."""
        required = cast("list[str]", result_schema().get("required", []))
        assert len(required) > 0

    def test_net_annual_schema(self) -> None:
        """``net_annual`` maps to ``{"type": "string"}`` (Decimal as str)."""
        props = cast("dict[str, object]", result_schema().get("properties", {}))
        assert props["net_annual"] == {"type": "string"}

    def test_as_of_schema(self) -> None:
        """``as_of`` maps to date format schema."""
        props = cast("dict[str, object]", result_schema().get("properties", {}))
        assert props["as_of"] == {"type": "string", "format": "date"}

    def test_year_schema(self) -> None:
        """``year`` maps to integer schema."""
        props = cast("dict[str, object]", result_schema().get("properties", {}))
        assert props["year"] == {"type": "integer"}

    def test_earnings_in_properties(self) -> None:
        """``earnings`` sub-object is present in the result schema properties."""
        props = cast("dict[str, object]", result_schema().get("properties", {}))
        assert "earnings" in props

    def test_schema_version_in_properties(self) -> None:
        """``schema_version`` is present in the result schema properties."""
        props = cast("dict[str, object]", result_schema().get("properties", {}))
        assert "schema_version" in props

    def test_no_additional_properties(self) -> None:
        """``additionalProperties`` is False (strict schema)."""
        assert result_schema()["additionalProperties"] is False

    def test_net_annual_in_required(self) -> None:
        """``net_annual`` is listed as a required field."""
        required = cast("list[str]", result_schema().get("required", []))
        assert "net_annual" in required

    def test_schema_version_not_required(self) -> None:
        """``schema_version`` is not in required (it has a default)."""
        required = cast("list[str]", result_schema().get("required", []))
        assert "schema_version" not in required


class TestHintToSchema:
    """_hint_to_schema handles edge cases not exercised via result_schema."""

    def test_non_optional_union_falls_through(self) -> None:
        """A Union of two non-None types returns the fallback empty dict."""
        assert _hint_to_schema(int | str) == {}

    def test_optional_union_returns_one_of(self) -> None:
        """Optional[str] (str | None) returns a oneOf with null."""
        assert _hint_to_schema(str | None) == {
            "oneOf": [{"type": "string"}, {"type": "null"}]
        }

    def test_literal_returns_enum(self) -> None:
        """Literal['a', 'b'] returns an enum schema."""
        assert _hint_to_schema(Literal["a", "b"]) == {"enum": ["a", "b"]}

    def test_frozenset_returns_array_of_strings(self) -> None:
        """frozenset[str] returns an array-of-strings schema."""
        assert _hint_to_schema(frozenset[str]) == {
            "type": "array",
            "items": {"type": "string"},
        }
