"""Seniority allowances: pass elapsed months to unlock scatti di anzianità."""

from datetime import date

from ccnl_engine import EmploymentFacts, PayrollEngine, PayrollRequest, PayrollRun

engine = PayrollEngine.bundled()

# No seniority (new hire)
result_0 = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        employment_facts=EmploymentFacts(num_employees=100),
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
            num_employees=100,
            seniority_months=60,
        ),
    )
)

print(f"Gross (no seniority):  {result_0.period_gross}")
print(f"Gross (60 months):     {result_60.period_gross}")
print(f"Seniority uplift:      {result_60.period_gross - result_0.period_gross}")
