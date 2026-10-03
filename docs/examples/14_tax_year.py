"""December paid in January: competence years, tax years and the conguaglio.

The December salary of 2026 paid on 13 January 2027 is income of tax year
2027 (TUIR art. 51 c. 1): tax year 2026 holds the other thirteen payments
and settles its conguaglio on the tredicesima; 2027 opens with the late
December.  Paid on 12 January it would still be 2026 income, and the last
payment, hence the conguaglio, of 2026.
"""

from datetime import date

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    TaxYearPlan,
)

engine = PayrollEngine.bundled()
employment = Employment(ccnl_slug="commercio-confcommercio.json", level_code="4")
employer = EmployerProfile(headcount=Headcount(50))


def plan(december: date) -> CompetenceYearPlan:
    """Return the 2026 plan with the December salary paid on ``december``.

    Returns:
        The competence-year plan.
    """
    return CompetenceYearPlan(
        year=2026,
        employment=employment,
        employer=employer,
        payment_dates={12: december},
    )


# The tax year 2026: the payments actually made in it.  December paid on 13
# January 2027 belongs to 2027, so the tredicesima settles the conguaglio.
late = engine.calculate_tax_year(
    TaxYearPlan(tax_year=2026, competence_years=(plan(date(2027, 1, 13)),))
)
print("13 January:", len(late.payments), "payments, conguaglio", late.conguaglio)
print("2027 opens with tax year", late.next_opening_state.tax_year)

# Paid on 12 January it is 2026 income: the competence year is also the
# tax year, and the December salary settles the conguaglio.
on_time = engine.calculate_competence_year(plan(date(2027, 1, 12)))
print(
    "12 January:",
    len(on_time.period_results),
    "payments, conguaglio",
    on_time.conguagli[0],
)
print("difference in 2026 gross:", on_time.annual_gross - late.annual_gross)

# With the 2027 tables, TaxYearPlan(tax_year=2027, competence_years=(the 2026
# plan, the 2027 plan), opening_state=late.next_opening_state) computes the
# late December first, then the 2027 runs; the last one settles 2027.
