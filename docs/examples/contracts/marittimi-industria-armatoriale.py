"""Usage example: CCNL Marittimi — Industria Armatoriale (CONFITARMA)."""

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

ccnl = load_ccnl("marittimi-industria-armatoriale.json")
rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=50)
employee = Employee(
    position=ContractPosition(
        level_code="IV",
        as_of=date(2026, 7, 1),
        employment=Permanent(),
    ),
    arrangement=WorkArrangement(),
)
p = compute(ccnl, rules, employee)
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost_annual} EUR")
