# CCNL Agenzie di Viaggio e Turismo — Fiavet/Confcommercio

| | |
|---|---|
| **CNEL code** | `H052` |
| **Sector** | Turismo (agenzie di viaggio) |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-07-26 |
| **Workers (est.)** | ~25k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Fiavet (Federazione Italiana Associazioni Imprese Viaggi e Turismo)
    - Federviaggio
    - Filcams-CGIL
    - Fisascat-CISL
    - Uiltucs-UIL

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
| `QA` | Quadro A — Top management function | € 2,495.21 | — |
| `QB` | Quadro B — Management function | € 2,310.11 | — |
| `1` | Level 1 — Conceptual employee with managerial functions | € 2,152.33 | — |
| `2` | Level 2 — Conceptual employee | € 1,967.21 | — |
| `3` | Level 3 — Qualified employee | € 1,855.32 | — |
| `4` | Level 4 — Employee | € 1,750.69 | — |
| `5` | Level 5 — Qualified clerical employee | € 1,641.83 | — |
| `6S` | Level 6S — Super clerical employee | € 1,578.72 | — |
| `6` | Level 6 — Clerical employee | € 1,556.35 | — |
| `7` | Level 7 — Auxiliary staff | € 1,458.41 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `QA` | € 40.80 |
| `QB` | € 39.25 |
| `1` | € 37.70 |
| `2` | € 36.15 |
| `3` | € 34.86 |
| `4` | € 33.05 |
| `5` | € 32.54 |
| `6S` | € 31.25 |
| `6` | € 30.99 |
| `7` | € 30.47 |

## Apprenticeship

**standard** (type: `percentage`)  
Destination levels: `1`, `2`, `3`, `4`, `5`, `6S`, `6`, `7`  
percentage: 0.90

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Levels QA and QB (Quadri) excluded from the apprenticeship track (apprenticeship not applicable to Quadri by law).

!!! warning ""
    Layer 3 (overtime, night shifts, public holidays) out of scope.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2019-07-11 | [↗](https://cdcpcnelblg01sa.blob.core.windows.net/archivio/2019//20108.pdf) |
| — | — | 2024-07-26 | [↗](https://cdcpcnelblg01sa.blob.core.windows.net/archivio/2024//20108.pdf) |

??? note "Coverage notes"
    Salary tables 2024-2027 from CCNL renewal of 26 July 2024 (CNEL PDF). Six tranches: Jun-24, Jul-24, Sep-25, Sep-26, Jun-27, Dec-27.
    
    Hourly divisor 172 from Art. 146 CCNL base 2019 (CNEL PDF doc 20108). Same basis as the Confcommercio tourism sector.
    
    14 additional monthly payments from Art. 157 (thirteenth month) and Art. 158 (fourteenth month) of the 2024 renewal.
    
    Triennial seniority increments (Art. 156 CCNL 2019): 36-month cadence, maximum 6 increments. Per-level amounts from the table attached to the 2024 renewal.
    
    Percentage-based apprenticeship from Art. 64 CCNL 2019 (OCR pages 32-33): first year 80%, second year 85%, third year 90%.
    
    CNEL code H052 confirmed from kitech.it CodiceCateg=81 (Confcommercio tourism sector, travel agencies included).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/agenzie-viaggio-fiavet.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/agenzie-viaggio-fiavet.py"
```
