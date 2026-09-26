"""Domestic work (CCNL colf): flat per-hour INPS contributions."""

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    Employer,
    EmploymentFacts,
    Headcount,
    PayrollEngine,
    PayrollRequest,
    PayrollRun,
)

engine = PayrollEngine.bundled()

# Non-convivente domestic worker, level B, 25 h/week, 108 hours in January
result = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="lavoro-domestico-non-convivente.json",
        level_code="B",
        employment_facts=EmploymentFacts(
            weekly_hours=25,
            contributable_hours=Decimal(108),
        ),
        employer=Employer(headcount=Headcount(1)),
    )
)

print(f"Period gross:         {result.period_gross}")
print(f"Period net:           {result.period_net}")
print(f"Period employer cost: {result.period_employer_cost}")

cb = result.contribution_breakdown
print(f"Employee INPS:        {cb.employee}")
print(f"Employer INPS:        {cb.employer}")
