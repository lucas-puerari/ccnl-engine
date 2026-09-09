# CCNL Terziario Distribuzione e Servizi — Confesercenti

| | |
|---|---|
| **CNEL code** | `H012` |
| **Sector** | Terziario distribuzione e servizi |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-03-22 |
| **Workers (est.)** | ~230k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Confesercenti
    - Filcams-CGIL
    - Fisascat-CISL
    - UILTuCS-UIL

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
| `Q` | Senior Manager (Quadro) | € 3,114.47 | — |
| `I` | First Level | € 2,621.36 | — |
| `II` | Second Level | € 2,335.07 | — |
| `III` | Third Level | € 2,068.56 | — |
| `IV` | Fourth Level | € 1,856.68 | — |
| `V` | Fifth Level | € 1,725.77 | — |
| `VI` | Sixth Level | € 1,600.54 | — |
| `VII` | Seventh Level | € 1,447.98 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 25.46 |
| `I` | € 24.84 |
| `II` | € 22.83 |
| `III` | € 21.95 |
| `IV` | € 20.66 |
| `V` | € 20.30 |
| `VI` | € 19.73 |
| `VII` | € 19.47 |

## Apprenticeship

**standard** (type: `under_classification`)  
Destination levels: `II`, `III`, `IV`, `V`

**sesto-livello** (type: `under_classification`)  
Destination levels: `VI`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    One-off lump sum of EUR 350 at grade IV (paid 175+175 in July 2024/2025) not modelled in base_salary — it is not a structural increase.

!!! warning ""
    Grade I not included as an apprenticeship destination: Art. 64 lists only II-VI.

!!! warning ""
    Track sesto-livello: Art. 53 exception — first half at grade VII since two levels below VI is not possible; second half 1 level below VI = VII. Both halves at grade VII.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2019-12-12 | [↗](https://www.confesercenti.it/wp-content/uploads/2023/01/CCNL_contratto-collettivo-nazionale.pdf) |
| — | — | 2024-03-22 | [↗](https://cdcpcnelblg01sa.blob.core.windows.net/archivio/2024//20260.pdf) |

??? note "Coverage notes"
    Apprenticeship type b (professionalizzante). Durations: II=36m, III=36m, IV=36m, V=36m, VI=24m. Half-period = 18m (II-V) and 12m (VI).
    
    Base salary table effective from 01.01.2020 (Table I, CCNL 12.12.2019, confesercenti.it PDF).
    
    2024 renewal salary increases from Art. 213 (CNEL id 20260, 22.03.2024). Tranches: 01/04/2023, 01/04/2024, 01/03/2025, 01/11/2025, 01/11/2026, 01/02/2027.
    
    Seniority increment amounts from Art. 205 CCNL 2019, effective from 01.01.1990 (triennial, max 10).
    
    Hourly divisor 168 from Art. 211 CCNL 2019 (40h/week).
    
    14 monthly payments from Art. 220 (thirteenth) and Art. 221 (fourteenth) CCNL 2019.
    
    Apprenticeship from Art. 53 (under-classification) and Art. 64 (durations: II-V 36 months, VI 24 months) CCNL 2019.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/terziario-confesercenti.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/terziario-confesercenti.py"
```
