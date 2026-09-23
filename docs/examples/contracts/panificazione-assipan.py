"""Usage example: CCNL Panificazione e Settori Affini — Industria (Assipan/Fiesa)."""

from datetime import date

from ccnl_engine import (
    Employee,
    Employer,
    Employment,
    AnnualEstimateInput,
    Permanent,
)
from ccnl_engine.engine.payroll.service.orchestrator import estimate_annual

p = estimate_annual(
    AnnualEstimateInput(
        employee=Employee(
            level_code="IIIB",
        ),
        employment=Employment(
            ccnl="panificazione-assipan.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 9, 1),
        ),
    )
).result
print(f"Gross monthly: {p.earnings.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost.employer_cost_annual} EUR")
