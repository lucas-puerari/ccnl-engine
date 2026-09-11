"""Usage example: CCNL Occhiali e Occhialeria — Industria (ANFAO)."""

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
            ccnl="occhiali-occhialeria-industria.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            calculation_date=date(2026, 3, 1),
        ),
    )
)
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost_annual} EUR")
