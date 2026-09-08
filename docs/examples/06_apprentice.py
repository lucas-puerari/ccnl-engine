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
    Employee,
    Employer,
    Employment,
    PayrollScenario,
    Permanent,
    compute,
)

# Metalmeccanico artigianato has an apprenticeship percentage track.
# Destination level: level 3. Apprentice at month 12 → 75% of destination pay.
apprentice = compute(
    PayrollScenario(
        employee=Employee(level_code="3"),
        employment=Employment(
            ccnl="metalmeccanico-artigianato.json",
            contract=Apprentice(months_elapsed=12),
            employer=Employer(num_employees=12),
            date=date(2026, 1, 1),
        ),
    )
)

# Compare with the same level at permanent employment.
permanent = compute(
    PayrollScenario(
        employee=Employee(level_code="3"),
        employment=Employment(
            ccnl="metalmeccanico-artigianato.json",
            contract=Permanent(),
            employer=Employer(num_employees=12),
            date=date(2026, 1, 1),
        ),
    )
)

print(f"Apprenticeship %:    {apprentice.apprenticeship_pct}")
print(f"Gross monthly — apprentice:  {apprentice.gross_monthly} EUR")
print(f"Gross monthly — permanent:   {permanent.gross_monthly} EUR")
print(f"Employer INPS — apprentice:  {apprentice.inps_employer_annual} EUR")
print(f"Employer INPS — permanent:   {permanent.inps_employer_annual} EUR")
print(f"Employer cost — apprentice:  {apprentice.employer_cost_annual} EUR")
print(f"Employer cost — permanent:   {permanent.employer_cost_annual} EUR")

assert apprentice.apprenticeship_pct is not None
assert apprentice.gross_annual < permanent.gross_annual
