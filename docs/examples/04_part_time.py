"""Family deductions (Art. 12 TUIR): dependent spouse and children reduce net IRPEF."""

from datetime import date

from ccnl_engine import (
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

# Dependent spouse + two minor children
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
                        birth_date=date(2015, 5, 10),
                    ),
                    Dependent(
                        relationship=DependentRelationship.CHILD,
                        birth_date=date(2018, 8, 20),
                    ),
                )
            ),
        ),
    )
)

print(f"Net (no dependents):  {result_single.period_net}")
print(f"Net (family):         {result_family.period_net}")
print(f"Art. 12 uplift:       {result_family.period_net - result_single.period_net}")
