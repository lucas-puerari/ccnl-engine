"""Usage example: CCNL Edilizia PMI CONFAPI ANIEM (F018)."""

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
            level_code="4",
        ),
        employment=Employment(
            ccnl="edilizia-pmi-confapi-aniem.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 1, 1),
        ),
    )
)
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost_annual} EUR")
