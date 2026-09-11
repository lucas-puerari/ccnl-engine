# CCNL Sistemazioni Idraulico-Forestali e Idraulico-Agraria (Operai OTI)

| | |
|---|---|
| **CNEL code** | `A181` |
| **Sector** | sistemazioni idraulico-forestali e idraulico-agrarie — operai a tempo indeterminato |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2025-12-04 |
| **Workers (est.)** | ~430 (operai OTI subset) |
| **Ruleset version** | `2026.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - AGCI-Agrital
    - Confcooperative-Fedagripesca
    - Confcooperative-Lavoro-e-Servizi
    - Federforeste
    - Legacoop-Agroalimentare
    - FAI-CISL
    - FLAI-CGIL
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
| `O5` | Operaio OTI 5° livello | € 1,695.97 | — |
| `O4` | Operaio OTI 4° livello | € 1,596.98 | — |
| `O3` | Operaio OTI 3° livello | € 1,528.08 | — |
| `O2` | Operaio OTI 2° livello | € 1,491.16 | — |
| `O1` | Operaio OTI 1° livello | € 1,376.66 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

| Level | Increment (monthly) |
|---|---:|
| `O1` | € 0.00 |
| `O2` | € 0.00 |
| `O3` | € 0.00 |
| `O4` | € 0.00 |
| `O5` | € 0.00 |

## Apprenticeship

**apprendistato_O3_22mesi** (type: `under_classification`)  
Destination levels: `O3`

**apprendistato_O4_32mesi** (type: `under_classification`)  
Destination levels: `O4`

**apprendistato_O5_36mesi** (type: `under_classification`)  
Destination levels: `O5`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Serie retributiva starts 01/01/2026 (first tranche with primary-source data). Retroactive 2025 tabella not available in machine-readable form; pre-2026 amounts omitted.

!!! warning ""
    Apprendistato: livelli O1 e O2 esclusi da destination_levels (engine requires at least 2 levels below minimum; O2 at order=2 cannot go 2 below). Only O3, O4, O5 supported.

!!! warning ""
    Structural rules (Art. 7, 49, 52) taken from 2021 previgente CCNL text. The 2025 rinnovo PDF is image-only and full text is unavailable for independent verification.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-12-04 | [↗](https://redigo.info/) |
| — | — | 2021-01-01 | [↗](file:ccnl-idraulico-forestali-2021.txt) |

??? note "Coverage notes"
    CCNL A181 — Sistemazioni Idraulico-Forestali (Operai OTI). Split from impiegati contract: salary bands overlap, requiring separate files for correct engine ordering and under-classification apprenticeship. 5 livelli operai (O1-O5). Conglobato. Divisore 169, 14 mensilita.
    
    Seniority operai: nessuno scatto di anzianita previsto a livello CCNL nazionale. Gli scatti sono disciplinati dai CIRL (contratti integrativi regionali). Modellati con importo zero e maximum_count=0.
    
    Apprendistato durate: la tabella Art. 7 elenca livelli 2-6 (scala impiegati). Le durate sono mappate su O3/O4/O5 per corrispondenza di livello; la ripartizione per categoria non e confermata dal testo.
    
    OVERTIME/LEAVE/ABSENCE (L3): Art. 50 CCNL 2023 — straordinario diurno 24%, notturno straordinario 38%, festivo straordinario 50%. Ferie 22 giorni (orario su 5 giorni, Art. 12). Malattia: trattamento INPS; nessuna integrazione datoriale a livello CCNL nazionale (Art. 60). Assenza: divisore 26. Rates from 2023 CCNL PDF; 2025 rinnovo structural rules assumed unchanged (text image-only).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/sistemazioni-idraulico-forestali-operai.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/sistemazioni-idraulico-forestali-operai.py"
```
