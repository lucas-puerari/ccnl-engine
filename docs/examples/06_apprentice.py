"""Apprenticeship contracts: percentage track.

The engine supports two apprenticeship tracks:
- Percentage track: the apprentice's pay is a % of the destination level's pay.
  The percentage increases with months_elapsed.
- Under-classification track: the apprentice is paid at a lower level code.

This example shows the percentage track, which is the most common.
"""

from datetime import date

from ccnl_engine import (
    Apprentice,
    Permanent,
    Scenario,
    compute,
    load_ccnl,
    load_year_rules,
)

# Metalmeccanico artigianato has an apprenticeship percentage track.
ccnl = load_ccnl("metalmeccanico-artigianato.json")
rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=12)

# Destination level: level 3. Apprentice at month 12 → 75% of destination pay.
scenario_apprentice = Scenario(
    level_code="3",
    as_of=date(2026, 1, 1),
    employment=Apprentice(months_elapsed=12),
    num_employees=12,
)

# Compare with the same level at permanent employment.
scenario_permanent = Scenario(
    level_code="3",
    as_of=date(2026, 1, 1),
    employment=Permanent(),
    num_employees=12,
)

apprentice = compute(ccnl, rules, scenario_apprentice)
permanent = compute(ccnl, rules, scenario_permanent)

print(f"Apprenticeship %:    {apprentice.apprenticeship_pct}")
print(f"Gross monthly — apprentice:  {apprentice.gross_monthly} EUR")
print(f"Gross monthly — permanent:   {permanent.gross_monthly} EUR")
print(f"Employer INPS — apprentice:  {apprentice.inps_employer_annual} EUR")
print(f"Employer INPS — permanent:   {permanent.inps_employer_annual} EUR")
print(f"Employer cost — apprentice:  {apprentice.employer_cost_annual} EUR")
print(f"Employer cost — permanent:   {permanent.employer_cost_annual} EUR")

assert apprentice.apprenticeship_pct is not None
assert apprentice.gross_annual < permanent.gross_annual
