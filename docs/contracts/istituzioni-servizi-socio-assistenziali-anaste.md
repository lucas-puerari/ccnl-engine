# CCNL Istituzioni e Servizi Socio-Assistenziali (ANASTE)

| | |
|---|---|
| **CNEL code** | `T131` |
| **Sector** | servizi socio-assistenziali |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~120k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🟢 Verified |

[← Contracts index](index.md)

??? note "Signatories"
    - ANASTE
    - FISASCAT-CISL
    - UILTuCS-UIL
    - UGL Terziario

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | ✅ implemented |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro (dirigente di struttura o coordinatore senior) | € 2,130.15 | — |
| `10` | Livello 10 — Responsabile di area/servizio | € 1,972.13 | — |
| `9` | Livello 9 — Coordinatore/Professionista senior | € 1,893.48 | — |
| `8` | Livello 8 — Operatore specializzato senior | € 1,769.59 | — |
| `7` | Livello 7 — Operatore specializzato | € 1,752.93 | — |
| `6` | Livello 6 — Operatore qualificato senior | € 1,696.37 | — |
| `5` | Livello 5 — Operatore qualificato | € 1,637.06 | — |
| `4` | Livello 4 — Operatore | € 1,562.10 | — |
| `3S` | Livello 3 Super — Operatore ausiliario specializzato | € 1,525.03 | — |
| `3` | Livello 3 — Operatore ausiliario | € 1,487.96 | — |
| `2` | Livello 2 — Addetto generico | € 1,390.12 | — |
| `1` | Livello 1 — Addetto base (introdotto nel rinnovo 2025) | € 1,295.43 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 35.12 |
| `10` | € 33.57 |
| `9` | € 30.99 |
| `8` | € 30.47 |
| `7` | € 29.95 |
| `6` | € 28.92 |
| `5` | € 28.41 |
| `4` | € 27.89 |
| `3S` | € 27.63 |
| `3` | € 27.37 |
| `2` | € 26.86 |
| `1` | € 25.31 |

## Apprenticeship

**professionalizzante_32** (type: `percentage`)  
Destination levels: `Q`, `10`, `9`, `8`, `7`, `6`, `5`, `4`, `3S`, `3`, `2`, `1`  
percentage: 0.95

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    LEVEL 1 PRE-2025: level 1 introduced ex-novo in 2025 renewal. Pre-2025 salary set equal to 2025-08-01 value (1295.43 EUR) — no historical data available.

!!! warning ""
    APPRENTICESHIP (Art. 22): modelled on levels 6-10 parameters (32 months, 90% mesi 1-28, 95% mesi 29+). Levels 1-5 have different duration (12 months, 95% from month 7) — not modelled separately.

!!! warning ""
    NURSES ALLOWANCE: indennita professionale infermieri 155 EUR/month (12 months) not included — qualifica-specific, not level-specific.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-07-23 | [↗](https://snalv.it/docs/anaste25/pdf6.pdf) |

??? note "Coverage notes"
    RENEWAL: CCNL signed 2025-07-23, triennio 2023-2025. Economic effects from 2025-08-01. Una tantum non modelled (non-recurring).
    
    CONGLOBATED (Art. 69): minimo contrattuale conglobato includes base wage, contingenza and EDR. No separate contingenza or EDR column.
    
    HOURLY DIVISOR (Art. 72): 164 h/month for 38h/week. Verified: 1696.37/10.34=164.06 (lvl 6), 1893.48/11.55=163.94 (lvl 9), 2130.15/12.99=163.98 (lvl Q).
    
    ADDITIONAL MONTHS (Art. 74): tredicesima only (paid December). Art. 75 states the quattordicesima equivalent is already embedded in the monthly conglobated minimum.
    
    SENIORITY (Art. 73): scatti triennali, max 10 scatti. Per-level amounts confirmed from Art. 73 table.
    
    LEVEL Q ALLOWANCE (Art. 70): indennita di funzione 77.47 EUR/month paid 13 months/year.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/istituzioni-servizi-socio-assistenziali-anaste.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/istituzioni-servizi-socio-assistenziali-anaste.py"
```
