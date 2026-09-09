# CCNL per i lavoratori addetti alle industrie delle pelli e dei succedanei della pelle (Assopellettieri)

| | |
|---|---|
| **CNEL code** | `D111` |
| **Sector** | industria |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~17k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Assopellettieri
    - Confindustria Moda
    - Filctem-Cgil
    - Femca-Cisl
    - Uiltec-Uil

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
| `6` | Level 6 — top-level quadri and sector executives | € 2,412.21 | — |
| `5` | Level 5 — white-collar employees with managerial functions and specialist technicians | € 2,185.24 | — |
| `4S` | Level 4 Super — technicians and white-collar employees with advanced duties | € 2,047.33 | — |
| `4` | Level 4 — highly specialised workers | € 2,000.26 | — |
| `3` | Level 3 — specialist workers | € 1,911.70 | — |
| `2` | Level 2 — skilled workers | € 1,814.00 | — |
| `1` | Level 1 — general workers (classification removed from 31/12/2023; table pay retained as apprenticeship reference Art. 55) | € 1,379.86 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 4 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 6.71 |
| `2` | € 7.41 |
| `3` | € 7.95 |
| `4` | € 8.39 |
| `4S` | € 8.91 |
| `5` | € 9.68 |
| `6` | € 11.88 |

## Apprenticeship

**dest_6** (type: `under_classification`)  
Destination levels: `6`

**dest_5** (type: `under_classification`)  
Destination levels: `5`

**dest_4S** (type: `under_classification`)  
Destination levels: `4S`

**dest_4** (type: `under_classification`)  
Destination levels: `4`

**dest_3** (type: `under_classification`)  
Destination levels: `3`

**dest_2** (type: `under_classification`)  
Destination levels: `2`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    LEVEL 1: from the agreement of 22/12/2023, level 1 is no longer a classification level for permanent workers (automatic reclassification to level 2 by 31/12/2023). The pay value for level 1 remains defined in the contract for the entire duration up to 2025 (table Art. 32, CNEL PDF, confirmed primary source). It is assumed that Art. 55 (apprenticeship) was not modified by the 22/12/2023 agreement: that agreement was not accessible from the public sources consulted (CNEL archive, union websites), so the continuity of level 1 as a pay reference for apprentices destined for level 2 and level 3 is assumed but not verified against the supplementary agreement text.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-05-26 | [↗](https://cdcpcnelblg01sa.blob.core.windows.net/archivio/2023//20098.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobato (table pay inclusive of base pay, former contingenza, E.d.r.). Art. 32 CCNL (CNEL PDF): 'Sono conglobati in un unica voce denominata Retribuzione tabellare i seguenti istituti: paga base, ex indennita di contingenza, E.d.r.' PELLETTERIA table with 7 levels and 4 tranches (Apr 2023, Dec 2023, Dec 2024, Dec 2025) from primary source CNEL PDF Art. 32.
    
    HOURLY DIVISOR 173: Art. 35 CCNL (CNEL PDF): 'La retribuzione e oraria e si ottiene dividendo la retribuzione mensile per 173'.
    
    ADDITIONAL MONTHS 13: tredicesima (thirteenth month). Source: ANCL summary CCNL D111.
    
    SENIORITY INCREMENTS: Art. 54 CCNL (CNEL PDF). 'quattro aumenti biennali periodici di anzianita' — 24-month cadence, maximum 4. Per-level amounts from Art. 54 CNEL PDF table.
    
    APPRENTICESHIP: Art. 55 CCNL (CNEL PDF). Under-classification model, maximum duration 36 months. Six distinct tracks (one per destination level) with specific pay progression for each level, as per Art. 55 table. Special note for level 2: 'Gli apprendisti con destinazione finale al secondo saranno inquadrati al livello di destinazione finale con decorrenza dall'inizio del secondo periodo di apprendistato' (from month 11 onwards at level 2).
    
    INPS: industry sector rates from 2026-industria.json (existing file reused). Employee 9.19%; employer: <=15 employees 30.13%, 16-50 employees 30.20%, >50 employees 30.50%.
    
    LEVEL 6Q: not present in the CCNL table of the CNEL PDF (August 2023). Excluded from the model.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/pelli-cuoio-industria-assopellettieri.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/pelli-cuoio-industria-assopellettieri.py"
```
