# CCNL Radiotelevisivo — Settore Televisivo Multimediale

| | |
|---|---|
| **CNEL code** | `G091` |
| **Sector** | radiotelevisione — settore televisivo multimediale |
| **Tax sector** | `industria` |
| **Last renewal** | 2026-01-08 |
| **Workers (est.)** |  |
| **Ruleset version** | `—` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Confindustria Radio TV
    - SLC-CGIL
    - FISTEL-CISL
    - UILCOM-UIL

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | 🔲 not_implemented |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `9` | 9° livello | € 2,282.56 | — |
| `8` | 8° livello | € 2,092.44 | — |
| `7` | 7° livello | € 1,929.62 | — |
| `6` | 6° livello | € 1,840.62 | — |
| `5` | 5° livello | € 1,696.00 | — |
| `4` | 4° livello | € 1,425.96 | — |
| `3` | 3° livello | € 1,190.33 | — |
| `2` | 2° livello | € 1,046.74 | — |
| `1` | 1° livello | € 902.11 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 12.39 |
| `2` | € 12.91 |
| `3` | € 15.49 |
| `4` | € 18.08 |
| `5` | € 19.63 |
| `6` | € 21.17 |
| `7` | € 21.69 |
| `8` | € 22.72 |
| `9` | € 24.79 |

## Apprenticeship

**professionalizzante_breve** (type: `percentage`)  
Destination levels: `3`  
percentage: 0.90

**professionalizzante_esteso** (type: `percentage`)  
Destination levels: `4`, `5`, `6`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    INPS rates reuse existing 2026-industria.json (tax_sector=industria). No bilateral fund substitution for broadcasting sector identified; standard Confindustria INPS rates apply.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-01-08 | [↗](https://www.confindustriaradiotv.it/) |

??? note "Coverage notes"
    CCNL Radiotelevisivo 2026 signed 08/01/2026. Employer: Confindustria Radio TV. Unions: SLC-CGIL, FISTEL-CISL, UILCOM-UIL.
    
    SPLIT model: paga base (minimo tabellare, Art. 43) + contingenza congelata al 1° novembre 1991 (Allegato A). EDR not present in 2026 CCNL.
    
    DUAL-SECTOR contract: Settore Televisivo Multimediale (9 livelli) and Settore Radiofonico (6 livelli) modelled in two separate files because the engine's monotonicity validator (higher order >= higher salary at every tranche date) rejects a merged 15-level file: at 01/01/2026 Radio L2 (868.41) > TV L1 (835.62) and Radio L6 (1632.31) > TV L5 (1571.00), inverting the relative ordering set at the CCNL base date.
    
    TV sector has three new tranches: 01/01/2026, 01/06/2027, 01/01/2028. Radio sector has only two: 01/01/2026, 01/06/2027 (no 01/01/2028 tranche). The pre-2026 CCNL column values (from the 2022 contract) are not modelled.
    
    Hourly divisor 173 sourced from Art. 43. Verified on levels 3, 5, 7: none of the three back-calculations from the published hourly rate yield a conglobated total — values are paga base only, confirming the split model.
    
    Apprenticeship (Art. 27): professionalizzante, percentage type. TV L3 max 24 months; TV L4-L6 max 48-60 months (same % schedule). Levels L7-L9 not accessible via apprenticeship per Art. 27.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/radiotelevisive-televisivo.json"
    ```
