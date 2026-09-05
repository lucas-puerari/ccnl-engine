"""Part-time contract: scaling gross, INPS, and TFR.

part_time_pct scales base pay, seniority, and most allowances.
ad_personam_monthly is NOT scaled (it is an individual frozen element).
"""

from datetime import date
from decimal import Decimal

from ccnl_engine import Permanent, Scenario, compute, load_ccnl, load_year_rules

ccnl = load_ccnl("commercio-confcommercio.json")
rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=50)

scenario_ft = Scenario(
    level_code="4",
    as_of=date(2026, 1, 1),
    employment=Permanent(),
    num_employees=50,
)
scenario_pt = Scenario(
    level_code="4",
    as_of=date(2026, 1, 1),
    employment=Permanent(),
    num_employees=50,
    part_time_pct=Decimal("0.6"),  # 60% — 3 giorni su 5
)

full_time = compute(ccnl, rules, scenario_ft)
part_time = compute(ccnl, rules, scenario_pt)

print(f"Gross monthly — full-time:  {full_time.gross_monthly} EUR")
print(f"Gross monthly — part-time:  {part_time.gross_monthly} EUR")
print(f"Net annual   — full-time:   {full_time.net_annual} EUR")
print(f"Net annual   — part-time:   {part_time.net_annual} EUR")
print(f"Employer cost — full-time:  {full_time.employer_cost_annual} EUR")
print(f"Employer cost — part-time:  {part_time.employer_cost_annual} EUR")

# Gross is scaled proportionally.
assert part_time.gross_monthly == full_time.gross_monthly * Decimal("0.6")
