"""Usage example: CCNL Scuole Materne FISM."""

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
            level_code="V",
        ),
        employment=Employment(
            ccnl="scuole-materne-fism.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            date=date(2026, 9, 1),
        ),
    )
)
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost_annual} EUR")
