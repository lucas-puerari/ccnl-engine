"""Full-year run: standard calendar derived from the CCNL, then an override.

Without ``calendar_override`` the engine runs the calendar the CCNL grants.  A custom
calendar is accepted only as a ``CalendarOverride`` with a domain reason; an
override that drops or lowers a CCNL extra month raises ``InvalidInputError``.
"""

from ccnl_engine import (
    CalendarOverride,
    CalendarOverrideReason,
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    WorkCalendar,
    PayrollEngine,
    YearInput,
)

engine = PayrollEngine.bundled()


def year_request(calendar: CalendarOverride | None = None) -> YearInput:
    """Build a Commercio level 4 input for 2026.

    Returns:
        The year input, with ``calendar`` as the optional override.
    """
    return YearInput(
        year=2026,
        employment=Employment(ccnl_slug="commercio-confcommercio.json", level_code="4"),
        employer=EmployerProfile(headcount=Headcount(50)),
        calendar_override=calendar,
    )


# Standard calendar: tredicesima in December, quattordicesima in June.
result = engine.calculate_year(year_request())

print(f"Annual gross:        {result.annual_gross}")
print(f"Annual net:          {result.annual_net}")
print(f"Annual employer cost:{result.annual_employer_cost}")
print(f"Runs computed:       {len(result.period_results)}")

for r in result.period_results:
    run_label = r.run.run_id if r.run else str(r.period_id)
    print(f"  {run_label:30s}  gross={r.period_gross}")

# Same entitlement, quattordicesima paid with the July salary.
july = CalendarOverride(
    calendar=WorkCalendar.from_additional_months(2026, 14, fourteenth_payment_month=7),
    reason=CalendarOverrideReason.PAYMENT_MONTH,
    note="quattordicesima paid with the July salary",
)
moved = engine.calculate_year(year_request(july))
print(f"Runs with July quattordicesima: {len(moved.period_results)}")

# Dropping the quattordicesima is rejected whatever the reason.
only_thirteenth = CalendarOverride(
    calendar=WorkCalendar.from_additional_months(2026, 13),
    reason=CalendarOverrideReason.PAYMENT_MONTH,
    note="attempt to skip the quattordicesima",
)
try:
    engine.calculate_year(year_request(only_thirteenth))
except InvalidInputError as exc:
    print(f"Rejected: {exc}")
