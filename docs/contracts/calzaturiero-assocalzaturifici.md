# CCNL per i lavoratori addetti all'industria delle calzature

| | |
|---|---|
| **CNEL code** | `D121` |
| **Sector** | industria |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~75k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Assocalzaturifici
    - FILCTEM-CGIL
    - FEMCA-CISL
    - UILTEC-UIL

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
| `8` | 8th level - Managers and workers with high-responsibility functions | € 2,509.13 | — |
| `7` | 7th level - Workers with managerial functions | € 2,355.70 | — |
| `6` | 6th level - Workers with high specialisation | € 2,163.79 | — |
| `5` | 5th level - Workers with coordination duties | € 2,054.43 | — |
| `4` | 4th level - Workers with intermediate duties | € 1,980.50 | — |
| `3S` | 3rd level Super - Specialist workers with higher-grade duties | € 1,933.07 | — |
| `3` | 3rd level - Specialist workers | € 1,891.45 | — |
| `2S` | 2nd level Super - Qualified workers with higher-grade duties | € 1,832.71 | — |
| `2` | 2nd level - Qualified workers | € 1,796.40 | — |
| `1` | 1st level - Entry-level workers | € 1,557.00 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `8` | € 12.24 |
| `7` | € 12.01 |
| `6` | € 9.94 |
| `5` | € 9.19 |
| `4` | € 8.47 |
| `3S` | € 7.98 |
| `3` | € 7.98 |
| `2S` | € 7.41 |
| `2` | € 7.41 |
| `1` | € 6.89 |

## Apprenticeship

**prof_L6_L8** (type: `percentage`)  
Destination levels: `6`, `7`, `8`  
percentage: 1.00

**prof_L3_L5** (type: `percentage`)  
Destination levels: `3`, `3S`, `4`, `5`  
percentage: 1.00

**prof_L2** (type: `percentage`)  
Destination levels: `2`, `2S`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Seniority cadence is triennale (36 months) for all levels; maximum 5 scatti. Scatto amounts derived from businessonline.it article (2025) cross-checked with kitech.it current table.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-07-17 | [↗](https://www.consulenza.it/Contenuti/News/news/9409/calzaturieri-industria-e-minimi-retributivi) |
| — | — | 2024-07-17 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=173) |
| — | — | 2024-07-17 | [↗](https://www.businessonline.it/articoli/scatti-anzianita-contratto-calzaturiero-tabella-ogni-quanto-ci-sono-e-stipendio-di-quanto-aumenta.html) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (minimi retributivi include paga base, contingenza, and EDR). Modeled as base_salary with fixed_allowances: [] for all levels except level 8 (IND_FUN for quadri). Confirmed by stable coefficient ratios across all tranche dates.
    
    LEVEL 8 IND_FUN: indennità di funzione per quadri 41.31 EUR/month applies only to quadri supervisory employees, not to all livello 8 workers. Engine models base salary only for L8; the allowance is excluded by contract scope, not by modelling omission.
    
    LEVEL 1 SPECIAL TRANCHE: separate wage correction from 1 January 2025 (EUR 1,502.46, up from EUR 1,315.70 at Aug 2024), independent of standard tranche dates Aug 2024/Aug 2025/Aug 2026. Confirmed by fiscoetasse.com (rinnovo 2024) and web search: Jan 2025=1502.46, Aug 2025=1530.00, Aug 2026=1557.00. Modeled as a four-period series for level 1 only.
    
    Workers covered: approximately 75,000 (Assocalzaturifici member companies). Agreement signed 2024-07-17; valid 2024-01-01 to 2026-12-31.
    
    INPS rates from 2026-industria.json (same sector as metalmeccanico). IRPEF 2026 brackets applied (L. 199/2025).
    
    APPRENTICESHIP (professionalizzante): 80/90/100% in three periods. Total duration 36 months per Art. apprendistato. Period splits by level group: L6-L8=10/10/16m, L3-L5=11/11/14m, L2-L2S=12/12/12m. L1 not eligible as destination. Source: CCNL 2024-07-17 Assocalzaturifici (D121), circolare apprendistato; businessonline.it article 2024; kitech.it scheda D121.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/calzaturiero-assocalzaturifici.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/calzaturiero-assocalzaturifici.py"
```
