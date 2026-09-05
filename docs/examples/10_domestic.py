"""Domestic work (lavoro domestico): flat per-hour contributions.

Domestic work uses a different contribution system: flat per-hour INPS
rates (not percentage-based), and the employer does NOT withhold IRPEF
(employer_withholds_irpef = False).

Required: pass weekly_hours in the Scenario.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine import Permanent, Scenario, compute, load_ccnl, load_year_rules

# Convivente (live-in) domestic worker, super-minimum level, 40h/week.
ccnl = load_ccnl("lavoro-domestico-convivente.json")
rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=1)

scenario = Scenario(
    level_code="CS",  # convivente super-minimum
    as_of=date(2026, 1, 1),
    employment=Permanent(),
    num_employees=1,
    weekly_hours=Decimal(40),
)

p = compute(ccnl, rules, scenario)

print(f"Gross monthly:         {p.gross_monthly} EUR")
print(f"INPS employee annual:  {p.inps_employee_annual} EUR")
print(f"INPS employer annual:  {p.inps_employer_annual} EUR")
print(f"Employer withholds IRPEF: {p.employer_withholds_irpef}")
print(f"IRPEF gross (informational): {p.irpef_gross} EUR")
print(f"IRPEF net (zero — not withheld): {p.irpef_net} EUR")
print(f"Net annual:            {p.net_annual} EUR")

# The employer is not a sostituto d'imposta for domestic workers.
assert not p.employer_withholds_irpef
assert p.irpef_net == Decimal(0)
