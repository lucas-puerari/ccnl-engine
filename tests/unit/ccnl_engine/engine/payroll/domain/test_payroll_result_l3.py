"""Coverage tests for L3 payroll_result paths (ScopeItem, to_dict, from_dict)."""

from __future__ import annotations

import dataclasses
from datetime import date
from typing import cast

import pytest

from ccnl_engine import (
    Employee,
    Employer,
    Employment,
    PayrollScenario,
    Permanent,
    compute,
)
from ccnl_engine.engine.payroll.domain.payroll_result import (
    PayrollResult,
    ScopeItem,
    _coerce_scalar,
)


@pytest.fixture(scope="module")
def payroll() -> PayrollResult:
    """Return a real PayrollResult for tests.

    Returns:
        A PayrollResult for CCNL Metalmeccanico Federmeccanica level C2.
    """
    return compute(
        PayrollScenario(
            employee=Employee(level_code="C2"),
            employment=Employment(
                ccnl="metalmeccanico-federmeccanica.json",
                contract=Permanent(),
                employer=Employer(num_employees=50),
                calculation_date=date(2026, 9, 1),
            ),
        )
    ).result


class TestScopeItemCoerce:
    """_coerce_scalar ScopeItem branch (payroll_result.py:62) is exercised here."""

    def test_coerce_scope_item_from_dict(self) -> None:
        """ScopeItem is reconstructed from a plain dict."""
        raw = {"feature": "overtime", "status": "verified"}
        result = _coerce_scalar(raw, ScopeItem)
        assert isinstance(result, ScopeItem)
        assert result.feature == "overtime"
        assert result.status == "verified"

    def test_coerce_non_dict_passthrough(self) -> None:
        """A non-dict raw value for ScopeItem is returned unchanged."""
        result = _coerce_scalar("already_string", ScopeItem)
        assert result == "already_string"


class TestToDictScopeItem:
    """to_dict tuple branch: dataclasses.is_dataclass path (lines 278-281)."""

    def test_scope_items_serialised_as_dicts(self, payroll: PayrollResult) -> None:
        """calculation_scope ScopeItem entries are serialised via asdict()."""
        result = dataclasses.replace(
            payroll,
            calculation_scope=(
                ScopeItem(feature="overtime", status="verified"),
                ScopeItem(feature="irpef", status="verified"),
            ),
        )
        d = result.to_dict()
        raw_scope = cast("list[object]", d["calculation_scope"])
        assert raw_scope == [
            {"feature": "overtime", "status": "verified"},
            {"feature": "irpef", "status": "verified"},
        ]

    def test_warnings_serialised_as_list(self, payroll: PayrollResult) -> None:
        """Warnings tuple is serialised as a plain list of strings."""
        result = dataclasses.replace(payroll, warnings=("something was skipped",))
        d = result.to_dict()
        assert d["warnings"] == ["something was skipped"]


class TestFromDictHasDefault:
    """from_dict skips fields with defaults missing from dict (line 318)."""

    def test_roundtrip_missing_l3_defaults(self, payroll: PayrollResult) -> None:
        """A dict lacking the new L3 fields round-trips via from_dict."""
        d = payroll.to_dict()
        # Remove all fields that have defaults to simulate an old serialised dict.
        for field in dataclasses.fields(PayrollResult):
            if (
                field.default is not dataclasses.MISSING
                or field.default_factory is not dataclasses.MISSING
            ):
                d.pop(field.name, None)

        rebuilt = PayrollResult.from_dict(d)
        # Required fields match.
        assert rebuilt.gross_monthly == payroll.gross_monthly
        assert rebuilt.net_annual == payroll.net_annual
        # Defaulted fields come back as their defaults.
        assert rebuilt.warnings == ()
        assert rebuilt.calculation_scope == ()
        assert rebuilt.status == "partial"

    def test_from_dict_with_scope_items(self, payroll: PayrollResult) -> None:
        """from_dict reconstructs ScopeItem entries from a serialised scope."""
        scope = (ScopeItem(feature="overtime", status="excluded"),)
        result = dataclasses.replace(payroll, calculation_scope=scope)
        d = result.to_dict()
        rebuilt = PayrollResult.from_dict(d)
        assert rebuilt.calculation_scope == scope
