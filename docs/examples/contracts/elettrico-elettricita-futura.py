"""Usage example: CCNL per i lavoratori delle imprese produttrici, distributrici di energia elettrica (Elettricita Futura)."""

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
            level_code="BS",
        ),
        employment=Employment(
            ccnl="elettrico-elettricita-futura.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            calculation_date=date(2026, 9, 1),
        ),
    )
)
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost_annual} EUR")
