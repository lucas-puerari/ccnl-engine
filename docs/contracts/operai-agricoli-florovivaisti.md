# CCNL Operai Agricoli e Florovivaisti — Coldiretti/Confagricoltura/CIA

| | |
|---|---|
| **CNEL code** | `A011` |
| **Sector** | agricoltura |
| **Tax sector** | `agricoltura` |
| **Last renewal** | — |
| **Workers (est.)** | ~600k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Coldiretti — Confederazione Nazionale Coldiretti
    - Confagricoltura — Confederazione Generale dell'Agricoltura Italiana
    - CIA — Confederazione Italiana Agricoltori
    - Assoverde — Associazione Italiana Costruttori del Verde
    - FLAI-CGIL — Federazione Lavoratori Agroindustria
    - FAI-CISL — Federazione Agro Alimentare
    - UILA-UIL — Unione Italiana Lavoratori Agroalimentari

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
| **Limits of this contract** | base_salary, bilateral_funds, inail, inps_employee, inps_employer, seniority, territorial_supplement |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | 2026-09-18 |

### Freschezza

| | |
|---|---|
| **Last renewal** | — |
| **Last verified** | 2026-09-18 |
| **Latest salary tranche** | 2027-01-01 |

### Semplificazioni note

12 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Area1` | Area 1 — Operai Specializzati (specialised agricultural workers) | € 1,533.84 | 2027-01-01 |
| `Area2` | Area 2 — Operai Qualificati (qualified agricultural workers) | € 1,398.86 | 2027-01-01 |
| `Area3` | Area 3 — Operai Comuni (unskilled general agricultural workers) | € 1,043.00 | 2027-01-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Area1` | € 11.36 |
| `Area2` | € 10.33 |
| `Area3` | € 8.99 |

## Apprenticeship

