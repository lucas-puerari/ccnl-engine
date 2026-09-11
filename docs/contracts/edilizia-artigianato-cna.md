# CCNL Edilizia e Affini Artigianato

| | |
|---|---|
| **CNEL code** | `F015` |
| **Sector** | edilizia |
| **Tax sector** | `artigianato` |
| **Last renewal** | — |
| **Workers (est.)** | ~350k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - CNA Costruzioni
    - ANAEPA-Confartigianato
    - FIAE-Casartigiani
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
| `7Q` | Quadro — manager with statutory Quadro status (Art. 2095 c.c., L. 190/1985) | € 2,358.36 | — |
| `7` | Senior executive employee / site manager — site manager / senior technical staff | € 2,358.36 | — |
| `6` | Technical employee / worker with supervisory duties — technical staff or team leader | € 2,097.48 | — |
| `5` | Highly specialised worker — highly specialized worker | € 1,748.04 | — |
| `4` | Specialised worker — specialized construction worker | € 1,628.40 | — |
| `3` | First-category worker — skilled worker | € 1,515.12 | — |
| `2` | Second-category worker — semi-skilled worker | € 1,358.35 | — |
| `1` | Common worker — unskilled construction worker | € 1,165.30 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 0.00 |
| `2` | € 9.86 |
| `3` | € 10.78 |
| `4` | € 11.54 |
| `5` | € 12.55 |
| `6` | € 15.92 |
| `7` | € 16.73 |
| `7Q` | € 16.73 |

## Apprenticeship

**standard_gruppo_4** (type: `percentage`)  
Destination levels: `4`  
percentage: 1.00

**standard_gruppi_1_3** (type: `percentage`)  
Destination levels: `3`, `4`, `5`  
percentage: 1.00

**specialistico_1sp** (type: `percentage`)  
Destination levels: `4`, `5`  
percentage: 1.00

**specialistico_2sp** (type: `percentage`)  
Destination levels: `3`, `4`  
percentage: 1.00

**specialistico_3sp** (type: `percentage`)  
Destination levels: `3`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Seniority increment cadence (24 months) and maximum count (5) taken from general CCNL Edilizia Artigianato provisions; F015-specific text not independently confirmed. Level 1 scatto = EUR 0.00 as published in kitech.it.

!!! warning ""
    For blue-collar workers in construction the Cassa Edile / EPR bilateral system provides additional accrual benefits (annual leave, Christmas bonus, seniority) that are separate from INPS seniority increments. These are not modelled; only the tabular seniority increments are implemented.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-05-20 | [↗](https://www.ediltecnico.it/ccnl-edilizia-artigianato-novita-su-campo-di-applicazione-classificazione-personale-e-apprendistato/) |
| — | — | 2025-05-20 | [↗](https://www.ilccnl.it/ccnl-edilizia-artigianato/) |
| — | — | 2026-01-01 | [↗](https://www.kitech.it/ccnl/edilizia-artigianato) |
| — | — | 2023-07-01 | [↗](https://lexplain.it/ccnl-edilizia-artigianato-tabelle-retributive/) |

??? note "Coverage notes"
    Split salary model: paga base (TimeSeries, 4 tranches May 2025/Jan 2026/Jan 2027/Jan 2028) + contingenza (frozen since July 1992 Protocol) + EDR (frozen EUR 10.33 since 1992).
    
    Paga base May 2025 and Jan 2026 verified directly against published salary tables (ilccnl.it, kitech.it). Jan 2026 cross-checked across all 8 levels.
    
    Jan 2027 and Jan 2028 paga base values confirmed from CCNL F015 renewal text (signed 2025-05-20): 4 tranches totalling +178 EUR at parametro 100 — May 2025 +75, Jan 2026 +35, Jan 2027 +35, Jan 2028 +33 (all at parametro 100 / L1). Parametro coefficients (L1=100, L2=115, L3=130, L4=139, L5=150, L6=180, L7=L7Q=205) applied proportionally; all 8 levels for all 4 periods cross-checked against Jan 2026 published figures (ilccnl.it, kitech.it); max deviation < 0.01 EUR. Source: confartigianatomarcatrevigiana.it citing F015 renewal.
    
    Level 7Q has the same paga base as level 7, plus a fixed indennita di funzione of EUR 140.00/month (F015 Art. on Quadri, L. 190/1985). Modelled at order 8 (above level 7 order 7).
    
    Apprenticeship standard professionalizzante Group 4 (Art. 7, Allegato D, renewal May 2025): 36 months / 6 semesters, destination level 4, 74/76/79/86/91/96% per semester, track 'standard_gruppo_4'. Source: ediltecnico.it citing F015 Allegato D.
    
    INPS contribution rates from 2026-artigianato.json (artigianato sector). No Cassa Edile contribution substitution modelled in the INPS rate; employer Cassa Edile contributions are additional and are out of scope.
    
    Layer 3 (overtime, Cassa Edile contributions, holiday/night premiums, accruals managed bilaterally) is out of scope.
    
    Apprenticeship specialistico tracks (Allegato D, verbale 05/09/2023, Art. 9): 1 Sp (54m, livelli 4-5): 0-12=78%, 12-24=80%, 24-36=86%, 36-42=91%, 42-54=96%. 3 Sp (42m, livello 3): 0-12=78%, 12-24=80%, 24-36=86%, 36-42=91%. SIMPLIFICATION: 2 Sp (45m, livelli 3-4): last 8th sem.=3m (not 6m) to reach 45m (the exact boundary of the last period is not published in textual form by any secondary source; total duration of 45m is confirmed). Source: studiodalmaschio.it; fareapprendistato.it; cdltorino.it.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/edilizia-artigianato-cna.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/edilizia-artigianato-cna.py"
```
