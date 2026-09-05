"""Reading the Payslip: key output fields and their meaning.

compute() returns a frozen dataclass with every component of gross-to-net
and employer cost. This example walks through the most commonly used fields.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    FiscalSimplification,
    Permanent,
    Scenario,
    compute,
    load_ccnl,
    load_year_rules,
)

ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=200)

scenario = Scenario(
    level_code="C2",
    as_of=date(2026, 6, 1),
    employment=Permanent(),
    num_employees=200,
)

p = compute(ccnl, rules, scenario)

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
