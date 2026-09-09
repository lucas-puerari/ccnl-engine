# CCNL Area Legno-Lapidei — Artigianato

| | |
|---|---|
| **CNEL code** | `F060` |
| **Sector** | legno arredamento lapidei artigianato |
| **Tax sector** | `artigianato` |
| **Last renewal** | 2024-03-05 |
| **Workers (est.)** | ~95k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - CNA Produzione
    - CNA Costruzioni
    - Confartigianato Legno e Arredo
    - Confartigianato Marmisti
    - Casartigiani
    - CLAAI
    - Feneal-UIL
    - Filca-CISL
    - Fillea-CGIL

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
| `AS` | Level AS — quadro / senior technical manager (top level) | € 2,278.43 | — |
| `A` | Level A — managerial employee / highly specialised technician | € 2,123.69 | — |
| `B` | Level B — white-collar employees / expert skilled workers | € 1,941.22 | — |
| `CS` | Level CS — expert skilled worker / senior white-collar employee | € 1,856.85 | — |
| `C` | Level C — skilled worker / white-collar employee | € 1,771.64 | — |
| `D` | Level D — qualified worker / employee | € 1,674.71 | — |
| `E` | Level E — general worker / clerical staff | € 1,585.97 | — |
| `F` | Level F — entry grade (transitional, max 12 months) | € 1,490.13 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `AS` | € 20.49 |
| `A` | € 18.94 |
| `B` | € 16.88 |
| `CS` | € 16.18 |
| `C` | € 15.33 |
| `D` | € 14.30 |
| `E` | € 13.52 |
| `F` | € 0.00 |

## Apprenticeship

**gruppo_1_legno** (type: `percentage`)  
Destination levels: `AS`, `A`, `B`  
percentage: 1.00

**gruppo_2_legno** (type: `percentage`)  
Destination levels: `CS`, `C`, `D`  
percentage: 1.00

**gruppo_3_legno** (type: `percentage`)  
Destination levels: `E`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Only Legno/Arredamento/Mobili sub-sector salary tables modelled. Lapidei (stone/marble) sub-sector uses different salary tables and is not modelled. CNEL code F060 covers both sub-sectors. Workers in Lapidei should verify against the specific Lapidei tables.

!!! warning ""
    Apprenticeship tables use operai duration tracks (5 years for gruppi 1-2, 2.5 years for gruppo 3). Impiegati and impiegati amministrativi have shorter 3-year apprenticeship durations with the same percentages — not separately modelled. For impiegato apprenticeships the operai duration overstates the period.

!!! warning ""
    LEVEL CATEGORY: all levels left null. Primary source text shows multiple levels map to both operai and impiegati (e.g. level B = 'Impiegati di concetto - Operai specializzati provetti') — this is a genuine one-to-many mapping that the schema cannot represent as a single category value, not a data gap. 2026-artigianato.json applies rate 0.2693 (default/operaio) for null category; impiegato rate 0.2471 not applied to impiegato-eligible levels.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2022-09-01 | [↗](https://www.direzionelavoro.it/files/ccnl_legno_lapidei_artigianato_2022.pdf) |
| — | — | 2024-03-05 | [↗](https://www.studiodalmaschio.it/rinnovo-ccnl-legno-lapidei-artigianato-2024) |
| — | — | 2024-03-05 | [↗](https://www.kitech.it/ccnl/legno-arredo-artigianato) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (minimi tabellari conglobati). Confirmed by primary source ('Contingenza: conglobata nei minimi retributivi'). Back-calculation at Jan 2025: AS=2176.39/174=12.508 EUR/h, D=1599.71/174=9.194 EUR/h, F=1423.40/174=8.180 EUR/h — all consistent with hourly divisor 174, confirming conglobated model.
    
    CNEL CODE: F060 confirmed from kitech.it page text ('Area Legno Lapidei (CNEL: F060)') and from direzionelavoro.it PDF URL slug.
    
    TRANCHE DATES: four tranches — 2024-03-01 (retroactive from renewal 5 Mar 2024), 2025-01-01, 2026-01-01, 2026-10-01. Source: studiodalmaschio.it rinnovo summary, cross-validated Jan 2026 values against kitech.it.
    
    HOURLY DIVISOR: 174. Source: primary CCNL text ('Coefficiente orario = 174'). Derived: 40h/week x 52/12 = 173.33, rounded to 174 per contract clause.
    
    ADDITIONAL MONTHS: 13 (tredicesima only). No quattordicesima in this CCNL. Source: direzionelavoro.it base CCNL PDF (mensilita aggiuntive clause).
    
    SENIORITY: biennale (every 24 months), maximum 5 scatti. Per-level amounts pre-Jan-2025 from 2022 base CCNL: AS=15.494, A=13.944, B=11.879, CS=11.181, C=10.329, D=9.296, E=8.522, F=none. From Jan 2025 (2024 rinnovo): AS=20.49, A=18.94, B=16.88, CS=16.18, C=15.33, D=14.30, E=13.52, F=none. Level F: transitional level (max 12 months), no seniority applies.
    
    APPRENTICE SENIORITY: EUR 8.00 from Jan 2025. New clause introduced by 2024 rinnovo. Source: studiodalmaschio.it rinnovo summary.
    
    LEVEL F: transitional insertion level, maximum duration 12 months. No seniority and no apprenticeship track apply. Workers in F are re-levelled to E or higher after the transitional period.
    
    APPRENTICESHIP: 3 gruppi from base CCNL 2022 (unchanged in 2024 rinnovo). Gruppo 1 (dest AS, A, B — operai 5 years = 60m), Gruppo 2 (dest CS, C, D — operai 5 years = 60m), Gruppo 3 (dest E — operai 2.5 years = 30m). Level F has no apprenticeship track.
    
    INPS: reuses 2026-artigianato.json (ARTIGIANATO sector).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/legno-lapidei-artigianato-confartigianato.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/legno-lapidei-artigianato-confartigianato.py"
```
