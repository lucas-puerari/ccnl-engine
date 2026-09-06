"""Usage example: CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (conviventi)."""

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    ContractPosition,
    Employee,
    Permanent,
    WorkArrangement,
    compute,
    load_ccnl,
    load_year_rules,
)

ccnl = load_ccnl("lavoro-domestico-convivente.json")
rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=1)

employee = Employee(
    position=ContractPosition(
        level_code="C",
        as_of=date(2026, 9, 1),
        employment=Permanent(),
    ),
    arrangement=WorkArrangement(weekly_hours=Decimal(40)),
)

p = compute(ccnl, rules, employee)
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"INPS employer annual: {p.inps_employer_annual} EUR")
print(f"Employer withholds IRPEF: {p.employer_withholds_irpef}")
