"""Why this number? — The engine's reliability story.

Every payroll figure is backed by three trust layers:

1. **Provenance** — each rule that contributed to the result links back to a
   primary source document (CCNL article, INPS circular, tax schedule).
2. **Versioning** — the ruleset snapshot is recorded verbatim so any figure
   can be reproduced exactly, even after a CCNL renewal.
3. **Scope** — the engine declares what it computed, what it excluded, and
   what it could not model, so callers are never silently wrong.

This example walks through all three layers for a metalmeccanico C2 payslip.
Period-specific events (overtime) live in PeriodPayrollInput, passed to estimate_period_effects().
"""

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    AnnualEstimateInput,
    Employee,
    Employer,
    Employment,
    OvertimeHours,
    PeriodPayrollInput,
    Permanent,
    PeriodPayroll,
    TaxPeriod,
    estimate_period_effects,
)

# --- 1. Compute ---
scenario = AnnualEstimateInput(
    employee=Employee(level_code="C2"),
    employment=Employment(
        ccnl="metalmeccanico-federmeccanica.json",
        contract=Permanent(),
        employer=Employer(num_employees=200),
        as_of=date(2026, 6, 1),
    ),
)
period = PeriodPayrollInput(
    tax_period=TaxPeriod(
        start=date(2026, 1, 1),
        end=date(2026, 12, 31),
        eligible_work_days=365,
    ),
    time_supplements=OvertimeHours(weekday_hours=Decimal(10)),
)
calculation = estimate_period_effects(scenario, period)
p = calculation.result
assert isinstance(p, PeriodPayroll)

# --- 2. The headline numbers ---
print("=== Payroll result ===")
print(f"  Gross monthly:         {p.earnings.gross_monthly} EUR")
print(f"  INPS employee (year):  {p.contributions.inps_employee_annual} EUR")
print(f"  IRPEF net (year):      {p.taxes.irpef_net} EUR")
print(f"  Net monthly:           {p.net_monthly} EUR")
print(f"  Employer cost (year):  {p.employer_cost.employer_cost_annual} EUR")

if p.overtime_supplement_monthly:
    print(f"\n  [L3] Overtime supplement: {p.overtime_supplement_monthly} EUR/month")
    print(f"  [L3] Total supplements:   {p.time_supplements_monthly} EUR/month")
    print(f"  [L3] Annual projection:   {p.time_supplements_annual_projection} EUR")

# --- 3. Explicit scope — what the engine did and did not compute ---
print("\n=== Calculation scope ===")
for item in p.coverage.calculation_scope:
    icon = {"computed": "✓", "excluded": "○", "not_computed": "?", "partial": "~"}.get(
        item.calculation_status, item.calculation_status
    )
    print(
        f"  {icon}  {item.feature}  [{item.calculation_status}/{item.integration_status}]"
    )

if p.coverage.warnings:
    print("\n  Warnings:")
    for w in p.coverage.warnings:
        print(f"    ! {w}")

# status and confidence are top-level signals for the caller
print(f"\n  status:     {p.coverage.status}")
print(f"  confidence: {p.coverage.confidence}")

# --- 4. Ruleset versioning — exact snapshot for reproducibility ---
print("\n=== Ruleset versions ===")
for key, version in calculation.ruleset_version.items():
    print(f"  {key:8} {version}")

print(f"\n  Engine:    {calculation.engine_version}")

# Any figure can be reproduced by pinning these three values.
# The knowledge layer version is embedded in the ruleset_version dict.

# --- 5. Provenance chain — where each rule comes from ---
print("\n=== Rule provenance (why this gross?) ===")
for prov in p.provenance:
    doc = prov.location.source_document
    section = prov.location.section
    status = prov.extraction.verification_status.value
    print(f"  [{doc.kind}] {doc.document_id}")
    print(f"    section : {section}")
    print(f"    url     : {doc.url}")
    print(f"    verified: {status}")
    print()

assert len(p.provenance) >= 1, "every computation must have at least one rule"
assert all(prov.location.source_document.url for prov in p.provenance), (
    "every rule must carry a source URL"
)

# --- 6. Calculation trace — step-by-step gross assembly ---
print("=== Calculation trace (gross build-up) ===")
for step in calculation.trace.steps:
    print(f"  {step.category:<20} {step.label:<30} {step.amount} EUR")

if calculation.trace.supplement_steps:
    print("\n  Supplement trace:")
    for step in calculation.trace.supplement_steps:
        print(f"  {step.category:<20} {step.label:<30} {step.amount} EUR")

# --- 7. Fiscal trace — annotated gross-to-net derivation ---
# Each step carries a formula (algebraic derivation), a source (statutory
# reference), and a rounding descriptor (set only when a rate multiplication
# or bracket computation is involved; absent for pure additions/subtractions).
print("\n=== Fiscal trace (gross → net, annual) ===")
for step in calculation.trace.fiscal_steps:
    print(f"  {step.category:<25} {step.amount:>12} EUR")
    if step.formula:
        print(f"    formula : {step.formula}")
    if step.source:
        print(f"    source  : {step.source}")
    if step.rounding:
        print(f"    rounding: {step.rounding}")

# The fiscal closure invariant: net can be independently verified from the
# other steps without trusting the engine's own net_annual field.
by_cat = {s.category: s for s in calculation.trace.fiscal_steps}

from ccnl_engine.engine.payroll.domain.calculation import TraceCategory  # noqa: E402

gross = by_cat[TraceCategory.GROSS].amount
inps = by_cat[TraceCategory.INPS_EMPLOYEE].amount
irpef = by_cat[TraceCategory.IRPEF_NET].amount
add_reg = by_cat[TraceCategory.ADDIZIONALE_REGIONALE].amount
add_com = by_cat[TraceCategory.ADDIZIONALE_COMUNALE].amount
ti = by_cat[TraceCategory.TRATTAMENTO_INTEGRATIVO].amount
net_from_trace = gross - inps - irpef - add_reg - add_com + ti

print(f"\n  Closure check: {net_from_trace} EUR (from trace steps)")
print(f"  Result field:  {p.net_annual} EUR (from AnnualEstimate)")
assert net_from_trace == p.net_annual, (
    f"fiscal closure violated: {net_from_trace} != {p.net_annual}"
)
