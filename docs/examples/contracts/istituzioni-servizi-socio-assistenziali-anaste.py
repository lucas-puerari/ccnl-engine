"""Usage example: CCNL Istituzioni e Servizi Socio-Assistenziali (ANASTE)."""

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
            level_code="6",
        ),
        employment=Employment(
            ccnl="istituzioni-servizi-socio-assistenziali-anaste.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            date=date(2026, 8, 1),
        ),
    )
)
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost_annual} EUR")
