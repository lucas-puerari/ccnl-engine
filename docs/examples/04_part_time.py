"""Family deductions (Art. 12 TUIR): dependent spouse and children reduce net IRPEF.

The deductions depend on the reddito complessivo of the year, so the run
needs the income beyond this employment: ``CurrentYearTaxFacts``, zero
included.  Without it the deductions are a simulation and the result is not
payable.  Children under 21 are covered by the assegno unico and give no
Art. 12 deduction; the one born in 2004 turned 21 in 2025, so it gives the
deduction for the whole of 2026.
"""

from datetime import date

from ccnl_engine import (
    CurrentYearTaxFacts,
    Dependent,
    DependentRelationship,
    EmployerProfile,
    Employment,
    FamilyComposition,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)

engine = PayrollEngine.bundled()

employment = Employment(ccnl_slug="commercio-confcommercio.json", level_code="4")
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
        facts=PeriodFacts(regione="IT-45"),
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
                    Dependent(relationship=DependentRelationship.SPOUSE),
                    Dependent(
                        relationship=DependentRelationship.CHILD,
                        birth_date=date(2004, 5, 10),
                    ),
                    Dependent(
                        relationship=DependentRelationship.CHILD,
                        birth_date=date(2018, 8, 20),
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
