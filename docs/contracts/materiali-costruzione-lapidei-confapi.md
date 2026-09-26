# CCNL Materiali da Costruzione PMI — Lapidei (CONFAPI ANIEM)

| | |
|---|---|
| **CNEL code** | `F020` |
| **Sector** | Industria materiali da costruzione — Lapidei piccola industria |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-09-09 |
| **Workers (est.)** | ~5000 |
| **Ruleset version** | `—` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CONFAPI ANIEM
    - FILLEA-CGIL
    - FENEAL-UIL
    - FILCA-CISL

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
| **Last renewal** | 2025-09-09 |
| **Last verified** | — |
| **Next salary event** | — |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1` | Livello 1 — Lavoratori con funzioni direttive apicali e autonomia decisionale (quadri, dirigenti) | € 2,795.46 | 2025-01-01 |
| `2` | Livello 2 — Lavoratori con responsabilità di unità organizzativa (responsabili amministrazione/produzione) | € 2,587.54 | 2025-01-01 |
| `3` | Livello 3 — Lavoratori di concetto e coordinamento (responsabili uffici, capi reparto/impianto) | € 2,202.40 | 2025-01-01 |
| `4` | Livello 4 — Lavoratori con rilevante preparazione tecnico-pratica (capi linea, tecnici specializzati) | € 2,096.25 | 2025-01-01 |
| `5` | Livello 5 — Lavoratori specializzati (caposquadra, escavatoristi, scalpellini artistici) | € 2,014.85 | 2025-01-01 |
| `6` | Livello 6 — Lavoratori qualificati con capacità tecnico-pratiche (minatori, scalpellini, gruisti) | € 1,925.43 | 2025-01-01 |
| `7` | Livello 7 — Lavoratori con normali capacità (cavatori, operai di cantiere, addetti linee produzione) | € 1,813.41 | 2025-01-01 |
| `8` | Livello 8 — Lavoratori addetti a mansioni semplici (pulizie, manovalanza, prima assunzione) | € 1,613.14 | 2025-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `8` | € 6.76 |
| `7` | € 7.57 |
| `6` | € 8.31 |
| `5` | € 8.99 |
| `4` | € 9.60 |
| `3` | € 10.14 |
| `2` | € 11.83 |
| `1` | € 12.76 |

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: Apprenticeship not modelled. Art. 3 defines three periods (0-12 months 2 levels below, 12-24 months 1 level below, 24-36 months destination pay) with a special 18-month track for L6 and destination pay in period 3. The engine supports ApprenticeshipUnderClassification with levels_below periods, but L6's shorter duration and period-3 destination-pay override require per-destination customisation not yet extracted from source. Deferred pending dedicated source review.

!!! warning ""
    SIMPLIFICATION: Work rules (overtime, leave, sickness) not modelled. Discipline lapidei spans multiple articles; scope deferred.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-09-09 | [↗](https://www.fenealuil.it/wp-content/uploads/2026/02/CCNL_MaterialiCostruzione_testo-completo.pdf) |

??? note "Coverage notes"
    SCOPE: Lapidei subsector only. Laterizi and Cemento subsectors have different level codes and salary structures; not modelled in this file.
    
    SALARY MODEL: split. Art. 25 Lapidei: contingenza congelata e conglobata nei minimi (Minimo = paga base + contingenza frozen). fixed_allowances: EDR 10.33 EUR (tutti i livelli) and supermin.coll 7.75 EUR (livello 8 only).
    
    SALARY HISTORY: 6 tranches from Allegato V (accordo 25.1.2024) and Art. 25 Lapidei dal 1.1.2025. Periods: 1.4.2019, 1.9.2020, 1.2.2021, 1.1.2022, 1.1.2024, 1.1.2025 (open). Source: CCNL testo completo FENEAL-UIL.
    
    HOURLY DIVISOR: 174. Art. 24 Disciplina Lapidei: 'Le quote orarie degli elementi mensilizzati della retribuzione si ottengono dividendo gli elementi stessi per 174'.
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Art. 73 Disciplina Lapidei: gratifica natalizia annuale pari a una mensilita'.
    
    SENIORITY: 5 scatti biennali (cadence 24 months). Art. 26 Lapidei: importi fissi calcolati al 5% dei minimi 1980 e trasformati in cifra fissa. Amounts: L1=12.76, L2=11.83, L3=10.14, L4=9.60, L5=8.99, L6=8.31, L7=7.57, L8=6.76.
    
    SIGNATORIES: CONFAPI ANIEM + FILLEA-CGIL + FENEAL-UIL + FILCA-CISL. Testo definitivo signed 9 settembre 2025. Contract period 1.7.2022-30.6.2025.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/materiali-costruzione-lapidei-confapi.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/materiali-costruzione-lapidei-confapi.py"
```
