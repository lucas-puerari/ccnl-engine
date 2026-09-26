"""Reference cases in ``tests/fixtures/expected/`` run through ``PayrollEngine``.

Each case pins the salary table components of one regular run to the signed
table its ``source`` cites: base salary, fixed allowances and period gross.
Only values read from that source are asserted; net pay, taxes and employer
cost depend on the engine's own rules and are owned by the oracle and legal
scenario tests instead.
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    PeriodResult,
)

_CASES_DIR = Path(__file__).parents[2] / "fixtures" / "expected"
_CASE_FILES = sorted(_CASES_DIR.glob("*.json"))
_ENGINE = PayrollEngine.bundled()


def _run(inputs: dict[str, Any]) -> PeriodResult:
    year = int(inputs["year"])
    month = int(inputs["month"])
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=year, month=month),
            payment_date=date(year, month, 27),
            employment=Employment(
                ccnl_slug=inputs["ccnl_slug"], level_code=inputs["level_code"]
            ),
            employer=EmployerProfile(headcount=Headcount(int(inputs["headcount"]))),
        )
    )


def _sum_of(result: PeriodResult, kind: str) -> Decimal:
    return sum(
        (item.amount for item in result.pay_items if item.kind == kind), Decimal(0)
    )


@pytest.mark.parametrize("path", _CASE_FILES, ids=lambda p: p.stem)
def test_reference_case_matches_cited_table(path: Path) -> None:
    """Base salary, allowances and gross equal the values of the cited table."""
    case = json.loads(path.read_text(encoding="utf-8"))
    expected = {key: Decimal(value) for key, value in case["expected"].items()}

    result = _run(case["inputs"])

    actual = {
        "base_salary": _sum_of(result, "base_salary_earning"),
        "fixed_allowances": _sum_of(result, "fixed_allowance_earning"),
        "period_gross": result.period_gross,
    }
    assert actual == expected
