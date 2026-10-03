"""Quickstart: one payroll run and one full year with PayrollEngine.

The engine takes a :class:`PeriodInput` for a single cedolino and a
:class:`YearInput` for every run of a tax year.  Both group the facts by
owner: :class:`Employment` for the contract and the worker,
:class:`EmployerProfile` for the employer and :class:`PeriodFacts` for what
holds in one run.  ``mode="operational"`` keeps the amounts and also blocks
payment from any CCNL ruleset that is not ``production``.
"""

from datetime import date

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    SeniorityFact,
    SenioritySource,
    YearInput,
)

engine = PayrollEngine.bundled()
employment = Employment(
    ccnl_slug="commercio-confcommercio.json",
    level_code="4",
    # Recognised seniority: 36 months on 1 January 2026, read from a payslip.
    seniority=SeniorityFact(36, date(2026, 1, 1), SenioritySource.PAYSLIP),
)
employer = EmployerProfile(headcount=Headcount(50))

# ── Single-period calculation ────────────────────────────────────────────────

result = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        employment=employment,
        employer=employer,
    )
)

print(f"Period gross:   {result.period_gross} EUR")
print(f"Period net:     {result.period_net} EUR")
print(f"Employer cost:  {result.period_employer_cost} EUR")
print(f"Payable:        {result.is_payable}")
for ruleset in result.rulesets:
    print(f"Ruleset:        {ruleset.id} ({ruleset.kind}, {ruleset.readiness})")

# ── Operational mode ─────────────────────────────────────────────────────────

# Same amounts; a CCNL ruleset short of production adds a
# ruleset_not_production blocker, so only production CCNLs can be payable.
strict = PayrollEngine.bundled(mode="operational")
reviewed = [c.ccnl_id for c in strict.list_contracts() if c.readiness == "reviewed"]
print(f"Reviewed CCNLs: {len(reviewed)} of {len(strict.list_contracts())}")

# ── Full-year calculation ────────────────────────────────────────────────────

# The calendar is derived from the CCNL: Commercio grants tredicesima and
# quattordicesima, so the year has 14 runs.
year_result = engine.calculate_year(
    YearInput(year=2026, employment=employment, employer=employer)
)

print(f"\nAnnual gross:   {year_result.annual_gross} EUR")
print(f"Runs computed:  {len(year_result.period_results)}")
