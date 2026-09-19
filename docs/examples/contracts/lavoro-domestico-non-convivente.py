"""Usage example: CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (non conviventi)."""

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    Employee,
    Employer,
    Employment,
    AnnualEstimateInput,
    Permanent,
    estimate_annual,
)

p = estimate_annual(
    AnnualEstimateInput(
        employee=Employee(
            level_code="C",
            weekly_hours=Decimal(40),
        ),
        employment=Employment(
            ccnl="lavoro-domestico-non-convivente.json",
            contract=Permanent(),
            employer=Employer(num_employees=1),
            as_of=date(2026, 9, 1),
        ),
    )
).result
print(f"Gross monthly: {p.earnings.gross_monthly} EUR")
print(f"INPS employer annual: {p.contributions.inps_employer_annual} EUR")
print(f"Employer withholds IRPEF: {p.taxes.employer_withholds_irpef}")
