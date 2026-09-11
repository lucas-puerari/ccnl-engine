"""Usage example: CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (non conviventi)."""

from datetime import date
from decimal import Decimal

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
            level_code="C",
            weekly_hours=Decimal(40),
        ),
        employment=Employment(
            ccnl="lavoro-domestico-non-convivente.json",
            contract=Permanent(),
            employer=Employer(num_employees=1),
            calculation_date=date(2026, 9, 1),
        ),
    )
)
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"INPS employer annual: {p.inps_employer_annual} EUR")
print(f"Employer withholds IRPEF: {p.employer_withholds_irpef}")
