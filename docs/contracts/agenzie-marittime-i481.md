# CCNL Agenzie Marittime Raccomandatarie, Agenzie Aeree e Mediatori Marittimi

| | |
|---|---|
| **CNEL code** | `I481` |
| **Sector** | Agenzie marittime e aeree |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-09-13 |
| **Workers (est.)** | ~5k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - FEDERAGENTI
    - FILT-CGIL
    - FIT-CISL
    - UILTRASPORTI

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
| `7` | Livello 7 (Quadro) | € 2,481.46 | — |
| `6` | Livello 6 | € 2,370.23 | — |
| `5` | Livello 5 | € 2,305.38 | — |
| `4` | Livello 4 | € 2,177.70 | — |
| `3` | Livello 3 | € 1,921.32 | — |
| `2` | Livello 2 | € 1,841.02 | — |
| `1` | Livello 1 (operaio comune) | € 1,601.09 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 0.00 |
| `2` | € 26.50 |
| `3` | € 27.75 |
| `4` | € 28.75 |
| `5` | € 32.00 |
| `6` | € 32.50 |
| `7` | € 33.00 |

## Apprenticeship

**professionalizzante - dest livello 3** (type: `under_classification`)  
Destination levels: `3`

**professionalizzante - dest livelli 4-5** (type: `under_classification`)  
Destination levels: `4`, `5`

**professionalizzante - dest livello 6** (type: `under_classification`)  
Destination levels: `6`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: 2021-2023 previgente salary values not modeled (not publicly available). Modeling starts from the 2024 renewal first tranche (01/09/2024).

!!! warning ""
    SIMPLIFICATION: Level 1 seniority amount = 0.00. Art. 23 table (primary source) lists levels 2-7 only; level 1 is absent. Interpreted as no entitlement. Verify against consolidated CCNL text.

!!! warning ""
    SIMPLIFICATION: Whether indennita' di funzione rides the quattordicesima is unconfirmed. Modeled as a standard fixed_allowance (paid 14 mensilita'). If Art. 5 excludes it from the quattordicesima calculation, the annual figure is overstated by ~51.65 EUR/year.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2021-07-30 | [↗](https://www.filtcgil.it/images/Contratti/Mobilit%C3%A0/ccnl-agenziemarittime21-23.pdf) |
| — | — | 2024-09-13 | [↗](https://www.zhrexpert.it/ccnl/i481-agenzie-marittime.html) |

??? note "Coverage notes"
    Salary model: conglobated (Art. 21: 'paga base, contingenza ed EDR'). Source: 2021 CCNL primary text (FILT-CGIL PDF, signed 30/07/2021).
    
    Hourly divisor 168 confirmed from Art. 20 primary source: 'La paga oraria si ottiene dividendo la retribuzione mensile per 168'. Cross-check: L4 Sep-2026 = 2177.70 / 168 = 12.96 EUR/h (matches lavoro-economia.it hourly rate).
    
    Additional months: 14. Art. 24 (tredicesima) and Art. 25 (quattordicesima) of the 2021 CCNL primary source.
    
    Seniority: 8 biennali (Art. 23, 2021 CCNL primary source). Amounts from Art. 23 table dated 01/04/2004: L7=33.00, L6=32.50, L5=32.00, L4=28.75, L3=27.75, L2=26.50. Level 1 not listed in Art. 23 table: modeled as 0.00.
    
    Apprenticeship: under-classification, Art. 8 of 2021 CCNL (D.Lgs. 81/2015). Destination levels 3-6 only. Three tracks: dest=3 (24 months), dest=4-5 (30 months), dest=6 (36 months). Source: Art. 8, 2021 CCNL primary text.
    
    Indennita' per i Quadri (level 7): 51.65 EUR/month. Source: Art. 5 of the 2021 CCNL primary text (FILT-CGIL PDF): 'A far data dal 1 gennaio 1992, tale indennita' viene elevata a Euro 51,65 lorde mensili.' Modeled as fixed_allowance FUNZIONE, level 7 only.
    
    Salary table (4 tranches): 01/09/2024, 01/09/2025, 01/01/2026, 01/09/2026 from 2024 renewal (signed 13/09/2024). Source: zhrexpert.it (proxy); all cells confirmed consistent with primary-source cross-checks (L4 Sep-2026: 2177.70 / 168 = 12.96 matches hourly rate). Best-attested cell: L4 at 01/01/2026 = 2137.70 (two independent proxy sources agree exactly).
    
    Headcount: approx. 5,000 workers (small sector, CNEL archive I481). Employers: FEDERAGENTI members (maritime agencies, shipping agents, air agencies).
    
    Indennita' per i Quadri amount 51.65 EUR confirmed from Art. 5, 2021 CCNL primary text. Amount unchanged since 01/01/1992 per contract text.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/agenzie-marittime-i481.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/agenzie-marittime-i481.py"
```
