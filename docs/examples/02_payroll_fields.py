"""Reading the PayrollResult: key output fields and their meaning.

compute() returns a Calculation that bundles the PayrollResult (``calculation.result``)
with the engine version, the ruleset revisions used and a snapshot of the
inputs. Attribute reads are also forwarded onto the PayrollResult, so
``calculation.net_annual`` works too. This example walks through the most
commonly used fields.
"""

from datetime import date
from decimal import Decimal
from typing import cast

from ccnl_engine import (
    ContractPosition,
    Employee,
    FiscalSimplification,
    Permanent,
    WorkArrangement,
    compute,
    load_ccnl,
    load_year_rules,
)

ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=200)

employee = Employee(
    position=ContractPosition(
        level_code="C2",
        as_of=date(2026, 6, 1),
        employment=Permanent(),
    ),
    arrangement=WorkArrangement(),
)

calculation = compute(ccnl, rules, employee)
p = calculation.result

# --- Pay components (monthly, already scaled by part_time_pct) ---
print("=== Monthly pay breakdown ===")
print(f"  Base:           {p.base_monthly} EUR")
print(f"  Seniority:      {p.seniority_monthly} EUR  ({p.seniority_count} scatti)")
print(f"  Allowances:     {p.allowances_monthly} EUR")
print(f"  Gross monthly:  {p.gross_monthly} EUR")
print(f"  Hourly rate:    {p.hourly_rate} EUR/h")

# --- Annual figures ---
print("\n=== Annual ===")
print(f"  Gross annual:          {p.gross_annual} EUR")
print(f"  INPS employee:         {p.inps_employee_annual} EUR")
print(f"  INPS employer:         {p.inps_employer_annual} EUR")
print(f"  TFR accrual:           {p.tfr_annual} EUR")
print(f"  Taxable income:        {p.taxable_income} EUR")
print(f"  IRPEF gross:           {p.irpef_gross} EUR")
print(f"  Work income deduction: {p.work_income_deduction} EUR")
print(f"  IRPEF net:             {p.irpef_net} EUR")
print(f"  Trattamento integrativo: {p.trattamento_integrativo} EUR")
print(f"  Net annual:            {p.net_annual} EUR")
print(f"  Net monthly:           {p.net_monthly} EUR")
print(f"  Employer cost annual:  {p.employer_cost_annual} EUR")

# --- Fiscal simplifications: items NOT computed by the engine ---
# Always check this set before presenting results to end users.
print("\n=== Fiscal simplifications (omitted items) ===")
for item in sorted(p.fiscal_simplifications, key=str):
    print(f"  {item.value}")

# Regional and municipal surcharges are zero when not explicitly requested.
assert FiscalSimplification.NO_ADDIZIONALE_REGIONALE in p.fiscal_simplifications
assert p.addizionale_regionale_annual == Decimal(0)

# --- Serialisation ---
as_dict = p.to_dict()  # all Decimal → str, date → ISO string, frozenset → list
as_json = p.to_json()  # compact JSON string
restored = type(p).from_json(as_json)  # round-trip
assert restored == p

# --- Calculation metadata ---
# engine_version and ruleset_version let you reproduce any figure exactly.
assert calculation.engine_version == "0.5.0"
assert (
    calculation.ruleset_version["ccnl"] == "ccnl/metalmeccanico-federmeccanica@2026.2"
)
pos = cast("dict[str, object]", calculation.input_snapshot.employee["position"])
assert pos["level_code"] == "C2"

# --- Rule provenance chain ---
# PayrollResult.provenance is an ordered tuple of RuleProvenance objects — one
# per rule that actually contributed to the computed pay (level declaration,
# active salary-period tranche, each applied allowance, seniority rule).
# Every entry links back to the primary source document and section.
print("\n=== Rule provenance chain ===")
for prov in p.provenance:
    doc = prov.location.source_document
    section = prov.location.section
    status = prov.extraction.verification_status.value
    print(f"  [{doc.kind}] {doc.document_id}")
    print(f"    section:  {section}")
    print(f"    url:      {doc.url}")
    print(f"    status:   {status}")

# Every rule must carry provenance — the engine rejects CCNL files that don't.
assert len(p.provenance) >= 1
assert all(prov.location.source_document.url for prov in p.provenance)
