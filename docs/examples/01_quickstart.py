"""Quickstart: compute one payroll period with PayrollEngine."""

from datetime import date

from ccnl_engine import EmploymentFacts, PayrollEngine, PayrollRequest, PayrollRun

engine = PayrollEngine.bundled()

result = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="commercio-confcommercio.json",
        level_code="4",
        employment_facts=EmploymentFacts(num_employees=50),
    )
)

print(f"Gross:  {result.period_gross} EUR")
print(f"Net:    {result.period_net} EUR")
print(f"Cost:   {result.period_employer_cost} EUR")
