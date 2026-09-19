"""Coverage tests for L3 payroll_result paths (ScopeItem, to_dict, from_dict)."""

from __future__ import annotations

import dataclasses
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
)
from ccnl_engine.engine.payroll.domain.payroll_result import (
    AnnualEstimate,
    ScopeItem,
    _coerce_scalar,
)


@pytest.fixture(scope="module")
def payroll() -> AnnualEstimate:
    """Return a real AnnualEstimate for tests.

    Returns:
        An :class:`AnnualEstimate` for metalmeccanico C2 level, 2026.
    """
    return estimate_annual(
        AnnualPayrollScenario(
            employee=Employee(level_code="C2"),
            employment=Employment(
                ccnl="metalmeccanico-federmeccanica.json",
                contract=Permanent(),
                employer=Employer(num_employees=50),
                as_of=date(2026, 9, 1),
            ),
        )
    ).result


class TestScopeItemCoerce:
    """_coerce_scalar ScopeItem branch is exercised here."""

    def test_coerce_scope_item_from_dict(self) -> None:
        """ScopeItem is reconstructed from a plain dict."""
        raw = {
            "feature": "overtime",
            "calculation_status": "computed",
            "integration_status": "included_in_totals",
            "eligibility_status": "engine_verified",
            "source_quality": "verified_primary",
        }
        result = _coerce_scalar(raw, ScopeItem)
        assert isinstance(result, ScopeItem)
        assert result.feature == "overtime"
        assert result.calculation_status == "computed"

    def test_coerce_non_dict_passthrough(self) -> None:
        """A non-dict raw value for ScopeItem is returned unchanged."""
        result = _coerce_scalar("already_string", ScopeItem)
        assert result == "already_string"


class TestToDictScopeItem:
    """to_dict tuple branch: dataclasses.is_dataclass path."""

    def test_scope_items_serialised_as_dicts(self, payroll: AnnualEstimate) -> None:
        """calculation_scope ScopeItem entries are serialised via asdict()."""
        new_coverage = dataclasses.replace(
            payroll.coverage,
            calculation_scope=(
                ScopeItem(
                    feature="overtime",
                    calculation_status="computed",
                    integration_status="included_in_totals",
                    eligibility_status="engine_verified",
                    source_quality="verified_primary",
                ),
                ScopeItem(
                    feature="irpef",
                    calculation_status="computed",
                    integration_status="included_in_totals",
                    eligibility_status="engine_verified",
                    source_quality="verified_primary",
                ),
            ),
        )
        result = dataclasses.replace(payroll, coverage=new_coverage)
        d = result.to_dict()
        raw_scope = cast("list[object]", d["coverage"]["calculation_scope"])  # type: ignore[index]
        assert raw_scope == [
            {
                "feature": "overtime",
                "calculation_status": "computed",
                "integration_status": "included_in_totals",
                "eligibility_status": "engine_verified",
                "source_quality": "verified_primary",
                "assumptions": [],
            },
            {
                "feature": "irpef",
                "calculation_status": "computed",
                "integration_status": "included_in_totals",
                "eligibility_status": "engine_verified",
                "source_quality": "verified_primary",
                "assumptions": [],
            },
        ]

    def test_warnings_serialised_as_list(self, payroll: AnnualEstimate) -> None:
        """Warnings tuple is serialised as a plain list of strings."""
        new_coverage = dataclasses.replace(
            payroll.coverage, warnings=("something was skipped",)
        )
        result = dataclasses.replace(payroll, coverage=new_coverage)
        d = result.to_dict()
        assert d["coverage"]["warnings"] == ["something was skipped"]  # type: ignore[index]


class TestFromDictHasDefault:
    """from_dict skips fields with defaults missing from dict."""

    def test_roundtrip_without_schema_version(self, payroll: AnnualEstimate) -> None:
        """A dict lacking schema_version round-trips via from_dict using the default."""
        d = payroll.to_dict()
        d.pop("schema_version")
        rebuilt = AnnualEstimate.from_dict(d)
        assert rebuilt.net_annual == payroll.net_annual
        assert rebuilt.coverage.warnings == payroll.coverage.warnings
        assert rebuilt.coverage.calculation_scope == payroll.coverage.calculation_scope
        assert rebuilt.coverage.status == payroll.coverage.status

    def test_from_dict_with_scope_items(self, payroll: AnnualEstimate) -> None:
        """from_dict reconstructs ScopeItem entries from a serialised scope."""
        scope = (
            ScopeItem(
                feature="overtime",
                calculation_status="excluded",
                integration_status="n_a",
                eligibility_status="n_a",
                source_quality="n_a",
            ),
        )
        new_coverage = dataclasses.replace(payroll.coverage, calculation_scope=scope)
        result = dataclasses.replace(payroll, coverage=new_coverage)
        d = result.to_dict()
        rebuilt = AnnualEstimate.from_dict(d)
        assert rebuilt.coverage.calculation_scope == scope
