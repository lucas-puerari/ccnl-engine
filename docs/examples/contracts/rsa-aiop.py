"""Usage example: CCNL RSA e Strutture Residenziali AIOP (T091)."""

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
            level_code="D2",
        ),
        employment=Employment(
            ccnl="rsa-aiop.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            date=date(2026, 1, 1),
        ),
    )
)
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost_annual} EUR")
