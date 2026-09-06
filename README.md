# ccnl-engine

[![PyPI version](https://img.shields.io/pypi/v/ccnl-engine?logo=pypi&logoColor=white)](https://pypi.org/project/ccnl-engine/)
[![Python](https://img.shields.io/pypi/pyversions/ccnl-engine?logo=python&logoColor=white)](https://pypi.org/project/ccnl-engine/)
[![CI](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/lucas-puerari/ccnl-engine/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/lucas-puerari/ccnl-engine/graph/badge.svg)](https://codecov.io/gh/lucas-puerari/ccnl-engine)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Python library for modeling Italian collective labor agreements (CCNL) as structured, versioned data and computing gross-to-net salary and employer cost from first principles.

**[Interactive demo](https://lucas-puerari.github.io/ccnl-engine/demo/) · [Documentation](https://lucas-puerari.github.io/ccnl-engine/docs/) · [CCNL coverage](https://lucas-puerari.github.io/ccnl-engine/docs/contracts/index.html)**

## Why

Italian payroll is governed by collective agreements (CCNL) that define base salaries, seniority increments, and allowances as time-series values — they change at negotiated renewal dates. Existing tools either lock this data inside proprietary systems or require a full HRMS. This library treats each CCNL as a validated JSON file and the computation as a pure function:

```
compute(ccnl, rules, employee) → Payslip
```

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
payslip = compute(ccnl, rules, employee)

print(payslip.net_annual)              # → Decimal('...')
print(payslip.trattamento_integrativo) # → Decimal('...') — Art. 1 D.L. 3/2020 bonus
print(payslip.fiscal_simplifications)  # → frozenset of items not computed by the engine
print(payslip.employer_cost_annual)    # → Decimal('...')
```

## CCNL coverage

85 contracts covering ~15 million employees across private and public sectors.

→ [**Full CCNL coverage table**](https://lucas-puerari.github.io/ccnl-engine/docs/contracts/index.html)

## What is not modelled

- Detrazioni per carichi di famiglia (Art. 12 TUIR)
- Bilateral system contributions (EST, Fon.Te, …)
- Overtime, night/holiday premiums, leave accruals, sick-pay integrations
- Preferential 5% tax on *premio di risultato* (Art. 1 c. 182 L. 208/2015)

See [API docs](https://lucas-puerari.github.io/ccnl-engine/docs/) for full detail.

## Disclaimer

This library is not legal or tax advice. Figures are computed from publicly available CCNL tables and statutory rates as of the dates indicated in the data files. Always verify results against official sources or a qualified payroll professional.
