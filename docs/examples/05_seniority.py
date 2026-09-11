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
    PayrollScenario,
    Permanent,
    SeniorityByCount,
    SeniorityByMonths,
    compute,
)

# --- Via explicit count ---
p_count = compute(
    PayrollScenario(
        employee=Employee(
            level_code="4",
            seniority=SeniorityByCount(3),  # 3 scatti già maturati
        ),
        employment=Employment(
            ccnl="commercio-confcommercio.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            calculation_date=date(2026, 1, 1),
        ),
    )
)

# --- Via service months (engine derives the count) ---
# Commercio cadence is 36 months. 108 months → 3 increments (at months 36, 72, 108).
p_months = compute(
    PayrollScenario(
        employee=Employee(
            level_code="4",
            seniority=SeniorityByMonths(108),
        ),
        employment=Employment(
            ccnl="commercio-confcommercio.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            calculation_date=date(2026, 1, 1),
        ),
    )
)

print(
    f"Via count   — seniority count: {p_count.seniority_count},"
    f" monthly: {p_count.seniority_monthly} EUR"
)
print(
    f"Via months  — seniority count: {p_months.seniority_count},"
    f" monthly: {p_months.seniority_monthly} EUR"
)

# Both yield the same result when the months imply the same number of increments.
assert p_count.seniority_count == p_months.seniority_count
assert p_count.seniority_monthly == p_months.seniority_monthly
assert p_count.gross_annual == p_months.gross_annual
