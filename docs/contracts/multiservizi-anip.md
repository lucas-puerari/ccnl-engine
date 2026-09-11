# CCNL Servizi di Pulizia e Servizi Integrati/Multiservizi (ANIP-Confindustria)

| | |
|---|---|
| **CNEL code** | `K511` |
| **Sector** | multiservizi |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~580k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ANIP-Confindustria
    - Legacoop Lavoro e Servizi
    - Confcooperative Lavoro e Servizi
    - AGCI Servizi
    - Unionservizi Confapi
    - Filcams-CGIL
    - Fisascat-CISL
    - Uiltrasporti-UIL

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
| `Q` | Quadri with high-responsibility managerial duties | € 2,006.64 | — |
| `7` | Employees with managerial functions | € 1,833.35 | — |
| `6` | Workers with specialist duties / Senior white-collar employees | € 1,587.07 | — |
| `5` | Expert workers / White-collar employees | € 1,276.96 | — |
| `4` | Specialist workers / Junior clerical employees | € 1,167.51 | — |
| `4par125` | Workers assigned to painting booths and lines employed as of 01/06/2001 (par. 125) | € 1,140.15 | — |
| `3` | Skilled workers / Clerical employees | € 1,076.30 | — |
| `2par115` | Workers assigned to auxiliary activities in school/healthcare settings (par. 115) | € 1,048.93 | — |
| `2` | General workers / Clerical employees (first 18 months) | € 994.21 | — |
| `1` | General labourers | € 912.12 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 51.02 |
| `2` | € 54.39 |
| `2par115` | € 55.50 |
| `3` | € 58.18 |
| `4par125` | € 62.59 |
| `4` | € 63.15 |
| `5` | € 97.29 |
| `6` | € 116.67 |
| `7` | € 132.06 |
| `Q` | € 142.89 |

## Apprenticeship

**destinazione_5** (type: `under_classification`)  
Destination levels: `5`

**destinazione_4** (type: `under_classification`)  
Destination levels: `4`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    INPS RATES PROXY. Terziario sector confirmed for multiservizi/pulizie: kitech.it (p=4_129, "Commercio - terziario Imprese appaltatrici servizi pulizia") lists rates matching 2026-terziario.json. Simplification: the CIGS threshold for imprese di pulizia is >15 dipendenti (not >50 as in the general terziario tier); for 16-50 employee companies the modeled employee rate (9.19%) understates the actual 9.49%. FIS (Fondo Integrazione Salariale) may also apply for non-CIGS-eligible firms. Source: kitech.it/Contributi-previdenziali.aspx?p=4_129

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2021-07-09 | [↗](https://www.oristanoservizi.it/wp-content/uploads/2021/11/CCNL-Multiservizi-scadenza-2024.pdf) |
| — | — | 2025-06-13 | [↗](https://www.redigo.info/2025/06/24/rinnovo-ccnl-imprese-di-pulizia-e-servizi-integrati-per-il-periodo-2025-2028/) |
| — | — | — | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=99) |
| — | — | — | [↗](https://www.ccnlportatili.it/ccnl/terziario-servizi/multiservizi-servizi-di-pulizia/) |

??? note "Coverage notes"
    Salary model: SPLIT. Paga base (minimo tabellare) is a time series; contingenza and EDR are frozen fixed_allowances. Source: oristanoservizi.it/CCNL-Multiservizi-scadenza-2024.pdf (2021-2024 contract, 5 tranches) and accordo integrativo 6 Aug 2025 (2025-2028 contract, 8 tranches) via redigo.info.
    
    hourly_divisor: 173 — confirmed per CCNL text: 'I divisori per ottenere la quota oraria e giornaliera sono, rispettivamente, 173 e 26'. Cross-checked: level Q July 2021 total 1953.62/11.29hr = 173 (hourly rate from table). Source: oristanoservizi.it PDF.
    
    additional_months: 14 (tredicesima + quattordicesima). Source: CCNL text — 'Tredicesima: entro il 20 dicembre; Quattordicesima: entro il 15 luglio'. Both in misura di una mensilità della retribuzione globale mensile.
    
    Seniority — impiegati (levels 5, 6, 7, Q): biennale scatti equal to 6.25% of (minimo tabellare + contingenza al 1 agosto 1983, EUR 279.60), maximum 8; amounts are recomputed at every salary tranche (verified against the July 2021 and July 2025 published values).
    
    Seniority — operai (levels 1, 2, 2par115, 3, 4par125, 4): 'anzianità forfettaria di settore', a single fixed monthly amount from the 5th year of sector seniority; modelled with first_cadence_months_by_level=48 and maximum_count_by_level=1. Amounts per CCNL text (June 2011 increase after E.d.a.r. cessation). Source: oristanoservizi.it PDF.
    
    Contingenza par levels: the CCNL text notes that contingenza values for 4par125 and 2par115 are not explicitly stated; by industry convention they match the values for levels 4 and 2 respectively. Source: note in oristanoservizi.it PDF.
    
    Apprenticeship: under-classification, 30 months for destination levels 4 and 5 (CCNL: '30 mesi per i livelli 4° e 5°'): first half two classification levels below the destination, second half one level below (the parametric sub-levels 2par115 and 4par125 are skipped, hence levels_below 3/1 for destination 5 and 4/2 for destination 4). Destination level 2 (apprentice stays at level 1 for the whole period) and other destinations are not modelled: durations not sourced. Source: ccnlportatili.it.
    
    July 2025 values: the 2021-2024 CCNL included a 5th salary tranche effective July 2025 (e.g. +10 EUR on level 2). This was superseded by the 2025-2028 renewal (signed 13 June 2025, definitive tables per accordo integrativo 6 August 2025, effective retroactively from 1 July 2025 per Art. 73). The JSON models post-renewal July 2025 values (819.21 for level 2) directly. Workers received the higher new-contract amount; the old 5th tranche value (779.21) was never separately operative.
    
    ANIP CONTRACT STATUS (2025): ANIP-Confindustria abandoned the final stages of the 2025 CCNL renewal negotiations without signing. The 2025 renewal was signed by Legacoop Produzione e Servizi, Unionservizi Confapi, AGCI + Filcams-CGIL/Fisascat-CISL/Uiltrasporti-UIL. ANIP companies continue to apply the previous CCNL (this file). A separate multiservizi-legacoop file would be needed to cover the new 2025-2028 renewal (levels 1-8: 1,296.39-2,256.14 EUR, 14 mensilità).
    
    Workers covered: ~403,000 per INPS-UNIEMENS 2025 data; largest uncovered CCNL at time of implementation.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/multiservizi-anip.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/multiservizi-anip.py"
```
