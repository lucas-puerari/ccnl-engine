# CCNL Organizzazioni Allevatori, Consorzi ed Enti Zootecnici (AIA-FLAI-FAI-UILA)

| | |
|---|---|
| **CNEL code** | `A221` |
| **Sector** | Agricoltura |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2024-12-12 |
| **Workers (est.)** | ~2k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - AIA
    - FLAI-CGIL
    - FAI-CISL
    - UILA-UIL
    - Confederdia

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | — out_of_scope |
| **L3 — Work rules** | ✅ implemented |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1/2` | Area 1 Livello 2 (Quadri) | € 2,392.51 | — |
| `1/3` | Area 1 Livello 3 | € 2,288.35 | — |
| `1/4` | Area 1 Livello 4 | € 2,183.71 | — |
| `1/5` | Area 1 Livello 5 | € 2,105.96 | — |
| `2/1` | Area 2 Livello 1 | € 2,028.26 | — |
| `2/2` | Area 2 Livello 2 | € 1,974.23 | — |
| `2/3` | Area 2 Livello 3 | € 1,895.67 | — |
| `2/4A` | Area 2 Livello 4A | € 1,791.72 | — |
| `2/4B` | Area 2 Livello 4B | € 1,757.61 | — |
| `2/5` | Area 2 Livello 5 | € 1,737.68 | — |
| `2/6` | Area 2 Livello 6 | € 1,659.20 | — |
| `3/1` | Area 3 Livello 1 | € 1,500.21 | — |
| `3/2` | Area 3 Livello 2 | € 1,372.00 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `1/2` | € 53.10 |
| `1/3` | € 50.36 |
| `1/4` | € 48.17 |
| `1/5` | € 45.97 |
| `2/1` | € 44.34 |
| `2/2` | € 43.24 |
| `2/3` | € 41.05 |
| `2/4A` | € 38.87 |
| `2/4B` | € 37.77 |
| `2/5` | € 37.22 |
| `2/6` | € 35.58 |
| `3/1` | € 31.74 |
| `3/2` | € 29.00 |

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: First tranche (Jan 2025) from Dec 2024 renewal not modeled; no per-level table confirmed for that date. Engine returns no result for as_of before 2025-09-01.

!!! warning ""
    SIMPLIFICATION: Third tranche (Sep 2026) not modeled; per-level amounts not yet published in primary sources.

!!! warning ""
    SIMPLIFICATION: Indennita di funzione for area 1 Quadri (min 13% monthly) not modeled — variable floor amount, not expressible as fixed allowance.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-12-12 | [↗](https://www.wolterskluwer.it/) |
| — | — | 2024-12-12 | [↗](https://www.kitech.it/) |
| — | — | 2023-11-14 | [↗](https://www.confederdia.it/2023/11/30/ipotesi-di-accordo-rinnovo-ccnl-dipendenti-dalle-organizzazioni-degli-allevatori-consorzi-ed-enti-zootecnici/) |
| — | — | 2024-12-12 | [↗](https://www.lavoro-economia.it/) |

??? note "Coverage notes"
    Salary model: conglobated. Wolters Kluwer tables show Minimo = Totale with no separate contingenza column. fixed_allowances = [] for all levels.
    
    Hourly divisor 164.67 = 38h/week x 52 / 12, confirmed from Art. 11 CCNL (FLAI PDF). Tredicesima + quattordicesima = 14 additional months (Art. 17 CCNL).
    
    Seniority: 10 biennial scatti per Art. 18 CCNL (FLAI PDF + Confederdia confirmed). Cadence biennale (24 months). Amounts effective 2025-01-01 per Dec 2024 economic renewal.
    
    Indennita di funzione for Quadri (area 1): at least 13% of monthly salary per Art. 19 CCNL. Not modeled: percentage-based floor, not a fixed amount.
    
    Apprenticeship: Annex 4 (profili formativi) referenced but not publicly parsed. layer_2 = out_of_scope.
    
    Headcount: ~1,822 workers (AIA, CNEL archive 2023).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/organizzazioni-allevatori-aia.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/organizzazioni-allevatori-aia.py"
```
