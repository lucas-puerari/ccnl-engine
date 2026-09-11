# CCNL Turismo (Assoturismo-Confesercenti)

| | |
|---|---|
| **CNEL code** | `H058` |
| **Sector** | turismo — alberghi, campeggi, pubblici esercizi, agenzie di viaggi |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-07-22 |
| **Workers (est.)** | — |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Assoturismo-Confesercenti
    - Assohotel
    - Assocamping
    - Assoviaggi
    - FIEPET
    - FIBA
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTuCS

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
| `QA` | Quadro A | € 2,495.22 | — |
| `QB` | Quadro B | € 2,310.11 | — |
| `1` | Livello 1 | € 2,152.32 | — |
| `2` | Livello 2 | € 1,967.20 | — |
| `3` | Livello 3 | € 1,855.32 | — |
| `4` | Livello 4 | € 1,750.69 | — |
| `5` | Livello 5 | € 1,641.85 | — |
| `6S` | Livello 6S | € 1,578.72 | — |
| `6` | Livello 6 | € 1,556.35 | — |
| `7` | Livello 7 | € 1,458.42 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `7` | € 30.47 |
| `6` | € 30.99 |
| `6S` | € 31.25 |
| `5` | € 32.54 |
| `4` | € 33.05 |
| `3` | € 34.86 |
| `2` | € 36.15 |
| `1` | € 37.70 |
| `QB` | € 39.25 |
| `QA` | € 40.80 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `7`, `6`, `6S`, `5`, `4`, `3`, `2`, `1`, `QB`, `QA`  
percentage: 1.00

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-07-22 | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=257) |
| — | — | 2024-07-22 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=82) |
| — | — | 2024-07-22 | [↗](https://www.redigo.info/2024/07/24/ccnl-turismo-confesercenti-il-rinnovo-consolida-il-contratto-unico/) |

??? note "Coverage notes"
    CCNL H058 — Assoturismo-Confesercenti. Conglobated. 10 levels: 7-6-6S-5-4-3-2-1-QB-QA. Divisor 172, 14 months. Seniority 36-month cadence, max 6. 5 tranches: Jul-2024 to Nov-2027.
    
    Models the alberghi/campeggi sub-sector only (CCNL H058, conglobated model). Pubblici esercizi and stabilimenti balneari use a split (paga base + contingenza) model with different values — out_of_scope deliberate: these sub-sectors have meaningfully different pay structures requiring separate files.
    
    Indennita di funzione for QA (EUR 75/month) and QB (EUR 70/month) conglobated into base_salary. Consistent with turismo-federalberghi.json modeling for the same allowances. The CCNL H058 does not publish them as separate line items in the tabella retributiva; absorption into base_salary matches the conglobated model.
    
    Apprenticeship model confirmed: CCNL Turismo Confesercenti provides sotto-inquadramento 2 levels below destination (consistent with Testo Unico apprendistato Art. 11, secondary sources). Engine uses 100% passthrough because schema requires static pay_level_code; the 2-level under-classification cannot be modelled dynamically. Modeled as 100% passthrough pending contract text.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/turismo-confesercenti.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/turismo-confesercenti.py"
```
