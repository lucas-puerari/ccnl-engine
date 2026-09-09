# CCNL Industria Turistica (Federturismo Confindustria)

| | |
|---|---|
| **CNEL code** | `H05B` |
| **Sector** | turismo — alberghi, campeggi, villaggi e strutture ricettive |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-01-01 |
| **Workers (est.)** | ~40k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Federturismo Confindustria
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTuCS

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
| `A1` | Livello A1 | € 2,500.91 | — |
| `A2` | Livello A2 | € 2,315.87 | — |
| `B1` | Livello B1 | € 2,158.18 | — |
| `B2` | Livello B2 | € 1,973.12 | — |
| `C1` | Livello C1 | € 1,861.27 | — |
| `C2` | Livello C2 | € 1,756.59 | — |
| `C3` | Livello C3 | € 1,647.90 | — |
| `D1` | Livello D1 | € 1,584.79 | — |
| `D2` | Livello D2 | € 1,464.57 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `D2` | € 30.47 |
| `D1` | € 31.25 |
| `C3` | € 32.54 |
| `C2` | € 33.05 |
| `C1` | € 34.86 |
| `B2` | € 36.15 |
| `B1` | € 37.70 |
| `A2` | € 39.25 |
| `A1` | € 40.80 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `D2`, `D1`, `C3`, `C2`, `C1`, `B2`, `B1`, `A2`, `A1`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Salary values for all levels except A1 and D2 derived via parametric ratio formula and verified against independent research to <EUR 0.02 accuracy.

!!! warning ""
    Pre-renewal salary (pre 01/01/2025) not modeled; series starts 2025-01-01. Agreement date set to first tranche date; actual signing date unverified.

!!! warning ""
    Seniority cadence set to 36 months; may be 36 or 48 per source ambiguity. Maximum scatti: 6.

!!! warning ""
    Apprenticeship is under_classification 2 levels below destination (per-destination-level), not supported by engine schema. Modeled as 100% passthrough.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-01-01 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=H05B) |

??? note "Coverage notes"
    CCNL H05B — Federturismo Confindustria. Conglobated model. 9 levels: D2-D1-C3-C2-C1-B2-B1-A2-A1. Divisor 172, 14 months. Function allowances: A1+75 EUR, A2+70 EUR (14 months). Seniority 36-month cadence, max 6.
    
    INPS: uses 2026-terziario.json (TaxSector.TERZIARIO). Same classification as H052 turismo-federalberghi.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/industria-turistica-federturismo.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/industria-turistica-federturismo.py"
```
