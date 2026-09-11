"""Usage example: CCNL Autostrade e Trafori Concessionari (I192)."""

from datetime import date

from ccnl_engine import (
    Employee,
    Employer,
    Employment,
    PayrollScenario,
    Permanent,
    compute,
)

p = compute(
    PayrollScenario(
        employee=Employee(
            level_code="B",
        ),
        employment=Employment(
            ccnl="autostrade-trafori.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            calculation_date=date(2026, 8, 1),
        ),
    )
)
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost_annual} EUR")
