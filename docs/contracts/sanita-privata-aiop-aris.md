# CCNL Case di Cura Private - Personale Non Medico (AIOP/ARIS)

| | |
|---|---|
| **CNEL code** | `T011` |
| **Sector** | Sanità privata |
| **Tax sector** | `terziario` |
| **Last renewal** | 2020-10-08 |
| **Workers (est.)** | ~150k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - AIOP
    - ARIS
    - FILCAMS CGIL
    - FP CGIL
    - FISASCAT CISL
    - CISL FP
    - UILTuCS
    - UILFPL
    - FIALS
    - CISAL SANITÀ

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
| `E2` | Categoria E — progressione orizzontale 2 | € 3,554.39 | — |
| `E1` | Categoria E — progressione orizzontale 1 | € 2,936.33 | — |
| `DS4` | Categoria DS — progressione orizzontale 4 | € 2,418.05 | — |
| `E` | Categoria E — quadro / specialista | € 2,410.22 | — |
| `DS3` | Categoria DS — progressione orizzontale 3 | € 2,345.38 | — |
| `DS2` | Categoria DS — progressione orizzontale 2 | € 2,261.56 | — |
| `D4` | Categoria D — progressione orizzontale 4 | € 2,209.98 | — |
| `DS1` | Categoria DS — progressione orizzontale 1 | € 2,180.26 | — |
| `D3` | Categoria D — progressione orizzontale 3 | € 2,147.12 | — |
| `DS` | Categoria DS — coordinatore | € 2,101.08 | — |
| `D2` | Categoria D — progressione orizzontale 2 | € 2,084.77 | — |
| `C4` | Categoria C — progressione orizzontale 4 | € 2,076.38 | — |
| `D1` | Categoria D — progressione orizzontale 1 | € 2,022.94 | — |
| `C3` | Categoria C — progressione orizzontale 3 | € 1,984.10 | — |
| `D` | Categoria D — professionista sanitario | € 1,953.87 | — |
| `C2` | Categoria C — progressione orizzontale 2 | € 1,921.25 | — |
| `C1` | Categoria C — progressione orizzontale 1 | € 1,857.14 | — |
| `C` | Categoria C — operatore qualificato | € 1,803.61 | — |
| `B4` | Categoria B — progressione orizzontale 4 | € 1,733.54 | — |
| `B3` | Categoria B — progressione orizzontale 3 | € 1,697.76 | — |
| `B2` | Categoria B — progressione orizzontale 2 | € 1,669.36 | — |
| `B1` | Categoria B — progressione orizzontale 1 | € 1,624.54 | — |
| `A4` | Categoria A — progressione orizzontale 4 | € 1,592.19 | — |
| `B` | Categoria B — operatore tecnico-pratico | € 1,579.86 | — |
| `A3` | Categoria A — progressione orizzontale 3 | € 1,566.67 | — |
| `A2` | Categoria A — progressione orizzontale 2 | € 1,544.35 | — |
| `A1` | Categoria A — progressione orizzontale 1 | € 1,506.44 | — |
| `A` | Categoria A — ausiliario generico | € 1,467.45 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**Apprendistato professionalizzante 36 mesi** (type: `percentage`)  
Destination levels: `A`, `B`, `C`, `D`  
percentage: 0.90

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    hourly_divisor=156 (Art. 58: paga giornaliera=monthly/26, oraria=giornaliera/6 for 36h/week). Levels D4, DS4, E, E1, E2 work 38h/week per Art. 18 (oraria=giornaliera/6.33, exact divisor≈164.6), modelled as 156 uniformly.

!!! warning ""
    Apprenticeship (Art. 23 §14, Art. 23 §2): destination levels are the four category entry positions A, B, C, D only. Horizontal-progression steps (A1-A4, B1-B4, C1-C4, D1-D4) are not apprenticeship destinations. DS and E categories excluded per Art. 23 §2. OSS and Albo-registered health professions excluded per Art. 23 §2 but per-qualification restriction not modellable at level granularity.

!!! warning ""
    INPS: uses 2026-terziario.json as proxy. Private healthcare (AIOP/ARIS) is classified in the terziario sector for INPS purposes; verify against INPS Circolare n. 6/2026.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2020-10-08 | [↗](https://www.fondazionerimed.eu/wp-content/uploads/2023/12/CCNL-CASE-DI-CURA-PRIVATE-08.10.2020.pdf) |
| — | — | — | [↗](https://www.contratticcnl.it/ccnl/t011/) |

??? note "Coverage notes"
    CCNL signed 2020-10-08; nominally covers 2016-2018 (Art. 4). Applied in ultrattività from 2019 onwards. Salary tables (Tabella 1) effective 2020-07-01 per Art. 51. No renewal signed as of 2026-09-03.
    
    Salary values are conglobated: EADR incorporated into tabellare from 2020-07-01 per Art. 55. Back-calculation: A 1467.45×13=19076.85 ✓; C4 2076.38×13=26992.94 ✓; DS4 2418.05×13=31434.65 ✓.
    
    28 levels (A, A1–A4, B, B1–B4, C, C1–C4, D, D1–D4, DS, DS1–DS4, E, E1, E2). Order assigned by 2020-07-01 salary because professional families A/B/C/D/DS/E have overlapping salary ranges — categories are not a single hierarchy. A4 (order 6) is paid above B (order 5) per Tabella 1. Horizontal progressions within each category are modelled as static levels per Art. 48; the engine does not auto-advance a worker's level after the contractual service threshold.
    
    Retribuzione individuale di anzianità frozen at 1993-12-31 per Art. 56 (no new seniority accruals). Modelled as seniority_increments.maximum_count=0.
    
    CCNL covers ospedalieri, IRCCS, riabilitazione (AIOP/ARIS members). Does not apply to RSA governed by separate AIOP RSA or Uneba agreements.
    
    CCNL applied in ultrattività; Decreto Lavoro 2026 introduced a statutory 30% IPCA auto-adjustment if no renewal within 12 months of expiry. If triggered, legally applicable 2026 minimums may exceed the 2020 Tabella 1 values modelled here. Engine models contractual tables only.
    
    CNEL code T011 verified at https://www.contratticcnl.it/ccnl/t011/ (146585 employees, ARIS/AIOP, ATECO 86).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/sanita-privata-aiop-aris.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/sanita-privata-aiop-aris.py"
```
