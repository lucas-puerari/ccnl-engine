# CCNL Scuole Materne — FISM

| | |
|---|---|
| **CNEL code** | `T271` |
| **Sector** | istruzione privata cattolica per l'infanzia |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~30k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🟢 Verified |

[← Contracts index](index.md)

??? note "Signatories"
    - FISM
    - CISL Scuola
    - FLC-CGIL
    - UIL Scuola RUA
    - SNALS-CONFSAL

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
| `VIII` | Livello VIII — Dirigente scolastico / direttore | € 1,955.38 | — |
| `VII` | Livello VII — Coordinatore pedagogico / insegnante senior | € 1,912.11 | — |
| `VI` | Livello VI — Insegnante di scuola dell'infanzia | € 1,739.55 | — |
| `V` | Livello V — Educatore di nido / personale specializzato | € 1,719.76 | — |
| `IV` | Livello IV — Educatore / personale qualificato | € 1,630.03 | — |
| `III` | Livello III — Personale amministrativo / ausiliario specializzato | € 1,579.50 | — |
| `II` | Livello II — Personale ausiliario qualificato / assistente | € 1,577.20 | — |
| `I` | Livello I — Personale ausiliario non qualificato | € 1,517.75 | — |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

| Level | Increment (monthly) |
|---|---:|
| `I` | € 0.00 |
| `II` | € 0.00 |
| `III` | € 0.00 |
| `IV` | € 0.00 |
| `V` | € 0.00 |
| `VI` | € 0.00 |
| `VII` | € 0.00 |
| `VIII` | € 0.00 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `I`, `II`, `III`, `IV`, `V`, `VI`, `VII`, `VIII`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SENIORITY (Arts. 44-46): periodic scatti (Arts. 35 CCNL 2006-2009) were frozen at 31/12/2015 and consolidated by CCNL 2016-2018. Salario di anzianita (Art. 46): 15 EUR/month (livelli I-II-III-IV) or 20 EUR/month (livelli V-VI-VII-VIII) as at 01/09/2025. Engine seniority model cannot express the milestone/hire-date nature; maximum_count=0 models new-hire case correctly but understates cost for long-tenure workers.

!!! warning ""
    APPRENTICESHIP: no apprenticeship clause found in main CCNL text. Sector primarily employs teachers on permanent contracts. Modelled as single percentage period at 100% (identity transform) for all levels; correct for permanent staff.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-05-28 | [↗](https://fism.net/wp-content/uploads/2026/06/28-05-25-ccnl-24-27-definitivo-con-firme.pdf) |
| — | — | 2026-07-07 | [↗](https://fism.net/wp-content/uploads/2026/07/CCNL-FISM-ACCORDO-ECONOMICO-2026-2027.pdf) |

??? note "Coverage notes"
    CCNL FISM signed 28/05/2025 (sede ASI). Validity 01/09/2023-31/08/2027. Economic accord for 2026-2027 signed 07/07/2026.
    
    CONGLOBATED (Art. 43): indennita di contingenza maturata al 30/11/1991 inglobata nella retribuzione tabellare (Art. 42 lett. B). No separate contingenza column.
    
    SALARY TABLE (Art. 42 lett. B): 5 tranches — 01/09/2023, 01/06/2025, 01/09/2025 from main CCNL PDF; 01/09/2026, 01/09/2027 from 2026-2027 economic accord.
    
    HOURLY DIVISOR (Art. 51): 160 h/month for 37h/week. Divisors for 35h=152, 32h=139 also stated.
    
    ADDITIONAL MONTHS (Art. 49): tredicesima only, paid by 20 December.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/scuole-materne-fism.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/scuole-materne-fism.py"
```
