# CCNL Industrie Cineaudiovisive (ANICA)

| | |
|---|---|
| **CNEL code** | `G111` |
| **Sector** | Cinema e audiovisivo |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-07-23 |
| **Workers (est.)** | ~2.3k |
| **Ruleset version** | `2025.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANICA
    - SLC-CGIL
    - FISTEL-CISL
    - UILCOM-UIL

## Coverage

### Funzionalità

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | ✅ implemented |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2025-07-23 |
| **Last verified** | — |
| **Next salary event** | 2027-07-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `7S` | Livello 7 Super (QA — Quadro) | € 2,880.55 | 2028-01-01 |
| `7` | Livello 7 (QB — Quadro) | € 2,758.66 | 2028-01-01 |
| `6S` | Livello 6 Super | € 2,510.69 | 2028-01-01 |
| `6` | Livello 6 | € 2,430.46 | 2028-01-01 |
| `5S` | Livello 5 Super | € 2,217.61 | 2028-01-01 |
| `5` | Livello 5 | € 2,164.88 | 2028-01-01 |
| `4S` | Livello 4 Super | € 2,103.30 | 2028-01-01 |
| `4` | Livello 4 | € 1,980.32 | 2028-01-01 |
| `3` | Livello 3 | € 1,796.03 | 2028-01-01 |
| `2` | Livello 2 | € 1,608.31 | 2028-01-01 |
| `1` | Livello 1 | € 1,440.48 | 2028-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 12.65 |
| `2` | € 13.17 |
| `3` | € 13.94 |
| `4` | € 14.46 |
| `4S` | € 14.46 |
| `5` | € 16.01 |
| `5S` | € 16.79 |
| `6` | € 17.56 |
| `6S` | € 17.56 |
| `7` | € 19.37 |
| `7S` | € 20.17 |

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: Apprenticeship provisions not modeled (primary CCNL text not publicly available). Field left empty.

!!! warning ""
    SIMPLIFICATION: No employer bilateral funds modeled. No public data found for a cinema-specific bilateral fund for impiegati/tecnici in production companies.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-07-23 | [↗](https://www.lavoro-economia.it/contratti-collettivi/ccnl.aspx?c=153) |

??? note "Coverage notes"
    Salary model: conglobated (paga base unica, nessuna contingenza/EDR separata). Source: lavoro-economia.it c=153 (CNEL G111), tabella Jul 2026.
    
    Hourly divisor 173 (industria standard, confirmed from lavoro-economia.it). Daily divisor: 26.
    
    Additional months: 14 (tredicesima + quattordicesima). UILCOM informativa 24/07/2025.
    
    Seniority: 5 scatti biennali (cadence_months=24, maximum_count=5). Amounts from published table Jul 2026.
    
    Salary periods: 5 tranches — Jan 2025 (+45 at L4), Jan 2026 (+45 at L4), Jul 2026 (+90, published anchor), Jul 2027 (+90), Jan 2028 (+90). Source: quotidianopiu.it + lavoro-economia.it.
    
    Non-Jul-2026 salary values computed parametrically: each level scaled by the L4 ratio at each tranche. Published Jul 2026 values are the direct source; others are derived.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/cinema-audiovisivi-industria.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/cinema-audiovisivi-industria.py"
```
