# CCNL Consorzi Agrari (ASSOCAP-FLAI-FAI-UILA)

| | |
|---|---|
| **CNEL code** | `A141` |
| **Sector** | Agricoltura |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2023-12-12 |
| **Workers (est.)** | ~2k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ASSOCAP
    - FLAI-CGIL
    - FAI-CISL
    - UILA-UIL

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
| `Q` | Quadro | € 2,212.99 | — |
| `1` | Livello 1 | € 2,212.99 | — |
| `2` | Livello 2 | € 2,002.97 | — |
| `3S` | Livello 3 Super | € 1,710.74 | — |
| `3` | Livello 3 | € 1,574.42 | — |
| `4S` | Livello 4 Super | € 1,468.82 | — |
| `4` | Livello 4 | € 1,375.68 | — |
| `5` | Livello 5 | € 1,233.03 | — |
| `6` | Livello 6 | € 1,070.87 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 53.20 |
| `1` | € 53.20 |
| `2` | € 50.61 |
| `3S` | € 47.00 |
| `3` | € 45.19 |
| `4S` | € 44.16 |
| `4` | € 43.12 |
| `5` | € 41.32 |
| `6` | € 39.51 |

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: Jan 2024 tranche (first of four per 12/12/2023 accord) not modeled; no per-level table found in public sources. Engine returns no result for as_of before 2025-01-01.

!!! warning ""
    SIMPLIFICATION: Jan 2027 tranche not yet published per-level; not modeled.

!!! warning ""
    SIMPLIFICATION: Indennita di cassa (EUR 55.00/month, cashiers only) not modeled — applies only to a subset of workers.

!!! warning ""
    SIMPLIFICATION: FILCOOP SANITARIO bilateral health fund not modeled.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-12-12 | [↗](https://www.wolterskluwer.it/) |
| — | — | 2023-12-12 | [↗](https://www.kitech.it/) |
| — | — | 2023-12-12 | [↗](https://www.flai.it/) |
| — | — | 2023-12-12 | [↗](https://ilccnl.it/contratto/ccnl/consorzi-agrari) |

??? note "Coverage notes"
    Salary model: split (paga base + contingenza) confirmed from ilccnl.it tables showing separate paga base, contingenza, and terzo elemento (0.00) columns.
    
    Indennita di funzione modeled as INDENNITA_DI_FUNZIONE fixed_allowance for levels Q (335.50), 1 (192.50), 2 (115.50 EUR/month). Source: kitech.
    
    Seniority: 5 biennial scatti per Art. 34 CCNL (FLAI-CGIL PDF primary source). Scatto amounts from kitech Jan 2026 table; applied from 2025-01-01 — no Jan 2025 per-level table found in public sources.
    
    Apprenticeship: Art. 16 delegates rules to Annex E, not publicly available. layer_2 = out_of_scope.
    
    Headcount: ~2,133 workers (ASSOCAP, CNEL archive 2023).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/consorzi-agrari-assocap.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/consorzi-agrari-assocap.py"
```
