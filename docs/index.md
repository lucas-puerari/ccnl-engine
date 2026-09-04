# ccnl-engine

Italian CCNL payroll engine — gross-to-net and employer cost from first principles.

[![PyPI](https://img.shields.io/pypi/v/ccnl-engine)](https://pypi.org/project/ccnl-engine/)
[![Python](https://img.shields.io/pypi/pyversions/ccnl-engine)](https://pypi.org/project/ccnl-engine/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/lucas-puerari/ccnl-engine/blob/main/LICENSE)

## Installation

```bash
pip install ccnl-engine
```

## Quick start

```python
from decimal import Decimal
from datetime import date

from ccnl_engine.contracts.loaders import load_ccnl
from ccnl_engine.tax.loaders import load_year_rules
from ccnl_engine.engine.compute import ComputeRequest, compute
from ccnl_engine.models.employment import Permanent

ccnl  = load_ccnl("metalmeccanico-federmeccanica.json")
rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=50)

result = compute(ccnl, rules, ComputeRequest(
    level_code="D3",
    as_of=date(2026, 1, 1),
    employment=Permanent(),
))

print(result.gross_monthly)         # Decimal('...')
print(result.net_monthly)           # Decimal('...')
print(result.employer_cost_annual)  # Decimal('...')
```

## Interactive demo

Try the engine in your browser — no installation required:
[**Open demo →**](../demo/)

## Scope and limitations

The engine models:

- IRPEF gross and net (Art. 11–13 TUIR), work income deductions
- INPS contributions (employee and employer), resolved by headcount tier
- TFR accrual
- Contractual employer funds
- Part-time scaling, seniority increments, fixed allowances
- Apprenticeship contracts (under-classification and percentage tracks)
- Domestic work (flat per-hour contributions, non-withholding employer)

**Not modelled** (documented per-CCNL in `coverage.notes`):

- Regional and municipal income tax surcharges (_addizionali_)
- Family-dependent deductions (Art. 12 TUIR)
- _Trattamento integrativo_ (Art. 1 D.L. 3/2020)
- IRPEF phaseout above €200k (Art. 1 cc. 3–4 L. 199/2025)
