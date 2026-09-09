# CCNL Istituzioni Socio-Assistenziali — UNEBA

| | |
|---|---|
| **CNEL code** | `T141` |
| **Sector** | servizi socio-assistenziali |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~130k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - UNEBA
    - FP-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL

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
| `Q` | Senior Manager (Quadro) — executive / top-level manager (with function allowance) | € 2,057.15 | — |
| `1` | Level 1 — director / facility manager | € 1,934.70 | — |
| `2` | Level 2 — service manager / coordinator | € 1,824.49 | — |
| `3S` | Level 3 Super — professional educator / qualified technician | € 1,689.78 | — |
| `3` | Level 3 — specialist technical worker / educator | € 1,628.56 | — |
| `4S` | Level 4 Super — social health care worker (OSS) | € 1,542.86 | — |
| `4` | Level 4 — social care worker | € 1,493.89 | — |
| `5S` | Level 5 Super — qualified care worker | € 1,469.42 | — |
| `5` | Level 5 — basic care worker | € 1,432.66 | — |
| `6S` | Level 6 Super — qualified auxiliary worker | € 1,395.94 | — |
| `6` | Level 6 — generic auxiliary worker | € 1,359.20 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 34.09 |
| `1` | € 32.54 |
| `2` | € 30.99 |
| `3S` | € 29.95 |
| `3` | € 28.92 |
| `4S` | € 28.41 |
| `4` | € 27.89 |
| `5S` | € 27.37 |
| `5` | € 26.86 |
| `6S` | € 26.34 |
| `6` | € 25.82 |

## Apprenticeship

**oss_4S** (type: `percentage`)  
Destination levels: `4S`  
percentage: 1.00

**standard_36** (type: `percentage`)  
Destination levels: `3`, `3S`, `2`  
percentage: 1.00

**standard_24** (type: `percentage`)  
Destination levels: `4`, `4S`  
percentage: 1.00

**standard_18** (type: `percentage`)  
Destination levels: `6`, `5`, `5S`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    APPRENTICESHIP generic rule (Art. 22): 90/95/100% in three bands over the destination-level duration: 36 months for 2, 3S, 3 (track 'standard_36'), 24 months for 4S and 4 (track 'standard_24'), 18 months for 5S, 5, 6 (track 'standard_18'). The three bands are assumed of equal length. 6S is not listed in Art. 22 and is not a destination; professionals excluded from apprenticeship (nurses, physiotherapists, psychologists, social workers) and levels 1/Q are not modelled.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-01-24 | [↗](https://www.uneba.org/wp-content/uploads/2025/01/contratto-uneba-2025-testo-firmato.pdf) |
| — | — | 2020-01-20 | [↗](https://olympus.uniurb.it/index.php?Itemid=139&catid=242&id=21943%3A2020uneba&option=com_content&view=article) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (minimi retributivi mensili conglobati per Art. 43 CCNL Jan 2025). All base_salary values are the conglobated tabular minimums; contingenza and EDR are fully absorbed. Back-calculation: Oct 2024 level 4S = 1467.86 / 164 = 8.95 EUR/h; level 2 = 1735.81 / 164 = 10.58 EUR/h; level Q = 1957.15 / 164 = 11.93 EUR/h — consistent across all levels, confirming divisor 164 and conglobated model.
    
    TRANCHE DATES: three tranches — Oct 2024, Jul 2025, Mar 2026. Renewal signed 24 Jan 2025 (CCNL 2023-2025). Level 7 abolished from 01.02.2025 per Art. 80 of the renewal; not modelled.
    
    HOURLY DIVISOR: 164, derived from Art. 50 (38-hour week). Formula: 38 h/week × 52/12 = 164.67, rounded to 164 per contract usage.
    
    ADDITIONAL MONTHS: 14 (tredicesima + quattordicesima). Quattordicesima confirmed by Art. 46 CCNL 2025 (erogata in luglio). Applies to all levels.
    
    SENIORITY: triennial (every 36 months), maximum 10 scatti. Per-level amounts from Art. 48 table (CCNL 2025 signed PDF). Valid from first tranche date Oct 2024.
    
    LEVEL Q — IND_FUN: fixed allowance EUR 100.00/month (Art. 43, 'indennità di funzioni pari a EUR 100,00 mensili lorde'). Paid over 14 mensilità, non-absorbable. Applied to all Q-level workers.
    
    APPRENTICESHIP OSS/4S rule (Art. 22 CCNL 2020, unchanged by the 2025 renewal; primary source olympus.uniurb.it): destination 4S (OSS), 18 months, 85% months 1-9 and 90% months 10-18, track 'oss_4S'. Select it with Apprentice(track='oss_4S'): level 4S is also covered by the generic 24-month track.
    
    TEP ABOLISHED: Art. 80 of the 2025 renewal abolishes the Trattamento Economico Progressivo (progressive 36-month phased salary for new hires). Not modelled as it is no longer in force from 01.02.2025.
    
    ERMT: Elemento Retributivo Mensile Territoriale is a territorial supplement, not part of the national CCNL salary table. Not modelled at national level.
    
    INPS: reuses 2026-terziario.json (TERZIARIO sector). No separate INPS circular rate published for UNEBA; rate is consistent with general terziario sector (same as Commercio and Cooperative Sociali).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/uneba-uneba.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/uneba-uneba.py"
```
