# CCNL Metalmeccanica e Installazione di Impianti — Artigianato

| | |
|---|---|
| **CNEL code** | `C030` |
| **Sector** | metalmeccanico |
| **Tax sector** | `artigianato` |
| **Last renewal** | — |
| **Workers (est.)** | ~350k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Confartigianato Imprese
    - CNA
    - Casartigiani
    - CLAAI
    - FIM-CISL
    - FIOM-CGIL
    - UILM-UIL

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
| `1Q` | Level 1Q — quadri: high-responsibility managerial functions | € 2,106.03 | — |
| `1` | Level 1 — white-collar employees with managerial functions | € 2,106.03 | — |
| `2` | Level 2 — conceptual tasks or high technical specialisation | € 1,959.57 | — |
| `2bis` | Level 2 bis — specialised tasks, high operative autonomy | € 1,850.31 | — |
| `3` | Level 3 — qualified tasks with operative autonomy | € 1,779.22 | — |
| `4` | Level 4 — qualified operative tasks, partial operative autonomy | € 1,676.98 | — |
| `5` | Level 5 — simple tasks with minimal operative autonomy | € 1,615.17 | — |
| `6` | Level 6 — elementary operations without autonomy | € 1,540.21 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1Q` | € 32.94 |
| `1` | € 32.94 |
| `2` | € 29.08 |
| `2bis` | € 26.13 |
| `3` | € 24.29 |
| `4` | € 21.72 |
| `5` | € 20.24 |
| `6` | € 18.40 |

## Apprenticeship

**operai** (type: `percentage`)  
Destination levels: `5`, `4`, `3`, `2bis`  
percentage: 1.00

**impiegati** (type: `percentage`)  
Destination levels: `2`, `1`  
percentage: 1.00

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2021-12-17 | [↗](https://www.ebna.it/wp-content/uploads/2022/01/CCNL-artigianato-metalmeccanico-2021.pdf) |
| — | — | 2024-11-19 | [↗](https://www.kitech.it/tabelle-retributive-metalmeccanici-artigianato/) |
| — | — | — | [↗](https://www.eblart.it/scheda-ccnl-artigianato-metalmeccanici/) |
| — | — | — | [↗](https://www.direzionelavoro.it/ccnl-metalmeccanici-artigianato-tabelle-retributive/) |

??? note "Coverage notes"
    CONGLOBATED MINIMUMS: base_salary values are conglobated minimum pay figures, incorporating base pay, contingenza and EDR in a single amount. Conglobation confirmed in force from 16.06.2011 (source: EBNA CCNL 17.12.2021, Art. 28 and attached tables). fixed_allowances is empty for all levels.
    
    2022 TRANCHES: three tranches CCNL 17.12.2021 (01.01.2022, 01.05.2022, 01.12.2022). Per-level increments verified against EBNA/Direzionelavoro.it. Values at 01.12.2022 confirmed from EBNA primary source.
    
    AFAC TRANCHES: Accordo Fondo Anticipazione Contrattuale 21.12.2023, two tranches (01.12.2023, 01.04.2024). Values at 01.04.2024 cross-verified against kitech.it for all 8 levels.
    
    2024 RENEWAL TRANCHES: agreement 19.11.2024 (operative 20.12.2024), four tranches (01.12.2024, 01.07.2025, 01.03.2026, 01.11.2026). All per-level amounts for all 8 levels confirmed from UILM national synthesis PDF (20250128 CCNL Artigianato area meccanica 2023-2026, url: https://www.uilmnazionale.it/). Values match kitech.it for levels verified there. All 4 tranches fully modelled with primary-source amounts.
    
    HOURLY DIVISOR: 173 hours/month (40h/week, Art. 28 CCNL 17.12.2021). Arithmetic monthly/hourly verification did not yield clean integer results on the available values; confirmation is based on the primary CCNL text.
    
    SENIORITY INCREMENTS: biennial (24 months), maximum 5 increments. Per-level amounts from EBLART/Direzionelavoro.it table (tab. 7.1). The effective date of the amounts (01.01.2022) is assumed to coincide with the first salary tranche; the primary source does not report a separate effective date for seniority increments.
    
    APPRENTICESHIP percentage, 10 semesters (60 months max), operai progression (source EBLART, apprenticeship professionalizzante article): 70% (sem. I-II), 75% (III), 78% (IV), 80% (V), 85% (VI), 88% (VII), 92% (VIII), 100% (IX-X); track 'operai' for destinations 5, 4, 3, 2bis. Since the 2015 reform level 6° cannot be used as a destination.
    
    INPS OPERAI/IMPIEGATI: 2026-artigianato.json models both categories via employer_rate_by_category (operai default 26.93%; impiegati/quadri 24.71%). Pass Employee(category='impiegato') or Employee(category='quadro') to receive the lower rate; omitting category routes to operaio rate. Components: IVS 23.81% + NASpI 1.61% + CUAF 0.68% + malattia operai ~0.83% = 26.93%; malattia for impiegati is lower (hence ~24.71%). No CIGO/CIGS (D.Lgs. 148/2015 Art. 3, artigianato excluded). FSBA (0.45% employer + 0.15% employee) is bilateral, excluded from the tax file.
    
    ADDITIONAL MONTHS: 13 (tredicesima). A quattordicesima is not provided for by the CCNL Artigianato Metalmeccanico.
    
    APPRENTICESHIP administrative impiegati (destination levels 2, 1): 3 years, percentages 70% (year 1), 77% (year 2), 87% (year 3), 100% thereafter. Track 'impiegati'. Level 1Q (quadro) excluded. Source: CCNL metalmeccanico artigianato renewal 17.12.2021 (EBLART summary); formazione-apprendistato.com; conflavoro.it 2021 summary.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/metalmeccanico-artigianato.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/metalmeccanico-artigianato.py"
```
