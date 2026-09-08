"""Usage example: CCNL Vigilanza Privata FEDERDAT — GPG (HV17)."""

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
            level_code="III",
        ),
        employment=Employment(
            ccnl="vigilanza-privata-federdat-gpg.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            date=date(2026, 4, 1),
        ),
    )
)
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost_annual} EUR")
