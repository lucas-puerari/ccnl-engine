"""Usage example: CCNL Vigilanza Privata FEDERDAT — SF (HV17)."""

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

ccnl = load_ccnl("vigilanza-privata-federdat-sf.json")
rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=50)
employee = Employee(
    position=ContractPosition(
        level_code="C",
        as_of=date(2026, 4, 1),
        employment=Permanent(),
    ),
    arrangement=WorkArrangement(),
)
p = compute(ccnl, rules, employee)
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost_annual} EUR")
