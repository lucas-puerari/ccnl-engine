# ccnl-engine

[![PyPI version](https://img.shields.io/pypi/v/ccnl-engine?logo=pypi&logoColor=white)](https://pypi.org/project/ccnl-engine/)
[![Python](https://img.shields.io/pypi/pyversions/ccnl-engine?logo=python&logoColor=white)](https://pypi.org/project/ccnl-engine/)
[![CI](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml)
[![Coverage](https://lucas-puerari.github.io/ccnl-engine/coverage-badge.svg)](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Python engine for auditable Italian payroll simulations. CCNL-aware gross-to-net and
employer cost, versioned rules, provenance tracking, and an explicit payability answer on every result.
Built for technical teams in HR, payroll, and compensation.

**[Documentation](https://lucas-puerari.github.io/ccnl-engine/docs/) · [Demo](https://lucas-puerari.github.io/ccnl-engine/demo/)**

## Motivation

I never really understood employment contracts or pay slips. The whole system strikes me as needlessly complicated. On top of that, finding reliable CCNL information online feels like an uphill battle: conflicting figures are everywhere, and identifying authoritative sources is harder than it should be. This project grew out of a desire to understand a little more. I make no claim to becoming an expert, but I hope to make this information more accessible and comprehensible for everyone.

## The Problem

Italian payroll is governed by collective agreements (CCNL) that define base salaries, seniority increments, and allowances as time-series values: they change at negotiated renewal dates. Existing tools either lock this data inside proprietary systems or require a full HRMS. This library treats each CCNL as a validated JSON file and the computation as a pure function:

```
PayrollEngine.calculate_period(PeriodInput) → PeriodResult
PayrollEngine.calculate_competence_year(CompetenceYearPlan) → CompetenceYearResult
PayrollEngine.calculate_tax_year(TaxYearPlan) → TaxYearResult
```

Each result says whether its amounts can be paid (`result.is_payable`), every
reason they cannot (`result.blockers`) and the decisions taken. It is fully itemised: gross, net, employer cost, INPS breakdown, IRPEF computation, pay items, and a ledger of every accounting entry, so any figure can be traced back to the engine and data that produced it.

## Quickstart

```python
from datetime import date
from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.inputs import FamilyComposition, SeniorityFact, SenioritySource

engine = PayrollEngine.bundled()
employment = Employment(
    ccnl_slug="commercio-confcommercio.json",
    level_code="4",
    # Recognised seniority: 36 months on 1 January 2026, read from a payslip.
    seniority=SeniorityFact(36, date(2026, 1, 1), SenioritySource.PAYSLIP),
)
employer = EmployerProfile(headcount=Headcount(50))

result = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        employment=employment,
        employer=employer,
        # Resident in Milan, no dependant: an unknown residence or family
        # would block the surtaxes and the family deductions.
        facts=PeriodFacts(
            regione="IT-25",
            comune_belfiore="F205",
            family_composition=FamilyComposition(),
        ),
    )
)

# → False: see result.blockers; among them the opening state of a worker
# employed before 2026 and the INPS base of other employments, not stated.
print(result.is_payable)
print(result.period_gross)  # → Decimal('...')
print(result.period_net)  # → Decimal('...')
for ruleset in result.rulesets:
    print(ruleset.id, ruleset.kind, ruleset.readiness)
# → ccnl/commercio-confcommercio ccnl reviewed
# → inps/2026/terziario inps None   (readiness tracked for CCNLs only)
# → surtax/2026/comunale surtax None
# → surtax/2026/regionale surtax None
# → tax/2026/family-deductions tax None
# → tax/2026/terziario tax None
```

The root `ccnl_engine` holds this common path: the facade, the request and
plan types, the results and the errors. Every other public name has one home:
`ccnl_engine.inputs` (further facts), `ccnl_engine.events` (work events),
`ccnl_engine.results` (assurance, decisions, limitations) and
`ccnl_engine.catalog` (contracts and ruleset readiness); see
[API reference](docs/api/index.md).

The inputs group the facts by owner: `Employment` (CCNL, level, contract,
employment period, hours, recognised seniority as a dated `SeniorityFact`,
sector), `EmployerProfile` (headcount,
activity), `PriorYearTaxFacts` (prior-year income and written waivers, read by
every substitute-tax regime), `CurrentYearTaxFacts` (income of the tax year
beyond this employment, read by the Art. 12 family deductions, and the INPS
base of the other employments of the year) and
`PeriodFacts` (events, surtax jurisdiction, family, contributable hours of one
run). Every input is validated when it is
built, its collections element by element: a value of the wrong type, `NaN`
or an infinity, a `bool` given as a number, a `datetime` given as a date or
an object in `events` that is not a work event raises `InvalidInputError`
naming the field (`error.field`, e.g. `"PeriodFacts.events[2]"`) with a
`remediation`. Every error the engine raises is a `CcnlEngineError` exported
at the root, with a stable `code`; none is a bare `ValueError`, `TypeError`
or `AttributeError`.

`result.is_payable` is the one answer to "can this amount be paid as it is?".
Payability is fail-closed: a result is payable only when it has no blocker,
and every capability the registry requires is decided on facts the caller
supplied or ruled out by a decision of the run, never decided by a default.
The residence and the family composition are such facts: left `None` they
add a `requirement_unresolved` blocker (an empty `FamilyComposition()`
states that there is no dependant). Every defaulted public input field is
classified as either the fact itself or a fact the caller must state, and a
fact the engine reports as missing (seniority, contribution history, sector,
prior-year income, ...) adds a `missing_fact` blocker. Some defaults still
select a branch without a blocker (opening state, dependant conditions,
hours, pension fund): see
[Assurance](docs/trust/confidence.md#defaults-of-the-public-inputs).
A result is also blocked by any issue, any capability of the catalog left
uncomputed, any executed rule `assumed` or `missing` in the bundle and any
rule supplied by the caller. Each `result.blockers` entry has a
stable `code`, the `feature` it concerns and a `detail`; `result.assurance`
holds the axes they come from. Today no bundled CCNL gives a payable result:
the amounts are for simulation. See
[Assurance](docs/trust/confidence.md).

`result.rulesets` names every ruleset the run read, with its identity, hash
and readiness. Readiness (`exploratory`, `reviewed`, `production`) is tracked
for CCNL rulesets only; tax, INPS and surtax rulesets report `None`. The
engine has two modes, with the same amounts:

```python
engine = PayrollEngine.bundled()  # mode="simulation", the default
strict = PayrollEngine.bundled(mode="operational")

for contract in engine.list_contracts():  # ContractSummary, with readiness
    print(contract.ccnl_id, contract.readiness, contract.validity)
ruleset = engine.inspect_ruleset("commercio-confcommercio")  # RulesetAssurance
print(ruleset.readiness, ruleset.confidence)  # → reviewed unverified
```

`simulation` reports readiness; `operational` also adds a
`ruleset_not_production` blocker when the CCNL ruleset is not `production`.
No bundled CCNL is `production` yet, so nothing is payable in operational
mode. See [Readiness](docs/trust/readiness.md). Known simplifications of the
model are typed limitations: `result.assurance.limitations` lists those that
apply to the run, and an open one that can move an amount adds an
`open_limitation` blocker (see [Assurance](docs/trust/confidence.md#model-limitations)).
`contract.validity` is the span of dates on which every rule of the CCNL has
a value; a competence year leaves out, with a `run_not_computed` blocker,
the runs before the pay tables of its level start.

A full year derives its calendar from the CCNL: Commercio grants tredicesima
and quattordicesima, so the year has 14 runs. A different calendar needs a
`CalendarOverride` with a reason, and an override that drops a CCNL extra
month raises `InvalidInputError`. `Employment.employment_period` selects the
runs: a worker employed from July to September gets three runs, and the
September run also pays the 3/12 of tredicesima and quattordicesima accrued
until the termination. A month employed only in part pays the CCNL daily
quotas of its employed days (one twenty-sixth per Monday to Saturday for
most CCNLs); a CCNL whose data define no daily quota leaves that month
undetermined and not payable, never paid in full.

```python
from ccnl_engine import CompetenceYearPlan, PeriodFacts

year = engine.calculate_competence_year(
    CompetenceYearPlan(
        year=2026,
        employment=employment,
        employer=employer,
        default_facts=PeriodFacts(regione="IT-45"),
    )
)
print(len(year.period_results))  # → 14
next_year = year.next_opening_state  # close_tax_year of the closing state
```

The state keeps competence and cash apart: `closing_state.accrual` lists the
runs closed over the employment and the INPS base of each competence year,
`closing_state.cash` the payments and year-to-date totals of the tax year.
A run is paid on `payment_day` of its month unless `payment_dates` names its
date. A December paid after 12 January is a payment of the next tax year
(TUIR art. 51 c. 1): `calculate_competence_year` settles the conguaglio of
the year on its last payment actually made in it and opens the next tax
year with the late December, and `calculate_tax_year(TaxYearPlan(...))`
computes every payment cashed in one tax year, late payments of an earlier
competence year included. A run opens with the history of the employment:
`PeriodState.zero()` is the fact only for the first run of an employment
whose start is stated, and a run without its history is not payable.
Totals of another provider enter through
`engine.import_opening_balances(OpeningBalances(...))`, and the INPS base of
the worker's other employments of the year through
`CurrentYearTaxFacts.other_employment_inps_base` or the imported
`inps_bases`; see
[Opening state and imported balances](docs/engine/opening-state.md).

`CompetenceYearPlan.periods` maps a month (1-12) or a run id such as
`"2026-12-thirteenth"` to the `PeriodFacts` of that run; runs without an entry
take `default_facts`.

## CCNL coverage

125 contract configurations covering an estimated 16 million employees across
private and public sectors (individual contracts may cover overlapping populations).

- **L1 (Gross):** base salary, seniority, fixed allowances, additional months, hourly rate.
- **L2 (Net):** INPS contributions, TFR, IRPEF, regional/municipal surtax.
- **L3 (Work rules):** overtime and night/holiday premiums, absence deduction,
  leave accrual, sickness episodes over several months (carenza, INPS bands
  and CCNL integration derived from the bundle; pass a `SicknessEpisode` to
  each run it touches), performance bonuses, welfare/benefits.
  Pass `OvertimeHours.weeks` (a `WeeklyOvertimeHours` per calendar week) for CCNLs
  with per-week band thresholds to get accurate band partitioning.

Functional coverage, source quality and readiness are separate axes, never
blended into one percentage. Coverage derives from one capability registry,
the same that drives the capability report of every run.

[**CCNL coverage table**](https://lucas-puerari.github.io/ccnl-engine/docs/contracts/index.html): per-contract coverage, verification status, and feature breakdown

## Disclaimer

This library is not legal or tax advice. Figures are computed from publicly available CCNL tables and statutory rates as of the dates indicated in the data files. Always verify results against official sources or a qualified payroll professional.
