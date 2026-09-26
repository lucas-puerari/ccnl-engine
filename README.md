# ccnl-engine

[![PyPI version](https://img.shields.io/pypi/v/ccnl-engine?logo=pypi&logoColor=white)](https://pypi.org/project/ccnl-engine/)
[![Python](https://img.shields.io/pypi/pyversions/ccnl-engine?logo=python&logoColor=white)](https://pypi.org/project/ccnl-engine/)
[![CI](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml)
[![Coverage](https://lucas-puerari.github.io/ccnl-engine/coverage-badge.svg)](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Python engine for auditable Italian payroll simulations. CCNL-aware gross-to-net and
employer cost, versioned rules, provenance tracking, and an explicit status on every result.
Built for technical teams in HR, payroll, and compensation.

**[Documentation](https://lucas-puerari.github.io/ccnl-engine/docs/) · [Demo](https://lucas-puerari.github.io/ccnl-engine/demo/)**

## Motivation

I never really understood employment contracts or pay slips. The whole system strikes me as needlessly complicated. On top of that, finding reliable CCNL information online feels like an uphill battle: conflicting figures are everywhere, and identifying authoritative sources is harder than it should be. This project grew out of a desire to understand a little more. I make no claim to becoming an expert, but I hope to make this information more accessible and comprehensible for everyone.

## The Problem

Italian payroll is governed by collective agreements (CCNL) that define base salaries, seniority increments, and allowances as time-series values — they change at negotiated renewal dates. Existing tools either lock this data inside proprietary systems or require a full HRMS. This library treats each CCNL as a validated JSON file and the computation as a pure function:

```
PayrollEngine.calculate_period(PeriodInput) → PeriodResult
PayrollEngine.calculate_year(YearInput) → YearResult
```

Each result carries a status (`final`, `provisional`, `incomplete` or `rejected`),
the issues that lowered it and the decisions taken. It is fully itemised: gross, net, employer cost, INPS breakdown, IRPEF computation, pay items, and a ledger of every accounting entry, so any figure can be traced back to the engine and data that produced it.

## Quickstart

```python
from datetime import date
from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)

engine = PayrollEngine.bundled()
employment = Employment(ccnl_slug="commercio-confcommercio.json", level_code="4")
employer = EmployerProfile(headcount=Headcount(50))

result = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        employment=employment,
        employer=employer,
    )
)

print(result.status)  # → final
print(result.period_gross)  # → Decimal('...')
print(result.period_net)  # → Decimal('...')
```

The inputs group the facts by owner: `Employment` (CCNL, level, contract,
employment period, hours, seniority, sector), `EmployerProfile` (headcount,
activity), `PriorYearTaxFacts` (prior-year income and written waivers, read by
every substitute-tax regime) and `PeriodFacts` (events, surtax jurisdiction,
family, contributable hours of one run). Every input is validated when it is
built. A fact left unknown never looks final: the regime it drives is not
applied and the result is `provisional`.

A full year derives its calendar from the CCNL: Commercio grants tredicesima
and quattordicesima, so the year has 14 runs. A different calendar needs a
`CalendarOverride` with a reason, and an override that drops a CCNL extra
month raises `InvalidInputError`. `Employment.employment_period` selects the
runs: a worker employed from July to September gets three runs, and the
September run also pays the 3/12 of tredicesima and quattordicesima accrued
until the termination.

```python
from ccnl_engine import PeriodFacts, YearInput

year = engine.calculate_year(
    YearInput(
        year=2026,
        employment=employment,
        employer=employer,
        default_facts=PeriodFacts(regione="IT-45"),
    )
)
print(len(year.period_results))  # → 14
next_year = engine.close_tax_year(year.closing_state)
```

`YearInput.periods` maps a month (1-12) or a run id such as
`"2026-12-thirteenth"` to the `PeriodFacts` of that run; runs without an entry
take `default_facts`.

## CCNL coverage

125 contract configurations covering an estimated 16 million employees across
private and public sectors (individual contracts may cover overlapping populations).

- **L1 — Gross:** base salary, seniority, fixed allowances, additional months, hourly rate.
- **L2 — Net:** INPS contributions, TFR, IRPEF, regional/municipal surtax.
- **L3 — Work rules:** overtime and night/holiday premiums, absence deduction,
  leave accrual, sick-pay integration, performance bonuses, welfare/benefits.
  Pass `OvertimeHours.weeks` (a `WeeklyOvertimeHours` per calendar week) for CCNLs
  with per-week band thresholds to get accurate band partitioning.

Coverage % = (L1 × 50% + L2 × 35% + L3 × 15%) − 5% per missing data note (max −20%).

[**CCNL coverage table**](https://lucas-puerari.github.io/ccnl-engine/docs/contracts/index.html) — per-contract coverage, verification status, and feature breakdown

## Disclaimer

This library is not legal or tax advice. Figures are computed from publicly available CCNL tables and statutory rates as of the dates indicated in the data files. Always verify results against official sources or a qualified payroll professional.
