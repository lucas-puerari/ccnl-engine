# CCNL Cooperative Sociali (Confcooperative/Legacoop/AGCI)

| | |
|---|---|
| **CNEL code** | `T151` |
| **Sector** | servizi socio-assistenziali |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~380k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Confcooperative-Federsolidarietà
    - Legacoop Sociali
    - AGCI-Solidarietà
    - FP-CGIL
    - CISL-FPS
    - UIL-FPL

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
| `F2Q` | Level F2Q — general director Quadro (with function allowance) | € 2,504.10 | — |
| `F2` | Level F2 — general director / highest responsibility function | € 2,504.10 | — |
| `F1Q` | Level F1Q — area director Quadro (with function allowance) | € 2,192.55 | — |
| `F1` | Level F1 — area director / senior managerial function | € 2,192.55 | — |
| `E2Q` | Level E2Q — senior manager Quadro (with function allowance) | € 1,985.39 | — |
| `E2` | Level E2 — senior manager / service director | € 1,985.39 | — |
| `E1` | Level E1 — junior manager / coordinator | € 1,839.16 | — |
| `D3` | Level D3 — senior technician | € 1,839.16 | — |
| `D2` | Level D2 — qualified technician | € 1,727.83 | — |
| `D1` | Level D1 — junior technician | € 1,637.56 | — |
| `C3` | Level C3 — specialised care worker | € 1,637.56 | — |
| `C2` | Level C2 — qualified care worker | € 1,591.06 | — |
| `C1` | Level C1 — basic care worker (OSS) | € 1,545.21 | — |
| `B` | Level B — qualified auxiliary worker | € 1,436.78 | — |
| `A2` | Level A2 — basic auxiliary worker | € 1,372.53 | — |
| `A1` | Level A1 — generic entry-level worker | € 1,359.88 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `A1` | € 11.62 |
| `A2` | € 13.43 |
| `B` | € 16.27 |
| `C1` | € 18.59 |
| `C2` | € 19.63 |
| `C3` | € 20.66 |
| `D1` | € 20.66 |
| `D2` | € 23.24 |
| `D3` | € 26.86 |
| `E1` | € 26.86 |
| `E2` | € 31.50 |
| `E2Q` | € 31.50 |
| `F1` | € 39.51 |
| `F1Q` | € 39.51 |
| `F2` | € 46.48 |
| `F2Q` | € 46.48 |

## Apprenticeship

**professionalizzante_18m** (type: `percentage`)  
Destination levels: `A2`  
percentage: 1.00

**professionalizzante_24m** (type: `percentage`)  
Destination levels: `B`, `C1`, `C2`, `C3`  
percentage: 1.00

**professionalizzante_36m** (type: `percentage`)  
Destination levels: `D1`, `D2`, `D3`, `E1`, `E2`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    INPS: uses 2026-terziario.json (same tax_sector as CCNL Commercio Confcommercio). The social cooperatives sector does not have a separate employer INPS rate verified from a primary circular; type-B social cooperatives may apply concessions under L. 381/1991 not modelled in this file.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-01-26 | [↗](https://www.lexplain.it/tabelle-retributive-ccnl-cooperative-sociali-2024-2025-e-anni-precedenti/) |

??? note "Coverage notes"
    CONSOLIDATED MINIMUMS: the base_salary values are the monthly consolidated tabular minimums (base pay + contingency + EDR included), as published by lexplain.it. Hourly divisor 165 (CCNL art. 75, 38-hour week). Back-calculation check: A1 October 2025 = 1359.88 / 165 = EUR 8.24/h; C1 = 1545.21 / 165 = EUR 9.37/h; F2 = 2504.10 / 165 = EUR 15.17/h — consistent with the hourly rates published by lexplain.it.
    
    QUADRO LEVELS: levels E2Q, F1Q, F2Q are modelled as separate levels with fixed_allowances (function allowance EUR 77.47, EUR 154.94, EUR 232.41/month respectively). The base_salary is identical to the corresponding non-Q level; the allowance is fixed and unchanged across tranches. Seniority increments for Q levels carry the same amount as the corresponding base level.
    
    ADDITIONAL MONTHS: 13 until 31 December 2024 (thirteenth month only). From 1 January 2025: 13.5 (thirteenth month + fourteenth month equal to 50% of one monthly salary, paid in June, introduced by the 26 January 2024 renewal).
    
    TRANCHES: February 2024 (first), October 2024 (second), October 2025 (third and last). Renewal signed on 26 January 2024. No pre-February-2024 tables modelled.
    
    LEVELS WITH THE SAME BASE: C3 and D1 have identical minimums at each tranche (orders 6/7). D3 and E1 are identical (orders 9/10). Q levels (E2Q/F1Q/F2Q) have the same base as the non-Q level but the next order: the engine allows equal salaries between adjacent levels.
    
    SENIORITY INCREMENTS: biennial (every 24 months), maximum 5 increments. Fixed amounts per level from the CCNL seniority table (source: ccnlcooperative.it, art. 80). C3 and D1 have the same amount (EUR 20.66); D3 and E1 have the same amount (EUR 26.86).
    
    APPRENTICESHIP (professionalizzante) under Art. 28 renewal 05/03/2024: 3 duration tracks by category: category A (dest=A2) 18m [0-9m=85%,9-18m=90%]; category B/C (dest=B,C1,C2,C3) 24m [0-12m=85%,12-24m=90%]; category D/E (dest=D1,D2,D3,E1,E2) 36m [0-18m=85%,18-36m=90%]. A1 and F/Q levels not eligible. Special: OSS in socio-sanitario reduced to 18m. Source: Art. 28 ccnlcooperative.it (consolidated text 2025, high confidence).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/cooperative-sociali.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/cooperative-sociali.py"
```
