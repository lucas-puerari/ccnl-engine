# CCNL Dipendenti delle Farmacie Private

| | |
|---|---|
| **CNEL code** | `H121` |
| **Sector** | Farmacie private |
| **Tax sector** | `terziario` |
| **Last renewal** | 2021-09-07 |
| **Workers (est.)** | ~60k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - FEDERFARMA
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS

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
| `Q1` | Area Q1 - Direttore responsabile di farmacia | € 1,668.97 | — |
| `Q2` | Area Q2 - Farmacista collaboratore specializzato | € 1,499.19 | — |
| `Q3` | Area Q3 - Farmacista collaboratore con 24+ mesi in qualifica | € 1,429.19 | — |
| `1` | 1o livello - Farmacista collaboratore | € 1,429.19 | — |
| `2` | 2o livello - Lavoratori di concetto con funzioni di coordinamento | € 1,215.92 | — |
| `3` | 3o livello - Lavoratori di concetto con conoscenze tecniche | € 1,130.17 | — |
| `4` | 4o livello - Lavoratori con compiti operativi e conoscenze tecnico-pratiche | € 1,017.02 | — |
| `5` | 5o livello - Lavoratori qualificati con normali conoscenze | € 898.97 | — |
| `6` | 6o livello - Lavoratori di pulizia e operazioni semplici | € 807.81 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 15 increments

| Level | Increment (monthly) |
|---|---:|
| `Q1` | € 25.82 |
| `Q2` | € 25.30 |
| `Q3` | € 25.30 |
| `1` | € 25.30 |
| `2` | € 23.24 |
| `3` | € 22.72 |
| `4` | € 20.65 |
| `5` | € 20.14 |
| `6` | € 19.62 |

## Apprenticeship

**farmacista_collaboratore** (type: `under_classification`)  
Destination levels: `1`

**professionalizzante** (type: `under_classification`)  
Destination levels: `4`

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2021-09-07 | [↗](https://www.mnlf.it/documenti/ContrattoCollettivoNazionalediLavorodeidipendentidafarmaciaprivata2021.pdf) |

??? note "Coverage notes"
    Salary model: split. base_salary = retribuzione base nazionale conglobata (Tabella A, Art. 58). fixed_allowances = contingenza (per-level, frozen since 1977 per settore commercio) + EDR 10.33 (all levels, accordo 31/07/1992) + ISQ (Q levels, Tabella C).
    
    Divisore convenzionale 173 confirmed from Art. 57 of primary CCNL text.
    
    Additional months: 14. Art. 62 (13a mensilita) and Art. 63 (14a mensilita) confirmed from primary source.
    
    Seniority: 15 scatti biennali (Art. 53). Amounts from Tabella D (1.2.1996 column) of primary CCNL PDF.
    
    Contract expired 31/08/2024 (Art. 102). No successor signed as of 2026-09-09 (INPS-CNEL spreadsheet updated 25/07/2026 shows Periodo finale=null for H121). Tables valid open-ended under ultrattività.
    
    SIMPLIFICATION resolved: The CCNL rinnovo 07/09/2021 (Tabella A confirmed from UILTUCS primary PDF) established ONE salary tranche from 01/11/2021 — not three separate tranches. Increases vs. Dec 2012 base: Q1=+89.97, Q2=+150.00 (incl. 70 Area Q2), Q3=+80.00, L1=+80.00, L2=+70.98, L3=+67.39, L4=+62.65, L5=+57.72, L6=+53.90. These are fully modelled in this file. The '3 tranches / +113 EUR' figure cited in some secondary sources refers to the separate CCNL farmacie speciali/municipalizzate (Assofarm H122), not this contract.
    
    Apprenticeship from Accordo 14 giugno 2012 (Allegato II). Farmacista collaboratore (dest 1o) stays at level 1o for all 36 months. Commesso/Magazziniere/Contabile (dest 4o): months 0-12 at level 6o, months 13-36 at level 5o.
    
    Headcount: 77,146 workers in 16,324 companies (INPS-CNEL archive, H121).
    
    SIMPLIFICATION: Farmacie Rurali Sussidiate (Tabella B) excluded. Rural pharmacies have lower base salaries; Tabella A (urban) is modelled only.
    
    SIMPLIFICATION: ISQ for Q2 and Q3 modelled at flat 100 EUR (the 2+ anni tier per Tabella C). Workers with 12+ anni receive 130 EUR (delta 30 EUR/month, max ~360 EUR/yr). The two-tier split at 144 months cannot be represented as a single fixed_allowance amount.
    
    SIMPLIFICATION: EDR (10.33 EUR, Art. 54e) is contractually due for 13 mensilita but the engine multiplies fixed_allowances by additional_months=14. Annual overcount ~10 EUR per worker.
    
    SIMPLIFICATION: Tabella D groups Q2, Q3, and 1o into a single scatto amount of 25.30 EUR. Q1 uses 25.82 EUR.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/farmacie-private-h121.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/farmacie-private-h121.py"
```
