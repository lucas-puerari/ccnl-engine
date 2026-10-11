"""Family deductions (Art. 12 TUIR): dependent spouse and children reduce net IRPEF.

The deductions depend on the reddito complessivo of the year, so the run
needs the income beyond this employment: ``CurrentYearTaxFacts``, zero
included.  Without it the deductions are a simulation and the result is not
payable.  Children under 21 are covered by the assegno unico and give no
Art. 12 deduction; the one born in 2004 turned 21 in 2025, so it gives the
deduction for the whole of 2026.

Every condition of a dependant is stated: own income (art. 12 c. 2),
residency (c. 2-bis), the share of a child (lett. c: the whole deduction,
because the spouse is a dependant of the worker) and the dependency interval
(``None`` for open ends).  A condition left ``None`` is unknown: the
dependant takes no deduction and the run has a ``missing_fact`` blocker.
"""

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
    CurrentYearTaxFacts,
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.inputs import Permanent

engine = PayrollEngine.bundled()

employment = Employment(
    ccnl_slug="commercio-confcommercio.json", level_code="4", contract_type=Permanent()
)
employer = EmployerProfile(headcount=Headcount(50))
run = PayrollRun.regular(year=2026, month=1)
payment = date(2026, 1, 28)

# No dependents
result_single = engine.calculate_period(
    PeriodInput(
        run=run,
        payment_date=payment,
        employment=employment,
        employer=employer,
        facts=PeriodFacts(regione="IT-45", family_composition=FamilyComposition()),
    )
)

# Dependent spouse, a child of 22 and a minor child; no other income in 2026
result_family = engine.calculate_period(
    PeriodInput(
        run=run,
        payment_date=payment,
        employment=employment,
        employer=employer,
        facts=PeriodFacts(
            regione="IT-45",
            family_composition=FamilyComposition(
                dependents=(
                    Dependent(
                        relationship=DependentRelationship.SPOUSE,
                        own_income=Decimal(0),
                        residency_eligibility=True,
                        dependent_from=None,
                        dependent_until=None,
                    ),
                    *(
                        Dependent(
                            relationship=DependentRelationship.CHILD,
                            birth_date=born,
                            own_income=Decimal(0),
                            allocation_pct=Decimal(100),
                            residency_eligibility=True,
                            dependent_from=None,
                            dependent_until=None,
                        )
                        for born in (date(2004, 5, 10), date(2018, 8, 20))
                    ),
                )
            ),
        ),
        current_year=CurrentYearTaxFacts.employment_only(2026, date(2026, 1, 2)),
    )
)
(family,) = [d for d in result_family.decisions if d.capability == "family_deductions"]

print(f"Net (no dependents):  {result_single.period_net}")
print(f"Net (family):         {result_family.period_net}")
print(f"Art. 12 uplift:       {result_family.period_net - result_single.period_net}")
print(f"Annual deductions:    {family.amount} ({family.inputs['months']})")
