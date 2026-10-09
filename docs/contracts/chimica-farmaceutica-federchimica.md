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
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federchimica
    - Farmindustria
    - Assistal
    - FILCTEM-CGIL
    - FEMCA-CISL
    - UILTEC-UIL

## Coverage

### Funzionalità

Derived from the capability registry, as in the [capability matrix](capability-matrix.md).

| | Functional coverage of a layer: its weakest capability |
|---|---|
| ✅ | Every capability native: computed from bundled rules and request facts |
| 📝 | At best caller-supplied: a capability takes a caller rate or amount |
| ⚠️ | A capability is partial: some variants only, or data the file lacks |
| 🔲 | A capability is unsupported: the engine does not compute it |

| Layer | Status |
|---|---|
| **L1 — Gross** | 🔲 |
| **L2 — Net** | 🔲 |
| **L3 — Work rules** | 🔲 |
| **Limits of this contract** | — |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | — |
| **Last verified** | — |
| **Latest salary tranche** | 2028-06-01 |

### Semplificazioni note

Nessuna semplificazione documentata.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A1` | A (Quadri) — QA/HSE/IT manager, senior scientist, plant manager, 1st grade | € 3,682.48 | 2028-06-01 |
| `A2` | A (Quadri) — laboratory manager, complex systems expert, 2nd grade | € 3,396.59 | 2028-06-01 |
| `A3` | A (Quadri) — area coordinator, department head, 3rd grade | € 3,325.22 | 2028-06-01 |
| `B1` | B — ISF, product manager, safety officer, 1st grade | € 3,080.98 | 2028-06-01 |
| `B2` | B — researcher, maintenance manager, senior programmer, 2nd grade | € 2,968.61 | 2028-06-01 |
| `C1` | C — shift supervisor, administrative coordinator, specialist technician, 1st grade | € 2,708.65 | 2028-06-01 |
| `C2` | C — specialist clerk, QC officer, senior accountant, 2nd grade | € 2,603.86 | 2028-06-01 |
| `D1` | D — team leader, senior multi-skilled operator, 1st grade | € 2,522.26 | 2028-06-01 |
| `D2` | D — distribution operator, QA inspector, 2nd grade | € 2,409.77 | 2028-06-01 |
| `D3` | D — clerical employee / multi-skilled worker, 3rd grade | € 2,342.76 | 2028-06-01 |
| `E1` | E — GMP production operator, 1st grade | € 2,226.28 | 2028-06-01 |
| `E2` | E — basic production operator, 2nd grade | € 2,105.14 | 2028-06-01 |
| `E3` | E — generic specialised operator, 3rd grade | € 2,029.29 | 2028-06-01 |
| `E4` | E — generic operator, 4th grade | € 1,978.04 | 2028-06-01 |
| `F` | F — simple executive and service duties | € 1,891.46 | 2028-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**professionalizzante** (type: `under_classification`)  
Destination levels: `E3`, `E2`, `E1`, `D3`, `D2`, `D1`, `C2`, `C1`, `B2`, `B1`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days. INPS computes it on its own daily base (retribuzione media globale giornaliera of the month before) and on calendar days. The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the INPS indemnity on the INPS daily base and calendar days of the INPS rules, with the pay of the month before, then resolve this limitation.

!!! warning "sickness_cumulation_window · sickness · impact unknown · open"
    The CCNL tier and the comporto are counted on the days of one episode and the relapses it continues. A CCNL that sums the sickness of separate episodes over a window (a calendar year, the last three years) can reach a lower tier or the end of the comporto earlier than the engine shows. The run is affected when an earlier episode outside the relapse chain is recorded.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Add the cumulation window of each CCNL to its sickness rule, with the source, and count the tier and the comporto over it.

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax ruleset marked provisional: the sources of its year are not published yet (budget law of the year; regional and municipal surtax resolutions), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

!!! warning "provisional_inps_ruleset · inps_employer · impact unknown · open"
    The run reads an INPS ruleset marked provisional: the INPS circulars of its year are not published yet, so the rates, the massimale and the minimale (and the hourly contributions of domestic work) are those of the year before, carried over. The indexed amounts change every January: the carried-over values understate them.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional INPS ruleset of the year with the values of the INPS circulars of the year, drop its provisional flag, then resolve this limitation.

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
