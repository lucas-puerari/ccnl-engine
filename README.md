# ccnl-engine

[![PyPI version](https://img.shields.io/pypi/v/ccnl-engine?logo=pypi&logoColor=white)](https://pypi.org/project/ccnl-engine/)
[![Python](https://img.shields.io/pypi/pyversions/ccnl-engine?logo=python&logoColor=white)](https://pypi.org/project/ccnl-engine/)
[![CI](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml)
[![Coverage](https://lucas-puerari.github.io/ccnl-engine/coverage-badge.svg)](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Python library for modeling Italian collective labor agreements (CCNL) as structured, versioned data and computing gross-to-net salary and employer cost from first principles.

**[Documentation](https://lucas-puerari.github.io/ccnl-engine/docs/) · [Demo](https://lucas-puerari.github.io/ccnl-engine/demo/)**

## Motivation

I never really understood employment contracts or pay slips. The whole system strikes me as needlessly complicated. On top of that, finding reliable CCNL information online feels like an uphill battle: conflicting figures are everywhere, and identifying authoritative sources is harder than it should be. This project grew out of a desire to understand a little more. I make no claim to becoming an expert, but I hope to make this information more accessible and comprehensible for everyone.

## The Problem

Italian payroll is governed by collective agreements (CCNL) that define base salaries, seniority increments, and allowances as time-series values — they change at negotiated renewal dates. Existing tools either lock this data inside proprietary systems or require a full HRMS. This library treats each CCNL as a validated JSON file and the computation as a pure function:

```
compute(PayrollScenario) → Calculation
```

The returned `Calculation` is self-describing: along with the `PayrollResult` (`.result`) it records the engine version, the exact CCNL / tax / INPS / surtax ruleset revisions used (`.ruleset_version`), and a snapshot of the inputs (`.input_snapshot`) — so any figure can be traced back to the engine and data that produced it.

## Quickstart

```python
from datetime import date
from ccnl_engine import (
    Employee, Employer, Employment,
    PayrollScenario, Permanent, compute,
)

calculation = compute(PayrollScenario(
    employee=Employee(level_code="4"),
    employment=Employment(
        ccnl="commercio-confcommercio.json",
        contract=Permanent(),
        employer=Employer(num_employees=50),
        date=date(2026, 9, 1),
    ),
))

payroll = calculation.result  # attributes are also forwarded onto the calculation
print(payroll.net_annual)              # → Decimal('...')
print(payroll.trattamento_integrativo) # → Decimal('...') — Art. 1 D.L. 3/2020 bonus
print(payroll.fiscal_simplifications)  # → frozenset of items not computed by the engine
print(payroll.employer_cost_annual)    # → Decimal('...')

print(calculation.engine_version)      # → '0.5.0'
print(calculation.ruleset_version)     # → {'ccnl': '…', 'tax': '…', 'inps': '…', 'surtax': '…'}
```

## CCNL coverage

Over 100 contracts covering approximately 16 million employees across private and public sectors.

- **L1 — Gross:** base salary, seniority, fixed allowances, additional months, hourly rate.
- **L2 — Net:** INPS contributions, TFR, IRPEF, regional/municipal surtax.
- **L3 — Extended:** overtime, sick/injury leave, performance bonuses, welfare/benefits.

Coverage % = (L1 × 50% + L2 × 35% + L3 × 15%) − 5% per missing data note (max −20%).
L3 is not yet implemented; current contracts score a maximum of 85%.

→ [**CCNL coverage table**](https://lucas-puerari.github.io/ccnl-engine/docs/contracts/index.html) — per-contract coverage, verification status, and feature breakdown across layers 1-3

## What is not modelled

**Outside engine scope (L1/L2 only):**

- Detrazioni per carichi di famiglia (Art. 12 TUIR)
- Bilateral system contributions (EST, Fon.Te, …)
- Preferential 5% tax on *premio di risultato* (Art. 1 c. 182 L. 208/2015)

**L3 — planned, not yet implemented:**

- Overtime and night/holiday premiums
- Sick-pay integrations and leave accruals
- Performance bonuses
- Welfare/benefits

See [API docs](https://lucas-puerari.github.io/ccnl-engine/docs/) for full detail.

## Disclaimer

This library is not legal or tax advice. Figures are computed from publicly available CCNL tables and statutory rates as of the dates indicated in the data files. Always verify results against official sources or a qualified payroll professional.
