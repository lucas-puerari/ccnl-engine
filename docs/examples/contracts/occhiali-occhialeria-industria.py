"""Usage example: CCNL Occhiali e Occhialeria — Industria (ANFAO)."""

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
            level_code="4",
        ),
        employment=Employment(
            ccnl="occhiali-occhialeria-industria.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 3, 1),
        ),
    )
).result
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost_annual} EUR")
