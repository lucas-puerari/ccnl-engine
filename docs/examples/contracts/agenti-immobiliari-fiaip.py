"""Usage example: CCNL Agenti Immobiliari Professionali FIAIP (H0B1)."""

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
            ccnl="agenti-immobiliari-fiaip.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            calculation_date=date(2026, 1, 1),
        ),
    )
)
print(f"Gross monthly: {p.result.gross_monthly} EUR")
print(f"Net annual:    {p.result.net_annual} EUR")
print(f"Employer cost: {p.result.employer_cost_annual} EUR")
