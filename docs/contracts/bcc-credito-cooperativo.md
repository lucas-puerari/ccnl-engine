# CCNL per i lavoratori delle Banche di Credito Cooperativo, Casse Rurali ed Artigiane

| | |
|---|---|
| **CNEL code** | `J271` |
| **Sector** | credito |
| **Tax sector** | `credito` |
| **Last renewal** | — |
| **Workers (est.)** | ~33k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Federcasse
    - FABI
    - FIRST-CISL
    - FISAC-CGIL
    - UGL Credito
    - UILCA

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
| `QD4` | Executive Managers - 4th pay level | € 5,160.06 | — |
| `QD3` | Executive Managers - 3rd pay level | € 4,396.88 | — |
| `QD2` | Executive Managers - 2nd pay level | € 3,965.48 | — |
| `QD1` | Executive Managers - 1st pay level | € 3,743.21 | — |
| `3AP4` | 3rd Professional Area - 4th pay level | € 3,341.90 | — |
| `3AP3` | 3rd Professional Area - 3rd pay level | € 3,059.49 | — |
| `3AP2` | 3rd Professional Area - 2nd pay level | € 2,890.41 | — |
| `3AP1` | 3rd Professional Area - 1st pay level | € 2,742.35 | — |
| `2AP2` | 2nd Professional Area - 2nd pay level | € 2,572.10 | — |
| `2AP1` | 2nd Professional Area - 1st pay level | € 2,406.80 | — |
| `1AP` | 1st Professional Area - single level | € 2,241.53 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `QD4` | € 95.31 |
| `QD3` | € 95.31 |
| `QD2` | € 41.55 |
| `QD1` | € 41.55 |
| `3AP4` | € 41.55 |
| `3AP3` | € 41.55 |
| `3AP2` | € 41.55 |
| `3AP1` | € 41.55 |
| `2AP2` | € 35.57 |
| `2AP1` | € 29.07 |
| `1AP` | € 20.12 |

## Apprenticeship

**terza_area** (type: `under_classification`)  
Destination levels: `3AP1`, `3AP2`, `3AP3`, `3AP4`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Apprenticeship (Art. 30) modelled for destination levels 3AP1-3AP4: months 0-18 one level below the destination, then the destination level. The Art. 3 comma 3 derogation (higher destination level) is assumed to follow the same 18-month rule.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-07-09 | [↗](https://www.fabi.it/wp-content/uploads/2025/01/CCNL-BCC-testo-coordinato-19-dicembre-2024.pdf) |
| — | — | 2024-07-09 | [↗](https://www.kitech.it/tabelle-retributive/banche-credito-cooperativo/) |

??? note "Coverage notes"
    Salary model is conglobated (stipendio per Art. 112 replaces paga base + scala mobile + EDR + other components). Modelled as base_salary with fixed_allowances: [].
    
    First period valid_from set to 2024-09-01 (first tranche date per Allegato A). Pre-tranche salaries belong to the previous CCNL and are not modelled.
    
    Seniority (Art. 113): first scatto after 4 years (48 months), then every 36 months; maximum 8 scatti for the Aree Professionali and 12 for the Quadri Direttivi (Art. 101), via maximum_count_by_level.
    
    Hourly divisor 160 in both periods per Art. 114 (rounding down to the nearest multiple of 5): 37.5h x 52 / 12 = 162.5 → 160 (pre-July 2025); 37h x 52 / 12 = 160.33 → 160 (from July 2025, Art. 118).
    
    Workers covered: approximately 36,000 (Federcasse / Banche di Credito Cooperativo, Casse Rurali ed Artigiane). Agreement signed 2024-07-09; valid until 2025-12-31 per Art. 9.
    
    INPS rates from 2026-credito.json (same sector as bancari-abi). IRPEF 2026 brackets applied (L. 199/2025).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/bcc-credito-cooperativo.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/bcc-credito-cooperativo.py"
```
