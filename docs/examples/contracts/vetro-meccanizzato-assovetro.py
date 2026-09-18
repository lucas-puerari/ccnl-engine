"""Usage example: CCNL Vetro Meccanizzato Settori Meccanizzati (Assovetro, B132)."""

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
            level_code="C",
        ),
        employment=Employment(
            ccnl="vetro-meccanizzato-assovetro.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 1, 1),
        ),
    )
).result
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost_annual} EUR")
