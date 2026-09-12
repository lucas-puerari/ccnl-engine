"""Usage example: CCNL Ortofrutticoli ed Agrumari (Import-Export)."""

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
            ccnl="ortofrutticoli-agrumari.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            calculation_date=date(2026, 6, 1),
        ),
    )
)
print(f"Gross monthly: {p.result.gross_monthly} EUR")
print(f"Net annual:    {p.result.net_annual} EUR")
print(f"Employer cost: {p.result.employer_cost_annual} EUR")