**apprendistato_professionalizzante** (type: `under_classification`)  
Destination levels: `Area1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "operai-agricoli-florovivaisti/provincial_supplement · territorial_supplement · impact yes · open"
    NATIONAL MINIMUMS ONLY. Provincial contracts (contratti provinciali di lavoro, 20 provinces) pay substantially more than national floor. The national tabella retributiva is the legal minimum. Actual employer cost in any province requires adding the CPL supplement.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the provincial (CPL) supplement outside the engine.

!!! warning "operai-agricoli-florovivaisti/otd_terzo_elemento · base_salary · impact yes · open"
    OTI ONLY. OTD (Operai a Tempo Determinato / seasonal) workers are not modelled. OTD workers receive a Terzo Elemento of 30.44% (festività 5.45% + ferie 8.33% + tredicesima 8.33% + quattordicesima 8.33%) in lieu of accruals; the engine cannot represent this structure. OTD represent a large share of agricultural workers.

    **Applies when:** `base_salary` applies; contract type in fixed_term.

    **Remediation:** Model the OTD terzo elemento structure for fixed-term agricultural workers.

!!! warning "operai-agricoli-florovivaisti/florovivaisti_tables · base_salary · impact yes · open"
    FLOROVIVAISTI NOT DISTINGUISHED. The CCNL covers both Operai Agricoli (OTA) and Operai Florovivaisti (OTF). OTF have separate (higher) tabelle retributive with their own area amounts. This file models OTA amounts only. Callers must use a separate file (not yet modelled) for OTF workers.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the OTF salary tables as a separate file.

!!! warning "operai-agricoli-florovivaisti/inps_on_actual_not_conventional_pay · inps_employee · impact yes · open"
    INPS CONTRIBUTION BASE. Agricultural OTI INPS contributions are legally computed on the 'retribuzione convenzionale' (set annually by INPS decree per DL 338/1989 Art. 1), NOT on the actual contractual salary. This engine applies rates to actual gross salary. The net INPS amounts will differ from statutory computations. Figures are indicative only.

    **Applies when:** `inps_employee` applies.

    **Remediation:** Compute agricultural INPS contributions on the retribuzione convenzionale set by INPS decree.

!!! warning "operai-agricoli-florovivaisti/inail_agricultural_premium · inail · impact yes · open"
    INAIL NOT MODELLED. INAIL agricultural premium (8.50% unified from 2026 per new tariff) is not modelled. The engine does not track INAIL.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the INAIL agricultural premium.

!!! warning "operai-agricoli-florovivaisti/seniority_amounts_unconfirmed · seniority · impact unknown · open"
    SENIORITY AMOUNTS. Art. 54 scatti di anzianità amounts (Area1=11.36, Area2=10.33, Area3=8.99) sourced from 2022-2025 CCNL via aggregators (contratticcnl.it). The 2026 renewal text has not been confirmed to have changed these amounts; INPS Circ. 94/2024 reports a different 5-level structure (L1=9.89, L2=11.36, L3=11.93, L4=12.50, L5=12.78) which may reflect a different classification schema. Update if the renewed Art. 54 specifies different area-based values.

    **Applies when:** `seniority` applies.

    **Remediation:** Confirm the Art. 54 seniority amounts against the 2026 renewal text.

!!! warning "operai-agricoli-florovivaisti/eban_fisa_agrifondo · bilateral_funds · impact yes · open"
    BILATERAL FUNDS. EBAN (Ente Bilaterale Agricolo Nazionale) and FISA (Fondo Integrativo di Settore Agricolo) bilateral fund contributions are set at provincial level and not modelled. Agrifondo (supplementary pension) contributions also omitted.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Pass the provincial EBAN, FISA and Agrifondo contributions as bilateral fund events.

!!! warning "operai-agricoli-florovivaisti/mountain_zone_reductions · inps_employer · impact yes · open"
    TERRITORIAL REDUCTIONS. INPS reductions for mountain/disadvantaged zones (75%/68%) are not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the INPS reductions for mountain and disadvantaged zones.

!!! warning "operai-agricoli-florovivaisti/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "operai-agricoli-florovivaisti/apprentice_inps_rates_unsourced · inps_employer · impact unknown · open"
    APPRENTICE INPS RATES: the apprentice rates of the sector (agricoltura) apply the 10% of L. 296/2006 art. 1 c. 773 plus the 1.61% NASpI, but no source found settles the disoccupazione and CISOA contributions of agricultural apprentices (INPS circ. 43/2026 gives no apprentice rates). The contributions of an apprentice may differ.

    **Applies when:** `inps_employer` applies; contract type in apprentice.

    **Remediation:** Source the apprentice rates of agricoltura (an INPS circular or an association table of 2026), mark the apprentice block of social_security/contribution/2026/agricoltura.json derived, then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

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

!!! warning "inps_minimum_base_exempt_category · inps_employer · impact unknown · open"
    D.L. 463/1983 art. 7 c. 5 keeps the operai agricoli out of the 9.50% minimum daily base, and the run applies no minimum to them. Tabella A of INPS circ. 6/2026 still lists 51.70 for the operai agricoli, 'non soggetto all'adeguamento' of art. 7 c. 1; no source found says whether it is a floor of their contribution base. A base below it may understate the contributions.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Source the role of the 51.70 of the operai agricoli (INPS circ. 43/2026 on the agricultural contributions, or the minimum daily wages of art. 1 L. 389/1989), then apply it as their minimum or record that none applies.

### Without monetary impact

!!! note ""
    CNEL CODE A011 sourced from ilccnl.it and contratticcnl.it; unverified against CNEL archive (archive returned 404 at time of extraction). Code A014 belongs to a separate expired minority CCNL (ASNALI/FAGRI) — do not confuse.

!!! note ""
    APPRENTICESHIP — AREA1 DESTINATION ONLY. Area2 destination under-classification would require 2 levels below Area2, which is below the national floor (Area3), and cannot be modelled in a 3-level system. Area3 destination apprenticeship has no lower level to start from. Only Area1 destination (0-12m at Area3, 12-24m at Area2, 24-36m at Area1) is modelled.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-05-28 | [↗](https://www.contratticcnl.it/agricoltura-florovivaisti/tabelle-retributive/) |
| — | — | 2026-01-01 | [↗](https://ciatreviso.it/contributi-inps-inail-2026-agricoli-aliquote-e-le-scadenze-per-operai-otd-e-oti/) |
| — | — | 2024-11-13 | [↗](https://www.inps.it/content/dam/inps-site/it/scorporati/circolari-e-messaggi/2024/11/Circolare_14697/Allegati/15379_Circolare-numero-94-del-13-11-2024_Allegato-n-1.pdf) |
| — | — | 2025-01-01 | [↗](https://www.dottrinalavoro.it/wp-content/uploads/2024/12/Retribuzioni-al-1_1_2025.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobated retribuzione tabellare minima (paga base + contingenza + EDR merged since 01/01/2009). Contingenza = 0.00 and EDR = 0.00 per ilccnl.it table. Single base_salary per area per period. Source: contratticcnl.it tabelle retributive, confirmed by research from ilccnl.it showing zero contingenza columns.
    
    RENEWAL: CCNL signed 23/05/2022 (valid 2022-2025), renewed 28/05/2026 (quadriennio 2026-2029). Two salary tranches: +3.4% from 2026-06-01, +1.7% from 2027-01-01 on June 2026 amounts. No una tantum.
    
    LEVELS: Three national professional areas (OTI, Operai a Tempo Indeterminato, national minimums). Area1=Specializzati, Area2=Qualificati, Area3=Comuni. National table sets floor only; provincial contracts (contratti provinciali di lavoro) always exceed these minimums.
    
    HOURLY DIVISOR: 169 hours/month. Formula: 39 h/week × 52 weeks / 12 = 169.00 exactly. Confirmed by ilccnl.it divisore orario field (169) and daily divisor 26 (169 / 6.5).
    
    ADDITIONAL MONTHS: 14 (tredicesima Art. 52 + quattordicesima Art. 53 CCNL). Tredicesima paid at year-end; quattordicesima paid 30 April. Both equal one full monthly retribuzione globale.
    
    SENIORITY: triennale (36 months), maximum 5 scatti. Euro amounts from Art. 54 CCNL 2022-2025 (aggregator-sourced: contratticcnl.it): Area1 EUR 11.36, Area2 EUR 10.33, Area3 EUR 8.99 per triennio. Amounts frazionabili at daily (÷26) and hourly (÷169) divisors.
    
    TAX SECTOR: AGRICOLTURA (new TaxSector). INPS rates: Gestione Previdenziale Speciale Agricola, OTI standard agriculture: employee 8.84%, employer 21.66%, total 30.50% (2026). Source: ciatreviso.it citing INPS 2026 rates.
    
    CNEL CODE: A011. Confirmed from ilccnl.it page header and contratticcnl.it/ccnl/a011/. CNEL archive (cnel.it) returned 404 at time of extraction.
    
    APPRENTICESHIP: sotto-inquadramento (under_classification) per Allegato n. 10 CCNL (23/02/2017 apprenticeship agreement, updated to D.Lgs. 81/2015). Area1 destination only — see SIMPLIFICATION note. Duration 36 months for Area1.
    
    HISTORICAL PERIODS ADDED (2026-09-09). Three salary periods now modelled per area: (1) 2023-01-01: INPS Circ. n.94/2024 Allegato 1 (primary source, Area1=1389.15, Area2=1266.90, Area3=944.62). (2) 2025-01-01: Dottrinalavoro Jan 2025 PDF (Area1=1458.61, Area2=1330.25, Area3=991.85). Cross-check: 2025 values / 2023 values = 1.050 (approx. +5% tranche per 2022-2025 CCNL). (3) 2026-06-01: first tranche of 2026-2029 renewal (+3.4%). 2023-01-01 is the earliest verified period; pre-2023 values not modelled.
    
    JANUARY 2027 TRANCHE. Amounts 1,533.84 / 1,398.86 / 1,043.00 computed as June 2026 values × 1.017 (second tranche +1.7% per CCNL renewal) rounded to 2 decimal places. Math verified: 1508.20×1.017=1533.84, 1375.48×1.017=1398.86, 1025.57×1.017=1043.00 (all exact). Update if official post-renewal tables show different rounding.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/operai-agricoli-florovivaisti.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/operai-agricoli-florovivaisti.py"
```
