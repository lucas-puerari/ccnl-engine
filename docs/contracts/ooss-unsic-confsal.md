# CCNL Lavoratori Dipendenti Organizzazioni Sindacali (UNSIC/CONFSAL)

| | |
|---|---|
| **CNEL code** | `V925` |
| **Sector** | Organizzazioni sindacali nazionali e territoriali |
| **Tax sector** | `terziario` |
| **Last renewal** | 2023-01-19 |
| **Workers (est.)** | ~7k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - UNSIC
    - CONFSAL
    - ASNALI
    - SNALV CONFSAL
    - FNA CONFSAL
    - CONFIAL
    - FISMIC CONFSAL
    - FAST CONFSAL
    - SNALA CONFSAL
    - FEDER.AGRI.
    - FENALCA INTERNATIONAL

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
| `1` | Livello I - Direttore Generale | € 2,788.00 | — |
| `2` | Livello II - Direttori Nazionali / Coordinatori | € 2,331.75 | — |
| `3` | Livello III - Responsabili Regionali / Impiegati di concetto | € 2,096.38 | — |
| `4` | Livello IV - Responsabili Zonali / Operatori servizi | € 1,863.44 | — |
| `5` | Livello V - Impiegati d'ordine / Addetti | € 1,735.04 | — |
| `6` | Livello VI - Usciere / Fattorino / Autista / Addetto pulizie | € 1,588.78 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 27.88 |
| `2` | € 23.32 |
| `3` | € 20.96 |
| `4` | € 18.63 |
| `5` | € 17.35 |
| `6` | € 15.89 |

## Apprenticeship

**professionalizzante - dest livello 3** (type: `under_classification`)  
Destination levels: `3`

**professionalizzante - dest livello 4** (type: `under_classification`)  
Destination levels: `4`

**professionalizzante - dest livello 5** (type: `under_classification`)  
Destination levels: `5`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: 2026 salary values (L1=2788.00, L2=2331.75, L3=2096.38, L4=1863.44, L5=1735.04, L6=1588.78) sourced from proxy (kitech.it) for the 2026-2028 renewal. Primary source PDF covers 2023-2025 only.

!!! warning ""
    SIMPLIFICATION: dest level 5 apprenticeship: lb=2 is structurally impossible (only 1 level below exists). Modelled as lb=1 for full 36mo duration per Art. 15 cap ('non piu di due livelli').

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-01-19 | [↗](https://unsic.it/wp-content/uploads/2023/02/CCNL-OOSS.pdf) |
| — | — | 2026-03-26 | [↗](https://www.kitech.it/) |

??? note "Coverage notes"
    CCNL OO.SS. signed 19/01/2023 by UNSIC/CONFSAL. Valid 01/01/2023-31/12/2025; renewed 26/03/2026 for 01/01/2026-31/12/2028.
    
    Salary model: conglobated. Art. 49 states 'paga base nazionale conglobata'. No split components.
    
    6 levels (1=highest: Direttore Generale, 6=lowest: Usciere/Fattorino). Art. 49 table.
    
    Hourly divisor 170: Art. 49 explicit ('divisore convenzionale 170'). Verified: 2746.80/170=16.16, 2065.40/170=12.15, 1565.30/170=9.21.
    
    Additional months: 14. Art. 52: gratifica natalizia (13ma) + quattordicesima mensilita.
    
    Seniority (Art. 51): triennale (36mo), max 5 scatti, 1% of current tabellare. Amounts stored per tranche.
    
    Apprenticeship (Art. 15): under_classification, max 2 levels below destination. 3 tracks (dest 3,4,5). Duration 36mo each with 18/18 split confirmed from CCNL text.
    
    No dedicated INPS code per contratticcnl.it. Tax sector=terziario applied.
    
    Headcount: 6,968 workers, 830 employers (ADAPT 18 Rapporto CNEL).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/ooss-unsic-confsal.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/ooss-unsic-confsal.py"
```
