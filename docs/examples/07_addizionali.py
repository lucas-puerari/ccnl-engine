"""Regional and municipal surtax: withheld the year after the conguaglio."""

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    OpeningBalances,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    SurtaxComponent,
    SurtaxObligation,
)

engine = PayrollEngine.bundled()

# The 2025 conguaglio, run by the previous provider, determined the 2025
# regional surtax and municipal saldo and the 2026 municipal acconto.
opening = OpeningBalances(
    tax_year=2026,
    surtax_obligations=(
        SurtaxObligation.open(
            SurtaxComponent.REGIONAL_BALANCE, 2025, "IT-45", Decimal("330.00")
        ),
        SurtaxObligation.open(
            SurtaxComponent.MUNICIPAL_BALANCE, 2025, "F257", Decimal("110.00")
        ),
        SurtaxObligation.open(
            SurtaxComponent.MUNICIPAL_ADVANCE, 2025, "F257", Decimal("45.00")
        ),
    ),
).to_state()


result = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=3),
        payment_date=date(2026, 3, 27),
        employment=Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json", level_code="C3"
        ),
        employer=EmployerProfile(headcount=Headcount(100)),
        facts=PeriodFacts(regione="IT-45", comune_belfiore="F257"),  # Modena
        opening_state=opening,
    )
)

# March withholds one installment of each 2025 saldo and the first one
# of the 2026 acconto: 30.00 (3802) + 10.00 (3848) + 5.00 (3847).
for line in result.remittance_summary():
    if line.account == "surtax":
        print(f"  {line.remittance_code}: {line.amount}")
print(f"Calculation: {result.assurance.calculation}")  # final: both tables known
# The 2026 surtax is determined by the conguaglio and withheld in 2027.
for obligation in result.closing_state.cash.obligations.surtax:
    print(f"  {obligation.component}: residual {obligation.plan.residual}")
