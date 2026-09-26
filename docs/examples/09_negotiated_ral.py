"""YTD state chaining: pass closing_state from one run as opening_state for the next."""

from datetime import date

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)

engine = PayrollEngine.bundled()

employment = Employment(ccnl_slug="metalmeccanico-federmeccanica.json", level_code="C3")
employer = EmployerProfile(headcount=Headcount(100))
facts = PeriodFacts(regione="IT-45")

# January: opening_state defaults to zero
jan = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        employment=employment,
        employer=employer,
        facts=facts,
    )
)

# February: carry forward YTD state from January
feb = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=2),
        payment_date=date(2026, 2, 27),
        employment=employment,
        employer=employer,
        facts=facts,
        opening_state=jan.closing_state,
    )
)

print(f"Jan gross: {jan.period_gross}  net: {jan.period_net}")
print(f"Feb gross: {feb.period_gross}  net: {feb.period_net}")

# Inspect YTD accumulators after February
state = feb.closing_state
print(f"YTD taxable income: {state.ytd.earnings.taxable}")
print(f"YTD IRPEF withheld: {state.ytd.tax.irpef}")
