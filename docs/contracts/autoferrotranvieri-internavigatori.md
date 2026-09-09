# CCNL Autoferrotranvieri e Internavigatori (Mobilita/TPL)

| | |
|---|---|
| **CNEL code** | `I022` |
| **Sector** | trasporti |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-12-11 |
| **Workers (est.)** | ~120k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - AGENS
    - ASSTRA
    - ANAV
    - FILT-CGIL
    - FIT-CISL
    - Uiltrasporti
    - Faisa-Cisal
    - UGL-FNA

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
| `250` | Parameter 250 — senior officials / executive managers | € 2,657.09 | — |
| `230` | Parameter 230 — officials / principal inspectors | € 2,470.97 | — |
| `210` | Parameter 210 — operations coordinators | € 2,254.23 | — |
| `205` | Parameter 205 — senior supervisors | € 2,213.96 | — |
| `202` | Parameter 202 — operations supervisors | € 2,189.81 | — |
| `193` | Parameter 193 — operations staff / station masters | € 2,113.32 | — |
| `190` | Parameter 190 — principal coordinators | € 2,089.14 | — |
| `188` | Parameter 188 — senior coordinators | € 2,071.18 | — |
| `183` | Parameter 183 — coordinating agents | € 2,030.87 | — |
| `180` | Parameter 180 — agents with coordination functions | € 2,005.84 | — |
| `178` | Parameter 178 — senior clerks | € 1,989.72 | — |
| `175` | Parameter 175 — office clerks / qualified agents | € 1,965.57 | — |
| `170` | Parameter 170 — advanced driving agents | € 1,925.30 | — |
| `165` | Parameter 165 — agents with managerial functions | € 1,882.02 | — |
| `160` | Parameter 160 — principal operations agents | € 1,841.75 | — |
| `158` | Parameter 158 — senior operations agents | € 1,825.64 | — |
| `155` | Parameter 155 — qualified driving agents (III) | € 1,798.44 | — |
| `154` | Parameter 154 — qualified driving agents (II) | € 1,790.40 | — |
| `153` | Parameter 153 — qualified driving agents (I) | € 1,782.36 | — |
| `151` | Parameter 151 — driving agents | € 1,766.25 | — |
| `145` | Parameter 145 — driving agents (entry) | € 1,717.92 | — |
| `143` | Parameter 143 — senior agents | € 1,701.81 | — |
| `140` | Parameter 140 — specialist operations agents | € 1,677.65 | — |
| `139` | Parameter 139 — specialist operators (II) | € 1,669.60 | — |
| `138` | Parameter 138 — specialist operators (I) | € 1,661.54 | — |
| `135` | Parameter 135 — operations agents | € 1,633.99 | — |
| `130` | Parameter 130 — qualified line agents | € 1,593.73 | — |
| `129` | Parameter 129 — line agents | € 1,585.66 | — |
| `123` | Parameter 123 — line agents (first year) | € 1,537.35 | — |
| `121` | Parameter 121 — qualified operators | € 1,518.61 | — |
| `116` | Parameter 116 — qualified operators (entry) | € 1,478.35 | — |
| `110` | Parameter 110 — entry-level operators | € 1,430.01 | — |
| `100` | Parameter 100 — auxiliary staff and entry-level apprentices | € 1,346.11 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `100` | € 15.33 |
| `110` | € 16.93 |
| `116` | € 17.78 |
| `121` | € 18.54 |
| `123` | € 19.10 |
| `129` | € 19.77 |
| `130` | € 19.92 |
| `135` | € 20.69 |
| `138` | € 21.06 |
| `139` | € 21.06 |
| `140` | € 21.46 |
| `143` | € 21.92 |
| `145` | € 22.22 |
| `151` | € 23.14 |
| `153` | € 23.45 |
| `154` | € 23.60 |
| `155` | € 23.75 |
| `158` | € 24.65 |
| `160` | € 24.65 |
| `165` | € 25.29 |
| `170` | € 26.05 |
| `175` | € 26.85 |
| `178` | € 27.28 |
| `180` | € 27.59 |
| `183` | € 27.83 |
| `188` | € 28.81 |
| `190` | € 29.12 |
| `193` | € 29.58 |
| `202` | € 30.96 |
| `205` | € 31.42 |
| `210` | € 32.18 |
| `230` | € 35.25 |
| `250` | € 38.31 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `100`, `110`, `116`, `121`, `123`, `129`, `130`, `135`, `138`, `139`, `140`, `143`, `145`, `151`, `153`, `154`, `155`, `158`, `160`, `165`, `170`, `175`, `178`, `180`, `183`, `188`, `190`, `193`, `202`, `205`, `210`, `230`, `250`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    INPS reuses 2026-terziario.json. The Autoferrotranvieri sector (TPL) includes both public-owned (ex-gestione governativa) and private operators. INPS classification is TERZIARIO for private TPL companies (confirmed by ASSTRA/ANAV membership profile and INPS contribution circulars for the trasporti locali sector). SIMPLIFICATION: some publicly-owned TPL operators may have different INPS contribution schemes; this file models private-sector employers.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-12-11 | [↗](https://www.uiltrasporti.it/wp-content/uploads/2025/03/TABELLA-AUTOFERRO.pdf) |
| — | — | 2024-12-11 | [↗](https://www.lavoro-economia.it/contratti/autoferrotranvieri) |
| — | — | 2024-12-11 | [↗](https://www.agens.it/wp-content/uploads/2025/03/Inf.-002_25.pdf) |
| — | — | 2024-12-11 | [↗](https://www.thaler.it/assets/files/Transparenzdekret/Autolinien_-_Autoferrotranvieri.pdf) |
| — | — | 2024-12-11 | [↗](https://www.lexplain.it/contratto-autoferrotranvieri-parametri-livelli-e-mansioni-come-orientarsi/) |

??? note "Coverage notes"
    CNEL CODE: I022 confirmed from CNEL archivio contratti (www.cnel.it/Contratti-Collettivi) for the Autoferrotranvieri e Internavigatori sector.
    
    SIGNATORIES: employer side — AGENS (aziende ex gestione governativa), ASSTRA (aziende di trasporto pubblico locale), ANAV (autolinee e autoservizi). Union side — FILT-CGIL, FIT-CISL, Uiltrasporti, Faisa-Cisal, UGL-FNA. Confirmed from AGENS circular 20/03/2025.
    
    AGREEMENT DATE: 2024-12-11 (intesa preliminare, confirmed in AGENS circular 20/03/2025 as the date that became definitively effective upon scioglimento delle riserve on 20/03/2025). Contract validity: 01/01/2024 to 31/12/2026.
    
    SALARY MODEL: conglobated (TOTALE). base_salary per level = tabellare (Sep 2023) + contingenza (frozen since 1992) + TDR (Trattamento Distinto della Retribuzione, 51.65 EUR at par.175) + mensa (16.53 EUR/month, in retribuzione normale per Art. 43) + indennita di funzione (72.30 EUR for par.250, 51.65 EUR for par.230, 0 for all others). Sources: UilTrasporti official salary table PDF (March 2025); Thaler 2022 CCNL summary (contingenza and TDR tables).
    
    SALARY TRANCHES: 3 periods. Period 1 (2024-12-11 to 2025-03-01): Sep 2023 tabellare values. Period 2 (2025-03-01 to 2026-08-01): +60 EUR at par.175, pro-rated. Period 3 (2026-08-01 to null): +100 EUR at par.175 (cumulative +160 EUR at par.175). Confirmed from UilTrasporti table and AGENS circular 20/03/2025.
    
    HOURLY DIVISOR: 195. Derived from CCNL Art. 15 (primary source, italpaghe.ilccnl.it): 'Gli importi orari si determinano dividendo la retribuzione giornaliera per l'orario medio giornaliero.' Daily = monthly/30; for 39h/week the CCNL Thaler 2022 summary specifies dividing by 6 to get daily hours: 39/6 = 6.5h/day; divisor = 30 * 6.5 = 195. Three independent sources (CCNL Art. 15, lexplain.it, Thaler 2022) confirm the formula. Note: lavoro-economia.it states 'divisore convenzionale 169' but this contradicts the CCNL primary text and two corroborating sources; not adopted.
    
    ADDITIONAL MONTHS: 14 (tredicesima in December + quattordicesima in June). Confirmed from CCNL Art. 40 (tredicesima) and Art. 41 (quattordicesima). Source: Thaler 2022 CCNL summary.
    
    SENIORITY: biennale (24 months), maximum 6 scatti. Per-level amounts (EUR/scatto) confirmed from Thaler 2022 CCNL summary table, all 33 parametri. Note: two pairs share the same scatto amount (par.158 = par.160 = 24.65; par.138 = par.139 = 21.06) — this is as published.
    
    EDR 2024: fixed_allowances per level, code 'edr_2024', 40 EUR at par.175 proportional to the parametro, active 2025-03-01 to 2026-04-30 (14 months). Per AGENS circular 20/03/2025 it is 'non computabile ai fini del TFR e della contribuzione al Fondo Priamo': modelled with tfr_relevant=false (Fondo Priamo is a bilateral pension fund, not modelled).
    
    APPRENTICESHIP: CCNL Art. 36-bis (apprendistato professionalizzante). No wage reduction: the apprentice earns 100% of the destination parametro from day one; the track therefore covers every parametro. Source: Art. 36-bis per AGENS circular 20/03/2025.
    
    LEVELS: 33 parametri from 100 to 250. The CCNL classification assigns one or more job profiles per parametro; this file models one level per parametro as the economic unit. Descriptions are representative summaries; multiple job profiles exist at each parametro.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/autoferrotranvieri-internavigatori.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/autoferrotranvieri-internavigatori.py"
```
