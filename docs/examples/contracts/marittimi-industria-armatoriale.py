"""Usage example: CCNL Marittimi — Industria Armatoriale (CONFITARMA)."""

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
            level_code="IV",
        ),
        employment=Employment(
            ccnl="marittimi-industria-armatoriale.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 7, 1),
        ),
    )
).result
print(f"Gross monthly: {p.earnings.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost.employer_cost_annual} EUR")
