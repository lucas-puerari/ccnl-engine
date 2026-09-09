# CCNL Energia e Petrolio (Confindustria Energia)

| | |
|---|---|
| **CNEL code** | `B254` |
| **Sector** | energia |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~38k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Confindustria Energia
    - Filctem-CGIL
    - Femca-CISL
    - Uiltec-UIL

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
| `1-5` | Quadro Gruppo 1/5 — manager, fifth CREA tier (highest) | € 3,748.10 | — |
| `1-4` | Quadro Gruppo 1/4 — manager, fourth CREA tier | € 3,748.10 | — |
| `1-3` | Quadro Gruppo 1/3 — manager, third CREA tier | € 3,748.10 | — |
| `1-2` | Quadro Gruppo 1/2 — manager, second CREA tier | € 3,748.10 | — |
| `1-1` | Quadro Gruppo 1/1 — manager, first CREA tier | € 3,748.10 | — |
| `2-4` | Gruppo 2/4 — specialist workers, fourth function allowance tier | € 3,394.47 | — |
| `2-3` | Gruppo 2/3 — specialist workers, third function allowance tier | € 3,394.47 | — |
| `2-2` | Gruppo 2/2 — specialist workers, second function allowance tier | € 3,394.47 | — |
| `2-1` | Gruppo 2/1 — specialist workers, first function allowance tier | € 3,394.47 | — |
| `3-4` | Gruppo 3/4 — senior workers, fourth function allowance tier | € 3,074.11 | — |
| `3-3` | Gruppo 3/3 — senior workers, third function allowance tier | € 3,074.11 | — |
| `3-2` | Gruppo 3/2 — senior workers, second function allowance tier | € 3,074.11 | — |
| `3-1` | Gruppo 3/1 — senior workers, first function allowance tier | € 3,074.11 | — |
| `4-4` | Gruppo 4/4 — skilled workers, fourth function allowance tier | € 2,716.61 | — |
| `4-3` | Gruppo 4/3 — skilled workers, third function allowance tier | € 2,716.61 | — |
| `4-2` | Gruppo 4/2 — skilled workers, second function allowance tier | € 2,716.61 | — |
| `4-1` | Gruppo 4/1 — skilled workers, first function allowance tier | € 2,716.61 | — |
| `5-4` | Gruppo 5/4 — standard workers, fourth function allowance tier | € 2,382.32 | — |
| `5-3` | Gruppo 5/3 — standard workers, third function allowance tier | € 2,382.32 | — |
| `5-2` | Gruppo 5/2 — standard workers, second function allowance tier | € 2,382.32 | — |
| `5-1` | Gruppo 5/1 — standard workers, first function allowance tier | € 2,382.32 | — |
| `5-0` | Gruppo 5/0 — standard workers, base position (no function allowance) | € 2,382.32 | — |
| `6-0` | Gruppo 6/0 — entry-level workers, basic routine operations | € 2,072.49 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**livelli_2_3** (type: `percentage`)  
Destination levels: `2-1`, `2-2`, `2-3`, `2-4`, `3-1`, `3-2`, `3-3`, `3-4`  
percentage: 0.95

**livello_4** (type: `percentage`)  
Destination levels: `4-1`, `4-2`, `4-3`, `4-4`  
percentage: 0.95

**livello_5** (type: `percentage`)  
Destination levels: `5-0`, `5-1`, `5-2`, `5-3`, `5-4`  
percentage: 0.90

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    HOURLY DIVISOR: 174.5 h/month. Source: previdenza-professionisti.it and lavoro-economia.it. The CCNL states EDR is 'omnicomprensivo' with no impact on other contractual institutes including the hourly calculation. The engine applies hourly_rate = gross_monthly / 174.5, where gross_monthly includes EDR. This overstates hourly_rate by EDR/174.5 (~0.29/h at group 4). Engine limitation: no per-allowance hourly_relevant flag exists.

!!! warning ""
    APPRENTICESHIP LEVEL 6: percentages not found in any consulted source (previdenza-professionisti.it lists only tracks for levels 2-3, 4, 5). Level 6-0 omitted from apprenticeship tracks.

!!! warning ""
    FUNCTION ALLOWANCE GROUPS 2-5: amounts assumed constant throughout the 2025-2027 CCNL (no published CCNL text or source indicates a change). Values derived from kitech Jul 2026 back-calculation; a second date was not available for verification.

