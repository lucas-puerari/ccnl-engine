# CCNL Industria Chimica e Farmaceutica (Federchimica-Farmindustria-Assistal)

| | |
|---|---|
| **CNEL code** | `B011` |
| **Sector** | chimica |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~210k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Federchimica
    - Farmindustria
    - Assistal
    - FILCTEM-CGIL
    - FEMCA-CISL
    - UILTEC-UIL

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
| `A1` | A (Quadri) — QA/HSE/IT manager, senior scientist, plant manager, 1st grade | € 3,682.48 | — |
| `A2` | A (Quadri) — laboratory manager, complex systems expert, 2nd grade | € 3,396.59 | — |
| `A3` | A (Quadri) — area coordinator, department head, 3rd grade | € 3,325.22 | — |
| `B1` | B — ISF, product manager, safety officer, 1st grade | € 3,080.98 | — |
| `B2` | B — researcher, maintenance manager, senior programmer, 2nd grade | € 2,968.61 | — |
| `C1` | C — shift supervisor, administrative coordinator, specialist technician, 1st grade | € 2,708.65 | — |
| `C2` | C — specialist clerk, QC officer, senior accountant, 2nd grade | € 2,603.86 | — |
| `D1` | D — team leader, senior multi-skilled operator, 1st grade | € 2,522.26 | — |
| `D2` | D — distribution operator, QA inspector, 2nd grade | € 2,409.77 | — |
| `D3` | D — clerical employee / multi-skilled worker, 3rd grade | € 2,342.76 | — |
| `E1` | E — GMP production operator, 1st grade | € 2,226.28 | — |
| `E2` | E — basic production operator, 2nd grade | € 2,105.14 | — |
| `E3` | E — generic specialised operator, 3rd grade | € 2,029.29 | — |
| `E4` | E — generic operator, 4th grade | € 1,978.04 | — |
| `F` | F — simple executive and service duties | € 1,891.46 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**professionalizzante** (type: `under_classification`)  
Destination levels: `E3`, `E2`, `E1`, `D3`, `D2`, `D1`, `C2`, `C1`, `B2`, `B1`

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-04-15 | [↗](https://informatori.it/wp-content/uploads/2025/04/Tabelle-Incrementi-TEM-CCNL-2025-2028.pdf) |
| — | — | 2026-07-01 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=105) |

??? note "Coverage notes"
    CONSOLIDATED TEM: the base_salary values represent the total Minimum Economic Treatment (TEM) = base minimum (Min) + IPO (Organisational Position Integration, per level) + EAR (Additional Pay Element: A=EUR 190, B=EUR 100, C-F=0, fixed throughout the contract) + EDR (Distinct Pay Element, added from 01/07/2027, per level). fixed_allowances is empty for all levels.
    
    PRIMARY SOURCE: TEM tables from the Federchimica/Farmindustria primary source (CCNL 2025-2028, signed 15/04/2025): informatori.it/wp-content/uploads/2025/04/Tabelle-Incrementi-TEM-CCNL-2025-2028.pdf. The PDF contains the increment tables (Min and IPO per tranche) and the absolute TEM values at each due date for all 15 levels.
    
    MODELLED TRANCHES: (1) Pre-existing (end of CCNL 2022-2025, valid_from 2025-06-01): Min+IPO+EAR from PDF page 2 column 'Previgente'. (2) 1/7/2025: first tranche CCNL 2025-2028. (3) 1/12/2025: second tranche. (4) 1/7/2026: third tranche — independently verified on kitech.it (CNEL B011), exact match. (5) 1/7/2027: fourth tranche + EDR (per level, PDF page 4). (6) 1/6/2028: fifth and final tranche.
    
    EDR: from 01/07/2027 the Distinct Pay Element (EDR) is added, monthly amounts per level: A1=39, A2=34, A3=33, B1=32, B2=30, C1=28, C2=27, D1=26, D2=25, D3=24, E1=22, E2=20, E3=19, E4=19, F=18. The modelled TEM already includes EDR in the periods from 01/07/2027.
    
    IPO VARIES BY TRANCHE: the IPO is not fixed across tranches but receives its own increments (table on PDF page 1, IPO columns per due date). TEM values are calculated by summing Min, IPO, and EAR (and EDR from 01/07/2027) for each tranche.
    
    PRE-JUNE-2025 TRANCHES (CCNL 2022-2025, 5 tranches July 2022 - June 2025) are outside the modelled window: the Federchimica PDF reports only the 'Previgente' column as the baseline.
    
    SENIORITY INCREMENTS abolished from 1 January 2010; amounts accrued up to 2009 are crystallised as a non-absorbable personal supplement, to be passed to compute() as ad_personam_monthly. maximum_count=0 and amount_by_level={}.
    
    HOURLY DIVISOR: 175 h/month (chemical-pharmaceutical sector). The 173 divisor applies only to the ceramics and abrasives sub-sector.
    
    ADDITIONAL MONTHS: 13 (thirteenth month only). The fourteenth month applies only to the lubricants/LPG, ceramics/abrasives, and insulation sub-sectors.
    
    INPS: uses 2026-industria.json (standard industry sector). CNEL code: B011.
    
    APPRENTICESHIP (sotto-inquadramento, Art. 3 CCNL): single track 'professionalizzante' covers all eligible destinations E3–B1 (10 levels). Rule: 0–18m = 2 levels below dest; 18m+ = 1 level below dest (two equal periods, total 36m typical). Excluded: F (Art. 3 explicit), E4 (2-below not resolvable), A3/A2/A1 (management tier, not standard apprenticeship). Prior track 'destinazione_D1' had levels_below=3 (error); corrected to 2. Source: Art. 3 CCNL Federchimica (lavoro-economia.it B011); informatori.it sintesi apprendistato B011.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/chimica-farmaceutica-federchimica.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/chimica-farmaceutica-federchimica.py"
```
