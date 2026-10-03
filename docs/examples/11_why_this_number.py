"""Explain a result: pay items, contributions, F24 remittance, capability report."""

from datetime import date

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    SeniorityMonths,
)

engine = PayrollEngine.bundled()

result = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        employment=Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            seniority_months=SeniorityMonths(36),
        ),
        employer=EmployerProfile(headcount=Headcount(100)),
        facts=PeriodFacts(regione="IT-45", comune_belfiore="F257"),
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

print("\n=== F24 remittance by codice tributo ===")
for line in result.remittance_summary():
    code = line.remittance_code or "-"
    column = line.column or "-"
    print(f"  {line.account:26s} {code:5s} {column:7s} {line.amount}")

print("\n=== Assurance ===")
assurance = result.assurance
print(f"  Payable: {result.is_payable}")
print(f"  Calculation: {assurance.calculation}  coverage: {assurance.coverage}")
print(f"  Evidence: {assurance.evidence}")
for ruleset in result.rulesets:
    print(f"  ruleset: {ruleset}")
for blocker in result.blockers:
    print(f"  blocker: {blocker.code.value:24s} {blocker.feature} {blocker.detail}")
