# CCNL per i dipendenti degli studi e delle attività professionali (Confprofessioni)

| | |
|---|---|
| **CNEL code** | `H442` |
| **Sector** | terziario |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~350k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Confprofessioni
    - Filcams-CGIL
    - Fisascat-CISL
    - Uiltucs-UIL

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
| `Q` | Manager (Quadro) — staff with managerial functions (Art. 2095 c.c., L. 190/1985) | € 2,436.76 | — |
| `1` | 1st Level — staff with directive functions or highly specialised technical role | € 2,156.38 | — |
| `2` | 2nd Level — senior concept-grade staff / highly specialised technicians | € 1,878.26 | — |
| `3S` | 3rd Level Super — senior concept-grade staff with specialised expertise | € 1,742.20 | — |
| `3` | 3rd Level — concept-grade staff with technical or administrative expertise | € 1,726.37 | — |
| `4S` | 4th Level Super — qualified staff with higher-grade duties | € 1,674.10 | — |
| `4` | 4th Level — qualified clerical staff | € 1,614.12 | — |
| `5` | 5th Level — clerical staff performing routine tasks | € 1,502.19 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 30.00 |
| `1` | € 26.00 |
| `2` | € 23.00 |
| `3S` | € 22.00 |
| `3` | € 22.00 |
| `4S` | € 20.00 |
| `4` | € 20.00 |
| `5` | € 20.00 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `4`, `4S`, `3`, `3S`, `2`, `1`  
percentage: 0.93

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    APPRENTICESHIP percentage (Allegato B Table 3 CCNL 2024): 70% months 1-12, 85% months 13-24, 93% from month 25, applied to all eligible destinations (4, 4S, 3, 3S, 2, 1); level V is excluded from professional apprenticeship (Art. 30B) and Quadri are not a destination. The same percentage table is assumed for all destination levels.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-02-16 | [↗](https://confprofessioni.eu/wp-content/uploads/2025/11/CCNL-Studi-2024-integrale-definitivo.pdf) |
| — | — | 2024-02-16 | [↗](https://www.confprofessioni.eu/wp-content/uploads/2026/07/00274046_CCNL_Studi_Professionali_2026.04.10_completo.pdf) |

??? note "Coverage notes"
    CONGLOBATED MINIMUMS: the minimum tabellare includes contingenza (up to 01/05/1992) and EDR (Interconfederal Agreement 31/07/1992), merged under CCNL 10/12/1992 and reaffirmed by Art. 138 CCNL 2024. fixed_allowances is empty for all levels.
    
    HOURLY DIVISOR: 170. Primary source: Art. 45 and Art. 137 CCNL 2024 ('divisore convenzionale orario fissato in 170').
    
    TRANCHES: four tranches — 01/03/2024, 01/10/2024, 01/10/2025, 01/12/2026. Source: Art. 139-140 and salary tables CCNL 2024 (confprofessioni.eu, complete version April 2026).
    
    ADDITIONAL MONTHS: 14 (tredicesima Art. 142 + quattordicesima Art. 143 CCNL 2024).
    
    SENIORITY INCREMENTS: triennial (36-month cadence), max 8 increments. Fixed amounts per Art. 134 CCNL 2024 in force from 01/10/2011: Q=30, 1=26, 2=23, 3S=22, 3=22, 4S=20, 4=20, 5=20.
    
    ENAC (Art. 141 CCNL 2024): EUR 42.35 (level 1), EUR 102.53 (level 2), EUR 110.40 (level 3S) per month, payable only to workers already classified under the Confedertecnica CCNL as of 01/07/2004; modelled as an allowance with role 'confedertecnica_pre_2004' (compute(..., roles={'confedertecnica_pre_2004'})).
    
    INPS: uses 2026-terziario.json (TaxSector.TERZIARIO). File already present — no changes to the tax file.
    
    CNEL code H442: confirmed from the CNEL archive 'Studi Professionali — Confprofessioni'. Workers covered: 317,554 (UNIEMENS 2022).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/studi-professionali-confprofessioni.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/studi-professionali-confprofessioni.py"
```
