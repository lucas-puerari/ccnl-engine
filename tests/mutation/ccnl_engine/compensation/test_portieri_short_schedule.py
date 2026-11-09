"""The 15% raise of a B5 cleaner working fewer than eight hours a week.

CCNL portieri Confedilizia, ipotesi of 30 October 2025 (sha256
4d08a1dd4a828e3d8da37a9eab21eca8b8ff81aa94d626d8365c95330b5f1e68), art.
122 c. 2 (PDF p. 75): for B5 "con orario di lavoro settimanale inferiore a
8 ore, il salario conglobato ... sarà maggiorato del 15%".  Tabella B
(p. 10): B5 conglobato 1264.51 in 2026, so the full-time allowance is
1264.51 x 15% = 189.68.  At 6 of 40 weekly hours it is
189.68 x 6 / 40 = 28.452, paid 28.45; at 8 hours nothing.
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
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import (
    EmploymentPeriod,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
)

_ENGINE = PayrollEngine.bundled()
_FULL_TIME = WeeklyHours(Decimal(40))


def _march(level_code: str, weekly_hours: WeeklyHours | None) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="portieri-fabbricati-confedilizia",
                level_code=level_code,
                seniority=SeniorityFact(0, date(2026, 1, 1), SenioritySource.PAYSLIP),
                weekly_hours=weekly_hours,
                full_time_weekly_hours=_FULL_TIME,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2026, 1, 1)),
            ),
            employer=EmployerProfile(headcount=Headcount(1)),
        )
    )


def _premium(result: PeriodResult) -> Decimal:
    return sum(
        (i.amount for i in result.pay_items if "B5_ORARIO_RIDOTTO" in i.item_id),
        Decimal(0),
    )


def test_six_weekly_hours_raise_the_b5_conglobato_by_15_percent() -> None:
    """189.68 x 6 / 40 = 28.45 on top of the proportioned conglobato."""
    assert _premium(_march("B5", WeeklyHours(Decimal(6)))) == Decimal("28.45")


@pytest.mark.parametrize(
    ("level_code", "hours"),
    [
        ("B5", WeeklyHours(Decimal(8))),
        ("B5", None),
        ("B4", WeeklyHours(Decimal(6))),
    ],
    ids=["eight-hours", "full-time", "other-level"],
)
def test_no_raise_outside_the_short_b5_schedule(
    level_code: str, hours: WeeklyHours | None
) -> None:
    """Exactly 8 hours, unstated hours and another B level earn nothing."""
    assert _premium(_march(level_code, hours)) == Decimal(0)
