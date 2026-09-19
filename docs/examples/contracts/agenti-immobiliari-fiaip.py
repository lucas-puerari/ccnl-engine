"""Usage example: CCNL Agenti Immobiliari Professionali FIAIP (H0B1)."""

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
            level_code="III",
        ),
        employment=Employment(
            ccnl="agenti-immobiliari-fiaip.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 1, 1),
        ),
    )
)
print(f"Gross monthly: {p.result.earnings.gross_monthly} EUR")
print(f"Net annual:    {p.result.net_annual} EUR")
print(f"Employer cost: {p.result.employer_cost.employer_cost_annual} EUR")
