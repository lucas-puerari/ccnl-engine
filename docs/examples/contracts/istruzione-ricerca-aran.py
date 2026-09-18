"""Usage example: CCNL Comparto Istruzione e Ricerca 2022-2024 — ARAN."""

from datetime import date

from ccnl_engine import (
    Employee,
    Employer,
    Employment,
    AnnualPayrollScenario,
    Permanent,
    estimate_annual,
)

p = estimate_annual(
    AnnualPayrollScenario(
        employee=Employee(
            level_code="DOCENTE_INFANZIA_PRIMARIA",
        ),
        employment=Employment(
            ccnl="istruzione-ricerca-aran.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 9, 1),
        ),
    )
).result
print(f"Gross monthly: {p.gross_monthly} EUR")
print(f"Net annual:    {p.net_annual} EUR")
print(f"Employer cost: {p.employer_cost_annual} EUR")
