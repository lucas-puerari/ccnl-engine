"""Explain a result: inspect pay_items, contribution components, capability_report."""

from datetime import date

from ccnl_engine import EmploymentFacts, PayrollEngine, PayrollRequest, PayrollRun

engine = PayrollEngine.bundled()

result = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        employment_facts=EmploymentFacts(num_employees=100, seniority_months=36),
        regione="ER",
        comune_belfiore="F257",
    )
)

print("=== Pay items ===")
for item in result.pay_items:
    print(f"  {item.kind:40s} {item.amount}")

print("\n=== Contribution components ===")
for c in result.contribution_breakdown.components:
    print(f"  {c.name:30s} base={c.base}  rate={c.rate}  amount={c.amount}")

print("\n=== Tax computation ===")
tc = result.tax_computation
print(f"  Ordinary IRPEF:           {tc.ordinary_tax}")
print(f"  Trattamento integrativo:  {tc.trattamento_integrativo}")
print(f"  Withholding due:          {tc.withholding_due}")

print("\n=== Capability report ===")
cr = result.capability_report
print(f"  Overall confidence: {cr.confidence}  status: {cr.status}")
for gap in cr.gaps:
    print(f"  gap: {gap.feature:30s} {gap.kind.value}")
