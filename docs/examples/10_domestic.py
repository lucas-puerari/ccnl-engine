"""Domestic work (CCNL colf): flat per-hour INPS contributions."""

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    ContributableHours,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    WeeklyHours,
)

engine = PayrollEngine.bundled()

# Non-convivente domestic worker, level B, 25 h/week, 108 hours in January
result = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        employment=Employment(
            ccnl_slug="lavoro-domestico-non-convivente.json",
            level_code="B",
            weekly_hours=WeeklyHours(25),
        ),
        employer=EmployerProfile(headcount=Headcount(1)),
        facts=PeriodFacts(contributable_hours=ContributableHours(Decimal(108))),
    )
)

print(f"Period gross:         {result.period_gross}")
print(f"Period net:           {result.period_net}")
print(f"Period employer cost: {result.period_employer_cost}")

cb = result.contribution_breakdown
print(f"Employee INPS:        {cb.employee}")
print(f"Employer INPS:        {cb.employer}")
