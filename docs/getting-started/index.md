# Get started

## Installation

```bash
pip install ccnl-engine
```

!!! warning "Version"
    These pages document the `main` branch. The package installed from PyPI
    may be an earlier release with a different API: compare
    `ccnl_engine.engine_version` with the
    [release notes](https://github.com/lucas-puerari/ccnl-engine/releases).

Requires Python 3.12+. Every pull request and every release run the API and
knowledge tests on Python 3.12, 3.13 and 3.14, and smoke-test the built
wheel on each.

## Find a CCNL and its level

`Employment.ccnl_id` takes the slug or the CNEL code of a CCNL, and
`level_code` one of its level codes.
Search the catalog by name or slug, pick the contract by slug or CNEL code
and list its levels:

```python
--8<-- "docs/examples/catalog/example.py"
```

`engine.list_contracts()` returns every contract of the engine's repository;
`search_ccnls()` matches name and slug of a bundled one; `get_ccnl()` and
`engine.list_levels()` take a slug or a CNEL code. A CNEL code shared by several bundled contracts raises
`UnknownCcnlError` with their slugs as `suggestions`.

## Quickstart

The minimum working example: load a CCNL, describe the employee, compute the
payroll.

```python
--8<-- "docs/examples/period/example.py"
```

Every result says whether its amounts can be paid as computed
(`result.is_payable`, `result.blockers`) and which rulesets it read, with
their readiness (`result.rulesets`). `engine.list_contracts()` and
`engine.inspect_ruleset(ccnl_id)` report readiness before any run.
`PayrollEngine.bundled()` simulates; `PayrollEngine.bundled(mode="operational")`
computes the same amounts but blocks payment unless the CCNL ruleset is
`production`: the [catalogue](../contracts/index.md) lists them. See
[Readiness](../trust/readiness.md#simulation-and-operational-modes).

## A full year

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
date, or the CCNL fixes the day of an extra month (Commercio: the
tredicesima on Christmas Eve, the quattordicesima on 1 July).
A December paid after 12 January is a payment of the next tax year
(TUIR art. 51 c. 1): `calculate_competence_year` settles the conguaglio of
the year on its last payment actually made in it and opens the next tax
year with the late December, and `calculate_tax_year(TaxYearPlan(...))`
computes every payment cashed in one tax year, late payments of an earlier
competence year included. The bundle ships the tax tables of 2026 and
provisional tables of 2027 (`ccnl_engine.catalog.supported_tax_years()`).
**The 2027 tables are provisional**: the 2027 sources are not published
yet, so they carry the 2026 values over (`RulesetIdentity.provisional`).
Every run that reads them, a December 2026 paid after 12 January
included, is computed and not payable, with the open limitation
`provisional_ruleset` (tax) or `provisional_inps_ruleset` (INPS). A payment of any other tax year raises
`UnsupportedTaxYearError`. A run opens with the history of the employment:
`PeriodState.zero()` is the fact only for the first run of an employment
whose start is stated, and a run without its history is not payable.
Totals of another provider enter through
`engine.import_opening_balances(OpeningBalances(...))`, and the INPS base of
the worker's other employments of the year through
`CurrentYearTaxFacts.other_employment_inps_base` or the imported
`inps_bases`; see
[Opening state and imported balances](../engine/opening-state.md).

`CompetenceYearPlan.periods` maps a month (1-12) or a run id such as
`"2026-12-thirteenth"` to the `PeriodFacts` of that run; runs without an entry
take `default_facts`.

## Supported CCNLs

Every bundled CCNL is listed in the contracts index with its CNEL code,
sector, estimated workforce, readiness and coverage; the list and its counts
are generated from the data.

Full list with sources and per-contract examples: [Contracts →](../contracts/index.md)

To understand the terminology used in each contract page, read
[Domain: What is a CCNL](../domain/index.md) first.

## Disclaimer

Not legal or tax advice. Always verify results against official sources or a
qualified payroll professional.
