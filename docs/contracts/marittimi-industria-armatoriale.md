# CCNL Marittimi — Industria Armatoriale (CONFITARMA)

| | |
|---|---|
| **CNEL code** | `I391` |
| **Sector** | navigazione marittima — personale di terra |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~15k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🟢 Verified |

[← Contracts index](index.md)

??? note "Signatories"
    - CONFITARMA
    - FILT-CGIL
    - FIT-CISL
    - UILTRASPORTI

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
| `VIIQ` | Livello VII Q — Quadri: VII minimo + INDENNITA_FUNZIONE EUR 225.00 (Art. 18 quinquies) | € 2,800.07 | — |
| `VII` | Livello VII — Lavoratori con responsabilita direttive di alto livello | € 2,800.07 | — |
| `VI` | Livello VI — Lavoratori con elevata autonomia e responsabilita gestionale | € 2,429.76 | — |
| `V` | Livello V — Lavoratori altamente specializzati con coordinamento | € 2,108.93 | — |
| `IV` | Livello IV — Lavoratori con qualifiche tecniche e responsabilita operative | € 1,989.32 | — |
| `III` | Livello III — Lavoratori specializzati con autonomia operativa | € 1,755.00 | — |
| `II` | Livello II — Lavoratori qualificati con mansioni esecutive | € 1,591.25 | — |
| `I` | Livello I — Lavoratori addetti a mansioni di semplice esecuzione | € 1,509.42 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `I` | € 23.74 |
| `II` | € 24.41 |
| `III` | € 25.76 |
| `IV` | € 29.35 |
| `V` | € 30.47 |
| `VI` | € 34.39 |
| `VII` | € 36.07 |
| `VIIQ` | € 36.07 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `III`, `IV`, `V`, `VI`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    PRE-2024 HISTORY: prior CCNL signed 16/12/2020. Values before 01/07/2024 not modelled (primary source covers 2024-2026 renewal only). Engine history starts at 01/07/2024.

!!! warning ""
    SENIORITY MAX: the contract provides 10 max increments for workers hired before 31/12/1988; modelled as max=5 (post-1988 hires, the prevailing case for active workforce).

!!! warning ""
    SUPERMINIMO LIVELLO: Art. 18 provides an additional EUR 7/month for L4 workers after 8 years in level, and EUR 7-11/month for L2-L3 workers under specific conditions. These are individual-level amounts tied to personal history — not modelled in base salary.

!!! warning ""
    EAR FOR VIIQ: the Allegato 1bis EAR table lists VII (not VIIQ separately). VIIQ receives the same EAR as VII (INDENNITA_FUNZIONE is the distinguishing element).

!!! warning ""
    UNA TANTUM: backpay EUR 200 paid Jul 2024 + EUR 180 paid Jan 2025, uniform all levels. Lump-sum, not recurring — not modelled.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-07-11 | [↗](https://www.filtcgil.it/images/Contratti/Mare/15_-_SEZIONE_PERSONALE_DI_TERRA.pdf) |

??? note "Coverage notes"
    CCNL 2024-2026 (CONFITARMA/FILT-CGIL/FIT-CISL/UILTRASPORTI), signed 11/07/2024, valid 01/07/2024-31/12/2026. Personale di terra (shore-based staff), Sezione 15 — Allegati 1 and 1bis.
    
    SPLIT model: minimo contrattuale (base_salary) + EAR Elemento Aggiuntivo della Retribuzione (per-level, omnicomprensivo) modelled as fixed_allowance. 3 tranches: 01/07/2024 (40%), 01/07/2025 (30%), 01/07/2026 (30%).
    
    VIIQ (Quadri): VII minimo + INDENNITA_FUNZIONE EUR 225.00/month fixed (since June 2007, not indexed). Included in TFR, 13th and 14th month, festivity. NOT included in overtime base.
    
    HOURLY DIVISOR: 173 (Art. 10 para 8). Daily divisor: 26. Verified on 3 levels: L1=1509.42/173=8.72, LIV=1989.32/173=11.50, LVII=2800.07/173=16.18.
    
    ADDITIONAL MONTHS: 14 — tredicesima (Christmas) and quattordicesima (Easter/summer). Art. 17: base = minimo + superminimo + scatti + contributo mensa + indennita funzione.
    
    SENIORITY: 24-month cadence (biennale), max 5 for workers hired from 1989 onwards. Per-level EUR from Allegato 1: I=23.74, II=24.41, III=25.76, IV=29.35, V=30.47, VI=34.39, VII=36.07.
    
    APPRENTICESHIP: professionalizzante, eligible levels III-VI only. Months 1-12: 70% of minimo; months 13-36: 80% of minimo. Minimum 6 months, maximum 36 months.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/marittimi-industria-armatoriale.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/marittimi-industria-armatoriale.py"
```
