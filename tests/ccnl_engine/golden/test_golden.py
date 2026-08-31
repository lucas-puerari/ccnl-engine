"""Golden tests: compute() output must match pre-recorded expected values exactly.

Each golden case is a JSON file in ``cases/``. The test loads the case, runs
:func:`~ccnl_engine.engine.compute.compute`, and compares every field in
``expected`` against the live output using exact :class:`~decimal.Decimal`
equality — no tolerance, since the computation is fully deterministic.

To regenerate a golden file after an intentional engine change, run
``compute()`` manually, inspect the output, and update the JSON. Never use
approximate comparison: a drift means a regression.
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from ccnl_engine.data import load_ccnl, load_year_rules
from ccnl_engine.engine.compute import compute
from ccnl_engine.models.ccnl import TaxSector
from ccnl_engine.models.employment import Apprentice, FixedTerm, Permanent

_CASES_DIR = Path(__file__).parent / "cases"
_CASE_FILES = sorted(_CASES_DIR.glob("*.json"))


def _build_employment(inputs: dict[str, Any]) -> Permanent | FixedTerm | Apprentice:
    """Construct an Employment model from the golden case inputs dict."""
    emp_type = inputs["employment_type"]
    if emp_type == "permanent":
        return Permanent(type="permanent")
    if emp_type == "fixed_term":
        return FixedTerm(type="fixed_term")
    months = inputs["months_elapsed"]
    return Apprentice(type="apprentice", months_elapsed=months)


@pytest.mark.parametrize("case_file", _CASE_FILES, ids=lambda p: p.stem)
def test_golden(case_file: Path) -> None:
    """Each golden JSON must match compute() output field-by-field."""
    case = json.loads(case_file.read_text(encoding="utf-8"))
    inputs = case["inputs"]
    expected = case["expected"]

    ccnl = load_ccnl(inputs["ccnl_file"])
    rules = load_year_rules(
        inputs["year"],
        TaxSector(inputs["tax_sector"]),
        int(inputs["num_employees"]),
    )
    employment = _build_employment(inputs)
    as_of = date.fromisoformat(inputs["as_of"])

    part_time_pct = Decimal(inputs["part_time_pct"])
    seniority_count = int(inputs["seniority_count"])
    negotiated_ral = (
        Decimal(inputs["negotiated_ral"])
        if inputs["negotiated_ral"] is not None
        else None
    )

    result = compute(
        ccnl,
        inputs["level_code"],
        as_of,
        rules,
        employment,
        part_time_pct=part_time_pct,
        seniority_count=seniority_count,
        negotiated_ral=negotiated_ral,
    )

    # Compare each field in expected against the live ComputationResult
    for field, raw_value in expected.items():
        actual = getattr(result, field)
        if raw_value is None:
            assert actual is None, f"{field}: expected None, got {actual!r}"
        elif isinstance(actual, Decimal):
            assert actual == Decimal(raw_value), (
                f"{field}: expected {raw_value!r}, got {actual!r}"
            )
        else:
            assert actual == raw_value, (
                f"{field}: expected {raw_value!r}, got {actual!r}"
            )
