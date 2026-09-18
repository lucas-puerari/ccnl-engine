# CCNL Attivita Minerarie (ASSORISORSE)

| | |
|---|---|
| **CNEL code** | `B282` |
| **Sector** | Industria estrattiva - Miniere, cave, saline, metallurgia estrattiva |
| **Tax sector** | `industria` |
| **Last renewal** | 2022-07-13 |
| **Workers (est.)** | ~3000 |
| **Ruleset version** | `2026.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ASSORISORSE
    - FILCTEM-CGIL
    - FEMCA-CISL
    - UILTEC-UIL

## Coverage

### Funzionalità

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | 🔲 not_implemented |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2022-07-13 |
| **Last verified** | — |
| **Next salary event** | — |

### Semplificazioni note

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1S` | Livello 1 Super - Quadri direttivi e tecnici di alta specializzazione | € 3,037.95 | 2025-01-01 |
| `1` | Livello 1 - Impiegati direttivi e tecnici specializzati | € 2,991.12 | 2025-01-01 |
| `2` | Livello 2 - Impiegati di concetto e operai altamente specializzati | € 2,768.11 | 2025-01-01 |
| `3` | Livello 3 - Impiegati d ordine e operai specializzati | € 2,460.22 | 2025-01-01 |
| `4` | Livello 4 - Operai qualificati e addetti a mansioni specifiche | € 2,228.15 | 2025-01-01 |
| `5` | Livello 5 - Operai comuni con autonomia operativa | € 2,103.19 | 2025-01-01 |
| `6` | Livello 6 - Operai comuni | € 1,981.71 | 2025-01-01 |
| `7` | Livello 7 - Operai generici con mansioni semplici | € 1,856.57 | 2025-01-01 |
| `8` | Livello 8 - Operai ausiliari e addetti a cernita | € 1,705.38 | 2025-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `1S`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`  
percentage: 0.95

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: Seniority increments (scatti di anzianita) not modeled — Art. anzianita not found in scanned PDF pages available (OCR coverage pages 1-10, table on page 9). Seniority amounts are unknown.

!!! warning ""
    SIMPLIFICATION: Source PDF is scanned (image-based, CCITT compression). Salary values extracted via OCR (Ghostscript + Tesseract). Amounts verified by cross-checking parametrale ratios and incremental consistency.

!!! warning ""
    SIMPLIFICATION: Work rules (overtime rates, leave, sickness) not modeled — source document is a renewal protocol covering salary increases and HSE provisions, not the full CCNL text.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2022-07-13 | [↗](https://www.filctemcgil.it/images/download/CONTRATTI/miniere/220713_ATTIVITA%20MINERARIE_RINNOVO%20CCNL%202022-2025.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobated. Art. 17 shows Minimi di Retribuzione as a single total amount per level with no separate contingenza column. base_salary = total monthly minimum; fixed_allowances = [] for all levels.
    
    SALARY PERIODS: 4 tranches — baseline 2022-04-01 (pre-increase values); I tranche 2023-01-01; II tranche 2023-12-01; III tranche 2025-01-01. IPCA 9% applied over contract duration 2022-2025.
    
    SIGNATORIES: ASSORISORSE (Risorse Naturali ed Energie Sostenibili) + FILCTEM-CGIL + FEMCA-CISL + UILTEC-UIL. Agreement signed Roma, 13 luglio 2022. Renews CCNL 11 aprile 2019.
    
    HOURLY DIVISOR: 173 assumed (40h/week x 52/12 = 173.33 standard industria convention). Not explicitly confirmed from scanned PDF — verify against Art. orario.
    
    ADDITIONAL MONTHS: 13 assumed (tredicesima only, standard for Confindustria-affiliated mining). Not explicitly confirmed from scanned PDF — verify against Art. gratifica natalizia.
    
    COVERAGE: ~3,000 workers, ~70 enterprises (miniere, cave, saline, metallurgia estrattiva non-ferrosa). INPS code B282 active.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/attivita-minerarie-assorisorse.json"
    ```
