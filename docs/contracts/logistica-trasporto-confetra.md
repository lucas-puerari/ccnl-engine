# CCNL Logistica, Trasporto Merci e Spedizione (Confetra)

| | |
|---|---|
| **CNEL code** | `I100` |
| **Sector** | logistica |
| **Tax sector** | `industria` |
| **Last renewal** | 2024-12-06 |
| **Workers (est.)** | ~430k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Confetra
    - Assoespressi
    - Federazione Autotrasportatori Italiani
    - Federlogistica
    - FIAP
    - FILT-CGIL
    - FIT-CISL
    - UILTrasporti

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
| `Q` | Quadro — quadro with high directional and managerial expertise | € 2,754.22 | — |
| `1` | Level 1 — management role / area manager | € 2,589.10 | — |
| `2` | Level 2 — operational unit manager / junior management role | € 2,382.07 | — |
| `3S` | Level 3 Super — reference technical/operational expert or process manager | € 2,240.37 | — |
| `3` | Level 3 — highly specialised operator / department coordinator | € 2,182.80 | — |
| `4` | Level 4 — specialist operator (C/CE licence driver, CED operator) | € 2,069.62 | — |
| `4J` | Level 4 Junior — recently graded senior operator | € 2,018.13 | — |
| `5` | Level 5 — qualified operator (cat. B driver, specialist warehouse worker) | € 1,971.13 | — |
| `6` | Level 6 — worker assigned to generic operational support tasks | € 1,841.61 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 30.99 |
| `1` | € 29.44 |
| `2` | € 26.86 |
| `3S` | € 24.79 |
| `3` | € 24.27 |
| `4` | € 23.24 |
| `4J` | € 22.34 |
| `5` | € 22.21 |
| `6` | € 20.66 |

## Apprenticeship

**standard** (type: `percentage`)  
Destination levels: `1`, `2`, `3`, `3S`, `4`, `4J`, `5`, `6`  
percentage: 1.00

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-12-06 | [↗](https://www.confetra.com/wp-content/uploads/2025/09/testo-unico-ccnl-logistica-2025.pdf) |
| — | — | 2024-12-19 | [↗](https://www.confetra.com/wp-content/uploads/2024/12/circ283-2024.pdf) |
| — | — | 2024-12-06 | [↗](https://www.contrattotrasporti.it/art-106-tabelle-retributive/) |

??? note "Coverage notes"
    STAFF: tables for non-travelling staff (clerical employees and sedentary workers). The CCNL also covers travelling staff (drivers engaged in international transport) with separate tables and rules — not modelled in this file.
    
    CONGLOBATED MINIMUMS: base_salary values are the conglobated monthly minimum pay (minimum pay table + contingenza per Art. 61 note + EPA). Primary check: Art. 61 of the consolidated text September 2025 — 'From 1.1.2001 the indennità di contingenza has been conglobated into the minimum pay tables together with the EDR of EUR 10.33 per month'. fixed_allowances is empty for all levels.
    
    HOURLY DIVISOR: 168 hours/month. Primary source: Art. 61 para. 3 consolidated text September 2025 — 'The hourly pay is obtained by dividing the monthly pay by 168'.
    
    TRANCHES: four tranches at 1.1.2025 (+120 for 3S), 1.1.2026 (+90 for 3S), 1.1.2027 (+40 for 3S), 1.6.2027 (+40 for 3S). Source: contrattotrasporti.it/art-106-tabelle-retributive (Art. 106 consolidated text) and Confetra circ283-2024 (January 2025 tranche).
    
    ICE: the Indennità di Copertura Economica (ICE) was a provisional element in force until 31.12.2024. It ceases from 1.1.2025 with the renewal taking effect. base_salary values do not include ICE (ceased element). The consolidated text cites net increases of EUR 230 at 3S compared to the previous pay including ICE — the difference from the algebraic sum of the tranches (EUR 290 from base without ICE) corresponds to the pre-existing ICE value for that level.
    
    ADDITIONAL MONTHS: 14 (tredicesima Art. 18 + quattordicesima Art. 19 consolidated text September 2025).
    
    SENIORITY INCREMENTS: biennial (24-month cadence), max 5 biennial periods. Amounts from Art. 17 consolidated text September 2025. Non-travelling staff.
    
    LEVEL 6° JUNIOR: abolished from 31.12.2025 (renewal of 6.12.2024, Confetra circ008-2025). All workers graded at 6J automatically promoted to 6°. Not modelled in this file.
    
    EPA: Elemento Professionale d'Area, a component introduced by the 6.12.2024 renewal. Included in base_salary values from 1.1.2025. Not shown separately because it forms an integral part of the minimum pay (it affects all contractual and statutory entitlements) — see Confetra circ283-2024.
    
    EDR: the EDR of EUR 10.33/month (agreement 26 Jan 2001) has been conglobated into the minimum pay tables from 1.1.2001 (Art. 61 note). Subsequent additional EDRs (agreement 2011, agreement 2021) are NON-incidente (do not affect contractual entitlements) — not modelled in base_salary; they represent a separate pay slip item outside the engine.
    
    INPS: uses 2026-industria.json (TaxSector.INDUSTRIA). File already present — no changes to the tax file.
    
    APPRENTICESHIP: percentage type from TABELLA A consolidated text September 2025. 75% year 1 (m1-12), 85% year 2 (m13-24), 100% from m25. Eligible levels: 1, 2, 3, 3S, 4, 4J, 5, 6 (level Q excluded). Maximum duration 36 months. Source: Art. 106 + TABELLA A consolidated text 09/2025 (contrattotrasporti.it).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/logistica-trasporto-confetra.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/logistica-trasporto-confetra.py"
```
