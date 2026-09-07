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
compute(ccnl, rules, employee) → Calculation
```

The returned `Calculation` is self-describing: along with the `PayrollResult` (`.result`) it records the engine version, the exact CCNL / tax / INPS / surtax ruleset revisions used (`.ruleset_version`), and a snapshot of the inputs (`.input_snapshot`) — so any figure can be traced back to the engine and data that produced it.

## Quickstart

```python
from datetime import date
from ccnl_engine import (
    ContractPosition, Employee, Permanent,
    WorkArrangement, compute, load_ccnl, load_year_rules,
)

ccnl = load_ccnl("commercio-confcommercio.json")
rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=50)
employee = Employee(
    position=ContractPosition(
        level_code="4",
        as_of=date(2026, 9, 1),
        employment=Permanent(),
    ),
    arrangement=WorkArrangement(),
)
calculation = compute(ccnl, rules, employee)

payroll = calculation.result  # attributes are also forwarded onto the calculation
print(payroll.net_annual)              # → Decimal('...')
print(payroll.trattamento_integrativo) # → Decimal('...') — Art. 1 D.L. 3/2020 bonus
print(payroll.fiscal_simplifications)  # → frozenset of items not computed by the engine
print(payroll.employer_cost_annual)    # → Decimal('...')

print(calculation.engine_version)      # → '0.5.0'
print(calculation.ruleset_version)     # → {'ccnl': '…', 'tax': '…', 'inps': '…', 'surtax': '…'}
```

## Provenance chain

Every `PayrollResult` carries a `provenance` tuple — an ordered chain of `RuleProvenance` objects, one for each rule that contributed to the computed pay: the level declaration, the active salary-period tranche, each applied allowance, and the seniority-increment rule.

```python
for prov in calculation.result.provenance:
    doc = prov.location.source_document
    print(doc.kind, doc.document_id, prov.location.section)
    print(doc.url)
    print(prov.extraction.verification_status)
```

Each `RuleProvenance` records:
- **`location.source_document`** — the primary source (kind, stable `document_id`, URL)
- **`location.section`** — the clause or table within that document
- **`extraction`** — method (`manual`, `ai_assisted`, `back_calculation`), timestamp, and verification status

The engine rejects any CCNL file where provenance is missing from even one rule, so every figure in the output is traceable to a specific source document and clause.

## CCNL coverage

Over 100 contracts covering approximately 16 million employees across private and public sectors.

→ [**Full CCNL coverage table**](https://lucas-puerari.github.io/ccnl-engine/docs/contracts/index.html)

## What is not modelled

- Detrazioni per carichi di famiglia (Art. 12 TUIR)
- Bilateral system contributions (EST, Fon.Te, …)
- Overtime, night/holiday premiums, leave accruals, sick-pay integrations
- Preferential 5% tax on *premio di risultato* (Art. 1 c. 182 L. 208/2015)

See [API docs](https://lucas-puerari.github.io/ccnl-engine/docs/) for full detail.

## Disclaimer

This library is not legal or tax advice. Figures are computed from publicly available CCNL tables and statutory rates as of the dates indicated in the data files. Always verify results against official sources or a qualified payroll professional.
