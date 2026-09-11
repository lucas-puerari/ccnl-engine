# CCNL Dipendenti da Proprietari di Fabbricati (Confedilizia)

| | |
|---|---|
| **CNEL code** | `H401` |
| **Sector** | portieri e custodi di condominio |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-10-30 |
| **Workers (est.)** | ~40k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🟢 Verified |

[← Contracts index](index.md)

??? note "Signatories"
    - Confedilizia
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
| `C3` | C3 — custode qualificato (qualified custodian, senior grade) | € 1,868.50 | — |
| `B1` | B1 — portiere con mansioni di custodia (senior doorman with custody duties) | € 1,580.47 | — |
| `C4` | C4 — custode (custodian, 40 h/week without accommodation) | € 1,573.72 | — |
| `B2` | B2 — portiere (doorman/caretaker, standard profile) | € 1,502.58 | — |
| `B3` | B3 — portiere part-time (part-time doorman/caretaker) | € 1,500.00 | — |
| `D1` | D1 — addetto servizi speciali (special services worker) | € 1,498.07 | — |
| `D2` | D2 — addetto servizi generali (general services worker) | € 1,496.70 | — |
| `D3` | D3 — addetto servizi generali (general services worker) | € 1,496.70 | — |
| `D4` | D4 — addetto servizi generali (general services worker) | € 1,496.70 | — |
| `B4` | B4 — addetto pulizie aree comuni (common areas cleaner) | € 1,396.57 | — |
| `B5` | B5 — pulitore/lavascale (cleaner/stair cleaner) | € 1,315.60 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 12 increments

| Level | Increment (monthly) |
|---|---:|
| `B1` | € 17.30 |
| `B2` | € 15.57 |
| `B3` | € 15.57 |
| `B4` | € 13.84 |
| `B5` | € 10.38 |
| `C3` | € 16.67 |
| `C4` | € 13.33 |
| `D1` | € 10.00 |
| `D2` | € 10.00 |
| `D3` | € 10.00 |
| `D4` | € 10.00 |

## Apprenticeship

**professionalizzante_36** (type: `percentage`)  
Destination levels: `B1`, `B2`, `B4`, `C3`, `C4`, `D1`, `D3`  
percentage: 1.00

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-10-30 | [↗](https://www.confedilizia.it/retribuzioni-dipendenti-da-proprietari-di-fabbricati/) |
| — | — | — | [↗](https://lexplain.it/ccnl-dipendenti-portieri-fabbricati-aumenti-stipendio/) |

??? note "Coverage notes"
    RENEWAL 2025: CCNL signed 2025-10-30. Normative provisions from 2025-11-01; economic provisions (salary tranches) from 2026-01-01. Contract expiry 2028-10-31. Signatories: Confedilizia + FILCAMS-CGIL, FISASCAT-CISL, UILTuCS.
    
    CONGLOBATED MINIMUMS: base_salary values are the monthly conglobated tabular minimums (paga base + contingenza rolled in), as published by Confedilizia at confedilizia.it/retribuzioni-dipendenti-da-proprietari-di-fabbricati. fixed_allowances is empty for all levels. Back-calculation: B1 2026 = 1519.10 / 173 = 8.78 EUR/h; C3 2026 = 1795.94 / 173 = 10.38 EUR/h; D1 2026 = 1439.90 / 173 = 8.32 EUR/h — consistent divisor confirmed.
    
    HOURLY DIVISOR: 173 h/month (40 h/week x 52/12). Applicable to profiles B (B1-B5), C3, C4, D (D1-D4) per Art. 60 (B profiles), Art. 62 comma 1 (C3/C4), Art. 69 commi 1-2 (D profiles) — all 40 h/week standard schedule.
    
    EXCLUDED PROFILES: A1-A9 (portieri con alloggio, 45 h or 48 h/week — divisor would be 195 or 208, incompatible with single CCNLParameters.hourly_divisor; also alloggio in-kind not modelled). C1 and C2 (preposti alla direzione tecnica o amministrativa — Art. 62 comma 2 exempts them from the 40 h ceiling; no fixed hourly divisor applies). C4 primo impiego (entry-rate sub-classification at EUR 1290.52/2026, transitional not permanent level).
    
    SALARY TRANCHES: three annual steps — 2026-01-01, 2027-01-01, 2028-01-01 — as published on Confedilizia official table (3-column layout: 2026, 2027, 2028). D1 is a separate row (1439.90/1468.70/1498.07); D2-D3-D4 share a combined row (1438.58/1467.35/1496.70), confirmed by parsing raw HTML from confedilizia.it.
    
    SENIORITY INCREMENTS: 36-month cadence (triennale), maximum 12 scatti per Art. 111-114. Art. 114 sets 12 scatti triennali for D profiles. D-profile scatto = 10.00 EUR (all D levels identical, per Art. 114; source: lexplain.it/scatti-di-anzianita-contratto-portieri-custodi-e-proprietari-di-fabbricati). B/C amounts from same source.
    
    ADDITIONAL MONTHS: 13 (tredicesima only — Art. 130 'Gratifica natalizia'). Art. 130 provides tredicesima in December equal to one monthly salary; no quattordicesima provision exists in this CCNL. Confirmed via ilccnl.it full CCNL text and targeted search.
    
    APPRENTICESHIP: percentage type per Art. 35-36 of the 2025 renewal. Art. 36 comma 6: 80% months 1-12, 85% months 13-24, 90% months 25-36. Two tracks exist: 36 months (B1, C3) and 24 months (B2, B4, C4, D1, D3). SIMPLIFICATION: all seven destinations use the single 36-month schedule; the five 24-month profiles are over-modelled by 12 months — an apprentice in those profiles is paid 90% during months 25-36 instead of 100%. Impact: slight under-payment for 1 year for 5 destination levels. B3, B5, D2, D4 have no CCNL apprenticeship provision; excluded from destination_levels.
    
    B5 PART-TIME NOTE: Art. 122 provides a 15% hourly premium for B5 (pulitori/lavascale) with weekly schedule below 8 hours. Not modelled (SIMPLIFICATION).
    
    INPS: uses 2026-terziario.json (same tax_sector as commercio-confcommercio and turismo-confcommercio).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/portieri-fabbricati-confedilizia.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/portieri-fabbricati-confedilizia.py"
```
