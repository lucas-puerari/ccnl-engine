"""YTD state chaining: pass closing_state from one run as opening_state for the next."""

from datetime import date

from ccnl_engine import EmploymentFacts, PayrollEngine, PayrollRequest, PayrollRun

engine = PayrollEngine.bundled()

facts = EmploymentFacts(num_employees=100)

# January — opening_state defaults to zero
jan = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        employment_facts=facts,
        regione="ER",
    )
)

# February — carry forward YTD state from January
feb = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=2),
        payment_date=date(2026, 2, 27),
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        employment_facts=facts,
        regione="ER",
        opening_state=jan.closing_state,
    )
)

print(f"Jan gross: {jan.period_gross}  net: {jan.period_net}")
print(f"Feb gross: {feb.period_gross}  net: {feb.period_net}")

# Inspect YTD accumulators after February
state = feb.closing_state
print(f"YTD taxable income: {state.taxable_ytd}")
print(f"YTD IRPEF withheld: {state.irpef_withheld_ytd}")