!!! warning ""
    CREA CONSTANCY: CREA amounts assumed constant throughout 2025-2027 (no source indicates time variation). Values from kitech Jul 2026 only.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-04-16 | [↗](https://www.redigo.info/2025/08/06/tabelle-retributive-ccnl-energia-e-petrolio/) |
| — | — | 2025-04-16 | [↗](https://www.previdenza-professionisti.it/diritto-del-lavoro/ccnl-energia-e-petrolio---scheda.html) |
| — | — | 2026-07-01 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=B254) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = paga_base (minimi tabellari) only. fixed_allowances per level include: (1) EDR_IPCA — Elemento Distinto della Retribuzione, group-specific TimeSeries from Jul 2025; (2) INDENNITA_FUNZIONE — level-specific function allowance (constant for groups 2-6, TimeSeries Jul 2025=190/Jan 2027=200 for group 1 quadri); (3) CREA — level-specific, constant, group 1 only. Total paga tabellare = base_salary + INDENNITA_FUNZIONE + CREA; verified against kitech at Jul 2026 (exact match 23/23 levels).
    
    MODELLED TRANCHES: 2025-07-01 (first tranche, new CCNL 2025-2027), 2025-12-01 (second), 2026-01-01 (third), 2026-07-01 (fourth), 2027-07-01 (fifth and final). Jan-Jun 2025 retroactive tranche (ipotesi signed 2025-04-16) not modelled — belongs to the transition period of the previous CCNL.
    
    EDR IPCA: introduced 2025-03-01 (pre-modelled). First modelled period from 2025-07-01 at increased amounts: G1=60.71, G2=54.98, G3=49.79, G4=44.00, G5=38.59, G6=33.57. Second period from 2026-01-01: G1=70.37, G2=63.73, G3=57.71, G4=51.00, G5=44.73, G6=38.91. Open-ended (no further increase published). Source: redigo.info.
    
    FUNCTION ALLOWANCE GROUP 1 (indennità di funzione quadri): 190 EUR/month for all 14 mensilità, valid 2025-07-01 to 2026-12-31; increases to 200 EUR from 2027-01-01. Source: contratticcnl.it (CCNL 2025-2027). Constant for groups 2-5; absent for group 6.
    
    CREA (Compenso per Risultato ed Eccellenza Aziendale): only for group 1 (quadri). Amounts from kitech Jul 2026 back-calculation: 1-1=90.65, 1-2=181.31, 1-3=271.96, 1-4=362.61, 1-5=453.26. Constant throughout the contract (no source indicates time variation).
    
    CATEGORY: group 1 levels (1-1 through 1-5) are Quadri under L. 190/1985. Groups 2-6 are impiegati/operai; category omitted as the CCNL does not publish a clean impiegato/operaio split by level.
    
    SENIORITY INCREMENTS: abolished from 2016-01-01 by the 2016 CCNL renewal. Amounts accrued up to 2015 are crystallised as a personal supplement. Modelled as maximum_count=0, amount_by_level={}, cadence_months=24 (historical biennial cadence).
    
    ADDITIONAL MONTHS: 14 (tredicesima December + quattordicesima June). Source: previdenza-professionisti.it.
    
    INPS: uses 2026-industria.json (standard industry sector). CNEL code: B254.
    
    APPRENTICESHIP: percentage type, 3 tracks (livelli_2_3, livello_4, livello_5). Source: previdenza-professionisti.it (2025-04-16 CCNL). Livelli 2-3 max 24 months (90% for first 12m, 95% thereafter). Livello 4 max 36 months (90% for first 12m, 95% thereafter). Livello 5 max 36 months (80% for first 12m, 90% thereafter). Reference retribution per CCNL Art.: 'il minimo del livello di inquadramento e del relativo CREA'.
    
    APPRENTICESHIP REFERENCE BASE: per CCNL, reference is 'minimo tabellare e relativo CREA'. Modelled correctly: INDENNITA_FUNZIONE and INDENNITA_FUNZIONE_QUADRI set apprenticeship_pct_relevant=false (paid at full value, not reduced); EDR set apprenticeship_pct_relevant=false (omnicomprensivo, no impact on other institutes); CREA set apprenticeship_pct_relevant=true (explicitly in CCNL base for group 1).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/energia-petrolio-confindustria.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/energia-petrolio-confindustria.py"
```
