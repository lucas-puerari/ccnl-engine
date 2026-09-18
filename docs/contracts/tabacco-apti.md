# CCNL per i dipendenti dalle aziende di lavorazione della foglia di tabacco secco allo stato sciolto

| | |
|---|---|
| **CNEL code** | `E042` |
| **Sector** | lavorazione foglia di tabacco |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-07-02 |
| **Workers (est.)** | ~2k |
| **Ruleset version** | `—` |
| **Extraction** | 🧑 Manual |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - APTI
    - FLAI-CGIL
    - FAI-CISL
    - UILA-UIL

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
| `1S` | Categoria Super — funzioni direttive di particolare rilievo | € 2,271.18 | 2028-01-01 |
| `1` | 1a Categoria — funzioni direttive amministrative o tecniche | € 2,106.68 | 2028-01-01 |
| `2` | 2a Categoria — funzioni di concetto con coordinamento | € 1,847.04 | 2028-01-01 |
| `3A` | 3a Categoria A — compiti esecutivi tecnici o amministrativi con iniziativa | € 1,625.55 | 2028-01-01 |
| `3B` | 3a Categoria B — compiti esecutivi tecnici o amministrativi | € 1,462.16 | 2028-01-01 |
| `4A` | 4a Categoria A — qualificazione per il processo di lavorazione del tabacco | € 1,334.90 | 2028-01-01 |
| `4B` | 4a Categoria B — conoscenze tecnico-pratiche di controllo o produzione | € 1,279.29 | 2028-01-01 |
| `5` | 5a Categoria — mansioni operative standard | € 1,242.28 | 2028-01-01 |
| `6` | 6a Categoria — mansioni semplici di prima assunzione | € 1,115.90 | 2028-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1S` | € 17.00 |
| `1` | € 17.00 |
| `2` | € 15.00 |
| `3A` | € 14.00 |
| `3B` | € 13.00 |
| `4A` | € 12.00 |
| `4B` | € 12.00 |
| `5` | € 11.00 |
| `6` | € 10.00 |

## Apprenticeship

**apprendistato professionalizzante (livelli 2-4)** (type: `under_classification`)  
Destination levels: `2`, `3A`, `3B`, `4A`, `4B`

**apprendistato professionalizzante (livello 1)** (type: `under_classification`)  
Destination levels: `1`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    APPRENTICESHIP: under_classification for destinations 2, 3A, 3B, 4A, 4B (36-month, 10/12/14 periods) and level 1 (36-month, 10/10/16 periods). Destination 5 (24-month exception, Article 6) not modeled. Level 1S is not an apprenticeship destination.

!!! warning ""
    ALIFOND employer contribution (1.50%) modeled from 01/07/2025 (renewal Art. 47). Pre-July-2025 ALIFOND contribution not modeled.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| CCNL Tabacco Lavorazione foglia 2025-2028 — Accordo 02/07/2025 | altro | — | [↗](https://www.uila.eu/web/wp-content/uploads/2022/04/Accordo-rinnovo-ccnl-nazionale-tabacco-sciolto-2025-2028-02-07-25.pdf) |
| CCNL Tabacco (Lavorazione) — lavoro-economia.it | tabella_retributiva | — | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=25) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = minimo tabellare (4 tranches: +60 at 4A on 01/01/2025, +50 on 01/01/2026, +50 on 01/01/2027, +40 on 01/01/2028). 50/50 parametric formula verified against published Allegato A table.
    
    CONTINGENZA: per-level amounts frozen at 01/11/1991 (Allegato B, CCNL 2021). EDR 10.33 EUR uniform for all levels (Accordo Interconfederale 31/07/1992).
    
    SENIORITY: cadence 24 months, maximum 5 scatti. Amounts from Article 32 of the 2025 renewal. Operai amounts roughly doubled vs 2021 CCNL (4A/B: 5.68->12.00, 5: 5.42->11.00, 6: 5.16->10.00).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/tabacco-apti.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/tabacco-apti.py"
```
