"""Fixed-term employment: NASpI addizionale applies."""

from datetime import date

from ccnl_engine import (
    EmployerProfile,
    Employment,
    FixedTerm,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)

engine = PayrollEngine.bundled()

result = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=3),
        payment_date=date(2026, 3, 27),
        employment=Employment(
            ccnl_slug="commercio-confcommercio.json",
            level_code="4",
            contract_type=FixedTerm(),
        ),
        employer=EmployerProfile(headcount=Headcount(50)),
    )
)

print(f"Period gross: {result.period_gross}")
print(f"Period net:   {result.period_net}")
print(f"Employer cost (includes NASpI addizionale): {result.period_employer_cost}")
