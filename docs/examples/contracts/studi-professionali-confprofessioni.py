"""Usage example: CCNL per i dipendenti degli studi e delle attività professionali (Confprofessioni)."""

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
            level_code="3S",
        ),
        employment=Employment(
            ccnl="studi-professionali-confprofessioni.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            date=date(2026, 9, 1),
        ),
    )
)
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost_annual} EUR")
