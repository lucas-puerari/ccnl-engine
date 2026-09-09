# CCNL per i lavoratori dipendenti dalle aziende di credito (ABI)

| | |
|---|---|
| **CNEL code** | `J241` |
| **Sector** | credito |
| **Tax sector** | `credito` |
| **Last renewal** | — |
| **Workers (est.)** | ~270k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ABI
    - FABI
    - FIRST-CISL
    - FISAC-CGIL
    - UILCA
    - UNISIN

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
| `QD4` | Executive Managers - 4th level | € 5,160.06 | — |
| `QD3` | Executive Managers - 3rd level | € 4,396.88 | — |
| `QD2` | Executive Managers - 2nd level | € 3,965.48 | — |
| `QD1` | Executive Managers - 1st level | € 3,743.21 | — |
| `3A4` | 3rd Professional Area - 4th level | € 3,341.90 | — |
| `3A3` | 3rd Professional Area - 3rd level | € 3,059.49 | — |
| `3A2` | 3rd Professional Area - 2nd level | € 2,890.41 | — |
| `3A1` | 3rd Professional Area - 1st level | € 2,742.34 | — |
| `1e2A` | 1st and 2nd Professional Area (Unified Area) | € 2,479.45 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `QD4` | € 95.31 |
| `QD3` | € 95.31 |
| `QD2` | € 41.55 |
| `QD1` | € 41.55 |
| `3A4` | € 41.55 |
| `3A3` | € 41.55 |
| `3A2` | € 41.55 |
| `3A1` | € 41.55 |
| `1e2A` | € 29.07 |

## Apprenticeship

**terza_area** (type: `under_classification`)  
Destination levels: `3A2`, `3A3`, `3A4`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Apprenticeship (Art. 35, rinnovo 23-11-2023) targets the 3ª area professionale without naming the level; modelled for destination levels 3A2, 3A3 and 3A4 with 18 months one level below, then the destination level. 3A1 is excluded because the level below (Area Unificata 1ª e 2ª area) is not an apprenticeship classification.

!!! warning ""
    INPS employer_rate 26.76% flat from kitech.it (Credito e Assicurazioni 2026); the Fondo di solidarietà del credito (bilateral) is presumed included in the aggregate rate. Verify against the annual INPS circular.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-11-23 | [↗](https://www.first-cisl.it/rinnovo-ccnl-bancari-2023/) |
| — | — | — | [↗](https://www.ccnlbancari.it/) |

??? note "Coverage notes"
    Hourly divisor 162 for the 37.5h/week period (2023-11-23 to 2024-06-30) and 160 from 2024-07-01 (37h/week).
    
    Seniority: first scatto after 48 months, then every 36 months; maximum 8 scatti for the Aree Professionali and 7 for QD3/QD4 (maximum_count_by_level).
    
    Apprenticeship: https://www.ccnlbancari.it/ Art. 35, post-rinnovo 2023-11-23.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/bancari-abi.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/bancari-abi.py"
```
