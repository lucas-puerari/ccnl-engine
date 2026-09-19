"""Usage example: CCNL Autostrade e Trafori Concessionari (I192)."""

from datetime import date

from ccnl_engine import (
    Employee,
    Employer,
    Employment,
    AnnualPayrollScenario,
    Permanent,
    estimate_annual,
)

p = estimate_annual(
    AnnualPayrollScenario(
        employee=Employee(
            level_code="B",
        ),
        employment=Employment(
            ccnl="autostrade-trafori.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 8, 1),
        ),
    )
).result
print(f"Gross monthly: {p.earnings.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost.employer_cost_annual} EUR")
