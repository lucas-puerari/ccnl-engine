# CCNL Dipendenti delle Farmacie Municipalizzate (ASSOFARM)

| | |
|---|---|
| **CNEL code** | `H124` |
| **Sector** | Farmacie municipalizzate e partecipate da enti locali |
| **Tax sector** | `terziario` |
| **Last renewal** | 2022-07-07 |
| **Workers (est.)** | ~6k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ASSOFARM
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTuCS

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
| `1Q` | 1o livello Q - Direttore responsabile e area manager | € 2,456.91 | — |
| `1S` | 1o livello super - Direttore responsabile con funzioni direttive | € 2,372.46 | — |
| `1C` | 1o livello C - Farmacista collaboratore con funzioni speciali | € 2,266.37 | — |
| `1_12` | 1o livello + 12 anni - Farmacista collaboratore con 12+ anni di servizio | € 2,109.97 | — |
| `1_2` | 1o livello + 2 anni - Farmacista collaboratore con 24+ mesi di servizio | € 2,109.97 | — |
| `1` | 1o livello - Farmacista collaboratore | € 2,109.97 | — |
| `2` | 2o livello - Lavoratori con funzioni di coordinamento o tecnico-specialistiche | € 1,872.16 | — |
| `3` | 3o livello - Lavoratori con conoscenze tecnico-pratiche qualificate | € 1,777.29 | — |
| `4` | 4o livello - Lavoratori con compiti esecutivi e conoscenze tecnico-pratiche | € 1,652.61 | — |
| `5` | 5o livello - Lavoratori qualificati con normali conoscenze operative | € 1,522.17 | — |
| `6` | 6o livello - Lavoratori con mansioni di pulizia e operazioni semplici | € 1,421.48 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 15 increments

| Level | Increment (monthly) |
|---|---:|
| `1Q` | € 26.50 |
| `1S` | € 25.82 |
| `1C` | € 25.31 |
| `1_12` | € 25.31 |
| `1_2` | € 25.31 |
| `1` | € 25.31 |
| `2` | € 23.24 |
| `3` | € 22.72 |
| `4` | € 20.66 |
| `5` | € 20.14 |
| `6` | € 19.63 |

## Apprenticeship

**farmacista_collaboratore** (type: `under_classification`)  
Destination levels: `1`

**professionalizzante** (type: `under_classification`)  
Destination levels: `4`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    INPS RATES. Terziario proxy used. ASSOFARM entities operate as aziende speciali or società di gestione farmacia (private-law entities under municipal control); the contract is registered CNEL H124 and negotiated by UGL Terziario — standard private-sector INPS regime (terziario) is the expected classification. Note: CCNL text references "INPS Gestione ex INPDAP" in benefit provisions, suggesting legacy workers transferred from public-sector management may retain the ex-INPDAP pension regime — contribution rates for those workers differ. No sector-specific INPS circular identified; kitech.it does not list a dedicated contribution table for farmacie municipalizzate. Simplification retained.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2022-07-07 | [↗](https://www.assofarm.it/wp-content/uploads/2024/12/CCNL2022.2024.signedcorrect.pdf) |

??? note "Coverage notes"
    Salary model: conglobated. Allegato B shows unified retribuzione di base with no separate contingenza or EDR columns. Back-calculation: L1=2109.97/173=12.20 EUR/h, L3=1777.29/173=10.27 EUR/h, L6=1421.48/173=8.22 EUR/h (all consistent with divisor 173).
    
    Hourly divisor 173: Art. 18 explicit: 'La quota oraria di retribuzione si ottiene dividendo la retribuzione mensile per 173'.
    
    Additional months: 14. Art. 20 explicit: quattordicesima (luglio) + tredicesima (dicembre).
    
    IQ (Indennita Quadri): Allegato C, effective 01/07/2022. Levels 1Q=160, 1S=150, 1C=145 EUR/month.
    
    IS (Indennita Speciale): Art. 19bis + Allegato A. Level 1+12anni=130, Level 1+2anni=100 EUR/month. Unchanged in 2022 renewal (Allegato C covers only IQ increments; Art. 19bis refers to Tabella A 2015 values).
    
    Seniority: 15 scatti biennali per Allegato E, decorrenza 1 gennaio 2014.
    
    Apprenticeship: Allegato F, under-classification. Farmacista collaboratore stays at Primo livello for all 36 months (levels_below=0). Non-pharmacist roles (Coadiutore, Capo settore, Addetto amministrativo): months 1-12 at Sesto, months 13-36 at Quinto, exit Quarto.
    
    Contract valid 07/07/2022-31/12/2024, ultrattivo since 01/01/2025 (no successor deposited at CNEL as of 2026-09-05). Third tranche (01/07/2024) modelled open-ended.
    
    Headcount: 6,389 workers, 335 employers (ASSOFARM primary source).
    
    Levels 1_12 and 1_2 (Farmacista Collaboratore with 12+ or 2+ years continuous service) are automatic time-in-grade progressions under Art. 19bis. Engine cannot model auto-advancement; implemented as static level codes distinguishable by IS allowance amount (1_12=130, 1_2=100 EUR/month). Structural engine limitation — correct payroll calculation requires knowing the worker's actual time-in-grade.
    
    Function and Tech-Prof allowances shown in kitech for L2/L3/quadri sub-levels are EXCLUDED. They appear in no allegato of the signed CCNL; Art. 17 defines retribuzione di base as Tabelle A+B only. Verification: 1Q base+IQ=2456.91+160=2616.91 vs kitech 2758.68; delta 141.77 = sum of the two extra kitech lines — confirming they are historical/personal elements outside the contractual minimum. Exclusion is correct.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/farmacie-municipalizzate-assofarm.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/farmacie-municipalizzate-assofarm.py"
```
