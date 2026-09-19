"""Quickstart: permanent employee, full-time, no seniority.

Build an AnnualPayrollScenario and pass it to estimate_annual(). The
returned Calculation wraps the AnnualEstimate (``calculation.result``)
together with the engine and ruleset versions that produced it.
"""

from datetime import date

from ccnl_engine import (
    AnnualPayrollScenario,
    Employee,
    Employer,
    Employment,
    Permanent,
    estimate_annual,
)

calculation = estimate_annual(
    AnnualPayrollScenario(
        employee=Employee(level_code="4"),
        employment=Employment(
            ccnl="commercio-confcommercio.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 1, 1),
        ),
    )
)
payroll = calculation.result

print(f"CCNL:              {payroll.ccnl_id}")
print(f"Level:             {payroll.level_code}")
print(f"Gross monthly:     {payroll.earnings.gross_monthly} EUR")
print(f"Gross annual:      {payroll.earnings.gross_annual} EUR")
print(f"Net annual:        {payroll.net_annual} EUR")
print(f"Net monthly:       {payroll.net_monthly} EUR")
print(f"Employer cost:     {payroll.employer_cost.employer_cost_annual} EUR")

# Grouped views give structured access to related output fields.
print(f"Status:            {payroll.coverage.status}")
print(f"Confidence:        {payroll.coverage.confidence}")

# The Calculation also records the engine/ruleset version and a full input
# snapshot, so any figure can be reproduced exactly at a later date.
print(f"Engine version:    {calculation.engine_version}")
print(f"Ruleset version:   {calculation.ruleset_version}")

# AnnualEstimate.provenance carries the ordered chain of RuleProvenance objects
# that contributed to the computed pay — one entry per level, active salary
# period, applied allowance, and seniority-increment rule.
for prov in payroll.provenance:
    doc = prov.location.source_document
    print(f"  [{doc.kind}] {doc.document_id} — {prov.location.section}")
