"""Regional and municipal surtax: withheld the year after the conguaglio."""

from dataclasses import replace
from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.inputs import (
    FamilyComposition,
    InpsBaseYtd,
    OpeningBalances,
    SeniorityFact,
    SenioritySource,
    SurtaxComponent,
    SurtaxObligation,
)

engine = PayrollEngine.bundled()

# The 2025 conguaglio, run by the previous provider, determined the 2025
# regional surtax and municipal saldo and the 2026 municipal acconto.
# import_opening_balances is the one entry point for totals the engine did
# not compute.
opening = engine.import_opening_balances(
    OpeningBalances(
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
        # No other employment of the worker in 2026, no recovery running.
        inps_bases=(InpsBaseYtd(2026, Decimal(0), Decimal(0)),),
        recoveries=(),
    )
)

request = PeriodInput(
    run=PayrollRun.regular(year=2026, month=1),
    payment_date=date(2026, 1, 27),
    employment=Employment(
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        seniority=SeniorityFact(36, date(2026, 1, 1), SenioritySource.PAYSLIP),
    ),
    employer=EmployerProfile(headcount=Headcount(100)),
    facts=PeriodFacts(
        regione="IT-45",  # Emilia-Romagna
        comune_belfiore="F257",  # Modena
        family_composition=FamilyComposition(),  # no dependant
    ),
    opening_state=opening,
)
result = engine.calculate_period(request)

# January, the first run of 2026 after the import, withholds one installment
# of each 2025 saldo, at most 11 from January (D.Lgs. 446/1997 art. 50 c. 4,
# D.Lgs. 360/1998 art. 1 c. 5): 330.00 / 11 = 30.00 (3802) and
# 110.00 / 11 = 10.00 (3848).  The 2026 acconto starts in March (art. 1 c. 5).
for line in result.remittance_summary():
    if line.account == "surtax":
        print(f"  {line.remittance_code}: {line.amount}")

# The 2026 surtax is determined only by the conguaglio of 2026 and withheld
# in 2027: before it, each annual decision is determined_at_conguaglio.
for decision in result.decisions:
    annual = "component" not in decision.inputs
    if decision.capability.startswith("addizionale_") and annual:
        print(f"  {decision.capability}: {decision.reason_code}")

# What is left of the imported debts after January.
for obligation in result.closing_state.cash.obligations.surtax:
    print(f"  {obligation.component}: residual {obligation.plan.residual}")

# Whether the run can be paid is the assurance, not the surtax lines: list
# what blocks it, if anything.
print(f"Calculation: {result.assurance.calculation}, payable: {result.is_payable}")
for blocker in result.blockers:
    print(f"  {blocker.code}: {blocker.feature} {blocker.detail}")

# Without the residence the surtax of 2026 is undetermined, not zero: each
# missing code records residence_unknown and names the fact to supply.
unknown = engine.calculate_period(
    replace(request, facts=PeriodFacts(family_composition=FamilyComposition()))
)
for decision in unknown.decisions:
    if decision.reason_code == "residence_unknown":
        print(f"  {decision.capability}: supply {decision.inputs['fact']}")
print(f"Calculation: {unknown.assurance.calculation}")  # incomplete
