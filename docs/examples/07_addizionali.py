"""Regional and municipal surtax: pass regione and comune_belfiore."""

from datetime import date

from ccnl_engine import (
    Employer,
    EmploymentFacts,
    Headcount,
    PayrollEngine,
    PayrollRequest,
    PayrollRun,
)

engine = PayrollEngine.bundled()

# No surtax (default)
result_no_surtax = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        employment_facts=EmploymentFacts(),
        employer=Employer(headcount=Headcount(100)),
    )
)

# Emilia-Romagna region + Modena municipality
result_surtax = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        employment_facts=EmploymentFacts(),
        employer=Employer(headcount=Headcount(100)),
        regione="IT-45",
        comune_belfiore="F257",  # Modena
    )
)

print(f"Net (no surtax):   {result_no_surtax.period_net}")
print(f"Net (IT-45 Modena): {result_surtax.period_net}")
print(f"Surtax withheld:   {result_no_surtax.period_net - result_surtax.period_net}")
print(f"Status:            {result_surtax.status}")  # final: both tables known
for decision in result_surtax.decisions:
    print(f"  {decision.capability}: {decision.reason_code} {decision.amount}")
