# ccnl-engine

[![PyPI](https://img.shields.io/pypi/v/ccnl-engine)](https://pypi.org/project/ccnl-engine/)
[![Python](https://img.shields.io/pypi/pyversions/ccnl-engine)](https://pypi.org/project/ccnl-engine/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/lucas-puerari/ccnl-engine/blob/main/LICENSE)

Python library for computing gross-to-net salary and employer cost from Italian CCNL
tables and statutory contribution rates.

→ [GitHub README](https://github.com/lucas-puerari/ccnl-engine) for the full CCNL coverage
matrix, quick-start, and design rationale.

## Installation

```bash
pip install ccnl-engine
```

## Interactive demo

Try the engine in your browser — no installation required:
[**Open demo →**](../demo/)

## Scope

The engine models:

- IRPEF gross and net (Art. 11–13 TUIR), work income deductions
- INPS contributions (employee and employer), resolved by headcount tier
- TFR accrual
- Contractual employer funds
- Part-time scaling, seniority increments, fixed allowances
- Apprenticeship contracts (under-classification and percentage tracks)
- Domestic work (flat per-hour contributions, non-withholding employer)

**Not modelled:**

- Regional and municipal income tax surcharges (*addizionali*)
- Family-dependent deductions (Art. 12 TUIR)
- IRPEF phaseout above €200k (Art. 1 cc. 3-4 L. 199/2025)
- Second-level bargaining (territorial and company agreements)
- Overtime, night/holiday premiums, leave accruals, sick-pay integrations

Each limitation is documented in the relevant data file's `coverage.notes` field.

## Disclaimer

Not legal or tax advice. Always verify results against official sources or a qualified
payroll professional.
