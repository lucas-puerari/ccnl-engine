"""Usage example: CCNL Gas e Acqua — Utilitalia/Proxigas/Anfida/Assogas."""

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
            level_code="5",
        ),
        employment=Employment(
            ccnl="gas-acqua-utilitalia.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 9, 1),
        ),
    )
).result
print(f"Gross monthly: {p.earnings.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost.employer_cost_annual} EUR")
