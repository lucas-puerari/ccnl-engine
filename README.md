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
estimate_annual(AnnualEstimateInput) → Calculation
```

The returned `Calculation` is self-describing: along with the `AnnualEstimate` (`.result`) it records the engine version, the exact CCNL / tax / INPS / surtax ruleset revisions used (`.ruleset_version`), and a snapshot of the inputs (`.input_snapshot`) — so any figure can be traced back to the engine and data that produced it.

## Quickstart

```python
from datetime import date
from ccnl_engine import (
    AnnualEstimateInput, Employee, Employer, Employment,
    Permanent, estimate_annual,
)

calculation = estimate_annual(
    AnnualEstimateInput(
        employee=Employee(level_code="4"),
        employment=Employment(
            ccnl="commercio-confcommercio",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 1, 1),
        ),
    )
)

payroll = calculation.result
print(payroll.net_annual)                          # → Decimal('...')
print(payroll.taxes.trattamento_integrativo)       # → Decimal('...') — Art. 1 D.L. 3/2020
print(payroll.coverage.status)                     # → 'complete' | 'partial'
print(payroll.employer_cost.employer_cost_annual)  # → Decimal('...')

print(calculation.engine_version)   # → '0.5.1'
print(calculation.ruleset_version)  # → {'ccnl': '…', 'tax': '…', 'inps': '…', 'surtax': '…'}
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
