"""Oracle schema enforcement tests.

These tests verify that actual engine outputs conform to the schemas declared
by ``result_schema()`` and ``scenario_schema()``.  Unlike the unit tests in
``test_schemas.py`` (which verify the shape of the schema itself), these tests
run a real computation and assert that its output satisfies every structural
constraint declared in the published schema.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, cast

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
from ccnl_engine.engine.payroll.service.orchestrator import estimate_annual

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.payroll_result import AnnualEstimate


@pytest.fixture(scope="module")
def scenario() -> AnnualEstimateInput:
    """Return a minimal AnnualEstimateInput for schema enforcement tests.

    Returns:
        A minimal :class:`AnnualEstimateInput` for Federmeccanica level 4.
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


@pytest.fixture(scope="module")
def result_dict(result: AnnualEstimate) -> dict[str, object]:
    """Return the to_dict() representation of the result.

    Returns:
        Plain dict from :meth:`AnnualEstimate.to_dict`.
    """
    return result.to_dict()


# ---------------------------------------------------------------------------
# Scenario schema structural enforcement
# ---------------------------------------------------------------------------


class TestScenarioSchemaEnforcement:
    """The declared scenario_schema() matches the actual AnnualEstimateInput shape."""

    def test_schema_has_properties(self) -> None:
        """scenario_schema() exposes a properties section."""
        schema = scenario_schema()
        assert "properties" in schema

    def test_scenario_properties_non_empty(self) -> None:
        """scenario_schema() properties is not empty."""
        schema = scenario_schema()
        props = cast("dict[str, object]", schema["properties"])
        assert len(props) > 0

    def test_scenario_roundtrip_validates_against_itself(
        self, scenario: AnnualEstimateInput
    ) -> None:
        """Serialised scenario can be reconstructed from its own dump."""
        raw = scenario.model_dump(mode="json")
        restored = AnnualEstimateInput.model_validate(raw)
        assert restored == scenario

    def test_scenario_json_roundtrip(self, scenario: AnnualEstimateInput) -> None:
        """JSON string roundtrip preserves the scenario."""
        json_str = scenario.model_dump_json()
        restored = AnnualEstimateInput.model_validate_json(json_str)
        assert restored == scenario


# ---------------------------------------------------------------------------
# Result schema: required fields present in actual output
# ---------------------------------------------------------------------------


class TestResultRequiredFieldsPresent:
    """Every field listed in result_schema()['required'] appears in to_dict()."""

    def test_all_required_fields_present(self, result_dict: dict[str, object]) -> None:
        """Every required field is a key in the to_dict() output."""
        required = cast("list[str]", result_schema()["required"])
        missing = [f for f in required if f not in result_dict]
        assert missing == [], f"Missing required fields: {missing}"

    @pytest.mark.parametrize("field", cast("list[str]", result_schema()["required"]))
    def test_required_field_not_none(
        self, field: str, result_dict: dict[str, object]
    ) -> None:
        """Each required field is not None in the actual output."""
        assert result_dict[field] is not None


# ---------------------------------------------------------------------------
# Result schema: no extra fields beyond schema properties
# ---------------------------------------------------------------------------


class TestResultNoExtraFields:
    """to_dict() produces only fields declared in result_schema()['properties']."""

    def test_no_extraneous_keys(self, result_dict: dict[str, object]) -> None:
        """All keys in to_dict() are declared in the schema properties."""
        allowed = set(cast("dict[str, object]", result_schema()["properties"]).keys())
        extra = set(result_dict.keys()) - allowed
        assert extra == set(), f"Undeclared keys in output: {extra}"


# ---------------------------------------------------------------------------
# Result schema: field type enforcement
# ---------------------------------------------------------------------------


class TestResultFieldTypes:
    """Actual output field types match what result_schema() declares."""

    def test_decimal_fields_serialised_as_string(
        self, result_dict: dict[str, object]
    ) -> None:
        """Fields declared with {type: string} are strings in the output."""
        props = cast("dict[str, object]", result_schema()["properties"])
        for field, spec in props.items():
            if spec == {"type": "string"} and field in result_dict:
                value = result_dict[field]
                if value is not None:
                    assert isinstance(value, str), (
                        f"Field {field!r} should be a str, got {type(value).__name__}"
                    )

    def test_integer_fields_serialised_as_int(
        self, result_dict: dict[str, object]
    ) -> None:
        """Fields declared with {type: integer} are ints in the output."""
        props = cast("dict[str, object]", result_schema()["properties"])
        for field, spec in props.items():
            if spec == {"type": "integer"} and field in result_dict:
                value = result_dict[field]
                if value is not None:
                    assert isinstance(value, int), (
                        f"Field {field!r} should be an int, got {type(value).__name__}"
                    )

    def test_date_fields_serialised_as_string(
        self, result_dict: dict[str, object]
    ) -> None:
        """Fields declared with {type: string, format: date} are str in the output."""
        props = cast("dict[str, object]", result_schema()["properties"])
        for field, spec in props.items():
            if spec == {"type": "string", "format": "date"} and field in result_dict:
                value = result_dict[field]
                if value is not None:
                    assert isinstance(value, str), (
                        f"Field {field!r} should be a date str, "
                        f"got {type(value).__name__}"
                    )


# ---------------------------------------------------------------------------
# Result schema: object fields contain sub-properties
# ---------------------------------------------------------------------------


class TestResultObjectFields:
    """Object fields in the output are non-empty dicts."""

    def test_earnings_is_dict(self, result_dict: dict[str, object]) -> None:
        """Earnings field is a non-empty dict."""
        earnings = result_dict["earnings"]
        assert isinstance(earnings, dict)
        assert len(cast("dict[str, object]", earnings)) > 0

    def test_contributions_is_dict(self, result_dict: dict[str, object]) -> None:
        """Contributions field is a non-empty dict."""
        contributions = result_dict["contributions"]
        assert isinstance(contributions, dict)
        assert len(cast("dict[str, object]", contributions)) > 0

    def test_employer_cost_is_dict(self, result_dict: dict[str, object]) -> None:
        """Employer cost field is a non-empty dict."""
        employer_cost = result_dict["employer_cost"]
        assert isinstance(employer_cost, dict)
        assert len(cast("dict[str, object]", employer_cost)) > 0


# ---------------------------------------------------------------------------
# Stable-field oracle: core output values are stable across minor changes
# ---------------------------------------------------------------------------


class TestResultSchemaStableKeys:
    """Key output fields are always present and never change name."""

    _STABLE_KEYS = frozenset({
        "as_of",
        "ccnl_id",
        "earnings",
        "contributions",
        "employer_cost",
        "net_annual",
        "schema_version",
    })

    def test_stable_keys_present(self, result_dict: dict[str, object]) -> None:
        """All stable keys are present in any valid result dict."""
        missing = self._STABLE_KEYS - set(result_dict.keys())
        assert missing == set(), f"Stable keys missing: {missing}"

    def test_stable_keys_subset_of_schema(self) -> None:
        """Stable keys are a subset of the declared schema properties."""
        declared = set(cast("dict[str, object]", result_schema()["properties"]).keys())
        undeclared = self._STABLE_KEYS - declared
        assert undeclared == set(), f"Stable keys not in schema: {undeclared}"
