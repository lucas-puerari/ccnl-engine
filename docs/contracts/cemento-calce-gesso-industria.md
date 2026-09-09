# CCNL Cemento, Calce e Gesso — Industria (Federbeton)

| | |
|---|---|
| **CNEL code** | `F032` |
| **Sector** | industria del cemento calce e gesso |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~25k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🟢 Verified |

[← Contracts index](index.md)

??? note "Signatories"
    - Federbeton
    - FILLEA-CGIL
    - FILCA-CISL
    - FENEAL-UIL

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
| `AD3` | Area Direttiva 3 — Quadro con responsabilita direttive superiori (Art. 2095 c.c.) | € 2,710.23 | — |
| `AD2` | Area Direttiva 2 — Lavoratori con funzioni direttive di secondo livello | € 2,426.28 | — |
| `AD1` | Area Direttiva 1 — Lavoratori con funzioni direttive di primo livello | € 2,219.77 | — |
| `AC3` | Area Concettuale 3 — Lavoratori con responsabilita di coordinamento complesso | € 2,103.67 | — |
| `AC2` | Area Concettuale 2 — Lavoratori con elevata autonomia e responsabilita funzionale | € 2,026.26 | — |
| `AC1` | Area Concettuale 1 — Lavoratori con funzioni di natura concettuale e autonomia decisionale | € 1,922.99 | — |
| `AS3` | Area Specialistica 3 — Lavoratori altamente specializzati o con funzioni di riferimento | € 1,806.82 | — |
| `AS2` | Area Specialistica 2 — Lavoratori specializzati con autonomia operativa | € 1,729.41 | — |
| `AS1` | Area Specialistica 1 — Lavoratori specializzati con competenze tecniche | € 1,664.89 | — |
| `AQ2` | Area Qualificata 2 — Lavoratori con qualifica professionale specializzata | € 1,561.62 | — |
| `AQ1` | Area Qualificata 1 — Lavoratori con qualifica professionale di base | € 1,497.04 | — |
| `AE1` | Area Esecutiva 1 — Lavoratori addetti a mansioni esecutive semplici | € 1,299.90 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `AE1` | € 7.70 |
| `AQ1` | € 8.30 |
| `AQ2` | € 8.50 |
| `AS1` | € 8.90 |
| `AS2` | € 9.10 |
| `AS3` | € 9.30 |
| `AC1` | € 9.80 |
| `AC2` | € 10.70 |
| `AC3` | € 11.00 |
| `AD1` | € 11.50 |
| `AD2` | € 13.00 |
| `AD3` | € 14.80 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `AQ2`, `AS1`, `AS2`, `AS3`, `AC1`, `AC2`, `AC3`, `AD1`, `AD2`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    APPRENTICESHIP (Art. 25): under_classification model — period 1 at 2 levels below target, period 2 at 1 level below target, period 3 (where applicable) at target level pay. The engine under_classification schema requires a fixed pay_level_code per period for all destination levels; expressing the level-relative structure requires per-destination-level entries with 9 separate apprenticeship objects. Modelled as 100% passthrough for all eligible levels (AQ2 and above); correct for permanent workers.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-05-08 | [↗](https://www.fenealuil.it/wp-content/uploads/2026/02/CEMENTO_STAMPA-CCNL_2025-NO-UGL.pdf) |

??? note "Coverage notes"
    CCNL signed 08/05/2025, valid 01/01/2025-31/12/2027 (Federbeton+FILLEA-CGIL+FILCA-CISL+FENEAL-UIL). Source: official PDF 248 pages.
    
    SPLIT model: paga base (Art. 44) + contingenza frozen Nov 1991 (Art. 45) + EDR 10.33 EUR all levels. Three separate components; only paga base changes at each tranche.
    
    PRE-RENEWAL RECOVERY: a +120 EUR recovery (at param 140 reference) was granted in Dec 2024, prior to the May 2025 renewal. The 31/12/2024 column already includes this recovery. Engine models from this base forward.
    
    TRANCHE AMOUNTS (Art. 44): increases proportional to param indices. Reference param=140 (AS3): +60 EUR (01/10/2025), +60 EUR (01/10/2026), +55 EUR (01/10/2027). All-level amounts confirmed from the PDF.
    
    AREA DIRETTIVA 3 (AD3, Quadro): indennita di funzione +41.32 EUR/month (Art. 15). Modelled as INDENNITA_FUNZIONE fixed allowance, months_per_year=13.
    
    AREA ESECUTIVA 1 (AE1): superminimum collettivo di gruppo +7.75 EUR/month treated as paga base for contractual purposes (Art. 44). Added to paga base values in this file.
    
    SENIORITY (Art. 48): 5 biennali (24-month) scatti. Per-level EUR amounts confirmed from Art. 48 of the PDF.
    
    ADDITIONAL MONTHS: 13 (tredicesima only).
    
    HOURLY DIVISOR: 175.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/cemento-calce-gesso-industria.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/cemento-calce-gesso-industria.py"
```
