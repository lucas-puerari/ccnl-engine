# CCNL per i dipendenti da aziende dei settori Pubblici Esercizi, Ristorazione Collettiva e Commerciale e Turismo

| | |
|---|---|
| **CNEL code** | `H05Y` |
| **Sector** | turismo |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~350k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - FIPE-Confcommercio
    - Legacoop Produzione e Servizi
    - Confcooperative Lavoro e Servizi
    - AGCI-Servizi
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
| `Qa` | Quadri A — managerial functions with a high level of management responsibility | € 2,578.07 | — |
| `Qb` | Quadri B — managerial functions with continuous responsibility over a complex unit | € 2,375.56 | — |
| `1` | Level 1 — staff with high professional content and operational autonomy | € 2,201.85 | — |
| `2` | Level 2 — staff with initiative and operational autonomy (coordination) | € 1,999.36 | — |
| `3` | Level 3 — staff with specialist technical knowledge (conceptual work) | € 1,877.00 | — |
| `4` | Level 4 — staff with executive autonomy (specialised technical-administrative duties) | € 1,762.69 | — |
| `5` | Level 5 — staff with qualified technical-practical knowledge and skills | € 1,643.50 | — |
| `6s` | Level 6 super — staff with adequate technical-practical skills (formerly qualified commis or experienced staff) | € 1,574.42 | — |
| `6` | Level 6 — staff with standard practical training and basic professional knowledge | € 1,549.78 | — |
| `7` | Level 7 — general assistants, cleaning staff (simple manual tasks) | € 1,442.45 | — |

## Seniority increments

**Cadence:** every 48 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `Qa` | € 40.80 |
| `Qb` | € 39.25 |
| `1` | € 37.70 |
| `2` | € 36.15 |
| `3` | € 34.86 |
| `4` | € 33.05 |
| `5` | € 32.54 |
| `6s` | € 31.25 |
| `6` | € 30.99 |
| `7` | € 30.47 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `1`, `2`, `3`, `4`, `5`, `6s`, `6`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SALARY MODEL: the contractual pay structure provides for a separate national base pay and contingenza. For engine purposes they are consolidated into base_salary (monthly total per tranche). The total values match the official FIPE pay tables (Tabelle retributive 2024, fipe.it). fixed_allowances models the function allowance for quadri: Qa=75 EUR and Qb=70 EUR, confirmed by lexplain.it (CCNL 2024-2027).

!!! warning ""
    CONTRACT CATERING: collective catering companies apply the 2nd and 3rd tranche one month later (Sep-25 instead of Jun-25, Sep-26 instead of Jun-26). Only the main sub-sector (public establishments / commercial catering / tourism) is modelled with Jun-25 and Jun-26 dates. Impact: negligible on an annual basis for collective catering companies.

!!! warning ""
    SMALLER COMPANIES: Art. 162 provides for a reduction in base pay for smaller companies (from €2.58 to €5.68 per level). Not modelled — applicable only to micro-enterprises under paragraph II Art. 1. Maximum impact: €5.68/month for Qa.

!!! warning ""
    APPRENTICESHIP (Art. 68): professionalizzante apprenticeship 36 months, percentages 80%/85%/90% confirmed by lexplain.it (CCNL 2024-2027 tables). Destination levels modelled as 1-6s and 6 (Qa/Qb excluded per D.Lgs. 81/2015 art. 41; level 7 excluded per tertiary CCNL convention, not verified against Art. 68 — fipe.it full text PDF not parseable: scanned without OCR). Art. 75 (apprenticeship for qualification/diploma) out of scope.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-06-05 | [↗](https://www.fipe.it/wp-content/uploads/2025/02/Tabelle-retributive-2024.pdf) |
| — | — | 2024-06-05 | [↗](https://www.lexplain.it/tabelle-retributive-ccnl-pubblici-esercizi-ristorazione-e-turismo-2024-2027/) |

??? note "Coverage notes"
    2024 RENEWAL: CCNL signed 5 June 2024, validity 1 June 2024 – 31 December 2027 (CNEL H05Y, ~592,364 workers Uniemens 2022 / over 1 million according to FIPE). Pay table source: fipe.it/wp-content/uploads/2025/02/Tabelle-retributive-2024.pdf.
    
    SENIORITY INCREMENTS: 6 quadrennial increments (48 months). Per-level amounts from FIPE pay tables (fipe.it/wp-content/uploads/2025/02/Tabelle-retributive-2024.pdf). Paid over 14 monthly instalments.
    
    MONTHLY PAYMENTS: 14 (tredicesima + quattordicesima). Source: lexplain.it (CCNL Pubblici Esercizi 2024-2027).
    
    HOURLY DIVISOR: 172 (confirmed by lexplain.it: 172 for 40 weekly hours). Verification: Qa Jun-24 = 2331.41 / 172 = 13.55 euro/hour.
    
    INPS: uses 2026-terziario.json (tax_sector terziario, same as commercio-confcommercio and turismo-confcommercio).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/pubblici-esercizi-fipe-angem.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/pubblici-esercizi-fipe-angem.py"
```
