"""Seniority allowances: pass elapsed months to unlock scatti di anzianità."""

from datetime import date

from ccnl_engine import (
    Employer,
    EmploymentFacts,
    Headcount,
    PayrollEngine,
    PayrollRequest,
    PayrollRun,
    WorkerCategory,
)

engine = PayrollEngine.bundled()

# No seniority (new hire)
result_0 = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        employment_facts=EmploymentFacts(),
        employer=Employer(headcount=Headcount(100)),
    )
)

# 5 years of service (60 months) → multiple scatti
result_60 = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        employment_facts=EmploymentFacts(
            seniority_months=60,
        ),
        employer=Employer(headcount=Headcount(100)),
    )
)

print(f"Gross (no seniority):  {result_0.period_gross}")
print(f"Gross (60 months):     {result_60.period_gross}")
print(f"Seniority uplift:      {result_60.period_gross - result_0.period_gross}")

# Category-specific increments: FISE level 2 at 60 months of service pays
# 56.66 to an operaio and 62.62 to an impiegato.
for category in (WorkerCategory.OPERAIO, WorkerCategory.IMPIEGATO):
    result = engine.calculate(
        PayrollRequest(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug="servizi-postali-appalto-fise.json",
            level_code="2",
            employment_facts=EmploymentFacts(seniority_months=60, category=category),
        )
    )
    print(f"FISE L2 {category}: {result.period_gross}")
