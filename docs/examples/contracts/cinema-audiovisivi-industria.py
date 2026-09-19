"""Usage example: CCNL Industrie Cineaudiovisive (ANICA, G111)."""

from datetime import date

from ccnl_engine import (
    Employee,
    Employer,
    Employment,
    AnnualEstimateInput,
    Permanent,
    estimate_annual,
)

p = estimate_annual(
    AnnualEstimateInput(
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
).result
print(f"Gross monthly: {p.earnings.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost.employer_cost_annual} EUR")
