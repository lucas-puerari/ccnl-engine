"""Fixed-term contract: NASpI addizionale on employer INPS.

FixedTerm() adds the 1.40% NASpI addizionale to the employer's INPS
contribution (Art. 2 c. 28 L. 92/2012). Everything else is identical
to a permanent contract.
"""

from datetime import date

from ccnl_engine import (
    FixedTerm,
    Permanent,
    Scenario,
    compute,
    load_ccnl,
    load_year_rules,
)

ccnl = load_ccnl("commercio-confcommercio.json")
rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=50)

base_scenario = Scenario(
    level_code="4",
    as_of=date(2026, 1, 1),
    employment=Permanent(),
    num_employees=50,
)
ft_scenario = Scenario(
    level_code="4",
    as_of=date(2026, 1, 1),
    employment=FixedTerm(),
    num_employees=50,
)

permanent = compute(ccnl, rules, base_scenario)
fixed_term = compute(ccnl, rules, ft_scenario)

print(f"Employer INPS — permanent:   {permanent.inps_employer_annual} EUR")
print(f"Employer INPS — fixed-term:  {fixed_term.inps_employer_annual} EUR")
print(
    f"NASpI addizionale:           {fixed_term.inps_employer_annual - permanent.inps_employer_annual} EUR"
)

# Gross and net are identical; only the employer side differs.
assert fixed_term.net_annual == permanent.net_annual
assert fixed_term.inps_employer_annual > permanent.inps_employer_annual
