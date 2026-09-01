# ccnl-engine

A Python library for modeling Italian collective labor agreements (CCNL) as structured, versioned data and computing gross-to-net salary and employer cost from first principles.

## Why

Italian payroll is governed by collective agreements (CCNL) that define base salaries, seniority increments, and allowances as time-series values — they change at negotiated renewal dates. Existing tools either lock this data inside proprietary systems or require a full HRMS. This library treats each CCNL as a validated JSON file and the computation as a pure function:

```
compute(ccnl, level, date, rules, employment) → ComputationResult
```

## Quickstart

```python
from datetime import date
from ccnl_engine.data.loaders import load_ccnl, load_year_rules
from ccnl_engine.engine.compute import compute
from ccnl_engine.models.ccnl import TaxSector
from ccnl_engine.models.employment import Permanent

ccnl  = load_ccnl("commercio-confcommercio.json")
rules = load_year_rules(2026, TaxSector.TERZIARIO, num_employees=50)
result = compute(ccnl, "4", date(2026, 9, 1), rules, Permanent(type="permanent"))

print(result.net_annual)           # → Decimal('...')
print(result.employer_cost_annual) # → Decimal('...')
```

## CCNL coverage

| CCNL | Sector | Layer 1 | Layer 2 | Layer 3 |
|---|---|:---:|:---:|:---:|
| Commercio — Confcommercio | Terziario | ✅ | ✅ | — |
| Metalmeccanico — Federmeccanica/Assistal | Industria | ✅ | ✅ | — |
| Metalmeccanico PMI — Unionmeccanica-Confapi | Industria | ✅ | ✅ | — |
| Chimica-Farmaceutica — Federchimica/Farmindustria/Assistal | Industria | ✅ | ✅ | — |
| Turismo — Confcommercio | Terziario | ✅ | ✅ | — |
| Edilizia — ANCE | Edilizia | ✅ | ✅ | — |
| Cooperative Sociali — Confcooperative/Legacoop/AGCI | Terziario | ✅ | ✅ | — |
| Logistica, Trasporto Merci e Spedizione — Confetra | Industria | ✅ | ✅ | — |

**Layer 1** — base salary, seniority increments (*scatti di anzianità*), fixed allowances, additional months.  
**Layer 2** — part-time, fixed-term (NASpI *addizionale*), apprenticeship (percentage or under-classification).  
**Layer 3** — overtime, night/holiday premiums, leave accruals, sick-pay integrations. Out of scope for now.

## Design principles

- **Data and engine are strictly separated.** CCNL economic values live in JSON files under `data/`; the engine reads them and knows nothing about any specific contract.
- **Every monetary value is a time series.** No bare decimals — every value is a `TimeSeries` with explicit `valid_from` / `valid_until` dates.
- **`Decimal` everywhere, never `float`.** Monetary values are strings in JSON, loaded as `Decimal` in Python.
- **Single rounding point.** `money()` in `rounding.py`, `ROUND_HALF_UP` to 2 decimal places — the only place rounding occurs.
- **Source traceability.** Every value in a data file is traceable to a primary source (official CCNL tables, CNEL archive). No value from blogs or secondary sources.
- **Coverage declared explicitly.** Each data file carries a `coverage` block declaring what is implemented, partial, or out of scope.
- **Every simplification is documented.** `# SIMPLIFICATION:` comments mark every approximation vs. full Italian payroll law.

## What is not modelled

- Addizionali regionali and addizionali comunali
- Detrazioni per carichi di famiglia (Art. 12 TUIR)
- IVS contributory ceiling split (Art. 1 L. 335/1995)
- Second-level bargaining (territorial and company agreements)
- Bilateral system contributions (EST, Fon.Te, …)
- Overtime, premiums, and leave (Layer 3)

Each limitation is documented in the relevant data file's `coverage.notes` field and marked with `# SIMPLIFICATION:` comments in the engine source.

## Disclaimer

This library is not legal or tax advice. Figures are computed from publicly available CCNL tables and statutory rates as of the dates indicated in the data files. Always verify results against official sources or a qualified payroll professional.

---

## Development

### Setup

```bash
make setup
```

Activates local git hooks (conventional commits, single-line messages).

