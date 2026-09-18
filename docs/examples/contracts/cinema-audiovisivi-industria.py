"""Usage example: CCNL Industrie Cineaudiovisive (ANICA, G111)."""

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
            ccnl="cinema-audiovisivi-industria.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 7, 1),
        ),
    )
)
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost_annual} EUR")
