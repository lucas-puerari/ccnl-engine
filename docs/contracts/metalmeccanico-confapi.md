# CCNL Metalmeccanici Piccola Industria (Unionmeccanica-Confapi)

| | |
|---|---|
| **CNEL code** | `C018` |
| **Sector** | metalmeccanico |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~350k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Unionmeccanica-Confapi
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
| `9` | Level 9 — highly qualified quadro | € 3,124.30 | — |
| `8` | Level 8 — highly specialised technician, quadro | € 2,809.37 | — |
| `7` | Level 7 — high technical or managerial expertise | € 2,583.36 | — |
| `6` | Level 6 — specialist technician, department head, senior technical employee | € 2,407.97 | — |
| `5` | Level 5 — specialist worker 2nd category, senior white-collar employee (CCNL reference level) | € 2,245.87 | — |
| `4` | Level 4 — specialist worker 1st category, white-collar employee | € 2,096.58 | — |
| `3` | Level 3 — skilled worker, clerical employee | € 2,009.48 | — |
| `2` | Level 2 — standardised operations, simple executive duties | € 1,811.11 | — |
| `1` | Level 1 — auxiliary duties, simple and repetitive operations | € 1,639.96 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 18.49 |
| `2` | € 21.59 |
| `3` | € 25.05 |
| `4` | € 26.75 |
| `5` | € 29.64 |
| `6` | € 32.43 |
| `7` | € 36.41 |
| `8` | € 40.95 |
| `9` | € 45.96 |

## Apprenticeship

**professionalizzante** (type: `under_classification`)  
Destination levels: `3`, `4`, `5`, `6`, `7`, `8`, `9`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    APPRENTICESHIP under-classification (Art. 10 consolidated CCNL text 26/05/2021): graded two levels below destination in the 1st period (0-12 months), one level below in the 2nd (12-24), at destination from the 25th month; 'professionalizzante' track for destinations from level 3 to level 9 (36-month duration assumed for all destinations).

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-06-01 | [↗](https://www.studiotuscano.it/news/nuovi-minimi-retributivi-per-il-ccnl-metalmeccanica-piccola-industria-confapi) |
| — | — | 2025-06-01 | [↗](https://www.studiomorettistp.it/aumento-retribuzione-tabellare-ccnl-metalmeccanici-piccola-industria-confapi-cnel-c018_n97.php) |
| — | — | 2026-06-01 | [↗](https://leggeinchiaro.it/ccnl-metalmeccanica-confapi-pmi-tabelle-retributive/) |
| — | — | — | [↗](https://www.lexplain.it/scatti-di-anzianita-ccnl-metalmeccanici-pmi-confapi/) |

??? note "Coverage notes"
    CONSOLIDATED MINIMUMS: the values in base_salary are the Confapi PMI 'consolidated table minimums', which incorporate base pay, contingenza, and terzo elemento into a single figure (ilccnl.it shows contingenza=0 and terzo elemento=0). fixed_allowances is empty for all levels.
    
    MODELLED TRANCHES: June 2024 (source: studiotuscano.it — Confapi June 2024 tables), June 2025 (source: studiomorettistp.it — FIM-CISL minutes 19/06/2025), September 2025 (derived by re-parametrisation, see note below), June 2026 (source: leggeinchiaro.it, Unionmeccanica tables).
    
    SEPTEMBER 2025 TRANCHE — RE-PARAMETRISATION: the agreement of 24 July 2025 provides +22.10 € at level 5 from 1 September 2025. The values for the other levels are calculated using the deterministic formula set out in the CCNL ('re-parametrisation of the other contractual levels'): level_increase = round(22.10 × (level_min_jun25 / 2173.76), 2). The same formula is verified against the June 2025 tranches (results matching to the cent with the FIM-CISL minutes). Verify the official table from Unionmeccanica or FIM-CISL for confirmation; possible deviation of ±0.01 € on some levels due to rounding.
    
    PRE-JUNE 2024 TRANCHES (CCNL in force since 26 May 2021) are outside the modelled window.
    
    SENIORITY INCREMENTS: amounts verified against Art. 41 of the CCNL consolidated text 26/05/2021 (source: www.htdi.it/CCNL%20Consolidato%20del%2026-05-2021.pdf). Full table: 1a=18.49 2a=21.59 3a=25.05 4a=26.75 5a=29.64 6a=32.43 7a=36.41 8a=40.95 9a=45.96 (in force from 1 January 2001). 24-month cadence, maximum 5 increments.
    
    HOURLY DIVISOR: 173 hours/month (40 h/week × 52/12, industry standard — confirmed by Art. 10 CCNL for calculation of apprentice hourly pay).
    
    MONTHLY PAYMENTS: 13 (thirteenth month). The fourteenth month is not provided for in the Confapi PMI CCNL.
    
    INPS: uses 2026-industria.json. Standard industry rates; verify whether Confapi PMI provides differentiated contributions compared to Federmeccanica for CIG/FIS.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/metalmeccanico-confapi.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/metalmeccanico-confapi.py"
```
