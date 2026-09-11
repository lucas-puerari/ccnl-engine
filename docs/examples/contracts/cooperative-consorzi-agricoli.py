"""Usage example: CCNL Cooperative e Consorzi Agricoli (A016)."""

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
            level_code="3",
        ),
        employment=Employment(
            ccnl="cooperative-consorzi-agricoli.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            calculation_date=date(2026, 5, 1),
        ),
    )
)
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost_annual} EUR")
