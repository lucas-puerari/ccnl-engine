# CCNL Comunicazione, Informatica e Servizi Innovativi PMI — Settore Informatico

| | |
|---|---|
| **CNEL code** | `G029` |
| **Sector** | informatica-servizi-innovativi |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~20k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Unigec Confapi
    - Unimatica Confapi
    - SLC-CGIL
    - Fistel-CISL
    - Uilcom-UIL

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
| `Q` | Quadro — manager, exceptional leadership and innovative thinking (PAR 248 + indennità funzione 51.65) | € 2,889.92 | — |
| `1` | Livello 1 — top professional, full strategic responsibility (PAR 247) | € 2,827.50 | — |
| `2` | Livello 2 — expert professional, strategic solutions, wide autonomy (PAR 209) | € 2,468.03 | — |
| `3` | Livello 3 — senior professional, leads in complex environments (PAR 195) | € 2,336.94 | — |
| `4` | Livello 4 — senior specialist, responsible for team performance (PAR 182) | € 2,218.03 | — |
| `5` | Livello 5 — reference level (PAR 169); experienced specialist with consultancy role | € 2,095.18 | — |
| `6` | Livello 6 — senior technician, coordinates others in limited contexts (PAR 150) | € 1,967.68 | — |
| `7` | Livello 7 — technical specialist, independent in structured contexts (PAR 133) | € 1,776.03 | — |
| `8` | Livello 8 — qualified technical worker, applies skills to defined problems (PAR 125) | € 1,678.58 | — |
| `9` | Livello 9 — basic technical tasks, limited autonomy (PAR 114) | € 1,575.27 | — |
| `10` | Livello 10 — entry-level worker, simple tasks under close supervision (PAR 100) | € 1,444.33 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 16.01 |
| `1` | € 16.01 |
| `2` | € 16.01 |
| `3` | € 14.46 |
| `4` | € 13.94 |
| `5` | € 13.43 |
| `6` | € 13.17 |
| `7` | € 12.91 |
| `8` | € 12.39 |
| `9` | € 11.88 |
| `10` | € 11.62 |

## Apprenticeship

**professionalizzante_36** (type: `under_classification`)  
Destination levels: `1`, `2`, `3`, `4`, `5`, `6`, `7`

**automatico_it** (type: `under_classification`)  
Destination levels: `8`, `9`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    APPRENTICESHIP GENERAL TRACK DURATION: the CCNL offers three duration options (36/30/24 months) by agreement between the parties; no per-destination-level assignment was found in the available text. The 36-month track (12+12+12) is used as representative for destination levels 1, 2, 3, 4, 5, 6, 7. Real durations may be shorter by agreement.

