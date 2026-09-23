"""Quickstart: period-first API using PayrollEngine.

Demonstrates the canonical entry point: PayrollEngine.from_builtin_data() +
calculate() for a single cedolino, and calculate_year() for a full-year run.

Both paths use strong types (PayrollRun, PeriodState) rather than plain
month integers, so the type checker prevents common mistakes such as passing
a PeriodId where a run is expected.
"""

from datetime import date

from ccnl_engine import EmploymentFacts, PayrollEngine, PayrollRequest, PayrollRun

# ── Single-period calculation ────────────────────────────────────────────────

engine = PayrollEngine.from_builtin_data()

result = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="commercio-confcommercio.json",
        level_code="4",
        employment_facts=EmploymentFacts(),
    )
)

print(f"Period gross:   {result.period_gross} EUR")
print(f"Period net:     {result.period_net} EUR")
print(f"Employer cost:  {result.period_employer_cost} EUR")

# ── Full-year calculation ────────────────────────────────────────────────────

from ccnl_engine import PayrollYearRequest  # noqa: E402
from ccnl_engine.payroll.domain.calendar import (  # noqa: E402
    ExtraMonthKind,
    ExtraMonthSchedule,
    WorkCalendar,
)

year_result = engine.calculate_year(
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
    )
)

print(f"\nAnnual gross:   {year_result.annual_gross} EUR")
print(f"Runs computed:  {len(year_result.period_results)}")
