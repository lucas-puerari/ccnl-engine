# CCNL CED, ICT, Professioni Digitali e STP (Assoced-UGL)

| | |
|---|---|
| **CNEL code** | `H601` |
| **Sector** | Terziario |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-07-28 |
| **Workers (est.)** | ~22k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Assoced
    - LAIT
    - Confterziario
    - UGL Terziario

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ⚠️ partial |
| **L3 — Work rules** | ✅ implemented |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QDIR` | Quadri di Direzione | € 3,186.49 | — |
| `Q` | Quadri | € 2,895.91 | — |
| `1` | 1° livello | € 2,486.32 | — |
| `2` | 2° livello | € 2,225.94 | — |
| `3S` | 3° livello Super | € 2,134.17 | — |
| `3` | 3° livello | € 1,997.93 | — |
| `4` | 4° livello | € 1,859.01 | — |
| `5` | 5° livello | € 1,769.98 | — |
| `6` | 6° livello | € 1,494.74 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**professionalizzante_36** (type: `under_classification`)  
Destination levels: `2`, `3S`, `3`, `4`

**professionalizzante_24** (type: `under_classification`)  
Destination levels: `5`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    INPS terziario rates reused from 2026-terziario.json (same sector as H016). Verify against annual INPS circular for exact H601 sub-sector rate.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2022-03-09 | [↗](https://www.fondoeasi.it/fondo-easi/ccnl-ced-ced-ict-professioni-digitali-e-stp/stesura-ccnl-ced-09-marzo-2022.pdf) |
| — | — | 2025-07-28 | [↗](https://www.redigo.info/ccnl-ced-ict-professioni-digitali-stp) |
| — | — | 2025-07-28 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=62) |

??? note "Coverage notes"
    Salary model: paga base nazionale conglobata (Art. 172, 2022 stesura). Single TimeSeries per level, no separate contingenza or EDR.
    
    Unified classification covers CED, ICT, Professioni Digitali and STP workers (Art. 172 + Tabella A, one scale). No separate STP salary table exists in the 2022 stesura or 2025 renewal.
    
    Divisore convenzionale 173 h/month (Art. 171) and 26 d/month (Art. 170). Source: 2022 stesura fondoeasi.it.
    
    Mensilita supplementari: tredicesima (Art. 175) and quattordicesima (Art. 176). additional_months = 14.
    
    Indennita di funzione (Tabella A note, 2025 renewal): QDIR 287/296/306 EUR, Q 250/258/266 EUR per 14 mensilita. Tranche dates: 01/09/2025, 01/09/2026, 01/09/2027, distinct from base salary tranches.
    
    Scatti di anzianita (Art. 166, 2022 stesura): abrogated from 01/01/2019. Grandfathered for personale in forza al 31-12-2018 only. New hires (post-2018): maximum_count=0. Per-level 2009 amounts: QDIR=52, Q=47, L1=44, L2=40, L3S=36, L3=33, L4=30, L5=27, L6=24 (frozen, not updated since 2009 across 2022 and 2025 renewals).
    
    Apprenticeship (Art. 23-24, 2022 stesura, ccnlced.it allegato): under_classification. First half 2 levels below, second half 1 level below. Level 5 exception: stays at Level 6 throughout 24-month track. Destination L2 duration 36 months (studiocerbone.com: 240 h/36 months for 2° livello). Source ccnlced.it showed '6 months' for L2 — treated as parsing artifact; 36 months adopted from studiocerbone.com.
    
    Salary tranches: 01/09/2025 (source-confirmed, redigo.info and kitech.it), 01/06/2026 (source-confirmed, both sources agree), 01/03/2027 (redigo.info only, single-source), 01/01/2028 (redigo.info only, single-source).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/ced-assoced.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/ced-assoced.py"
```