!!! warning ""
    APPRENTICESHIP — QUADRO (Q) NOT MODELLED AS DESTINATION: Art. 52 and Art. 64 contain no affirmative listing of Q as an apprendistato professionalizzante destination. Following repo precedent (telecomunicazioni-asstel, gomma-plastica) where Quadri are excluded from apprenticeship destinations when no explicit contractual text lists them, Q is omitted from destination_levels of the general track.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-04-14 | [↗](https://www.cdltorino.it/ccnl-informatica-piccola-industria-rettifica-tabelle-retributive/) |
| — | — | 2025-04-14 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=302) |
| — | — | 2021-03-09 | [↗](https://slc.cgil.it/ccnl/20210309-CCNL_CONFAPI_UNIGEC_UNIMATICA.pdf) |

??? note "Coverage notes"
    SCOPE: models the SETTORE INFORMATICO E SERVIZI INNOVATIVI sub-sector of G029 only (levels Q, 1–10). The SETTORE GRAFICO-EDITORIALE and SETTORE CARTARIO-CARTOTECNICO sub-sectors of G029 are NOT modelled here. Applicable to ICT companies covered by Art. 1 of the CCNL.
    
    SALARY MODEL — CONGLOBATED: base_salary values are the total contractual retribuzione mensile (paga base + contingenza + EDR + indennità di funzione for Q) at each tranche date. Contingenza per level is frozen since 1994 and sourced from Allegato 24 of the G029 CCNL 09/03/2021 PDF. EDR = EUR 10.33 (all levels). Q level includes indennità di funzione = EUR 51.65 introduced from 01/01/2025 (sourced from kitech.it April 2025 tables, component-level breakdown). fixed_allowances is empty for all levels.
    
    CONGLOBATED CHECK (non-circular): paga_base values from the April 14 2025 corrected tables (cdltorino.it) plus frozen contingenza (Allegato 24 PDF) plus EDR 10.33 independently sum to the kitech Jan 2026 totals to within EUR 0.01 on all 11 levels. Example at Jan 2026: level 5 paga_base 1529.38 + contingenza 525.47 + EDR 10.33 = 2065.18 (kitech ✓); level 10: 903.38 + 512.87 + 10.33 = 1426.58 (kitech ✓); Q: 2242.26 + 541.65 + 10.33 + 51.65 = 2845.89 (kitech ✓). The kitech values ARE the conglobated total, not paga_base only.
    
    HOURLY DIVISOR = 169. Source: Art. 113 G029 CCNL 2021 PDF ('dal 1° gennaio 2019 si dividerà per 169'). Independent cross-check: contractual weekly hours = 39 h from 01/01/2019 (same Art. text); 39 × 52 / 12 = 169.00 exactly.
    
    PAR COEFFICIENTS from Art. 116 G029 CCNL 2021 PDF (Settori Grafico-Editoriale, Informatico-Servizi Innovativi): Q=248, 1=247, 2=209, 3=195, 4=182, 5=169, 7=133, 8=125, 9=114, 10=100. CORRECTION: level 6 PAR was changed from 156 (2021 CCNL) to 150 in the April 14 2025 verbale integrativo corrected tables. This is confirmed by cdltorino.it rettifica article (PAR=150 shown explicitly) and is consistent with the kitech Jan 2026 total for level 6 (1407.71 + 523.01 + 10.33 = 1941.05). All base_salary values are computed from official paga_base (cdltorino April 2025) + frozen contingenza (Allegato 24 CCNL PDF) + EDR 10.33.
    
    TRANCHE DATES: 01/01/2025 (first, effective retroactively from April 2025 per verbale); 01/01/2026 (second); 01/01/2027 (third). Reference level 5 increases: +60, +60, +30 EUR paga base. Confirmed by search results (bollettinoadapt.it, fiscoetasse.com).
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: Art. 97 G029 CCNL 2021 PDF (tredicesima mensilità). No quattordicesima article exists in G029.
    
    SENIORITY: 5 scatti biennali (cadence 24 months). Source: Art. 45 G029 CCNL 2021 PDF ('per ogni biennio, e fino ad un massimo di 5 bienni'). Per-level amounts from same article (effective from 01/01/2002 update). kitech April 2025 table confirms same amounts unchanged in the 2025 renewal.
    
    INPS: reuses 2026-industria.json (Confapi/industria sector). Unimatica-Confapi belongs to industria. CIGO applies (D.Lgs. 148/2015). No Cassa Edile or bilateral fund substituting INPS contributions.
    
    APPRENTICESHIP GENERAL TRACK (Art. 52 CCNL, para. C Apprendistato professionalizzante): first period 2 levels below destination; second period 1 level below; third period classification stays 1 below but retribuzione is at destination level (levels_below=0 in engine, which models pay, not classification). Duration options: 36, 30 or 24 months by agreement. The 36-month (12+12+12) track is modelled as representative.
    
    APPRENTICESHIP AUTOMATICO TRACK (Art. 52 CCNL, settore informatico-servizi innovativi Area Tecnica): destination level 8 → entry at level 9 (1 below), 18 months; destination level 9 → entry at level 10 (1 below), 18 months. After permanent hire, destination-level 8 apprentices spend 6 months at level 9 before final assignment (this post-apprenticeship transition is not modelled; it occurs outside the apprendistato period).
    
    EDR ROLL-UP: rolling EDR (EUR 10.33) into base_salary is safe for G029 because G029 uses under_classification apprenticeship, meaning the apprentice pay is determined by the classified level's base_salary directly. The EDR percentage-of-base exemption (Art. 3 L. 537/1993) does not apply to under_classification.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/informatica-pmi-unimatica.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/informatica-pmi-unimatica.py"
```
