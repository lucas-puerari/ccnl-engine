"""Negotiated RAL: individual salary agreed outside the CCNL tables.

When a worker's gross annual salary (RAL) is individually negotiated
above the CCNL minimum, pass it as RalOverride inside SalaryOverrides.
The engine uses this figure directly instead of deriving pay from the
level's base salary.

This is mutually exclusive with Employer.second_level_allowances.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    ContractPosition,
    Employee,
    SalaryOverrides,
    Permanent,
    RalOverride,
    WorkArrangement,
    compute,
    load_ccnl,
    load_year_rules,
)

ccnl = load_ccnl("studi-professionali-confprofessioni.json")
rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=10)

# CCNL minimum for the level.
employee_ccnl = Employee(
    position=ContractPosition(
        level_code="3",
        as_of=date(2026, 1, 1),
        employment=Permanent(),
    ),
    arrangement=WorkArrangement(),
)

# Same worker with a negotiated RAL of 40 000 EUR.
employee_ral = Employee(
    position=ContractPosition(
        level_code="3",
        as_of=date(2026, 1, 1),
        employment=Permanent(),
    ),
    arrangement=WorkArrangement(),
    agreement=SalaryOverrides(ral_override=RalOverride(Decimal("40000.00"))),
)

ccnl_min = compute(ccnl, rules, employee_ccnl)
negotiated = compute(ccnl, rules, employee_ral)

print(f"Gross annual — CCNL minimum:  {ccnl_min.gross_annual} EUR")
print(f"Gross annual — negotiated:    {negotiated.gross_annual} EUR")
print(f"Net annual   — CCNL minimum:  {ccnl_min.net_annual} EUR")
print(f"Net annual   — negotiated:    {negotiated.net_annual} EUR")
