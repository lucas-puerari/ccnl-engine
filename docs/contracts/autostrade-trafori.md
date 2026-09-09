# CCNL Autostrade e Trafori Concessionari

| | |
|---|---|
| **CNEL code** | `I192` |
| **Sector** | autostrade e trafori — addetti alle concessionarie autostradali |
| **Tax sector** | `industria` |
| **Last renewal** | 2023-01-01 |
| **Workers (est.)** | ~15k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - AISCAT
    - FILT-CGIL
    - FIT-CISL
    - UILTRASPORTI

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
| `AQ` | Livello AQ (Quadro) | € 3,430.84 | — |
| `A` | Livello A | € 3,430.84 | — |
| `A1` | Livello A1 | € 3,065.88 | — |
| `B+` | Livello B Superiore | € 2,803.04 | — |
| `B` | Livello B | € 2,700.85 | — |
| `B1+` | Livello B1 Superiore | € 2,569.52 | — |
| `B1` | Livello B1 | € 2,467.30 | — |
| `C+` | Livello C Superiore | € 2,262.89 | — |
| `C` | Livello C | € 2,160.70 | — |
| `C1` | Livello C1 | € 1,970.92 | — |
| `D` | Livello D | € 1,459.92 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 9 increments

| Level | Increment (monthly) |
|---|---:|
| `D` | € 24.17 |
| `C1` | € 25.49 |
| `C` | € 26.47 |
| `C+` | € 26.47 |
| `B1` | € 28.59 |
| `B1+` | € 28.59 |
| `B` | € 30.68 |
| `B+` | € 30.68 |
| `A1` | € 33.58 |
| `A` | € 36.48 |
| `AQ` | € 36.48 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `D`, `C1`, `C`, `C+`, `B1`, `B1+`, `B`, `B+`, `A1`, `A`, `AQ`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Levels B+, B1+, C+ are parametrically derived as D × param/100 for the 2023 contract tranches (params: B+=192, B1+=176, C+=155). Verified against D values to within rounding. 2026 contract values taken from research agent sources.

!!! warning ""
    IDR 2021: modeled as 0.00 for 01/01/2023–01/08/2023 (element not yet established in first 2023 tranches). Period 1 values from 01/08/2023; period 2 from 01/01/2024 onwards.

!!! warning ""
    Apprenticeship: CCNL provides under-classification 2 levels below (engine schema requires static pay_level_code). Modeled as 100% passthrough.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-01-01 | [↗](https://www.aiscat.it/contratto-collettivo-autostrade-trafori) |

??? note "Coverage notes"
    CCNL I192 — Autostrade e Trafori Concessionari. Split model: paga base (minimo tabellare) + CONTINGENZA (frozen, 14m) + EDR 1991 (13m, EUR 10.33 uniform) + EDR 1997 (frozen, 14m, per-level) + IDR 2021 (14m, 2 tranches). AQ level has additional Indennità di Funzione EUR 72.30/month (14m). Seniority: 9 biennali.
    
    Contract covers two renewal periods: 2023 CCNL (01/01/2023–01/01/2025) and 2026 CCNL (01/08/2026–01/01/2028 open). Gap period 01/01/2025–01/08/2026 modeled at 2023 final-tranche values (inter-contract ultrattività).
    
    INPS: uses 2026-industria.json (TaxSector.INDUSTRIA). Divisor 167 derived from contract sources.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/autostrade-trafori.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/autostrade-trafori.py"
```
