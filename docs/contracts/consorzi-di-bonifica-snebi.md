# CCNL Consorzi di Bonifica (SNEBI-FLAI-FAI-FILBI)

| | |
|---|---|
| **CNEL code** | `A131` |
| **Sector** | Agricoltura |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2025-05-21 |
| **Workers (est.)** | ~4k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - SNEBI
    - FLAI-CGIL
    - FAI-CISL
    - FILBI-UIL

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | — out_of_scope |
| **L3 — Work rules** | ✅ implemented |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `AQ187` | AQ187 — quadro | € 2,868.89 | — |
| `AQ185` | AQ185 — quadro | € 2,838.21 | — |
| `A184` | A184 | € 2,822.87 | — |
| `A170` | A170 | € 2,608.08 | — |
| `AQ164` | AQ164 — quadro | € 2,516.04 | — |
| `AQ162` | AQ162 — quadro | € 2,485.35 | — |
| `A160` | A160 | € 2,454.67 | — |
| `A159` | A159 | € 2,439.32 | — |
| `A157` | A157 | € 2,408.65 | — |
| `A135` | A135 | € 2,071.13 | — |
| `A134` | A134 | € 2,055.79 | — |
| `B132_ex51` | B132 — ex cat. 5/1 (alternate scatto 47.73) | € 2,025.10 | — |
| `B132` | B132 — ex cat. 4/1 (best-guess scatto 50.05) | € 2,025.10 | — |
| `B128_ex52` | B128 — ex cat. 5/2 (alternate scatto 44.44) | € 1,963.73 | — |
| `B128` | B128 — ex cat. 4/2 (best-guess scatto 47.92) | € 1,963.73 | — |
| `C127` | C127 | € 1,948.38 | — |
| `C122` | C122 | € 1,871.68 | — |
| `C118` | C118 | € 1,810.32 | — |
| `D117` | D117 | € 1,794.97 | — |
| `D116` | D116 | € 1,779.62 | — |
| `D115` | D115 | € 1,764.29 | — |
| `D112` | D112 | € 1,718.28 | — |
| `D107` | D107 | € 1,641.56 | — |
| `D104` | D104 | € 1,595.53 | — |
| `D100` | D100 | € 1,534.16 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 10 increments

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Dual-cohort: workers hired by 15-07-2000 have a lower salary table (~1.4% below post-2000) not modeled here. Those workers are a declining cohort (tenure 25+ years); new hires always enter the post-2000 table.

!!! warning ""
    B128 and B132 each contain two ex-classification sub-levels (B128: ex-4/2 and ex-5/2; B132: ex-4/1 and ex-5/1) sharing the same base salary but with different scatto amounts. Modeled as B128/B128_ex52 and B132/B132_ex51. Plain codes carry the ex-4 (higher) scatto as best-guess; _ex52/_ex51 codes carry the ex-5 (lower) scatto. Mapping is unverifiable from public sources (B128: 47.92 vs 44.44; B132: 50.05 vs 47.73).

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-05-21 | [↗](https://www.redigo.info/2026/03/06/ccnl-consorzi-di-bonifica-le-tabelle-retributive-aggiornate/) |
| — | — | 2025-05-21 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=286) |
| — | — | 2025-05-21 | [↗](https://ilccnl.it/contratto/ccnl/consorzi-di-bonifica) |

??? note "Coverage notes"
    Salary model: split (paga base + contingenza) per ilccnl.it, contingenza frozen at EUR 0.00, terzo elemento 0.00 (confirmed via ilccnl.it for D100, D104, D107). base_salary is the full minimo tabellare. Note: ilccnl.it tabelle show the pre-2000 cohort (e.g. D100 Jan2026=1513.09); post-2000 values (D100 Jan2026=1534.16) are sourced from redigo.info and kitech=286.
    
    Cohort: two salary tables — 'in servizio al 15-07-2000' (pre-2000) and 'in servizio dal 15-07-2000' (post-2000). This file models the post-2000 table. kitech.it CodiceCateg=286 title confirms post-2000 identity; redigo.info column 2 matches (D100 Jan2026=1534.16). Pre-2000 table is ~1.4% lower.
    
    Hourly divisor 164.67 h/month from ilccnl.it (single source). Consistent with 38h/week: 52x38/12=164.67. Daily divisor: 26.
    
    Additional months: 14 — tredicesima (dicembre) + quattordicesima (giugno). Source: ilccnl.it ('quattordici mensilitA').
    
    Tranches: 2025-07-01 (+3%) and 2026-01-01 (+2.2%). Both sourced from redigo.info primary table. No pre-July-2025 salary is modeled; engine returns no result for as_of before 2025-07-01.
    
    Seniority: 10 scatti total — tier 1: 6 biennali (cadence 24 months), tier 2: 1 dodicennale (cadence 144 months after tier 1 exhausted), tier 3: 3 quadriennali (cadence 48 months). All tiers modeled. Per-scatto amounts for tiers 2-3 assumed equal to tier 1 amounts (no independent source found for higher-tier amounts; best-guess from standard CCNL practice).
    
    AQ-category levels (AQ162, AQ164, AQ185, AQ187) are quadri. An indennita di funzione may apply per standard quadri CCNL practice, but the amount could not be confirmed from available public sources; not modeled.
    
    layer_2 out_of_scope: no apprenticeship data found in available public sources. Full CCNL PDF required.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/consorzi-di-bonifica-snebi.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/consorzi-di-bonifica-snebi.py"
```
