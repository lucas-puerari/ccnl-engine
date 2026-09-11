"""Part-time contract: scaling gross, INPS, and TFR.

part_time_pct scales base pay, seniority, and most allowances.
ad_personam_monthly is NOT scaled (it is an individual frozen element).
"""

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

full_time = compute(
    PayrollScenario(
        employee=Employee(level_code="4"),
        employment=Employment(
            ccnl="commercio-confcommercio.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            calculation_date=date(2026, 1, 1),
        ),
    )
)
part_time = compute(
    PayrollScenario(
        employee=Employee(
            level_code="4", part_time_pct=Decimal("0.6")
        ),  # 60% — 3/5 days
        employment=Employment(
            ccnl="commercio-confcommercio.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            calculation_date=date(2026, 1, 1),
        ),
    )
)

print(f"Gross monthly — full-time:  {full_time.gross_monthly} EUR")
print(f"Gross monthly — part-time:  {part_time.gross_monthly} EUR")
print(f"Net annual   — full-time:   {full_time.net_annual} EUR")
print(f"Net annual   — part-time:   {part_time.net_annual} EUR")
print(f"Employer cost — full-time:  {full_time.employer_cost_annual} EUR")
print(f"Employer cost — part-time:  {part_time.employer_cost_annual} EUR")

# Gross is scaled proportionally.
assert part_time.gross_monthly == full_time.gross_monthly * Decimal("0.6")
