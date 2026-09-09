# CCNL Edilizia — Industria (ANCE)

| | |
|---|---|
| **CNEL code** | `F012` |
| **Sector** | edilizia |
| **Tax sector** | `edilizia` |
| **Last renewal** | — |
| **Workers (est.)** | ~550k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ANCE
    - Legacoop Costruzioni
    - Confcooperative Lavoro e Servizi
    - AGCI
    - Fillea-CGIL
    - Filca-Cisl
    - Feneal-Uil

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
| `7` | Quadro / 1st-category employee — managerial function, sector responsibility | € 2,878.86 | — |
| `6` | Senior technical / administrative employee — surveyor, draughtsperson, chief accountant | € 2,641.19 | — |
| `5` | Ordinary clerical employee — routine tasks, basic accounting | € 2,284.70 | — |
| `4` | 4th-category worker — gang leader / highly specialised worker | € 2,165.89 | — |
| `3` | Specialised worker — bricklayer, carpenter, ironworker, tiler | € 2,047.05 | — |
| `2` | Qualified worker — directed construction work, use of trade tools | € 1,892.57 | — |
| `1` | Common worker — general labourer, material handling | € 1,690.56 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 8.22 |
| `2` | € 8.22 |
| `3` | € 8.99 |
| `4` | € 9.62 |
| `5` | € 10.46 |
| `6` | € 12.85 |
| `7` | € 13.94 |

## Apprenticeship

**standard** (type: `percentage`)  
Destination levels: `2`, `3`, `4`, `5`, `6`, `7`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    CASSA EDILE: the Cassa Edile manages for blue-collar workers: annual leave (8.5%), Christmas bonus (10%), TFR, APE (Professional Building Seniority). None of these components is modelled by the engine. Consequences: (1) employer_cost_annual is underestimated by ~18.5% of gross for blue-collar workers; (2) tfr_annual is calculated using the standard INPS formula (÷ 13.5) while for blue-collar workers the TFR flows to the Cassa Edile; (3) net_monthly is correct (Cassa Edile does not affect the employee's payslip).

!!! warning ""
    BLUE-COLLAR SENIORITY: for blue-collar workers (levels 1-4), the ANCE CCNL provides APE (Professional Building Seniority) through the Cassa Edile instead of standard seniority increments. The engine models the tabular increment amounts for all levels (L1-L2: EUR 8.22, L3: EUR 8.99, L4: EUR 9.62 biennial) as an approximation; the real APE mechanism is managed by the Cassa Edile and is not modelled.

!!! warning ""
    EVR: the Variable Pay Element (EVR) is a variable provincial/company bonus. It is not modelled (varies by province and year).

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-02-21 | [↗](https://www.idealista.it/news/finanza/lavoro/2025/07/10/251640-ccnl-edilizia-livelli-inquadramento-2025-e-tutte-le-novita) |
| — | — | 2025-02-21 | [↗](https://leggeinchiaro.it/ccnl-edilizia-industria-tabelle-retributive/) |
| — | — | — | [↗](https://www.businessonline.it/articoli/scatti-anzianita-contratto-edile-tabella-ogni-quanto-avvengono-e-di-quanto-aumenta-stipendio.html) |

??? note "Coverage notes"
    RENEWAL: CCNL signed on 21 February 2025, effective 1/2/2025-30/6/2028. Three pay increases: 1st from 1/2/2025, 2nd from 1/3/2026, 3rd from 1/3/2027.
    
    CONSOLIDATED MINIMUMS: the base_salary values are the monthly consolidated tabular minimums (base pay + contingency + EDR). Feb 2025 breakdown for reference: L1 = 1067.36 + 512.87 + 10.33; L2 = 1248.81 + 516.43 + 10.33; L3 = 1387.56 + 519.16 + 10.33; L4 = 1494.31 + 521.25 + 10.33; L5 = 1601.02 + 523.35 + 10.33; L6 = 1921.23 + 529.63 + 10.33; L7 = 2134.71 + 533.82 + 10.33. fixed_allowances is empty for all levels. Verification: L1 Feb 2025 = 1590.56 / 173 = EUR 9.19/h (matches the hourly rate on idealista.it).
    
    DUAL STRUCTURE: the CCNL distinguishes blue-collar workers (levels 1-4, paid hourly) and white-collar/managerial staff (levels 5-7, paid monthly). The engine works with monthly values only. Monthly minimums for blue-collar workers are the official published tabular values (hourly rate × 173 hours already incorporated in the monthly minimums). hourly_divisor=173 (40h/week × 52/12 ≈ 173.33, rounded to 173 as per the official hourly table).
    
    ADDITIONAL_MONTHS: 13 monthly payments (Christmas bonus). The 14th monthly payment is not provided for in the construction industry CCNL. For blue-collar workers the Christmas bonus is paid through the Cassa Edile — the engine includes it in gross_annual via the ×13 multiplier as an approximation.
    
    INPS: uses 2026-edilizia.json with proxy rates (kitech.it). Employee 9.19%, employer tiers 28.46%/29.06%/29.50%. Cassa Edile (~18.5%) is separate — not included.
    
    APPRENTICESHIP (Art. 92 CCNL, as reformed by CNCE notice n.660 of 04/04/2019): percentage type, single scheme for all levels 2-7 (level 1 excluded). 6 semesters = 36 months: 72%/72%/78%/78%/85%/90% then 100%. The old under-classification system was explicitly abolished from 01/04/2019. Craft/artistic figures: 48 months (8 semesters, semesters 7-8 at 90%); not modelled separately (no specific level code available). Structure confirmed unchanged in the 21/02/2025 renewal. Source: CNCE notice n.660/2019 (cassaedilevarese.it); cassaedilesavona.com Art.92; BibLus/ANCE dossier.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/edilizia-ance.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/edilizia-ance.py"
```
