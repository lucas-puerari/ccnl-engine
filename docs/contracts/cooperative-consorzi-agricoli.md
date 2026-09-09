# CCNL Cooperative e Consorzi Agricoli

| | |
|---|---|
| **CNEL code** | `A016` |
| **Sector** | cooperative e consorzi agricoli — impiegati e operai agricoli |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2024-07-19 |
| **Workers (est.)** | ~60k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - AGCI-Agrital
    - Confcooperative-Fedagripesca
    - Legacoop-Agroalimentare
    - FLAI-CGIL
    - FAI-CISL
    - UILA-UIL

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ⚠️ partial |
| **L3 — Work rules** | ✅ implemented |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1` | Livello 1° | € 2,303.40 | — |
| `2` | Livello 2° | € 2,070.77 | — |
| `3` | Livello 3° | € 1,906.06 | — |
| `4` | Livello 4° | € 1,772.31 | — |
| `5` | Livello 5° | € 1,685.38 | — |
| `6` | Livello 6° | € 1,636.55 | — |
| `7` | Livello 7° | € 1,518.40 | — |
| `np` | Area non professionalizzati | € 1,280.82 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 12 increments

| Level | Increment (monthly) |
|---|---:|
| `np` | € 0.00 |
| `7` | € 9.44 |
| `6` | € 10.85 |
| `5` | € 11.39 |
| `4` | € 11.93 |
| `3` | € 12.20 |
| `2` | € 29.44 |
| `1` | € 33.05 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `np`, `7`, `6`, `5`, `4`, `3`, `2`, `1`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Scatti anzianità: Art. 61 (operai, max 5 biennali) e Art. 49 (impiegati, max 12 biennali) hanno importi differenti per i livelli 3-7. Modellati con gli importi operai (dominanti nelle cooperative). maximum_count=12 (impiegati); query operai con seniority_count>5 producono scatti sovrastimati.

!!! warning ""
    Apprendistato: regola non reperita nel PDF 2024. Modellato come 100% passthrough.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-07-19 | [↗](https://www.flai.it/wp-content/uploads/2018/11/CCNL-Cooperative-e-consorzi-agricoli-2024-2027.pdf) |

??? note "Coverage notes"
    CCNL A016 — Cooperative e Consorzi Agricoli. Conglobated model. 8 livelli: np-7-6-5-4-3-2-1. Divisore 169, 14 mesi. 4 tranches: apr-2024, mag-2025, mag-2026, feb-2027.
    
    Quadri: i livelli 1Q e 2Q del precedente impianto corrispondono a livello 1° e 2° con aggiunta dell'indennità di funzione quadri (Art. 45): 1Q +EUR 180→230/mese, 2Q +EUR 125→160/mese dal 01/08/2024. Modellata come fixed_allowance a 14 mensilità su ciascun livello.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/cooperative-consorzi-agricoli.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/cooperative-consorzi-agricoli.py"
```
