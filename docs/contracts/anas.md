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

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    IIS months_per_year=13 assumed equal to additional_months; verify against contract text.

!!! warning ""
    Seniority maximum_count=10 — no explicit cap found in source; verify against art. on scatti di anzianita.

!!! warning ""
    Apprenticeship 70/85/92% from contract text; last period open-ended (months_until=null at 92%).

!!! warning ""
    Overtime base (Art. 101): la retribuzione oraria include minimo tabellare + contingenza (IIS) + RIA + AEP + EDR. Il modello usa hourly_base_method=minimo_tabellare (sottostima); le voci aggiuntive non sono modellate.

!!! warning ""
    Malattia: 100% mesi 1-12, 50% mesi 13+ modellati con SicknessTier. Il tasso è selezionato in base al cumulative_sick_days all'inizio del periodo; periodi di paga a cavallo di una soglia mensile ricevono un unico tasso.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-12-18 | [↗](https://www.stradeanas.it/sites/default/files/Azienda/Lavora_con_noi/CCNL-2025-2027.pdf) |

??? note "Coverage notes"
    Split model: minimo tabellare + IIS (Indennita Integrativa Speciale, frozen). 7 levels C1-C-B2-B1-B-A1-A. Divisor 156, 13 months. 4 tranches: 01/03/2026, 01/09/2026, 01/03/2027, 01/07/2027.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/anas.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/anas.py"
```
