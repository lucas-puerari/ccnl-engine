# CCNL per i lavoratori dell'industria tessile, abbigliamento, moda (SMI)

| | |
|---|---|
| **CNEL code** | `D014` |
| **Sector** | industria |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~160k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - SMI
    - FILCTEM-CGIL
    - FEMCA-CISL
    - UILTEC-UIL

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
| `8` | Grade 8 — department head/supervisor with managerial functions | € 2,518.68 | — |
| `7` | Grade 7 — managers with managerial responsibility | € 2,376.10 | — |
| `6` | Grade 6 — managers and technicians with area responsibility | € 2,229.13 | — |
| `5` | Grade 5 — junior managers and specialist technicians | € 2,088.36 | — |
| `4` | Grade 4 — highly specialist workers and skilled clerical employees | € 1,986.95 | — |
| `3S` | Grade 3 super — specialist workers with autonomy and executive clerical employees | € 1,941.98 | — |
| `3` | Grade 3 — specialist workers and routine clerical employees | € 1,899.25 | — |
| `2S` | Grade 2 super — qualified workers with executive autonomy | € 1,843.81 | — |
| `2` | Grade 2 — basic qualified workers | € 1,803.70 | — |
| `1` | Grade 1 — elementary operations requiring no prior experience | € 1,560.00 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 4 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 6.71 |
| `2` | € 7.23 |
| `2S` | € 7.23 |
| `3` | € 7.75 |
| `3S` | € 7.75 |
| `4` | € 8.26 |
| `5` | € 9.81 |
| `6` | € 10.33 |
| `7` | € 11.88 |
| `8` | € 12.91 |

## Apprenticeship

**prof_L6_L8** (type: `under_classification`)  
Destination levels: `6`, `7`, `8`

**prof_L5** (type: `under_classification`)  
Destination levels: `5`

**prof_L4** (type: `under_classification`)  
Destination levels: `4`

**prof_L3S** (type: `under_classification`)  
Destination levels: `3S`

**prof_L3** (type: `under_classification`)  
Destination levels: `3`

**prof_L2S** (type: `under_classification`)  
Destination levels: `2S`

**prof_L2** (type: `under_classification`)  
Destination levels: `2`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Seniority increments: amounts from lexplain.it (article on CCNL tessile seniority increments). It was not possible to verify whether the amounts were updated with the 2024 renewal or whether they date from the previous contract. SIMPLIFICATION: the available amounts are used as an estimate for both periods.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-11-11 | [↗](https://www.sistemamodaitalia.com/) |
| — | — | — | [↗](https://www.lexplain.it/tabelle-retributive-ccnl-tessile-abbigliamento-smi/) |
| — | — | — | [↗](https://www.kitech.it/tabelle-retributive-tessile-abbigliamento) |

??? note "Coverage notes"
    December 2024 tranche (01/12/2024): per-level values derived proportionally from the +EUR 95 increase at grade 4 (2024 SMI renewal, source filctemcgil.it). Rationale: Dec-2024 increment = 95/152 = 5/8 of the total increase Nov-2024→Jan-2026; verified by exact closure on all levels against Jan-2026 values from kitech.it.
    
    Level 8 function allowance: the total ERN published on lexplain.it (2,316.33) includes the function allowance (EUR 51.65). base_salary = ERN - 51.65 = 2,264.68 (pre-Dec 2024) and 2,457.72 (Jan 2026). Source kitech.it reports minimum and total separately for Level 8. Verification: combined increase (Dec2024+Jan2026) at Level 8 = EUR 193.04, expected proportional = 126.74% × 152.24 = EUR 193.12 (delta < 0.1 EUR). Interpretation confirmed.
    
    VV.PP. (Travelling and Area Salespeople): not modelled. Special category with their own rates (1st cat.: 1,932.91/1,932.91 pre-Dec 2024; 2nd cat.: 1,823.07); excluded due to complexity.
    
    Source for pre-Dec 2024 tables: lexplain.it, retrieved September 2026. Source for Jan 2026 tables: kitech.it, retrieved September 2026. Source for TEM and effective dates: SMI press release (sistemamodaitalia.com), November 2024.
    
    APPRENTICESHIP: sotto-inquadramento. Group A (L4-L8) 36m total: 0-15m = 2 full levels below dest, 15-30m = 1 full level below, 30-36m+ = dest. Note: 'full level' skips S-variants, so levels_below in order arithmetic: L6-L8 → 2/1, L5 → 3/1, L4 → 4/2. Group B (L3/3S) 36m: 0-12m at L1, 12-30m at L2, 30m+ at dest. Group B (L2/2S) 36m: 0-12m at L1, then dest. L1 excluded as destination. Source: CCNL SMI (CNEL D014) + Gruppo24ORE scheda Oct 2023 + MySolution sintesi 2017. SIMPLIFICATION: MySolution notes 3S second period uses L2 pay (not L3).
    
    JANUARY 2027 TRANCHE: +60.96 at L8 basis, proportional to parametri. Values from rinnovo 11/11/2024 (Chapter VI column 'da gennaio 2027'). Source: studiobergonzini.it ipotesi 11/11/2024 PDF.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/tessile-smi.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/tessile-smi.py"
```
