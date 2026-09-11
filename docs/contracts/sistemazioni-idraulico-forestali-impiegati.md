# CCNL Sistemazioni Idraulico-Forestali e Idraulico-Agraria (Impiegati)

| | |
|---|---|
| **CNEL code** | `A181` |
| **Sector** | sistemazioni idraulico-forestali e idraulico-agrarie — impiegati |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2025-12-04 |
| **Workers (est.)** | ~430 (impiegati subset) |
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
| `I6Q` | Impiegato 6° livello — Quadro (Art. 36 CCNL) | € 2,095.91 | — |
| `I6` | Impiegato 6° livello | € 2,095.91 | — |
| `I5` | Impiegato 5° livello | € 1,827.07 | — |
| `I4` | Impiegato 4° livello | € 1,679.91 | — |
| `I3` | Impiegato 3° livello | € 1,579.56 | — |
| `I2` | Impiegato 2° livello | € 1,488.46 | — |
| `I1` | Impiegato 1° livello | € 1,376.66 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 12 increments

| Level | Increment (monthly) |
|---|---:|
| `I1` | € 22.21 |
| `I2` | € 23.76 |
| `I3` | € 24.79 |
| `I4` | € 26.86 |
| `I5` | € 29.44 |
| `I6` | € 33.05 |
| `I6Q` | € 33.05 |

## Apprenticeship

**apprendistato_I3_22mesi** (type: `under_classification`)  
Destination levels: `I3`

**apprendistato_I4_32mesi** (type: `under_classification`)  
Destination levels: `I4`

**apprendistato_I5I6_36mesi** (type: `under_classification`)  
Destination levels: `I5`, `I6`, `I6Q`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Serie retributiva starts 01/01/2026 (first tranche with primary-source data). Retroactive 2025 tabella not available in machine-readable form; pre-2026 amounts omitted.

!!! warning ""
    Tranches 01/01/2027 and 01/01/2028 for impiegati derived from confirmed Art. 35 parametri (L1=100, L2=108, L3=115, L4=122, L5=133, L6=152) applied to 01/01/2026 base. Rounding wobble up to 0.15 EUR on L4-L6 compared to rounded CCNL tables.

!!! warning ""
    Apprendistato: livelli I1 e I2 esclusi da destination_levels (engine requires at least 2 levels below minimum; I2 at order=2 cannot go 2 below). Only I3, I4, I5, I6, I6Q supported.

!!! warning ""
    IND_FUNZIONE quadri: modelled at 120.00 EUR/month from 2026-01-01 (current published value per lavoro-economia.it). The 2021 CCNL shows 103.00 from 01/08/2002; transition date to 120.00 not confirmed from 2025 rinnovo (PDF image-only).

!!! warning ""
    Structural rules (Art. 7, 35, 41, 52) taken from 2021 previgente CCNL text. The 2025 rinnovo PDF is image-only and full text is unavailable for independent verification.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-12-04 | [↗](https://www.lavoro-economia.it/?c=9) |
| — | — | 2021-01-01 | [↗](file:ccnl-idraulico-forestali-2021.txt) |

??? note "Coverage notes"
    CCNL A181 — Sistemazioni Idraulico-Forestali (Impiegati). Split from operai contract: salary bands overlap, requiring separate files for correct engine ordering and under-classification apprenticeship. 7 livelli impiegati (I1-I6, I6Q). Conglobated model. Divisore 169, 14 mensilita.
    
    Seniority: Art. 41 CCNL 2021 — 12 scatti biennali. Amounts per level confirmed from 2021 previgente text; carried forward to 2025 rinnovo (structural rules unchanged per summary).
    
    OVERTIME/LEAVE/ABSENCE (L3): Art. 37 CCNL 2023 — straordinario 30%, notturno 50%, festivo 50%. Ferie 22 giorni (orario su 5 giorni, Art. 12). Malattia: integrazione datoriale al 100% per max 6 mesi (Art. 44). Assenza: divisore 26. Rates from 2023 CCNL PDF; 2025 rinnovo structural rules assumed unchanged (text image-only).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/sistemazioni-idraulico-forestali-impiegati.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/sistemazioni-idraulico-forestali-impiegati.py"
```
