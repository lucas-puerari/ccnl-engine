# Distribuzione Moderna Organizzata — Federdistribuzione

| | |
|---|---|
| **CNEL code** | `H008` |
| **Sector** | terziario |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~460k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Federdistribuzione
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
| `Q` | Managers (Quadri) | € 2,313.29 | — |
| `I` | First level | € 2,083.84 | — |
| `II` | Second level | € 1,802.50 | — |
| `III` | Third level | € 1,540.66 | — |
| `IV` | Fourth level | € 1,332.46 | — |
| `V` | Fifth level | € 1,203.83 | — |
| `VI` | Sixth level | € 1,080.77 | — |
| `VII` | Seventh level | € 925.31 | — |

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

**standard_II_V** (type: `under_classification`)  
Destination levels: `II`, `III`, `IV`, `V`

**standard_VI** (type: `under_classification`)  
Destination levels: `VI`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Terzo elemento nazionale (Art. 199): EUR 2.07/month (lire 4,000) for workers in provinces without provincial terzi elementi (Art. 198, frozen since 1973). Modelled as 'edr' fixed allowance for all workers. # SIMPLIFICATION: some provinces have higher provincial elements (second-level bargaining, out of scope).

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-04-23 | [↗](https://www.federdistribuzione.it/wp-content/uploads/2025/01/CCNL-DMO-Testo-Unico-29.09.2025.pdf) |

??? note "Coverage notes"
    Salary tables: 6 tranches from 01/04/2023 through 01/02/2027 per Allegato 11, Testo Unico CCNL DMO 29/09/2025 (Federdistribuzione). 47/48 cells verified arithmetic; L4 01/04/2023 PDF OCR reads '1112.46' but total (1646.68) and contingenza (524.22) prove 1122.46 — consistent with pre-acconto 1092.46 + 30 EUR acconto (Dec 2022 Protocol).
    
    Split model confirmed: total / 168 at L1 = 14.905, L4 = 10.605, L7 = 8.309 — all non-integer. Source: Art. 194 (divisore 168 for 40h/week), Allegato 11.
    
    Contingenza: frozen values from Allegato 11 column. EDR (lire 20,000 = 10.33 EUR) conglobated into contingenza on 01/01/1995 per Art. 190 — no separate EDR allowance modelled.
    
    Indennità di funzione Quadri (Art. 113): EUR 260.76/month for 14 months (cumulative increments: 51.65+77.47+51.65+70.00+10.00=260.77; 0.01 rounding from lire). Allegato 11 shows 260.76.
    
    Indennità di funzione 7° livello: EUR 5.16/month (lire 10,000) in 'altri elementi' column of Allegato 11 for Level VII. Same element and amount as Commercio Confcommercio 'ind_funzione' for livello 7.
    
    Seniority: 10 scatti triennali (Art. 188), amounts from Testo Unico Art. 188 table. valid_from set to 2024-04-23 (renewal date).
    
    Additional months: 14 (tredicesima Art. 204 + quattordicesima Art. 205).
    
    APPRENTICESHIP: sotto-inquadramento per Art. 46 + Art. 57 Testo Unico DMO 29/09/2025. Art. 55: destinazioni ammesse livelli II–VI (I e Q esclusi). Livelli II–V: 36 mesi, 0–18m = 2 livelli sotto dest, 18m+ = 1 livello sotto. Livello VI: 24 mesi, 0–12m = 1 livello sotto (VII), 12m+ = livello VI (dest). Source: Testo Unico Federdistribuzione 29/09/2025 (Allegato apprendistato).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/dmo-federdistribuzione.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/dmo-federdistribuzione.py"
```
