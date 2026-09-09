# CCNL Area Comunicazione — Artigianato

| | |
|---|---|
| **CNEL code** | `G016` |
| **Sector** | comunicazione grafica editoria stampa artigianato |
| **Tax sector** | `artigianato` |
| **Last renewal** | 2024-11-18 |
| **Workers (est.)** | ~60k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - CNA Comunicazione e Terziario Avanzato
    - Confartigianato Comunicazione
    - Casartigiani
    - CLAAI
    - SLC-CGIL
    - FISTEL-CISL
    - UILCOM-UIL

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
| `1A` | Level 1A — senior manager / department head (+ function allowance EUR 51.65) | € 2,546.29 | — |
| `1B` | Level 1B — intermediate manager / executive employee | € 2,264.27 | — |
| `2` | Level 2 — technician / senior white-collar employee | € 2,124.16 | — |
| `3` | Level 3 — highly specialised worker / white-collar employee | € 1,992.23 | — |
| `4` | Level 4 — higher-grade specialised worker | € 1,848.56 | — |
| `5bis` | Level 5 BIS — specialised worker (intermediate between 5 and 4) | € 1,690.94 | — |
| `5` | Level 5 — qualified worker | € 1,616.72 | — |
| `6` | Level 6 — common worker, assigned to routine duties | € 1,522.42 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1A` | € 16.01 |
| `1B` | € 16.01 |
| `2` | € 14.20 |
| `3` | € 13.43 |
| `4` | € 12.65 |
| `5bis` | € 11.88 |
| `5` | € 11.36 |
| `6` | € 10.33 |

## Apprenticeship

**operai_tecnici** (type: `percentage`)  
Destination levels: `1A`, `1B`, `2`, `3`, `4`, `5bis`, `5`, `6`  
percentage: 1.00

**amministrativi** (type: `percentage`)  
Destination levels: `1A`, `1B`, `2`, `3`, `4`, `5bis`, `5`, `6`  
percentage: 0.90

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Only aziende artigiane salary tables modelled. PMI non-artigiane tables (Art. 4, with EUR 207 total increase vs EUR 200 for artigiane, difference of EUR 7 in the Nov 2026 tranche) are not modelled. Applies to a small minority of firms covered by this CCNL.

!!! warning ""
    Only post-Nov-18-2024 apprenticeship rules modelled. Pre-renewal CCNL used a semestrali hybrid model (old percentage tables). Firms with apprenticeship contracts signed before Nov 18, 2024 may still follow the previgente rules.

!!! warning ""
    Centraliniste (switchboard operators) have a 2-year apprenticeship track per the 2024 rinnovo. Modelled as the general 3-year amministrativi track (overstates duration by 1 year for that role).

!!! warning ""
    Both apprenticeship tracks (operai_tecnici and amministrativi) are assigned to all 8 destination levels. In practice, the CCNL differentiates by job role, not only by destination level. Firms must select the correct track by role type.

!!! warning ""
    LEVEL CATEGORY: all levels left null. Multiple levels map to both operai and impiegati roles — a genuine one-to-many mapping the schema cannot represent as a single category value.

!!! warning ""
    Level 1A indennita di funzione EUR 51.65 assumed constant across all four tranches (Dec 2024 through Nov 2026+). Kitech.it only shows the Mar 2026 value; no primary source confirms the amount in Dec 2024 or Jul 2025. Difference is likely zero (function allowances are rarely changed in salary renewals) but not verified.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-11-18 | [↗](https://www.redigo.info/ccnl/comunicazione-artigianato) |
| — | — | 2024-11-18 | [↗](https://www.kitech.it/ccnl/comunicazione-artigianato) |
| — | — | 2024-11-18 | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=155) |
| — | — | 2024-11-18 | [↗](https://farecontrattazione.adapt.it/per-una-storia-della-contrattazione-collettiva-in-italia-247-il-nuovo-ccnl-artigianato-area-comunicazione-un-rinnovo-contrattuale-al-passo-con-i-tempi/) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (minimi tabellari conglobati). Confirmed: ilccnl.it shows contingenza=0.00 for all levels. Back-calculation at Jul 2025: livello 4=1763.56/173=10.194 EUR/h, livello 1B=2160.15/173=12.487 EUR/h, livello 6=1452.42/173=8.394 EUR/h — all values divide to proportional hourly rates consistent with divisor 173, confirming conglobated model.
    
    CNEL CODE: G016 confirmed from kitech.it and ADAPT farecontrattazione.it.
    
    TRANCHE DATES: four tranches — 2024-12-01 (from Nov 2024 verbale integrativo), 2025-07-01, 2026-03-01, 2026-11-01. Source: redigo.info. Cross-validated Mar 2026 values against kitech.it.
    
    HOURLY DIVISOR: 173. Source: ilccnl.it explicit '173.00 ore'. Cross-validated via back-calculation across 3 levels (see conglobated check above).
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: ilccnl.it ('una mensilita globale di fatto'). No quattordicesima.
    
    SENIORITY: biennale (every 24 months), maximum 5 scatti. Per-level EUR amounts from two independent aggregators (kitech.it, lavoro-economia.it): 1A=16.01, 1B=16.01, 2=14.20, 3=13.43, 4=12.65, 5bis=11.88, 5=11.36, 6=10.33. Cadence confirmed '5 aumenti biennali' from lavoro-economia.it. SIMPLIFICATION: primary source (CCNL PDF or official signatory site) not fetched; amounts not disputed by the 2024 rinnovo analysis (informaimpresa.it mentions only the NEW EUR 10 apprentice scatto, not a change to permanent scatti).
    
    APPRENTICE SENIORITY: EUR 10.00 from 2025-01-01. New clause introduced by Nov 2024 rinnovo ('Migliorata la norma relativa agli apprendisti che andranno a maturare gli scatti di anzianita'). Amount EUR 10.00 from CNA Ancona official communication. Zero before Jan 2025.
    
    LEVEL 1A FUNCTION ALLOWANCE: indennita di funzione EUR 51.65, confirmed kitech.it Mar 2026 (base 2490.07 + allowance 51.65 = total 2541.72). Assumed constant from Dec 2024; no primary source shows a change in this amount through the 2024 rinnovo.
    
    LEVEL ORDERING: 6 (lowest) < 5 < 5bis < 4 < 3 < 2 < 1B < 1A (highest). Level 5bis has higher salary than level 5 — this is correct per the CCNL (5bis = specializzato BIS, above the basic specializzato).
    
    APPRENTICESHIP: new rules from 2024-11-18 rinnovo for post-Nov-18-2024 contracts. Track durations confirmed from adapt.it (G016-specific): operai/tecnici max 5 years, amministrativi max 3 years, centraliniste 2 years. Percentage progressions (70/78/85/92/100% for operai/tecnici; 70/80/90% for amministrativi) follow the Confartigianato/CNA artigianato national framework agreement (CCNA); G016-specific source (adapt.it) confirms durations but not the individual percentages. SIMPLIFICATION: percentages assumed from artigianato CCNA framework; not found in a G016-specific primary source (CCNL PDF not fetched).
    
    INPS: reuses 2026-artigianato.json (ARTIGIANATO sector).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/comunicazione-artigianato-confartigianato.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/comunicazione-artigianato-confartigianato.py"
```
