"""Quickstart: permanent employee, full-time, no seniority.

This is the minimal call: load a CCNL, build an Employee, call compute().
The returned Calculation wraps the PayrollResult (``calculation.result``) together
with the engine and ruleset versions that produced it.
"""

from datetime import date

from ccnl_engine import (
    ContractPosition,
    Employee,
    Permanent,
    WorkArrangement,
    compute,
    load_ccnl,
    load_year_rules,
)

# Load CCNL data and the fiscal/contribution rules for the same year.
ccnl = load_ccnl("commercio-confcommercio.json")
rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=50)

employee = Employee(
    position=ContractPosition(
        level_code="4",
        as_of=date(2026, 1, 1),
        employment=Permanent(),
    ),
    arrangement=WorkArrangement(),
)

calculation = compute(ccnl, rules, employee)
payroll = calculation.result

print(f"CCNL:              {payroll.ccnl_id}")
print(f"Level:             {payroll.level_code}")
print(f"Gross monthly:     {payroll.gross_monthly} EUR")
print(f"Gross annual:      {payroll.gross_annual} EUR")
print(f"Net annual:        {payroll.net_annual} EUR")
print(f"Net monthly:       {payroll.net_monthly} EUR")
print(f"Employer cost:     {payroll.employer_cost_annual} EUR")

# The Calculation also records the provenance of the figures above.
print(f"Engine version:    {calculation.engine_version}")
print(f"Ruleset version:   {calculation.ruleset_version}")
print(f"Input snapshot:    {calculation.input_snapshot}")
