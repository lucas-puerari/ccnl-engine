# CCNL Noleggio Autobus con Conducente (ANAV)

| | |
|---|---|
| **CNEL code** | `IC36` |
| **Sector** | Trasporti - Noleggio autobus con conducente |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-05-23 |
| **Workers (est.)** | ~5422 |
| **Ruleset version** | `1.0.0` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ANAV
    - FILT-CGIL
    - FIT-CISL
    - UILTRASPORTI

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | ⚠️ partial |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q1` | Livello Q1 (quadro) | € 1,831.31 | 2026-08-01 |
| `Q2` | Livello Q2 (quadro) | € 1,831.31 | 2026-08-01 |
| `A1` | Livello A1 | € 1,831.31 | 2026-08-01 |
| `A2` | Livello A2 | € 1,721.42 | 2026-08-01 |
| `B1` | Livello B1 | € 1,556.61 | 2026-08-01 |
| `B2` | Livello B2 | € 1,483.35 | 2026-08-01 |
| `B3` | Livello B3 | € 1,419.26 | 2026-08-01 |
| `C1` | Livello C1 | € 1,391.79 | 2026-08-01 |
| `C2` | Livello C2 | € 1,226.97 | 2026-08-01 |
| `C3` | Livello C3 | € 1,144.55 | 2026-08-01 |
| `C4` | Livello C4 | € 915.65 | 2026-08-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 9 increments

| Level | Increment (monthly) |
|---|---:|
| `Q1` | € 33.10 |
| `Q2` | € 33.10 |
| `A1` | € 33.10 |
| `A2` | € 32.19 |
| `B1` | € 30.36 |
| `B2` | € 29.57 |
| `B3` | € 29.39 |
| `C1` | € 29.23 |
| `C2` | € 27.17 |
| `C3` | € 26.61 |
| `C4` | € 25.35 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `Q1`, `Q2`, `A1`, `A2`, `B1`, `B2`, `B3`, `C1`, `C2`, `C3`, `C4`  
percentage: 0.95

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: T0 salary table (valid_from 2024-01-01, valid_until 2025-06-30) back-calculated from T1 minus riparametrated increment. Pre-2025-07-01 values are derived, not sourced from an official table. Results for dates before 2025-07-01 should not be relied upon.

!!! warning ""
    SIMPLIFICATION: Seniority amounts (cadence_months=24, max 9 tranches) taken from kitech.it tables for IC36, which show identical values to IC35 (ANIASA). Cross-contract borrowing — verify against official ANAV CCNL text.

!!! warning ""
    SIMPLIFICATION: Una-tantum payment of 600 EUR at C2 (split June 2025 + Jan 2026) covering Jan-May 2025 gap is excluded: one-off, not a recurring salary element.

!!! warning ""
    SIMPLIFICATION: Overtime bands not modeled (no standard rates found in public sources; article-specific complexity).

!!! warning ""
    SIMPLIFICATION: salary tables sourced from kitech.it (dati proxy, verificare con testo ufficiale ANAV). No official CNEL PDF or ANAV archive source was found during research.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-05-23 | [↗](https://www.redigo.info/2025/05/27/ccnl-noleggio-autobus-con-conducente-laccordo-di-rinnovo-2024-2026/) |
| — | — | 2025-05-23 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=548) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = retribuzione tabellare; fixed_allowances per level: CONTINGENZA (frozen) + EDR (10.33, frozen since Protocollo 1992) + EDR_RINNOVO (new EDR from 2025-07-01, per level, 14 mensilita) + INDENNITA_FUNZIONE (Q1=67.00, Q2=51.00 only).
    
    SALARY TABLE: 2024-2026 contract signed 23/05/2025, validity 01/01/2024-31/12/2026. Two salary tranches: T1 from 01/07/2025 (+60 EUR at C2, riparametrate), T2 from 01/08/2026 (+100 EUR at C2, riparametrate). New EDR (EDR_RINNOVO) introduced from 01/07/2025: 40.00 EUR at C2, riparametrate per level, paid for 14 mensilita.
    
    HOURLY DIVISOR: 173, consistent with 40h/week x 52/12 = 173.33 convention; ADDITIONAL MONTHS: 14 (tredicesima + quattordicesima).
    
    TAX SECTOR: terziario (same classification as IC35 autorimesse; bus rental companies fall under ATECO division 49 which uses terziario INPS rates).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/noleggio-autobus-conducente-anav.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/noleggio-autobus-conducente-anav.py"
```
