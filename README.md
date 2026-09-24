# ccnl-engine

[![PyPI version](https://img.shields.io/pypi/v/ccnl-engine?logo=pypi&logoColor=white)](https://pypi.org/project/ccnl-engine/)
[![Python](https://img.shields.io/pypi/pyversions/ccnl-engine?logo=python&logoColor=white)](https://pypi.org/project/ccnl-engine/)
[![CI](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml)
[![Coverage](https://lucas-puerari.github.io/ccnl-engine/coverage-badge.svg)](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Python engine for auditable Italian payroll simulations. CCNL-aware gross-to-net and
employer cost, versioned rules, provenance tracking, and explicit calculation scope.
Built for technical teams in HR, payroll, and compensation.

**[Documentation](https://lucas-puerari.github.io/ccnl-engine/docs/) · [Demo](https://lucas-puerari.github.io/ccnl-engine/demo/)**

## Motivation

I never really understood employment contracts or pay slips. The whole system strikes me as needlessly complicated. On top of that, finding reliable CCNL information online feels like an uphill battle: conflicting figures are everywhere, and identifying authoritative sources is harder than it should be. This project grew out of a desire to understand a little more. I make no claim to becoming an expert, but I hope to make this information more accessible and comprehensible for everyone.

## The Problem

Italian payroll is governed by collective agreements (CCNL) that define base salaries, seniority increments, and allowances as time-series values — they change at negotiated renewal dates. Existing tools either lock this data inside proprietary systems or require a full HRMS. This library treats each CCNL as a validated JSON file and the computation as a pure function:

```
PayrollEngine.calculate(PayrollRequest) → PeriodCalculationResult
```

Each result is fully itemised: gross, net, employer cost, INPS breakdown, IRPEF computation, pay items, and a ledger of every accounting entry — so any figure can be traced back to the engine and data that produced it.

## Quickstart

```python
from datetime import date
from ccnl_engine import EmploymentFacts, PayrollEngine, PayrollRequest, PayrollRun

engine = PayrollEngine.from_builtin_data()
result = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="commercio-confcommercio.json",
        level_code="4",
        employment_facts=EmploymentFacts(num_employees=50),
    )
)

print(result.period_gross)  # → Decimal('...')
print(result.period_net)  # → Decimal('...')
print(result.period_id)  # → PeriodId(year=2026, month=1)
```

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
