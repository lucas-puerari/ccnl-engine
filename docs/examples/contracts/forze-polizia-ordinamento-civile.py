"""Usage example: DPR 24 marzo 2025, n. 53 — Forze di Polizia ad ordinamento civile (Triennio 2022-2024)."""

from datetime import date

from ccnl_engine import (
    Employee,
    Employer,
    Employment,
    PayrollScenario,
    Permanent,
    compute,
)

p = compute(
    PayrollScenario(
        employee=Employee(
            level_code="SOV_CAPO_4A",
        ),
        employment=Employment(
            ccnl="forze-polizia-ordinamento-civile.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            calculation_date=date(2026, 9, 1),
        ),
    )
)
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost_annual} EUR")
