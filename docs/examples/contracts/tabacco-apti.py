"""Usage example: CCNL Tabacco Lavorazione Foglia Secca (APTI, E042)."""

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
            level_code="4A",
        ),
        employment=Employment(
            ccnl="tabacco-apti.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 1, 1),
        ),
    )
).result
print(f"Gross monthly: {p.earnings.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost.employer_cost_annual} EUR")
