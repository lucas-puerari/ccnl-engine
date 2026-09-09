# CCNL per il personale dipendente non dirigente delle imprese di assicurazione (ANIA)

| | |
|---|---|
| **CNEL code** | `J121` |
| **Sector** | assicurazioni |
| **Tax sector** | `credito` |
| **Last renewal** | 2026-05-13 |
| **Workers (est.)** | ~45k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ANIA
    - FIRST-CISL
    - FISAC-CGIL
    - FNA
    - SNFIA
    - UILCA

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ⚠️ partial |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | ✅ implemented |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `L7` | 7° livello — Funzionario | € 3,112.27 | — |
| `L6` | 6° livello — Quadro | € 2,629.37 | — |
| `L5` | 5° livello — Impiegato | € 2,463.96 | — |
| `L4` | 4° livello — Impiegato | € 2,324.66 | — |
| `L3` | 3° livello — Impiegato | € 2,130.75 | — |
| `L2` | 2° livello — Impiegato | € 1,946.58 | — |
| `L1` | 1° livello — Impiegato | € 1,846.38 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 11 increments

| Level | Increment (monthly) |
|---|---:|
| `L7` | € 102.08 |
| `L6` | € 81.77 |
| `L5` | € 76.63 |
| `L4` | € 72.30 |
| `L3` | € 66.27 |
| `L2` | € 60.54 |
| `L1` | € 57.42 |

## Apprenticeship

**area_c_l3** (type: `under_classification`)  
Destination levels: `L3`

**area_b_l4** (type: `under_classification`)  
Destination levels: `L4`

**area_b_l5** (type: `under_classification`)  
Destination levels: `L5`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Seniority increment = modal per-class difference in the 1/14 monthly table (Allegato 2/B); classes above CL01 may differ from the official table by ±0.02. Source: Allegato 2/B, Rinnovo 13/05/2026.

!!! warning ""
    INPS employer_rate 26.76% flat from kitech.it (Credito e Assicurazioni 2026); reuses 2026-credito.json. Verify against the annual INPS circular.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-05-13 | [↗](https://www.first-cisl.it/) |
| — | — | — | [↗](https://www.contratticcnl.it/) |

??? note "Coverage notes"
    Covers personale amministrativo assunto dal 18/12/1999 (Allegato 2/B — tabella omnicomprensiva). Pre-1999 hires (Allegato 2/A) are out of scope.
    
    First tranche decorrenza 01/01/2026 is retroactive; CCNL signed 13/05/2026. Arretrati January–July 2026 paid in July 2026 (Allegato 7). Period start is 2026-01-01 in the engine.
    
    Additional months = 14 (tredicesima + quattordicesima). Monthly amounts are 1/14 of annual retribuzione. Source: Allegato 2/B header, FirstCISL PDF rinnovo 13/05/2026.
    
    Seniority: cl 1 = anni 1-4 (48 months, quadriennale); cl 2 onward = 3 years each (36 months, triennale). Source: Art. 113 CCNL + Allegato 2/B class table.
    
    L7 maximum seniority class is CL08 (anni 23-25); L1-L6 reach CL12 (oltre 34 anni). maximum_count_by_level overrides L7 to 7 advances.
    
    Hourly divisor 160 (37h/week). Source: ilccnl.it, confirmed from Art. orario di lavoro CCNL ANIA.
    
    Seniority increment amounts vary across tranches (e.g. L4: 67.51 → 70.17 → 72.30). Represented exactly via TimeSeries in amount_by_level.
    
    Indennità profilo J) 4° livello (Allegato 2/E) — modelled as fixed_allowance IND_PROFILO_J on L4 with role 'profilo_j'. Amounts: €57.26/mese dal 01/01/2026, €59.51 dal 01/01/2027, €61.32 dal 01/01/2028. Pass roles={'profilo_j'} in Scenario to include it.
    
    Indennità economica 6° livello quadro (Allegato 2/F) — modelled as fixed_allowance IND_QUADRO_6 on L6 with role 'quadro_6'. Amount: €74.09/mese dal 01/01/2026. Pass roles={'quadro_6'} in Scenario to include it.
    
    Salary tables: FirstCISL Gruppo Unipol, Allegato 2/B — Tabella omnicomprensiva post-1999, decorrenza 01/01/2026, 01/01/2027, 01/01/2028.
    
    Apprenticeship: Art. 5, Allegato 18 (Accordo apprendistato professionalizzante), CCNL testo 2017/2018, confirmed applicable post-rinnovo 2026.
    
    Class cadence: Art. 113 CCNL + column 'Anni serv.' Allegato 2/B.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/assicurazioni-ania.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/assicurazioni-ania.py"
```
