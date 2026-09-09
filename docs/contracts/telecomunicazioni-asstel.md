# CCNL Telecomunicazioni — Assotelecomunicazioni (Asstel)

| | |
|---|---|
| **CNEL code** | `K411` |
| **Sector** | telecomunicazioni |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-11-11 |
| **Workers (est.)** | ~110k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Assotelecomunicazioni-Asstel
    - SLC-CGIL
    - Fistel-CISL
    - Uilcom-UIL

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
| `D1` | D1 — Quadri, maximum managerial and professional responsibility | € 2,814.86 | — |
| `C4` | C4 — Grade 7, managerial functions of high organisational complexity | € 2,814.86 | — |
| `C3` | C3 — Grade 6, high and consolidated professional and managerial expertise | € 2,559.28 | — |
| `C2` | C2 — Grade 5S, specialist profiles with a high degree of specialisation | € 2,263.82 | — |
| `C1` | C1 — Grade 5, advanced professional and managerial capabilities with high-level knowledge | € 2,186.73 | — |
| `B2` | B2 — Grade 4, qualified specialist knowledge | € 2,020.45 | — |
| `B1` | B1 — Grade 3, theoretical and practical knowledge of medium complexity | € 1,862.81 | — |
| `A2` | A2 — Grade 2, basic professional knowledge | € 1,701.25 | — |
| `A1` | A1 — Grade 1, predominantly manual tasks requiring no professional knowledge | € 1,518.96 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 7 increments

| Level | Increment (monthly) |
|---|---:|
| `A1` | € 21.54 |
| `A2` | € 21.54 |
| `B1` | € 23.24 |
| `B2` | € 24.38 |
| `C1` | € 25.56 |
| `C2` | € 25.56 |
| `C3` | € 28.10 |
| `C4` | € 30.73 |
| `D1` | € 30.73 |

## Apprenticeship

**professionalizzante** (type: `under_classification`)  
Destination levels: `B1`, `B2`, `C1`, `C2`, `C3`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    APPRENTICESHIP professionalizzante, under_classification (Art. 20 CCNL 12/11/2020): 36 months, first 18 months two levels below the destination, next 18 months one level below, then the destination. Track covers destinations B1, B2, C1, C2, C3; A1/A2 (no level two steps below), C4 and D1 (funzioni direttive/Quadri) are not destinations.

!!! warning ""
    INPS: reuses 2026-industria.json (Confindustria/CIGO). SIMPLIFICATION: tax_sector='industria' is a modelling choice. Supporting facts: (a) Asstel is a Confindustria federation; (b) large TLC operators (Telecom Italia, etc.) have historically accessed CIGO/CIGS; (c) the CCNL itself (Art. 58 rinnovo 11/11/2025) describes the Fondo di Solidarietà Bilaterale TLC as 'in aggiunta' (supplementary), not as a CIG substitute. Counterargument: D.Lgs. 148/2015 Art. 26 bilateral funds are formally for sectors without CIG coverage; this was not verified against an INPS circular. If TERZIARIO rates apply instead, employer contribution at ≤50 employees would be 28.98% vs. 30.20% modelled here (difference ~1.2 pp). The Fondo di Solidarietà Bilaterale (0.20% datore + 0.10% lavoratore) is NOT modelled in either case.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-11-11 | [↗](https://www.asstel.it/lavoro-e-relazioni-industriali/ccnl-tlc/) |
| — | — | 2020-11-12 | [↗](https://www.asstel.it/wp-content/uploads/2023/05/CCNL-TLC-Slc-Cgil-Fistel-Cisl-Uilcom-Uil-12-novembre-2020-nuovo.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (TEM = minimo tabellare + ex-contingenza + EDR + Elemento Retributivo di Settore), confirmed by footnote in rinnovo PDF (11/11/2025), tabelle retributive p.99-100. Back-calculation: C1(01/01/2026)=1988.73/173=11.50 EUR/h; A1=1399.68/173=8.09 EUR/h; C3=2317.44/173=13.39 EUR/h — all consistent with divisor 173. base_salary = TEM; fixed_allowances=[] for levels A1-C3.
    
    FIXED ALLOWANCES: C4 (7° livello) carries Elemento Retributivo di Settore EUR 59.39/month separate from TEM (rinnovo PDF p.97). D1 (Quadri) carries Indennità di Funzione EUR 98.13/month inclusive of the 59.39 ERS (rinnovo PDF + CCNL 12/11/2020 sezione Quadri). Both use TEM parametro=228, identical base_salary. The validator checks base_salary only so the equal values are valid.
    
    SALARY TRANCHES: four tranches from rinnovo 11/11/2025 — 01/01/2026, 01/12/2026, 01/07/2027, 01/12/2028. Pre-rinnovo salary tables (CCNL 12/11/2020) not modelled; engine scope starts from first 2026 tranche.
    
    NEW CLASSIFICATION SYSTEM: rinnovo 11/11/2025 Art. 23 introduces Professional Areas A-D (effective 01/07/2026). Old→new mapping: 1°→A1, 2°→A2, 3°→B1, 4°→B2, 5°→C1, 5°S→C2, 6°→C3, 7°→C4, Q→D1. TEM values are identical regardless of which code system is in use; engine uses new codes throughout.
    
    HOURLY DIVISOR: 173 (Art. 40, CCNL 12/11/2020: 'dividendo per 173'; 40h/week standard).
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: Art. 42, CCNL 12/11/2020. Quattordicesima not provided by this CCNL.
    
    SENIORITY biennale (24 months), max 7 scatti, amounts from Art. 41 CCNL 12/11/2020: 6 of 9 levels confirmed (A2, B1, B2, C1, C3, C4); A1=A2 (21.54), C2=C1 (25.56) and D1=C4 (30.73) by adjacent-level approximation (1° livello, 5°S and Quadri absent from the Art. 41 table).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/telecomunicazioni-asstel.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/telecomunicazioni-asstel.py"
```
