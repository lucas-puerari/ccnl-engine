"""Golden tests: compute() output must match pre-recorded expected values exactly."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from ccnl_engine.contracts.loaders import load_ccnl
from ccnl_engine.engine.compute import Scenario, compute
from ccnl_engine.models.ccnl import TaxSector
from ccnl_engine.models.employment import Apprentice, FixedTerm, Permanent
from ccnl_engine.tax.loaders import load_year_rules

_CASES_DIR = Path(__file__).parent / "cases"
_CASE_FILES = sorted(_CASES_DIR.glob("*.json"))


def _build_employment(inputs: dict[str, Any]) -> Permanent | FixedTerm | Apprentice:
    """Construct an Employment model from the golden case inputs dict.

    Returns:
        A Permanent, FixedTerm, or Apprentice instance based on employment_type.
    """
    emp_type = inputs["employment_type"]
    if emp_type == "permanent":
        return Permanent()
    if emp_type == "fixed_term":
        return FixedTerm()
    months = inputs["months_elapsed"]
    return Apprentice(months_elapsed=months)


class TestGolden:
    """Each golden JSON must match compute() output field-by-field."""

    @pytest.mark.parametrize("case_file", _CASE_FILES, ids=lambda p: p.stem)
    def test_golden(self, case_file: Path) -> None:
        """Run compute() and compare every field against the golden JSON."""
        case = json.loads(case_file.read_text(encoding="utf-8"))
        inputs = case["inputs"]
        expected = case["expected"]

        ccnl = load_ccnl(inputs["ccnl_file"])
        num_employees = int(inputs["num_employees"])
        rules = load_year_rules(
            inputs["year"],
            TaxSector(inputs["tax_sector"]),
            num_employees,
        )
        employment = _build_employment(inputs)
        as_of = date.fromisoformat(inputs["as_of"])

        weekly_hours_raw = inputs.get("weekly_hours")
        result = compute(
            ccnl,
            rules,
            Scenario(
                level_code=inputs["level_code"],
                as_of=as_of,
                employment=employment,
                num_employees=num_employees,
                part_time_pct=Decimal(inputs["part_time_pct"]),
                seniority_count=int(inputs["seniority_count"]),
                negotiated_ral=(
                    Decimal(inputs["negotiated_ral"])
                    if inputs["negotiated_ral"] is not None
                    else None
                ),
                weekly_hours=(
                    Decimal(str(weekly_hours_raw))
                    if weekly_hours_raw is not None
                    else None
                ),
                ivs_ceiling_applies=bool(inputs.get("ivs_ceiling_applies", False)),
            ),
        )

        # Compare each field in expected against the live Payslip
        for field, raw_value in expected.items():
            actual = getattr(result, field)
            if raw_value is None:
                assert actual is None, f"{field}: expected None, got {actual!r}"
            elif isinstance(actual, Decimal):
                assert actual == Decimal(raw_value), (
                    f"{field}: expected {raw_value!r}, got {actual!r}"
                )
            elif isinstance(actual, frozenset):
                # Stored in JSON as a sorted list of strings for determinism.
                actual_sorted = sorted(str(v) for v in actual)
                assert actual_sorted == raw_value, (
                    f"{field}: expected {raw_value!r}, got {actual_sorted!r}"
                )
            else:
                assert actual == raw_value, (
                    f"{field}: expected {raw_value!r}, got {actual!r}"
                )
