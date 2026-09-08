"""Negotiated RAL: individual salary agreed outside the CCNL tables.

When a worker's gross annual salary (RAL) is individually negotiated
above the CCNL minimum, pass it as RalOverride inside Agreement.
The engine uses this figure directly instead of deriving pay from the
level's base salary.

This is mutually exclusive with Employer.second_level_allowances.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    Agreement,
    Employee,
    Employer,
    Employment,
    PayrollScenario,
    Permanent,
    RalOverride,
    compute,
)

# CCNL minimum for the level.
ccnl_min = compute(
    PayrollScenario(
        employee=Employee(level_code="3"),
        employment=Employment(
            ccnl="studi-professionali-confprofessioni.json",
            contract=Permanent(),
            employer=Employer(num_employees=10),
            date=date(2026, 1, 1),
        ),
    )
)

# Same worker with a negotiated RAL of 40 000 EUR.
negotiated = compute(
    PayrollScenario(
        employee=Employee(
            level_code="3",
            agreement=Agreement(ral_override=RalOverride(Decimal("40000.00"))),
        ),
        employment=Employment(
            ccnl="studi-professionali-confprofessioni.json",
            contract=Permanent(),
            employer=Employer(num_employees=10),
            date=date(2026, 1, 1),
        ),
    )
)

print(f"Gross annual — CCNL minimum:  {ccnl_min.gross_annual} EUR")
print(f"Gross annual — negotiated:    {negotiated.gross_annual} EUR")
print(f"Net annual   — CCNL minimum:  {ccnl_min.net_annual} EUR")
print(f"Net annual   — negotiated:    {negotiated.net_annual} EUR")
