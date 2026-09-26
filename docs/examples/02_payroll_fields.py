"""Payroll result fields: gross, net, contributions, pay items."""

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

result = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=6),
        payment_date=date(2026, 6, 27),
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        employment_facts=EmploymentFacts(),
        employer=Employer(headcount=Headcount(100)),
    )
)

print(f"Period gross:         {result.period_gross}")
print(f"Period net:           {result.period_net}")
print(f"Employer cost:        {result.period_employer_cost}")

cb = result.contribution_breakdown
print(f"Employee INPS:        {cb.employee}")
print(f"Employer INPS:        {cb.employer}")

tc = result.tax_computation
print(f"IRPEF withheld:       {tc.ordinary_tax}")
print(f"Trattamento integr.:  {tc.trattamento_integrativo}")
for comp in tc.components:
    print(f"  {comp.name}: {comp.amount} ({comp.fonte})")

for item in result.pay_items:
    print(f"  {item.kind}: {item.amount}")
