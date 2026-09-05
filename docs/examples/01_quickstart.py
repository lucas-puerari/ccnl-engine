"""Quickstart: permanent employee, full-time, no seniority.

This is the minimal call: load a CCNL, build a Scenario, call compute().
"""

from datetime import date

from ccnl_engine import Permanent, Scenario, compute, load_ccnl, load_year_rules

# Load CCNL data and the fiscal/contribution rules for the same year.
ccnl = load_ccnl("commercio-confcommercio.json")
rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=50)

scenario = Scenario(
    level_code="4",
    as_of=date(2026, 1, 1),
    employment=Permanent(),
    num_employees=50,
)

payslip = compute(ccnl, rules, scenario)

print(f"CCNL:              {payslip.ccnl_id}")
print(f"Level:             {payslip.level_code}")
print(f"Gross monthly:     {payslip.gross_monthly} EUR")
print(f"Gross annual:      {payslip.gross_annual} EUR")
print(f"Net annual:        {payslip.net_annual} EUR")
print(f"Net monthly:       {payslip.net_monthly} EUR")
print(f"Employer cost:     {payslip.employer_cost_annual} EUR")
