"""Seniority increments (scatti di anzianità): count vs. months.

Two ways to express seniority:
- SeniorityByCount: you already know how many increments have matured.
- SeniorityByMonths: total service months; the engine derives the count
  from the CCNL cadence (e.g. every 24 months, max 5 scatti).
"""

from datetime import date

from ccnl_engine import (
    Employee,
    Employer,
    Employment,
    AnnualPayrollScenario,
    Permanent,
    SeniorityByCount,
    SeniorityByMonths,
    estimate_annual,
)

# --- Via explicit count ---
p_count = estimate_annual(
    AnnualPayrollScenario(
        employee=Employee(
            level_code="4",
            seniority=SeniorityByCount(value=3),  # 3 scatti già maturati
        ),
        employment=Employment(
            ccnl="commercio-confcommercio.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 1, 1),
        ),
    )
).result

# --- Via service months (engine derives the count) ---
# Commercio cadence is 36 months. 108 months → 3 increments (at months 36, 72, 108).
p_months = estimate_annual(
    AnnualPayrollScenario(
        employee=Employee(
            level_code="4",
            seniority=SeniorityByMonths(value=108),
        ),
        employment=Employment(
            ccnl="commercio-confcommercio.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 1, 1),
        ),
    )
).result

print(
    f"Via count   — seniority count: {p_count.earnings.seniority_count},"
    f" monthly: {p_count.earnings.seniority_monthly} EUR"
)
print(
    f"Via months  — seniority count: {p_months.earnings.seniority_count},"
    f" monthly: {p_months.earnings.seniority_monthly} EUR"
)

# Both yield the same result when the months imply the same number of increments.
assert p_count.earnings.seniority_count == p_months.earnings.seniority_count
assert p_count.earnings.seniority_monthly == p_months.earnings.seniority_monthly
assert p_count.earnings.gross_annual == p_months.earnings.gross_annual
