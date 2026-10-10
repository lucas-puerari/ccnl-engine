"""Reference cases in ``tests/fixtures/reference_tables/`` run through the engine.

Each case pins the salary table components of one regular run to the signed
table its ``source`` cites: base salary, fixed allowances and period gross.
Only values read from that source are asserted, each case naming those it
pins (an observed payslip pins the base salary only: its allowances and
gross carry provincial and individual items); net pay, taxes and employer
cost depend on the engine's own rules and are owned by the oracle and legal
scenario tests instead.  A case may state ``weekly_hours`` and
``contributable_hours`` among its inputs: a domestic CCNL needs both to
select and charge its hourly contributions.
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
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import ContributableHours, Permanent, WeeklyHours

_CASES_DIR = Path(__file__).parents[2] / "fixtures" / "reference_tables"
_CASE_FILES = sorted(_CASES_DIR.glob("*.json"))
_ENGINE = PayrollEngine.bundled()


def _run(inputs: dict[str, Any]) -> PeriodResult:
    year = int(inputs["year"])
    month = int(inputs["month"])
    weekly = inputs.get("weekly_hours")
    hours = inputs.get("contributable_hours")
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=year, month=month),
            payment_date=date(year, month, 27),
            employment=Employment(
                ccnl_slug=inputs["ccnl_slug"],
                level_code=inputs["level_code"],
                contract_type=Permanent(),
                weekly_hours=None if weekly is None else WeeklyHours(int(weekly)),
            ),
            employer=EmployerProfile(headcount=Headcount(int(inputs["headcount"]))),
            facts=PeriodFacts(
                contributable_hours=(
                    None if hours is None else ContributableHours(Decimal(hours))
                )
            ),
        )
    )


def _sum_of(result: PeriodResult, kind: str) -> Decimal:
    return sum(
        (item.amount for item in result.pay_items if item.kind == kind), Decimal(0)
    )


@pytest.mark.parametrize("path", _CASE_FILES, ids=lambda p: p.stem)
def test_reference_case_matches_cited_table(path: Path) -> None:
    """The components a case pins equal the values of its cited source."""
    case = json.loads(path.read_text(encoding="utf-8"))
    expected = {key: Decimal(value) for key, value in case["expected"].items()}

    result = _run(case["inputs"])

    actual = {
        "base_salary": _sum_of(result, "base_salary_earning"),
        "fixed_allowances": _sum_of(result, "fixed_allowance_earning"),
        "period_gross": result.period_gross,
    }
    assert {key: actual[key] for key in expected} == expected
