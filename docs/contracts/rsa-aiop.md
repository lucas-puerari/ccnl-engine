# CCNL RSA e Strutture Residenziali Socio-Assistenziali (AIOP)

| | |
|---|---|
| **CNEL code** | `T091` |
| **Sector** | residenze sanitarie assistenziali — personale non medico |
| **Tax sector** | `terziario` |
| **Last renewal** | 2012-03-22 |
| **Workers (est.)** | ~17k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - AIOP
    - FP-CGIL
    - CISL-FP
    - UIL-FPL
    - UGL Sanità
    - FISMIC-CONFSAL
    - FIALS

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
| `H` | Livello H | € 3,294.68 | — |
| `G` | Livello G | € 2,749.49 | — |
| `F` | Livello F | € 2,095.50 | — |
| `E3` | Livello E3 | € 1,806.00 | — |
| `E2` | Livello E2 | € 1,746.00 | — |
| `E1` | Livello E1 | € 1,550.56 | — |
| `D3` | Livello D3 | € 1,496.06 | — |
| `D2` | Livello D2 | € 1,463.33 | — |
| `D1` | Livello D1 | € 1,419.80 | — |
| `C` | Livello C | € 1,419.80 | — |
| `B` | Livello B | € 1,311.68 | — |
| `A` | Livello A | € 1,223.57 | — |

## Seniority increments

**Cadence:** every 60 months  
**Maximum:** 1 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 40.00 |
| `B` | € 40.00 |
| `C` | € 40.00 |
| `D1` | € 40.00 |
| `D2` | € 40.00 |
| `D3` | € 40.00 |
| `E1` | € 40.00 |
| `E2` | € 40.00 |
| `E3` | € 40.00 |
| `F` | € 0.00 |
| `G` | € 0.00 |
| `H` | € 0.00 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `A`, `B`, `C`, `D1`, `D2`, `D3`, `E1`, `E2`, `E3`, `F`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Seniority: contract uses a flat EUR 40/month bonus at 5 years of service (levels A-E3 only; F/G/H excluded). Modeled as cadence_months=60, maximum_count=1. The Oct 2023 'premio di anzianita' (EUR 40 for 10+ year workers) is a one-time payment and is out_of_scope.

!!! warning ""
    Apprenticeship: contract specifies sotto-inquadramento up to 2 levels below destination (levels A-F eligible, 36 months). Engine schema requires a static pay_level_code; modeled as 100% passthrough.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2012-03-22 | [↗](https://acopnazionale.it/wp-content/uploads/2022/03/ccnl-rsa-aiop-2012.pdf) |
| — | — | 2023-10-03 | [↗](https://www.frgeditore.it/images/cop/pdf/titolo-6/ccnl/rsa/63_accordo_3-10-2023_aiop.pdf) |

??? note "Coverage notes"
    CCNL T091 — AIOP RSA. Conglobated. 12 levels: A-B-C-D1-D2-D3-E1-E2-E3-F-G-H. Divisor 165, 13 months. Original 2012 contract, updated by accordo ponte Oct 2023.
    
    Accordo ponte (Oct 2023) expired June 2024. Contract applied in ultrattività pending renewal. Oct 2023 table modeled as current (valid_until null).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/rsa-aiop.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/rsa-aiop.py"
```
