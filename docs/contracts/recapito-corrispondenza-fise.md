# CCNL Recapito Corrispondenza (FISE-ARE)

| | |
|---|---|
| **CNEL code** | `K711` |
| **Sector** | Recapito corrispondenza e spedizioni |
| **Tax sector** | `terziario` |
| **Last renewal** | 2023-11-14 |
| **Workers (est.)** | ~1k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - FISE-ARE
    - SLC-CGIL
    - SLP-CISL
    - UILPOSTE-UIL

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
| `1` | Livello 1 | € 2,224.51 | — |
| `2` | Livello 2 | € 2,006.77 | — |
| `3S` | Livello 3 Super | € 1,791.30 | — |
| `3` | Livello 3 | € 1,687.29 | — |
| `4` | Livello 4 | € 1,600.99 | — |
| `5S` | Livello 5 Super | € 1,489.70 | — |
| `5` | Livello 5 | € 1,446.71 | — |
| `6` | Livello 6 | € 1,359.91 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 36.15 |
| `2` | € 33.05 |
| `3S` | € 32.54 |
| `3` | € 31.50 |
| `4` | € 30.47 |
| `5S` | € 29.70 |
| `5` | € 29.44 |
| `6` | € 28.41 |

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: apprenticeship type and percentages not publicly available from any free source (paywalled). Modelled as apprenticeship: [] with no rules defined.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-11-14 | [↗](https://www.redigo.info/2023/11/20/ccnl-recapito-corrispondenza-fise-nuove-tabelle-dal-rinnovo-di-novembre-2023/) |
| — | — | 2023-11-14 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=26) |

??? note "Coverage notes"
    CCNL Recapito Corrispondenza (FISE-ARE) signed 14/11/2023 by FISE-ARE, SLC-CGIL, SLP-CISL, UILPOSTE-UIL.
    
    Salary model: split — base_salary = paga tabellare + contingenza combined (rolled); EDR=10.33 as fixed_allowance. GOAL.md CCNL research confirms this structure from ilccnl.it cross-check.
    
    8 levels (1 highest, 6 lowest): 1, 2, 3S, 3, 4, 5S, 5, 6. 4 tranches: 01/02/2024, 01/09/2024, 01/07/2025, 01/06/2026. Values from redigo.info (14/11/2023 renewal article).
    
    Hourly divisor 173 confirmed from ilccnl.it cross-check (4 levels). Back-calc: 2224.51+10.33=2234.84 / 173 = 12.92 EUR/h for level 1 at Jun 2026.
    
    Additional months: 14 (tredicesima + quattordicesima) confirmed from GOAL.md research.
    
    Seniority: biennale (cadence=24), maximum 8 scatti. Per-level amounts from lavoro-economia.it (c=26), confirmed against kitech at Jun 2026 (L1=36.15, L2=33.05, L3S=32.54, L3=31.50, L4=30.47, L5S=29.70, L5=29.44, L6=28.41).
    
    Levels 1Q (Quadri), Operatore A (1650), Operatore B (1540) exist from Jun 2026 only — no prior tranche history. Not modelled to avoid open-ended periods with single-tranche data.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/recapito-corrispondenza-fise.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/recapito-corrispondenza-fise.py"
```
