"""Family deductions (Art. 12 TUIR): dependent spouse and children reduce net IRPEF."""

from datetime import date

from ccnl_engine import (
    Dependent,
    DependentRelationship,
    Employer,
    EmploymentFacts,
    FamilyComposition,
    Headcount,
    PayrollEngine,
    PayrollRequest,
    PayrollRun,
)

engine = PayrollEngine.bundled()

facts = EmploymentFacts()
employer = Employer(headcount=Headcount(50))
run = PayrollRun.regular(year=2026, month=1)
payment = date(2026, 1, 28)
slug = "commercio-confcommercio.json"
level = "4"

# No dependents
result_single = engine.calculate(
    PayrollRequest(
        run=run,
        payment_date=payment,
        ccnl_slug=slug,
        level_code=level,
        employment_facts=facts,
        employer=employer,
        regione="ER",
    )
)

# Dependent spouse + two minor children
result_family = engine.calculate(
    PayrollRequest(
        run=run,
        payment_date=payment,
        ccnl_slug=slug,
        level_code=level,
        employment_facts=facts,
        employer=employer,
        regione="ER",
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
    )
)

print(f"Net (no dependents):  {result_single.period_net}")
print(f"Net (family):         {result_family.period_net}")
print(f"Art. 12 uplift:       {result_family.period_net - result_single.period_net}")
