"""Usage example: CCNL Cemento, Calce e Gesso — Industria (Federbeton)."""

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
            level_code="AS3",
        ),
        employment=Employment(
            ccnl="cemento-calce-gesso-industria.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            date=date(2026, 10, 1),
        ),
    )
)
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost_annual} EUR")
