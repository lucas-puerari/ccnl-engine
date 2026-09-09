# CCNL Ceramica Industria (Confindustria-Assopiastrelle)

| | |
|---|---|
| **CNEL code** | `B122` |
| **Sector** | ceramica |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~23k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Confindustria Ceramica
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
| `A` | Level A — quadri and workers with maximum autonomy and managerial responsibility | € 2,793.96 | — |
| `B1` | Level B1 — workers with high professional skill or specialisation and full IPO | € 2,515.17 | — |
| `B2` | Level B2 — workers with high professional skill or specialisation, without IPO | € 2,515.17 | — |
| `C1` | Level C1 — workers with basic technical or managerial responsibility and full IPO | € 2,194.75 | — |
| `C2` | Level C2 — workers with basic technical or managerial responsibility and reduced IPO | € 2,194.75 | — |
| `C3` | Level C3 — workers with basic technical or managerial responsibility, without IPO | € 2,194.75 | — |
| `D1` | Level D1 — workers with medium-complexity operative functions and full IPO | € 1,972.36 | — |
| `D2` | Level D2 — workers with medium-complexity operative functions and reduced IPO | € 1,972.36 | — |
| `D3` | Level D3 — workers with medium-complexity operative functions, without IPO | € 1,972.36 | — |
| `E1` | Level E1 — workers with executive duties and position IPO allowance (CCNL IPO art.) | € 1,783.43 | — |
| `E2` | Level E2 — workers with executive duties, standardised operative tasks | € 1,783.43 | — |
| `F` | Level F — entry-level workers performing basic operations | € 1,666.45 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 19.63 |
| `B1` | € 17.56 |
| `B2` | € 17.56 |
| `C1` | € 12.91 |
| `C2` | € 12.91 |
| `C3` | € 12.91 |
| `D1` | € 12.14 |
| `D2` | € 12.14 |
| `D3` | € 12.14 |
| `E1` | € 8.78 |
| `E2` | € 8.78 |
| `F` | € 7.75 |

## Apprenticeship

**qualificazione_professionale** (type: `percentage`)  
Destination levels: `A`, `B1`, `B2`, `C1`, `C2`, `C3`, `D1`, `D2`, `D3`, `E1`, `E2`, `F`  
percentage: 0.95

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SENIORITY: 5 biennial increments (cadence 24 months, maximum 5). Amounts from kitech.it (B122, primary levels). Amounts for B2, C2, C3, D2, D3, E2 assumed equal to B1, C1, D1, E1 respectively (same tabular minimum, standard practice for CCNL ceramica); not confirmed from a primary source.

!!! warning ""
    APPRENTICESHIP: 95% percentage on destination (base + IPO). Percentage from pre-2024-renewal aggregator sources; the 22/07/2024 renewal does not appear to have changed the apprenticeship structure according to the same sources. The main CCNL PDF is scanned and cannot be extracted. Maximum legal duration (D.Lgs 81/2015 Art. 44).

!!! warning ""
    APPRENTICE INCREMENT: apprentice_amount=null. No confirmation from any accessible primary source for B122 industria. The EUR 6 value from Jan 2025 is confirmed only for CCNL Ceramica Artigianato (V751), not for B122.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-07-22 | [↗](https://www.filctemcgil.it/images/download/CONTRATTI/ceramica_piastrelle/240722_CERAMICHE_RINNOVO_1LUGLIO2023_30GIUGNO2027_TABELLE.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobated tabular minimum (single base pay absorbing contingency and EDR) + IPO (Organisational Position Allowance) as a separate fixed_allowance for the levels that receive it. Source: official FILCTEM-CGIL tables (PDF signed 22/07/2024, PIASTRELLE sub-sector). REFRACTORY MATERIALS has tables identical to PIASTRELLE.
    
    HOURLY_DIVISOR: 173 hours/month (40h weeks × 52/12 = 173.33 rounded). Verified on lavoro-economia.it for CCNL B122.
    
    SUB-SECTORS: CCNL B122 covers Tiles (porcelain and stoneware), Refractory Materials, Sanitary Ceramics and Tableware, and Artistic and Traditional Ceramics. This file models the PIASTRELLE sub-sector (and REFRATTARI, which has identical tables). Sanitary Ceramics has a different pay structure (significantly higher IPO) and is not modelled here.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/ceramica-industria-confindustria.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/ceramica-industria-confindustria.py"
```
