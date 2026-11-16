"""The INAIL premium of the operai agricoli at the sector rate.

Operai agricoli florovivaisti Area2, March 2026: INPS collects the INAIL
premium of agriculture at 8.50% of the contribution base (circ. 43/2026,
allegato 1), the default when the employer states no rate of its own.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

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
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.inputs import EmploymentPeriod, Permanent, WeeklyHours
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

_ENGINE = PayrollEngine.bundled()


def _run(category: WorkerCategory | None, rate: Decimal | None) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="operai-agricoli-florovivaisti",
                level_code="Area2",
                seniority=new_hire(2023),
                roles=frozenset(),
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2023, 3, 1)),
                weekly_hours=WeeklyHours(Decimal(39)),
                full_time_weekly_hours=WeeklyHours(Decimal(39)),
                category=category,
            ),
            employer=EmployerProfile(headcount=Headcount(20), inail_rate=rate),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="A005"),
        )
    )


def _rates(result: PeriodResult) -> list[str]:
    return [
        str(d.inputs["rate_per_mille"])
        for d in result.decisions
        if d.capability == "inail"
    ]


@pytest.mark.parametrize(
    ("category", "rate", "expected"),
    [
        (WorkerCategory.OPERAIO, None, ["85.000"]),
        (WorkerCategory.OPERAIO, Decimal(30), ["30"]),
        (None, None, []),
    ],
    ids=["sector-default", "stated-rate-wins", "no-category"],
)
def test_the_sector_rate_of_the_operai(
    category: WorkerCategory | None, rate: Decimal | None, expected: list[str]
) -> None:
    """The sector rate fills only a missing employer rate of a stated operaio."""
    assert _rates(_run(category, rate)) == expected


def test_the_premium_is_the_base_at_the_sector_rate() -> None:
    """8.50% of the INPS base of the run."""
    (decision,) = (
        d
        for d in _run(WorkerCategory.OPERAIO, None).decisions
        if d.capability == "inail"
    )
    base = Decimal(str(decision.inputs["base"]))
    assert base > 0
    assert decision.amount == (base * Decimal("0.085")).quantize(Decimal("0.01"))
