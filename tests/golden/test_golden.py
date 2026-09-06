"""Golden tests: compute() output must match pre-recorded expected values exactly."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from ccnl_engine.contract.domain.ccnl import TaxSector
from ccnl_engine.contract.service.loaders import load_ccnl
from ccnl_engine.payroll.domain.employee import (
    ContractPosition,
    Employee,
    RalOverride,
    SalaryOverrides,
    SeniorityByCount,
    TaxProfile,
    WorkArrangement,
)
from ccnl_engine.payroll.domain.employment import Apprentice, FixedTerm, Permanent
from ccnl_engine.payroll.service.orchestrator import compute
from ccnl_engine.surtax.service.loaders import load_surtax_rules
from ccnl_engine.tax.service.loaders import load_year_rules

if TYPE_CHECKING:
    from ccnl_engine.surtax.domain.rules import SurtaxRules

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
        regione = inputs.get("regione")
        comune_belfiore = inputs.get("comune_belfiore")
        surtax: SurtaxRules | None = None
        if regione is not None or comune_belfiore is not None:
            surtax = load_surtax_rules(inputs["year"])

        seniority_count_raw = int(inputs["seniority_count"])
        negotiated_ral_raw = inputs["negotiated_ral"]
        ivs_ceiling_applies = bool(inputs.get("ivs_ceiling_applies", False))

        seniority = (
            SeniorityByCount(seniority_count_raw) if seniority_count_raw else None
        )
        arrangement = WorkArrangement(
            part_time_pct=Decimal(inputs["part_time_pct"]),
            seniority=seniority,
            weekly_hours=(
                Decimal(str(weekly_hours_raw)) if weekly_hours_raw is not None else None
            ),
        )
        tax = (
            TaxProfile(
                regione=regione,
                comune_belfiore=comune_belfiore,
                ivs_ceiling_applies=ivs_ceiling_applies,
            )
            if regione is not None or comune_belfiore is not None or ivs_ceiling_applies
            else None
        )
        agreement = (
            SalaryOverrides(ral_override=RalOverride(Decimal(negotiated_ral_raw)))
            if negotiated_ral_raw is not None
            else None
        )

        result = compute(
            ccnl,
            rules,
            Employee(
                position=ContractPosition(
                    level_code=inputs["level_code"],
                    as_of=as_of,
                    employment=employment,
                    category=inputs.get("category"),
                ),
                arrangement=arrangement,
                tax=tax,
                agreement=agreement,
            ),
            surtax=surtax,
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
