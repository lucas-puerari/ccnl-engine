# CCNL Turismo, Pubblici Esercizi e Ristorazione (Confcommercio)

| | |
|---|---|
| **CNEL code** | `H052` |
| **Sector** | turismo |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~300k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Federalberghi
    - FIPE-Confcommercio
    - Federviaggio
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
| `QA` | Grade QA — senior manager with maximum managerial responsibility | € 2,495.22 | — |
| `QB` | Grade QB — senior manager with high managerial professionalism | € 2,310.11 | — |
| `1` | Grade 1 — management function / maître / head receptionist | € 2,152.32 | — |
| `2` | Grade 2 — junior management function / chef de rang / deputy manager | € 1,967.20 | — |
| `3` | Grade 3 — senior technician / section chef / senior front-office | € 1,855.32 | — |
| `4` | Grade 4 — process technician / shift leader / receptionist | € 1,750.69 | — |
| `5` | Grade 5 — specialist operator (waiter, cook, receptionist) | € 1,641.85 | — |
| `6S` | Grade 6 super — qualified operator (room attendant, basic bar staff) | € 1,578.72 | — |
| `6` | Grade 6 — basic operator (dishwasher, porter, commis) | € 1,556.35 | — |
| `7` | Grade 7 — assigned to general tasks, cleaning and support operations | € 1,458.42 | — |

## Seniority increments

**Cadence:** every 48 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `QA` | € 40.80 |
| `QB` | € 39.25 |
| `1` | € 37.70 |
| `2` | € 36.15 |
| `3` | € 34.86 |
| `4` | € 33.05 |
| `5` | € 32.54 |
| `6S` | € 31.25 |
| `6` | € 30.99 |
| `7` | € 30.47 |

## Apprenticeship

**professionalizzante_36** (type: `percentage`)  
Destination levels: `5`, `4`, `3`, `2`, `6S`  
percentage: 1.00

**professionalizzante_24** (type: `percentage`)  
Destination levels: `6`  
percentage: 1.00

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-06-05 | [↗](https://www.lexplain.it/tabelle-retributive-ccnl-alberghi-turismo-confcommercio-aumenti-stipendio-2024-2027/) |
| — | — | — | [↗](https://www.lexplain.it/scatti-di-anzianita-ccnl-turismo-ristorazione-e-pubblici-esercizi/) |

??? note "Coverage notes"
    SUB-SECTOR: salary tables from the hotels/tourism renewal signed on 5 June 2024 (CCNL H052 hotels special section). CCNL H052 also covers the public establishments/FIPE sub-sector (renewal March 2025, slightly different tables) not modelled in this file.
    
    CONGLOBATED MINIMUMS: the base_salary values are the monthly conglobated tabular minimums (basic pay + contingency included), as published by lexplain.it/tabelle-retributive-ccnl-alberghi-turismo-confcommercio-aumenti-stipendio-2024-2027. fixed_allowances is empty for all levels. Verification: level 7 November 2027 = 1458.42 / 172 = 8.48 EUR/h (matches published hourly table).
    
    QA/QB FUNCTION ALLOWANCE: some sources (public establishments) show a separate function allowance (QA=EUR 75, QB=EUR 70). For the hotels sub-sector, the values in the conglobated table appear to already include this component. If checks against actual payslips show a discrepancy, add fixed_allowances QA=EUR 75 and QB=EUR 70.
    
    TRANCHES: July 2024, June 2025, May 2026, April 2027, November 2027. No prior tranches modelled (lower bound: 2024-07-01).
    
    SENIORITY INCREMENTS: 6 four-yearly increments (every 48 months). Amounts from lexplain.it/scatti-di-anzianita-ccnl-turismo-ristorazione-e-pubblici-esercizi. The increments are paid over 14 monthly instalments (including the 13th and 14th) — the gross_annual component is already captured by the additional_months=14 multiplier in the engine.
    
    APPRENTICESHIP percentage (2024 renewal): 80% months 1-12, 85% months 13-24, 90% months 25-36 (source: albergoatenericcione.it, confirmed by research on the 2024 renewal). Duration 36 months for grades 2-5 and 6S (track 'professionalizzante_36'), 24 months for grade 6 (track 'professionalizzante_24'); beyond the contractual duration the worker is fully qualified at 100%. Grade 7, grade 1, and Quadri are not destinations. The under-classification (2 levels below / 1 level below) applied to the previous CCNL.
    
    MONTHLY PAYMENTS: 14 (thirteenth in June, fourteenth in December). Confirmed by CCNL and by the note 'amounts paid over 14 monthly instalments' for seniority increments.
    
    HOURLY DIVISOR: 172 hours/month (40 h/week × 52/12). Verified by back-calculation: 1458.42 / 172 = 8.478 ≈ 8.48 EUR/h (level 7, November 2027 — matches lexplain hourly table).
    
    INPS: uses 2026-terziario.json (same tax_sector as commercio-confcommercio).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/turismo-confcommercio.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/turismo-confcommercio.py"
```
