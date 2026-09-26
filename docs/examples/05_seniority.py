"""Seniority allowances: pass elapsed months to unlock scatti di anzianità."""

from datetime import date

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    SeniorityMonths,
    WorkerCategory,
)

engine = PayrollEngine.bundled()
run = PayrollRun.regular(year=2026, month=1)
payment = date(2026, 1, 28)
employer = EmployerProfile(headcount=Headcount(100))

# No seniority (new hire)
result_0 = engine.calculate_period(
    PeriodInput(
        run=run,
        payment_date=payment,
        employment=Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json", level_code="C3"
        ),
        employer=employer,
    )
)

# 5 years of service (60 months) → multiple scatti
result_60 = engine.calculate_period(
    PeriodInput(
        run=run,
        payment_date=payment,
        employment=Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            seniority_months=SeniorityMonths(60),
        ),
        employer=employer,
    )
)

print(f"Gross (no seniority):  {result_0.period_gross}")
print(f"Gross (60 months):     {result_60.period_gross}")
print(f"Seniority uplift:      {result_60.period_gross - result_0.period_gross}")

# Category-specific increments: FISE level 2 at 60 months of service pays
# 56.66 to an operaio and 62.62 to an impiegato.
for category in (WorkerCategory.OPERAIO, WorkerCategory.IMPIEGATO):
    result = engine.calculate_period(
        PeriodInput(
            run=run,
            payment_date=payment,
            employment=Employment(
                ccnl_slug="servizi-postali-appalto-fise.json",
                level_code="2",
                seniority_months=SeniorityMonths(60),
                category=category,
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
        )
    )
    print(f"FISE L2 {category}: {result.period_gross}")
