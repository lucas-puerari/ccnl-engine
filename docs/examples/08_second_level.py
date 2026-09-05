"""Second-level bargaining (contrattazione di secondo livello).

Territorial or company agreements add supplementary allowances on top of
the CCNL minimums. Pass them via Scenario.second_level_allowances using
SupplementaryAllowance objects.

Each allowance carries:
- monthly: resolved EUR amount (no time-series; you own the schedule).
- months_per_year: override for annualisation (e.g. 1 for an annual prize).
- contribution_relevant: whether to include in the INPS base.
- tfr_relevant: whether to include in the TFR base.
- apprenticeship_pct_relevant: whether the apprenticeship % applies.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine import Permanent, Scenario, compute, load_ccnl, load_year_rules
from ccnl_engine.models.ccnl import SupplementaryAllowance

ccnl = load_ccnl("commercio-confcommercio.json")
rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=50)

# A monthly productivity bonus of 150 EUR + an annual prize of 800 EUR.
second_level = (
    SupplementaryAllowance(
        code="PROD",
        description="Premio produttività mensile",
        monthly=Decimal("150.00"),
        # contribution_relevant=True by default → enters INPS and TFR base
    ),
    SupplementaryAllowance(
        code="PRIZE",
        description="Premio annuo aziendale",
        monthly=Decimal("800.00"),
        months_per_year=1,  # paid once a year, not 13x
        contribution_relevant=False,  # excluded from INPS base (common for prizes)
        tfr_relevant=False,
    ),
)

scenario_base = Scenario(
    level_code="4",
    as_of=date(2026, 1, 1),
    employment=Permanent(),
    num_employees=50,
)
scenario_2l = Scenario(
    level_code="4",
    as_of=date(2026, 1, 1),
    employment=Permanent(),
    num_employees=50,
    second_level_allowances=second_level,
)

base = compute(ccnl, rules, scenario_base)
with_2l = compute(ccnl, rules, scenario_2l)

print(f"Second-level monthly:     {with_2l.second_level_monthly} EUR")
print(f"Gross monthly — base:     {base.gross_monthly} EUR")
print(f"Gross monthly — with 2L:  {with_2l.gross_monthly} EUR")
print(f"Net annual   — base:      {base.net_annual} EUR")
print(f"Net annual   — with 2L:   {with_2l.net_annual} EUR")
print(f"Employer cost — base:     {base.employer_cost_annual} EUR")
print(f"Employer cost — with 2L:  {with_2l.employer_cost_annual} EUR")

assert with_2l.gross_annual > base.gross_annual
assert with_2l.net_annual > base.net_annual
