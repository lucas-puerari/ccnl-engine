"""Hand oracle: ASIM of the Multiservizi (art. 69), June 2026.

6 EUR a month of the employer above 28 hours a week, 4 EUR up to 28; a
health fund, 10% INPS solidarity: 0.60 and 0.40.
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
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
)
from ccnl_engine.results import AccountKind

_HIRED = date(2025, 1, 1)


def _run(hours: int | None) -> PeriodResult:
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=Employment(
                ccnl_id="multiservizi-anip",
                level_code="2",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                weekly_hours=None if hours is None else WeeklyHours(Decimal(hours)),
                full_time_weekly_hours=None
                if hours is None
                else WeeklyHours(Decimal(40)),
            ),
            employer=EmployerProfile(
                headcount=Headcount(30), contractual_funds=frozenset({"asim"})
            ),
        )
    )


@pytest.mark.parametrize(
    ("hours", "employer", "solidarity"),
    [(None, "6.00", "0.60"), (29, "6.00", "0.60"), (28, "4.00", "0.40")],
)
def test_asim_by_weekly_hours(
    hours: int | None, employer: str, solidarity: str
) -> None:
    """Above 28 hours 6 EUR, up to 28 hours 4 EUR, no worker share."""
    result = _run(hours)
    posted = [
        e.amount
        for e in result.ledger_entries
        if e.account is AccountKind.BILATERAL_FUND_EMPLOYER
    ]
    paid = [
        e.amount for e in result.ledger_entries if e.entry_id.endswith("_solidarity")
    ]

    assert posted == [Decimal(employer)]
    assert paid == [Decimal(solidarity)]
    assert not any(
        e.account is AccountKind.BILATERAL_FUND_EMPLOYEE for e in result.ledger_entries
    )
