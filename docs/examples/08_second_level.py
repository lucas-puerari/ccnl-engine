"""Full-year run with tredicesima: WorkCalendar schedules extra-month runs."""

from ccnl_engine import (
    Employer,
    EmploymentFacts,
    Headcount,
    PayrollEngine,
    PayrollYearRequest,
)
from ccnl_engine.payroll.domain.calendar import (
    ExtraMonthKind,
    ExtraMonthSchedule,
    WorkCalendar,
)

engine = PayrollEngine.bundled()

result = engine.calculate_year(
    PayrollYearRequest(
        year=2026,
        ccnl_slug="commercio-confcommercio.json",
        level_code="4",
        calendar=WorkCalendar(
            year=2026,
            extra_months=(
                ExtraMonthSchedule(
                    kind=ExtraMonthKind.THIRTEENTH,
                    name="tredicesima",
                    payment_month=12,
                ),
            ),
        ),
        employment_facts=EmploymentFacts(),
        employer=Employer(headcount=Headcount(50)),
    )
)

print(f"Annual gross:        {result.annual_gross}")
print(f"Annual net:          {result.annual_net}")
print(f"Annual employer cost:{result.annual_employer_cost}")
print(f"Runs computed:       {len(result.period_results)}")

for r in result.period_results:
    run_label = r.run.run_id if r.run else str(r.period_id)
    print(f"  {run_label:30s}  gross={r.period_gross}")
