# CCNL Gruppo ANAS

| | |
|---|---|
| **CNEL code** | `T511` |
| **Sector** | anas spa - personale non dirigente |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-12-18 |
| **Workers (est.)** | ~7k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ANAS SpA
    - FILT-CGIL
    - FIT-CISL
    - UILTRASPORTI
    - UGL Viabilità e Logistica

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
| `A` | Livello A | € 3,475.91 | — |
| `A1` | Livello A1 | € 2,896.61 | — |
| `B` | Livello B | € 2,462.15 | — |
| `B1` | Livello B1 | € 2,244.84 | — |
| `B2` | Livello B2 | € 2,027.55 | — |
| `C` | Livello C | € 1,665.53 | — |
| `C1` | Livello C1 | € 1,448.36 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `C1` | € 16.66 |
| `C` | € 19.16 |
| `B2` | € 23.32 |
| `B1` | € 25.82 |
| `B` | € 28.30 |
| `A1` | € 33.31 |
| `A` | € 39.97 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `C1`, `C`, `B2`, `B1`, `B`, `A1`, `A`  
percentage: 0.92

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-12-18 | [↗](https://www.stradeanas.it/sites/default/files/Azienda/Lavora_con_noi/CCNL-2025-2027.pdf) |

??? note "Coverage notes"
    Split model: minimo tabellare + IIS (Indennita Integrativa Speciale, frozen). 7 levels C1-C-B2-B1-B-A1-A. Divisor 156, 13 months. 4 tranches: 01/03/2026, 01/09/2026, 01/03/2027, 01/07/2027.
    
    IIS months_per_year=13: confirmed equal to additional_months (ANAS CCNL: 13 mensilità standard; INPS/secondary sources confirm 13-month pay cycle).
    
    Seniority maximum_count=10 — confirmed: ANAS CCNL provides 10 biennial seniority increments (secondary source cross-reference, consistent with comparable PA-adjacent contracts).
    
    Apprenticeship 70/85/92% confirmed from CCNL ANAS 2025-2027 Art. 28 text. Last period (months_until=null at 92%) reflects the contractual open-ended formulation; upon qualification the worker moves to full pay at the destination level.
    
    Overtime base (Art. 101 CCNL ANAS): the official retribuzione oraria includes minimo tabellare + IIS (contingenza) + RIA + AEP + EDR. Engine uses hourly_base_method=minimo_tabellare, which understates the overtime base by excluding IIS, RIA, AEP, EDR. Structural engine limitation (no per-allowance hourly_relevant flag); monthly/annual figures unaffected.
    
    Malattia: 100% mesi 1-12, 50% mesi 13+ — CCNL ANAS 2025-2027 Art. malattia. Modellato con SicknessTier (comporto standard). Periodi a cavallo di soglia mensile ricevono un unico tasso (engine limitation accettabile).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/anas.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/anas.py"
```
