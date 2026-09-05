"""Seniority increments (scatti di anzianità): count vs. months.

Two ways to express seniority:
- seniority_count: you already know how many increments have matured.
- seniority_months: total service months; the engine derives the count
  from the CCNL cadence (e.g. every 24 months, max 5 scatti).

The two forms are mutually exclusive.
"""

from datetime import date

from ccnl_engine import Permanent, Scenario, compute, load_ccnl, load_year_rules

ccnl = load_ccnl("commercio-confcommercio.json")
rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=50)

# --- Via explicit count ---
scenario_count = Scenario(
    level_code="4",
    as_of=date(2026, 1, 1),
    employment=Permanent(),
    num_employees=50,
    seniority_count=3,  # 3 scatti già maturati
)

# --- Via service months (engine derives the count) ---
# Commercio cadence is 36 months. 108 months → 3 increments (at months 36, 72, 108).
scenario_months = Scenario(
    level_code="4",
    as_of=date(2026, 1, 1),
    employment=Permanent(),
    num_employees=50,
    seniority_months=108,
)

p_count = compute(ccnl, rules, scenario_count)
p_months = compute(ccnl, rules, scenario_months)

print(
    f"Via count   — seniority count: {p_count.seniority_count}, monthly: {p_count.seniority_monthly} EUR"
)
print(
    f"Via months  — seniority count: {p_months.seniority_count}, monthly: {p_months.seniority_monthly} EUR"
)

# Both yield the same result when the months imply the same number of increments.
assert p_count.seniority_count == p_months.seniority_count
assert p_count.seniority_monthly == p_months.seniority_monthly
assert p_count.gross_annual == p_months.gross_annual
