# CCNL Operai Agricoli e Florovivaisti — Coldiretti/Confagricoltura/CIA

| | |
|---|---|
| **CNEL code** | `A011` |
| **Sector** | agricoltura |
| **Tax sector** | `agricoltura` |
| **Last renewal** | — |
| **Workers (est.)** | ~600k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Coldiretti — Confederazione Nazionale Coldiretti
    - Confagricoltura — Confederazione Generale dell'Agricoltura Italiana
    - CIA — Confederazione Italiana Agricoltori
    - Assoverde — Associazione Italiana Costruttori del Verde
    - FLAI-CGIL — Federazione Lavoratori Agroindustria
    - FAI-CISL — Federazione Agro Alimentare
    - UILA-UIL — Unione Italiana Lavoratori Agroalimentari

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
| `Area1` | Area 1 — Operai Specializzati (specialised agricultural workers) | € 1,533.84 | — |
| `Area2` | Area 2 — Operai Qualificati (qualified agricultural workers) | € 1,398.86 | — |
| `Area3` | Area 3 — Operai Comuni (unskilled general agricultural workers) | € 1,043.00 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Area1` | € 11.36 |
| `Area2` | € 10.33 |
| `Area3` | € 8.99 |

## Apprenticeship

**apprendistato_professionalizzante** (type: `under_classification`)  
Destination levels: `Area1`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    NATIONAL MINIMUMS ONLY. Provincial contracts (contratti provinciali di lavoro, 20 provinces) pay substantially more than national floor. The national tabella retributiva is the legal minimum. Actual employer cost in any province requires adding the CPL supplement.

!!! warning ""
    OTI ONLY. OTD (Operai a Tempo Determinato / seasonal) workers are not modelled. OTD workers receive a Terzo Elemento of 30.44% (festività 5.45% + ferie 8.33% + tredicesima 8.33% + quattordicesima 8.33%) in lieu of accruals; the engine cannot represent this structure. OTD represent a large share of agricultural workers.

!!! warning ""
    FLOROVIVAISTI NOT DISTINGUISHED. The CCNL covers both Operai Agricoli (OTA) and Operai Florovivaisti (OTF). OTF have separate (higher) tabelle retributive with their own area amounts. This file models OTA amounts only. Callers must use a separate file (not yet modelled) for OTF workers.

!!! warning ""
    INPS CONTRIBUTION BASE. Agricultural OTI INPS contributions are legally computed on the 'retribuzione convenzionale' (set annually by INPS decree per DL 338/1989 Art. 1), NOT on the actual contractual salary. This engine applies rates to actual gross salary. The net INPS amounts will differ from statutory computations. Figures are indicative only.

!!! warning ""
    INAIL NOT MODELLED. INAIL agricultural premium (8.50% unified from 2026 per new tariff) is not modelled. The engine does not track INAIL.

!!! warning ""
    CNEL CODE A011 sourced from ilccnl.it and contratticcnl.it; unverified against CNEL archive (archive returned 404 at time of extraction). Code A014 belongs to a separate expired minority CCNL (ASNALI/FAGRI) — do not confuse.

!!! warning ""
    SENIORITY AMOUNTS. Art. 54 amounts (11.36 / 10.33 / 8.99) are from the 2022-2025 CCNL via aggregators (contratticcnl.it). The 2026 renewal text has not been confirmed to have changed these amounts; update manually if the renewed Art. 54 specifies different values.

!!! warning ""
    JANUARY 2027 TRANCHE. Amounts 1,533.84 / 1,398.86 / 1,043.00 computed as June 2026 values × 1.017 rounded to 2 decimal places. Exact CCNL renewal table values were not accessible at time of extraction; update if official tables show different rounding.

!!! warning ""
    APPRENTICESHIP — AREA1 DESTINATION ONLY. Area2 destination under-classification would require 2 levels below Area2, which is below the national floor (Area3), and cannot be modelled in a 3-level system. Area3 destination apprenticeship has no lower level to start from. Only Area1 destination (0-12m at Area3, 12-24m at Area2, 24-36m at Area1) is modelled.

!!! warning ""
    BILATERAL FUNDS. EBAN (Ente Bilaterale Agricolo Nazionale) and FISA (Fondo Integrativo di Settore Agricolo) bilateral fund contributions are set at provincial level and not modelled. Agrifondo (supplementary pension) contributions also omitted.

!!! warning ""
    TERRITORIAL REDUCTIONS. INPS reductions for mountain/disadvantaged zones (75%/68%) are not modelled.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-05-28 | [↗](https://www.contratticcnl.it/agricoltura-florovivaisti/tabelle-retributive/) |
| — | — | 2026-01-01 | [↗](https://ciatreviso.it/contributi-inps-inail-2026-agricoli-aliquote-e-le-scadenze-per-operai-otd-e-oti/) |

??? note "Coverage notes"
    SALARY MODEL: conglobated retribuzione tabellare minima (paga base + contingenza + EDR merged since 01/01/2009). Contingenza = 0.00 and EDR = 0.00 per ilccnl.it table. Single base_salary per area per period. Source: contratticcnl.it tabelle retributive, confirmed by research from ilccnl.it showing zero contingenza columns.
    
    RENEWAL: CCNL signed 23/05/2022 (valid 2022-2025), renewed 28/05/2026 (quadriennio 2026-2029). Two salary tranches: +3.4% from 2026-06-01, +1.7% from 2027-01-01 on June 2026 amounts. No una tantum.
    
    LEVELS: Three national professional areas (OTI, Operai a Tempo Indeterminato, national minimums). Area1=Specializzati, Area2=Qualificati, Area3=Comuni. National table sets floor only; provincial contracts (contratti provinciali di lavoro) always exceed these minimums.
    
    HOURLY DIVISOR: 169 hours/month. Formula: 39 h/week × 52 weeks / 12 = 169.00 exactly. Confirmed by ilccnl.it divisore orario field (169) and daily divisor 26 (169 / 6.5).
    
    ADDITIONAL MONTHS: 14 (tredicesima Art. 52 + quattordicesima Art. 53 CCNL). Tredicesima paid at year-end; quattordicesima paid 30 April. Both equal one full monthly retribuzione globale.
    
    SENIORITY: triennale (36 months), maximum 5 scatti. Euro amounts from Art. 54 CCNL 2022-2025 (aggregator-sourced: contratticcnl.it): Area1 EUR 11.36, Area2 EUR 10.33, Area3 EUR 8.99 per triennio. Amounts frazionabili at daily (÷26) and hourly (÷169) divisors.
    
    TAX SECTOR: AGRICOLTURA (new TaxSector). INPS rates: Gestione Previdenziale Speciale Agricola, OTI standard agriculture: employee 8.84%, employer 21.66%, total 30.50% (2026). Source: ciatreviso.it citing INPS 2026 rates.
    
    CNEL CODE: A011. Confirmed from ilccnl.it page header and contratticcnl.it/ccnl/a011/. CNEL archive (cnel.it) returned 404 at time of extraction.
    
    APPRENTICESHIP: sotto-inquadramento (under_classification) per Allegato n. 10 CCNL (23/02/2017 apprenticeship agreement, updated to D.Lgs. 81/2015). Area1 destination only — see SIMPLIFICATION note. Duration 36 months for Area1.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/operai-agricoli-florovivaisti.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/operai-agricoli-florovivaisti.py"
```
