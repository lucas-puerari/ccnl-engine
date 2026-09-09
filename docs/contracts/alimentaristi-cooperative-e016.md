# CCNL Alimentaristi Cooperative (Fedagripesca/Legacoop Agroalimentare/AGCI-Agrital)

| | |
|---|---|
| **CNEL code** | `E016` |
| **Sector** | industria alimentare — cooperative di produzione e lavoro |
| **Tax sector** | `industria` |
| **Last renewal** | 2024-05-14 |
| **Workers (est.)** | ~15k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Fedagripesca-Confcooperative
    - Legacoop Agroalimentare
    - AGCI-Agrital
    - FLAI-CGIL
    - FAI-CISL
    - UILA-UIL

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
| `1A` | Livello 1A | € 2,836.32 | — |
| `1` | Livello 1 | € 2,466.34 | — |
| `2` | Livello 2 | € 2,034.77 | — |
| `3A` | Livello 3A | € 1,788.12 | — |
| `3` | Livello 3 | € 1,603.17 | — |
| `4` | Livello 4 | € 1,479.82 | — |
| `5` | Livello 5 | € 1,356.52 | — |
| `6` | Livello 6 | € 1,233.20 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `6` | € 22.35 |
| `5` | € 24.59 |
| `4` | € 26.83 |
| `3` | € 29.06 |
| `3A` | € 32.42 |
| `2` | € 36.89 |
| `1` | € 44.71 |
| `1A` | € 51.42 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `6`, `5`, `4`, `3`, `3A`, `2`, `1`, `1A`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Apprenticeship rules involve per-level classification reduction not fully resolvable from available sources. Modeled as 100% passthrough for all levels.

!!! warning ""
    Quadri (livello 1A Q) and V.P. variants not modeled. Only the 8 standard levels are implemented.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-05-14 | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=E016) |

??? note "Coverage notes"
    CCNL E016 renewed 14/05/2024, valid 01/12/2023-30/11/2027. Signatories: Fedagripesca-Confcooperative, Legacoop Agroalimentare, AGCI-Agrital + FLAI-CGIL/FAI-CISL/UILA-UIL.
    
    SPLIT model: paga base (time-series, 5 tranches) + CONTINGENZA (frozen, 14 months) + EDR (EUR 10.33, all levels, 13 months) + IAR (Indennita Aggiuntiva dei Redditi, per-level, 14 months, 2 periods).
    
    8 core levels: 6 (lowest, order 1) to 1A (highest, order 8). Divisor 173, 14 months. Seniority: 24-month cadence, max 5 scatti biennali.
    
    IAR first period from 01/12/2023: 1A=151.11, 1=131.39, 2=108.40, 3A=95.26, 3=85.41, 4=78.84, 5=72.27, 6=65.70. Second period from 01/09/2027.
    
    INPS: uses 2026-industria.json (TaxSector.INDUSTRIA). Alimentaristi cooperative are classified as industria for INPS purposes.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/alimentaristi-cooperative-e016.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/alimentaristi-cooperative-e016.py"
```
