"""Apprenticeship: reduced salary percentage from CCNL percentage track."""

from datetime import date

from ccnl_engine import (
    Apprentice,
    Employer,
    EmploymentFacts,
    Headcount,
    PayrollEngine,
    PayrollRequest,
    PayrollRun,
)

engine = PayrollEngine.bundled()

# Month 0: start of apprenticeship (lowest percentage)
result_start = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="commercio-confcommercio.json",
        level_code="4",
        employment_facts=EmploymentFacts(
            contract_type=Apprentice(months_elapsed=0),
        ),
        employer=Employer(headcount=Headcount(50)),
    )
)

# Month 24: further into the track (higher percentage)
result_24 = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="commercio-confcommercio.json",
        level_code="4",
        employment_facts=EmploymentFacts(
            contract_type=Apprentice(months_elapsed=24),
        ),
        employer=Employer(headcount=Headcount(50)),
    )
)

print(f"Gross at month 0:   {result_start.period_gross}")
print(f"Gross at month 24:  {result_24.period_gross}")
