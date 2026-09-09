# CCNL Grafica e Editoria Industria (AIEG-Acigraf)

| | |
|---|---|
| **CNEL code** | `G011` |
| **Sector** | grafica-editoria |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~70k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - AIEG
    - Acigraf
    - SLC-CGIL
    - Fistel-CISL
    - Uilcom-UIL

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
| `Q` | Q — quadro, highest technical or managerial responsibility | € 2,882.11 | — |
| `AS` | AS — special grade, senior technical-editorial manager | € 2,871.24 | — |
| `A` | A — 6th category worker, production manager | € 2,504.43 | — |
| `B1S` | B1S — upper 5th category worker, technical department head | € 2,425.41 | — |
| `B1` | B1 — 5th category worker, highly qualified technician | € 2,371.11 | — |
| `B2` | B2 — upper 4th category worker, complex equipment operator | € 2,252.04 | — |
| `B3` | B3 — 4th category worker, expert graphic technician | € 2,126.85 | — |
| `C1` | C1 — 3rd category worker, specialist graphic technician | € 2,002.49 | — |
| `C2` | C2 — 3rd category worker, general graphic technician | € 1,827.37 | — |
| `D1` | D1 — upper 2nd category worker, qualified operator | € 1,702.44 | — |
| `D2` | D2 — 2nd category worker, machine operator | € 1,595.11 | — |
| `E` | E — 1st category worker, simple and routine tasks | € 1,460.85 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 16.01 |
| `AS` | € 16.01 |
| `A` | € 16.01 |
| `B1S` | € 14.46 |
| `B1` | € 14.46 |
| `B2` | € 13.94 |
| `B3` | € 13.43 |
| `C1` | € 12.91 |
| `C2` | € 12.39 |
| `D1` | € 11.88 |
| `D2` | € 11.36 |
| `E` | € 10.33 |

## Apprenticeship

**triennale** (type: `percentage`)  
Destination levels: `C2`, `C1`, `B3`, `B2`, `B1`, `B1S`, `A`, `AS`, `Q`  
percentage: 1.00

**biennale** (type: `percentage`)  
Destination levels: `D2`, `D1`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    HOURLY DIVISOR: 173. SIMPLIFICATION: no official hourly rate table recovered for G011. The value 173 is derived from 40h/week standard (40×52/12=173.33→173). The CCNL uses divisore convenzionale 26 for daily calculations; the hourly divisor is inferred from the weekly-hours convention. If the actual contractual hours differ (e.g., 37.5h/week→163), divisore must be corrected.

!!! warning ""
    SENIORITY: 5 scatti biennali (24 months), valid from kitech.it July 2026. SIMPLIFICATION: pre-July 2026 scatto amounts not modelled (prior rinnovo values not recovered). The engine uses July 2026 amounts for all periods — impact negligible for current-date calculations.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-12-20 | [↗](https://www.lexplain.it/tabelle-retributive-grafici-editoriali-industria-2024-2026/) |
| — | — | 2026-07-01 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=156) |

??? note "Coverage notes"
    SALARY MODEL: the CCNL Grafica e Editoria Industria (G011) uses a split model with separate paga base (TEM), contingenza (frozen since 1992 per Prot. 31/07/1992), and EDR (10.33 EUR, all levels). The base_salary values in this file are the TOTAL (paga base + contingenza + EDR) per level and tranche, sourced from the official lexplain.it table (all 5 tranches) and kitech.it (July 2026 breakdown). Modeling the total as base_salary produces the same gross_monthly as the split representation. fixed_allowances is empty for all levels (no additional fixed components).
    
    CONGLOBATED CHECK: inter-level increase ratios are stable across all 5 tranches (e.g., Q/E = 1.937, C1/E = 1.357 at all dates), confirming a single parametric coefficient system. Contingenza is frozen per level (E=512.87, Q=539.99); EDR=10.33 uniform. Total values from lexplain cross-check with kitech July 2026 breakdown to within ±0.03 EUR (rounding difference).
    
    TRANCHE DATES: 01.03.2024, 01.09.2024, 01.05.2025, 01.10.2025, 01.07.2026. Values from rinnovo 20.12.2024 (retroactive application). Fonte: lexplain.it (5 tranches, all 12 Grafici levels) and kitech.it (componenti breakdown July 2026).
    
    SECTOR SCOPE: models the GRAFICI (graphics workers) sector only (12 levels: E, D2, D1, C2, C1, B3, B2, B1, B1S, A, AS, Q). The EDITORI (publishers) sector (9 levels: 8°-0°/Q) with slightly different pay tables is NOT modelled. Coverage marked as layer_1=implemented for Grafici only.
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Confirmed by secondary source (lavoro-economia.it / contratticcnl.it). A quattordicesima is not provided for by CCNL G011 Grafici.
    
    INPS: reuses 2026-industria.json (Confindustria). AIEG/Acigraf are members of Confindustria; CIGO applicable for the graphic arts industry sector (D.Lgs. 148/2015).
    
    APPRENTICESHIP (Art. 26e, Type 2, CCNL 19/01/2021, p.42; confirmed in force in the 20.12.2024 renewal): 'triennale' track (groups C,B,A,Q → levels C2,C1,B3,B2,B1,B1S,A,AS,Q): 36 months / 6 semesters, 70/75/80/85/90/95% then 100%. 'biennale' track (group D → levels D2,D1): 24 months / 6 four-month periods (4 months each), 70/75/80/85/90/95% then 100%. Level E not listed as an apprenticeship destination. EDITORI sector not modelled in this JSON. Source: fistelcisl.it PDF CCNL grafici-editoriali.pdf (p. 41-42).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/grafica-editoria-aieg.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/grafica-editoria-aieg.py"
```
