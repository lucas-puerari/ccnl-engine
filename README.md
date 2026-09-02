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
from ccnl_engine.contracts.loaders import load_ccnl
from ccnl_engine.tax.loaders import load_year_rules
from ccnl_engine.engine.compute import compute
from ccnl_engine.models.ccnl import TaxSector
from ccnl_engine.models.employment import Permanent

ccnl = load_ccnl("commercio-confcommercio.json")
rules = load_year_rules(2026, TaxSector.TERZIARIO, num_employees=50)
result = compute(ccnl, "4", date(2026, 9, 1), rules, Permanent())

print(result.net_annual)  # → Decimal('...')
print(result.employer_cost_annual)  # → Decimal('...')
```

## CCNL coverage

| # | CCNL | Sector | Layer 1 | Layer 2 | Layer 3 |
|---|---|---|:---:|:---:|:---:|
| 1 | Commercio — Confcommercio | Terziario | ✅ | ✅ | — |
| 2 | Metalmeccanico — Federmeccanica/Assistal | Industria | ✅ | ✅ | — |
| 3 | Metalmeccanico PMI — Unionmeccanica-Confapi | Industria | ✅ | ✅ | — |
| 4 | Chimica-Farmaceutica — Federchimica/Farmindustria/Assistal | Industria | ✅ | ✅ | — |
| 5 | Turismo — Confcommercio | Terziario | ✅ | ✅ | — |
| 6 | Edilizia — ANCE | Edilizia | ✅ | ✅ | — |
| 7 | Cooperative Sociali — Confcooperative/Legacoop/AGCI | Terziario | ✅ | ✅ | — |
| 8 | Logistica, Trasporto Merci e Spedizione — Confetra | Industria | ✅ | ✅ | — |
| 9 | Servizi di Pulizia e Multiservizi — ANIP-Confindustria | Terziario | ✅ | ✅ | — |
| 10 | Studi e Attività Professionali — Confprofessioni | Terziario | ✅ | ✅ | — |
| 11 | Credito — ABI | Credito | ✅ | ✅ | — |
| 12 | Tessile Abbigliamento Moda — SMI | Industria | ✅ | ✅ | — |
| 13 | Alimentari Industria — Federalimentare | Industria | ✅ | ✅ | — |
| 14 | Distribuzione Moderna Organizzata — Federdistribuzione | Terziario | ✅ | ✅ | — |
| 15 | Metalmeccanica e Installazione Impianti — Artigianato | Artigianato | ✅ | ✅ | — |
| 16 | Gomma e Plastica Industria — Federazione Gomma Plastica | Industria | ✅ | ✅ | — |
| 17 | Grafica e Editoria — AIEG-Acigraf | Industria | ✅ | ✅ | — |
| 18 | Carta e Cartone — Assocarta | Industria | ✅ | ✅ | — |
| 19 | Telecomunicazioni — Asstel | Industria | ✅ | ✅ | — |
| 20 | Vigilanza Privata — ASSIV/ANIVP/UNIV (GPG) | Terziario | ✅ | ✅ | — |
| 21 | Legno e Arredamento — Federlegno-Arredo | Industria | ✅ | ✅ | — |
| 22 | Edilizia e Affini — CNA/Confartigianato/Casartigiani | Artigianato | ✅ | ✅ | — |
| 23 | Gas e Acqua — Utilitalia/Proxigas/Anfida/Assogas | Industria | ✅ | ✅ | — |
| 24 | Istituzioni Socio-Assistenziali — UNEBA | Terziario | ✅ | ✅ | — |
| 25 | Acconciatura ed Estetica — Confartigianato/CNA | Artigianato | ✅ | ✅ | — |
| 26 | Area Alimentazione e Panificazione — Artigianato (Confartigianato/CNA) | Artigianato | ✅ | ✅ | — |
| 27 | Autoferrotranvieri e Internavigatori (Mobilita/TPL) — AGENS/ASSTRA/ANAV | Terziario | ✅ | ✅ | — |
| 28 | Credito Cooperativo (BCC/CRA) — Federcasse | Credito | ✅ | ✅ | — |
| 29 | Elettrico (produzione/distribuzione energia) — Elettricita Futura | Industria | ✅ | ✅ | — |
| 30 | Calzaturiero (industria delle calzature) — Assocalzaturifici | Industria | ✅ | ✅ | — |
| 31 | Area Tessile-Moda e Chimica-Ceramica — Artigianato (Confartigianato/CNA) | Artigianato | ✅ | ✅ | — |
| 32 | Area Legno-Lapidei — Artigianato (Confartigianato/CNA) | Artigianato | ✅ | ✅ | — |
| 33 | Area Comunicazione — Artigianato (Confartigianato/CNA) | Artigianato | ✅ | ✅ | — |
| 34 | Ceramica Industria — Confindustria Ceramica (Assopiastrelle) | Industria | ✅ | ✅ | — |
| 35 | Orafi e Argentieri — Federorafi | Industria | ✅ | ✅ | — |

**Layer 1** — base salary, seniority increments (*scatti di anzianità*), fixed allowances, additional months.  
**Layer 2** — part-time, fixed-term (NASpI *addizionale*), apprenticeship (percentage or under-classification).  
**Layer 3** — overtime, night/holiday premiums, leave accruals, sick-pay integrations. Out of scope for now.

✅ implemented · ⚠️ partial (documented simplifications or missing sub-tracks) · — out of scope

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
