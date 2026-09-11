# CCNL Lapidei — Industria (Confindustria Marmomacchine/ANEPLA)

| | |
|---|---|
| **CNEL code** | `F041` |
| **Sector** | industria lapidea e delle cave |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~18k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🟢 Verified |

[← Contracts index](index.md)

??? note "Signatories"
    - Confindustria Marmomacchine
    - ANEPLA
    - FENEAL-UIL
    - FILCA-CISL
    - FILLEA-CGIL

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
| `AS` | Livello AS — A Super: lavoratori con responsabilita direttive di alto livello | € 2,562.44 | — |
| `A` | Livello A — Lavoratori con elevata autonomia e responsabilita gestionale | € 2,357.34 | — |
| `B` | Livello B — Lavoratori altamente specializzati con coordinamento operativo | € 1,921.76 | — |
| `CS` | Livello CS — C Super: lavoratori specializzati con responsabilita di processo | € 1,845.14 | — |
| `C` | Livello C — Livello di riferimento parametrico (lavoratori con qualifiche tecniche) | € 1,742.64 | — |
| `D` | Livello D — Lavoratori specializzati con autonomia operativa | € 1,642.89 | — |
| `E` | Livello E — Lavoratori qualificati con mansioni esecutive | € 1,514.52 | — |
| `F` | Livello F — Lavoratori addetti a mansioni semplici (+ superminimum collettivo 7.75 EUR) | € 1,290.23 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `F` | € 6.65 |
| `E` | € 7.69 |
| `D` | € 8.31 |
| `C` | € 8.82 |
| `CS` | € 9.45 |
| `B` | € 9.80 |
| `A` | € 11.97 |
| `AS` | € 13.01 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `F`, `E`, `D`, `C`, `CS`, `B`, `A`, `AS`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    PRE-31/12/2022 HISTORY: the 2022-2025 CCNL is retroactively valid from 01/04/2022. Values for April 2022 through November 2022 are not modelled (data not retrieved from public sources). Engine history starts at 31/12/2022.

!!! warning ""
    APPRENTICESHIP: 2022 CCNL Art. 3d changed system from sotto-inquadramento to percentage ('calcolate in percentuale...come da allegata tabella'). Pre-2022 system confirmed from full CCNL 2008 text (integrating Accordo 15/03/2006): 2 levels below destination for first half of apprenticeship, 1 level below for second half, no seniority increments accrued. Post-2022 percentage values from scanned allegata tabella not extractable (OCR-confirmed: image-only PDF). 2025-2028 rinnovo (12-page OCR) does not modify apprenticeship. Modelled as 1.00 passthrough pending actual 2022+ percentage values.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2022-11-24 | [↗](https://www.consulenza.it/Contenuti/Scadenziario/Scadenza/19851/lapidei-industria) |
| — | — | 2025-07-15 | [↗](https://www.cdltorino.it/ccnl-lapidei-industria-con-ladeguamento-ipca-in-arrivo-nuovi-minimi/) |

??? note "Coverage notes"
    CCNL 2022-2025 signed 24/11/2022 (valid 01/04/2022-31/03/2025). CCNL 2025-2028 signed 15/07/2025 (valid 01/04/2025-31/03/2028). Signatories: Confindustria Marmomacchine+ANEPLA+FENEAL-UIL+FILCA-CISL+FILLEA-CGIL.
    
    SPLIT model: paga base + contingenza frozen Nov 1991 + EDR 10.33 EUR. Paga base changes at each tranche; contingenza and EDR modelled as fixed_allowances.
    
    2022-2025 paga base tranches: 31/12/2022 (base), 01/01/2023 (+40 EUR at C), 01/01/2024 (+39 EUR at C), 01/01/2025 (+44 EUR at C). Confirmed from consulenza.it per-level tables.
    
    2025-2028 totals confirmed from cdltorino.it: 01/07/2025, 01/07/2026, 01/07/2027 (+80 EUR per tranche at C reference). Paga base derived by subtracting frozen contingenza and EDR from confirmed totals.
    
    LEVEL F superminimum: +7.75 EUR/month collective superminimum treated as paga base for contractual purposes. Added to paga base values in this file.
    
    HOURLY DIVISOR: 174. Daily divisor: 25.
    
    ADDITIONAL MONTHS: 13 (tredicesima only).
    
    SENIORITY: 5 biennali (24-month) scatti. Per-level EUR amounts: F=6.65, E=7.69, D=8.31, C=8.82, CS=9.45, B=9.80, A=11.97, AS=13.01. Confirmed from ilccnl.it.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/lapidei-industria.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/lapidei-industria.py"
```
