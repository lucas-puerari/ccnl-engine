# CCNL Operai Agricoli e Florovivaisti — Coldiretti/Confagricoltura/CIA

| | |
|---|---|
| **CNEL code** | `A011` |
| **Sector** | agricoltura |
| **Family** | `agricoltura` |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2026-05-28 |
| **Workers (est.)** | ~600k |
| **Ruleset version** | `2026.2` |
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

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, bilateral_funds, inail, inps_employee, inps_employer, overtime, seniority, sickness, territorial_supplement |

16 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 11 verified / 6 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2026-05-28 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2026-06-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-14 | claude-opus-5-5 (ai) | P1 audit: the salary tranches of the renewal of 28 May 2026 against the signed verbale (Art. 50, Art. 54-bis, Allegato n. 1). | corrected | Allegato n. 1 prints the minimi of area 1532,999 / 1398,093 / 1042,434: the January 2027 salaries, compounded in the bundle (1533.84 / 1398.86 / 1043.00), are corrected to the printed minimi taken to the cent (1533.00 / 1398.09 / 1042.43) and verified.<br>June 2026: +3.4% of the 28 May 2026 salary (Art. 50): derived, the verbale prints no amount.<br>Art. 54-bis (0.4% for fixed-term workers with three years of 150 days) is new and not modelled: declared.<br>Art. 54 (seniority) is not amended by the verbale; the amounts stay aggregator-sourced (seniority_amounts_unconfirmed). |
| 2026-10-15 | claude-opus-5-5 (ai) | Registry check: CNEL code, name, signatories and term against the 21st CNEL report of CCNLs in force (30 June 2025) and the term clause of the text read in the P1 review. | confirmed | CNEL A011 matches; the verbale of 28 May 2026 is signed by Confagricoltura, Coldiretti and CIA with FLAI, FAI and UILA. The report also lists Assoverde, API, the family-farm federations and UGL Agroalimentare as parties of the earlier text.<br>Term: the verbale renews the CCNL 'scaduto il 31 dicembre 2025' and is titled 2026-2029 (quadriennale): 1/1/2026 to 31/12/2029. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'straordinario, notturno, festivo, turni e maggiorazioni cumulabili': the overtime bands and the night, holiday and shift premiums of the file against the text read in the P1 review. | flagged | The overtime bands (20% weekday, 40% night, 50% holiday) stay derived: the CCNL of 23 May 2022 is not published by a party, and the verbale of 28 May 2026 does not amend the overtime article. Provincial contracts may set higher rates. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'ferie, permessi, festività, assenze, malattia e comporto': the leave, accrual, absence and sickness rules of the file against the text read in the P1 review. | corrected | Ferie 26 working days (Art. 36, p. 22), comporto 180 days (Art. 61, p. 37) and daily divisor 26 (Art. 50, p. 29): match and verified, cited to the verbale of 28 May 2026 instead of an aggregator.<br>Art. 62 (p. 38) gives the florovivaisti an employer integration of 25% of the daily wage for 90 days a year that the single file cannot pay: declared as an outside-input limitation. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'scatti di anzianità, indennità e altri elementi fissi', re-read on the full text published by a party, found on 15 October 2026. | corrected | Art. 54 (p. 55): the scatti are biennial, not triennial: cadence corrected from 36 to 24 months; amounts 8,99 / 10,33 / 11,36 and the maximum of 5 match: verified. The super profiles (10,85 and 11,62) are declared. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'straordinario, notturno, festivo, turni e maggiorazioni cumulabili', re-read on the full text published by a party, found on 15 October 2026. | corrected | Art. 43 (p. 48): straordinario 25% (was 20%), straordinario festivo 40% (was 50%), notturno 40%, festivo notturno 45% (added): corrected and verified. The florovivaisti rates of Art. 44 (p. 49) are declared. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'part-time, tempo determinato, apprendistato e periodo di prova', re-read on the full text published by a party. | flagged | Allegato n. 10 (pp. 122-125): the under-classification counts provincial levels inside the areas, not the national areas the file uses: apprentice runs are now blocked by a limitation instead of paying the Area3 and Area2 minima. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'confrontare lordo, netto e costo azienda con esempi indipendenti': a run of the engine against the labour cost table of the Regione Toscana price list (Allegato 3, section 4, operai agricoli e florovivaisti, CCNL 2022-2025). | flagged | The table prices the provincial wages of Firenze, Arezzo and the other provinces, not the national area minima of the file: only its structure compares. TFR: 1.312,85 on 17.723,44 a year is 1/13.5, as the engine accrues (991.85 / 13.5 = 73.47 for Area3). Match.<br>Deviation: the table's employer contributions in zona normale are 35.37% of the pay including INAIL; the engine applies 33.953% including the 8.50% INAIL of INPS circ. 43/2026 (25.453% without it). Cause not established (the table states neither its year nor its composition beyond the INAIL share of 13.24%); decision: flagged, the engine keeps the rates of circ. 43/2026. No independent net pay example. |
| 2026-10-15 | claude-opus-5-5 (ai) | Closure of the divergence left open by the review 2026-10-15-ai-cost-check: the employer contributions against the labour cost table of the Regione Toscana price list. | confirmed | Year: the price list is the edition of December 2025 (file metadata 2 December 2025; the idraulico-forestale tables are dated 2025 and 2026), but its agricultural section (pp. 29-37) is headed 'CCNL operai agricoli e flovivaistici 2022-2025', prices the provincial wages of that contract and states 'in agricoltura i contributi inail sono compresi nell'inps e sono il 13,24% del totale'. The 2026 rates replace the INAIL share with the unified 8.50% of INPS circ. 43/2026, which the engine applies. The table's 35.37% (6.268,78 on 17.723,44, Firenze e Prato, comune) is built on rates before 2026 and does not split them further.<br>The engine keeps the 2026 rates of circ. 43/2026; the table compares for the TFR structure only.<br>Divergence (external_artifact_error): Employer contributions of an operaio comune in zona normale: 35.37% of the pay with INAIL in the Regione Toscana table against 33.953% with the 8.50% INAIL in the engine for 2026. Cause: The table applies the agricultural rates of the CCNL 2022-2025 years, INAIL included as 13.24% of the total, not the 2026 rates with the unified INAIL of INPS circ. 43/2026: it is no evidence for 2026 contributions. |
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Art. 52 - Tredicesima mensilità (p. 54-55): "l'operaio ha diritto a tanti dodicesimi dell'ammontare della tredicesima quanti sono i mesi di servizio prestati presso l'azienda. [...] La frazione di mese superiore ai quindici giorni viene considerata, a questi effetti, come mese intero.". Added: more_than 15 (the file applied the engine default, at least 15 days). |
| 2026-10-18 | claude-opus-5-5 (ai) | Base salaries (minimi salariali di area mensili, operai agricoli, Areas 1-3) of every period, checked against the signed verbali of 23 May 2022 and 28 May 2026. | corrected | The 2023 values (1.389,15 / 1.266,90 / 944,62) match Allegato n. 1, Tabella n. 1 of the signed verbale of 23 May 2022 (scanned, OCR plus visual check of p. 33).<br>Date of the 2023 period: Art. 49 of the 2022 verbale applies the minimi from 1 June 2022 in provinces without a CPL under the CCNL 19 June 2018 and, elsewhere, from the CPL renewal date and not later than 1 January 2025; the accord of 27 October 2023 brought that date forward to 1 January 2024. The file start 2023-01-01 comes from the INPS label 'in vigore dall'1.1.2023' and is not a date stated by the parties; the value is in force throughout the file period in provinces without a CPL.<br>The 2025 values are not printed in any signatory text found: they follow from the 2022 minimi plus 5% (accord of 27 October 2023, signed text not located; the rule is reported by Confagricoltura Rovigo and Belluno) and are confirmed exactly by the 2026 minimi, which equal them times 1.051. Area 2 rounds 1330.245 half-up to 1330.25, which is the base the 2026 table uses (1330.25 x 1.051 = 1398.093).<br>The 2027 values are printed to three decimals (1532,999 / 1398,093 / 1042,434) and kept rounded to the cent.<br>Art. 50 of the 2026 verbale applies the new minimi (which already include both tranches) from 1 June 2026 in provinces without a CPL renewed under the CCNL of 23 May 2022, and elsewhere from the CPL renewal date and not later than 1 January 2029. No text supports a national minimo of 1025.57 / 1375.48 / 1508.20 for June to December 2026: those figures apply the 3.4% first tranche (which raises provincial salari contrattuali) to the 2025 minimi. The 2026-06-01 periods are left unbacked.<br>Maintainer decision: the 2026-06-01 periods take the printed minimi of Allegato n. 1 (p. 52), +5.1%, replacing the file values built on +3.4% (1508.20, 1375.48, 1025.57); the 2027-01-01 periods carried the same printed minimi and are merged into them.<br>Corrected to the printed table: Area1 2026-06-01: 1508.20 -> 1533.00; Area2 2026-06-01: 1375.48 -> 1398.09; Area3 2026-06-01: 1025.57 -> 1042.43. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Area1` | Area 1 — Operai Specializzati (specialised agricultural workers) | € 1,533.00 | 2026-06-01 |
| `Area2` | Area 2 — Operai Qualificati (qualified agricultural workers) | € 1,398.09 | 2026-06-01 |
| `Area3` | Area 3 — Operai Comuni (unskilled general agricultural workers) | € 1,042.43 | 2026-06-01 |

## Seniority increments

**Cadence:** every 24 months  
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

    **Applies when:** `territorial_supplement` applies.

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

!!! warning "operai-agricoli-florovivaisti/super_profile_scatti · seniority · impact yes · open"
    SENIORITY OF THE SUPER PROFILES: Art. 54 (p. 55) pays 10,85 a month to the operai qualificati super and 11,62 to the specializzati super; the three areas of the file pay the amount of the qualificati (10,33) and of the specializzati (11,36), and the request does not say whether the operaio is a super profile.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the super profiles as levels with their scatto amounts.

!!! warning "operai-agricoli-florovivaisti/eban_fisa_agrifondo · bilateral_funds · impact yes · open"
    BILATERAL FUNDS. EBAN (Ente Bilaterale Agricolo Nazionale) and FISA (Fondo Integrativo di Settore Agricolo) bilateral fund contributions are set at provincial level and not modelled. Agrifondo (supplementary pension) contributions also omitted.

    **Applies when:** `bilateral_funds` applies.

    **Remediation:** Pass the provincial EBAN, FISA and Agrifondo contributions as bilateral fund events.

!!! note "operai-agricoli-florovivaisti/mountain_zone_reductions · inps_employer · impact yes · resolved"
    TERRITORIAL REDUCTIONS. INPS reductions for mountain/disadvantaged zones (75%/68%) are not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Resolved (review of 2026-10-30): EmployerProfile.agricultural_zone and contribution/zone/models.py with_zone_reduction apply the mountain and disadvantaged zone cuts of INPS circ. 43/2026 par. 7 (zone_reduction in contribution/2026/agricoltura.json); an unknown zone blocks the run. Tests: tests/integration/ccnl_engine/period/context/agreement/services/test_contract_agricultural_zone.py::test_mountain_zone_cuts_the_employer_contributions, ::test_unknown_zone_charges_the_full_rates_and_blocks.

!!! warning "operai-agricoli-florovivaisti/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "operai-agricoli-florovivaisti/apprentice_inps_rates_unsourced · inps_employer · impact unknown · open"
    APPRENTICE INPS RATES: the apprentice rates of the sector (agricoltura) apply the 10% of L. 296/2006 art. 1 c. 773 plus the 1.61% NASpI, but no source found settles the disoccupazione and CISOA contributions of agricultural apprentices (INPS circ. 43/2026 gives no apprentice rates). The contributions of an apprentice may differ.

    **Applies when:** `inps_employer` applies; contract type in apprentice.

    **Remediation:** Source the apprentice rates of agricoltura (an INPS circular or an association table of 2026), mark the apprentice block of contribution/2026/agricoltura.json derived, then remove this note.

!!! warning "operai-agricoli-florovivaisti/fixed_term_seniority_element · base_salary · impact yes · open"
    ELEMENTO AGGIUNTIVO DELLA RETRIBUZIONE (Art. 54-bis, new, verbale of 28 May 2026): from 1 January 2027 a fixed-term operaio who worked at least 150 days a year for the same employer for three consecutive years receives, from the fourth year, 0.4% of the salario contrattuale. The request carries no history of days per employer, so it is not paid.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the consecutive years of at least 150 days with the employer to the request and pay 0.4% of the salary, then remove this note.

!!! warning "operai-agricoli-florovivaisti/florovivaisti_sickness_integration · sickness · impact yes · open"
    FLOROVIVAISTI SICKNESS: the operaio florovivaista a tempo indeterminato receives from the employer, on top of the INPS indemnity, 25% of the contractual daily wage for at most 90 days a year, from the first day when the sickness lasts more than three days (Art. 62, verbale of 28 May 2026, p. 38); the file pays the operai agricoli rule, with no employer integration, and the request does not say whether the operaio is a florovivaista.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Split the florovivaisti into their own levels or file, with a sickness rule paying 25% of the daily wage for 90 days a year past the third day.

!!! warning "operai-agricoli-florovivaisti/florovivaisti_overtime_rates · overtime · impact yes · open"
    FLOROVIVAISTI OVERTIME AND HOLIDAY WORK: the operai florovivaisti are paid 29% overtime, 40% holiday work, 48% night work, 50% holiday overtime and 55% night holiday work (Art. 44, p. 49), against the 25, 35, 40, 40 and 45% of the operai agricoli (Art. 43) the file pays; ordinary holiday work (35% and 40%) has no band. The request does not say whether the operaio is a florovivaista. The rates apply to the provincial salario contrattuale.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Split the florovivaisti into their own levels or file with the Art. 44 rates.

!!! warning "operai-agricoli-florovivaisti/agricoli_apprentice_provincial_levels · base_salary · impact unknown · open"
    APPRENTICESHIP (Allegato n. 10, CCNL 23 May 2022, pp. 122-123): two levels below the destination in the first 12 months, one level below in the next 12, the destination in the last 12 (Area 1 and 2: 36 months; Area 3: 24 months, from one level below, only for the highest provincial level of the area). The levels are the provincial professional levels inside each area, not the three national areas the file holds: the file places an Area1 apprentice at the Area3 and then the Area2 minimum, a reading the text does not support. A fixed-term apprentice operaio is never paid below the lowest level of the destination area (p. 125).

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Model the provincial levels of each area, or pass the apprentice classification of the provincial contract.

!!! warning "operai-agricoli-florovivaisti/cpl_minimi_timing · base_salary · impact yes · open"
    CPL TIMING: the minimi di area of the renewal of 28/05/2026 (Allegato n. 1, p. 52) apply from 1 June 2026 only in the provinces without a contratto provinciale di lavoro (CPL); where a CPL is in force they apply from its renewal, by 1 January 2029 at the latest (Art. 50, p. 30). The file applies them from 1 June 2026 everywhere: a worker in a province with a CPL not yet renewed is paid above the national floor in force for that province.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add an employer fact for the CPL status of the province, or pass the minimo in force as an input.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! note "sickness_inps_daily_base · sickness · impact unknown · resolved"
    The INPS share of a sick day is computed on the INPS daily base of the episode, on the days INPS pays (the weekdays of an operaio, every day but the national holidays on a Sunday of an impiegato, point 7.3 of INPS circ. 134368/1981): the retribuzione media globale giornaliera of the month before the illness (INPS circ. 134368/1981 point 11; circ. 55/2024 Allegato 1), whole or partial month, impiegato or operaio, or for the lavoratori dello spettacolo the average pay of the last 40 daily contributions, capped for a fixed-term worker (INPS circ. 132/2021 par. 2.4). The base is a fact of the payroll history the episode states (SicknessEpisode.inps_base).

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Resolved: the INPS share is computed on the base of every regime of the bundle; an episode that states no base the engine can read has the missing_fact issue sickness_inps_base_unknown (fact inps_base), which blocks the run. Tests: tests/integration/ccnl_engine/sickness/base/test_rules.py, tests/unit/ccnl_engine/sickness/base/test_rules.py.

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

!!! warning "maternity_daily_base · maternity_leave · impact unknown · open"
    The INPS maternity indemnity of an operaia, or of a leave whose month before was not worked in full, is 80% of the pay of the run over 30 with the rateo of the extra months, not of the pay of the month before the leave: art. 23 c. 5 D.Lgs. 151/2001 divides the pay of an operaia by the days worked or paid (or by the hours, when fewer than the contract), and the divisor of her daily rateo of the 13th is not settled by a primary source. The base of another worker over a whole month is computed from MaternityLeaveEvent.base_pay.

    **Applies when:** `maternity_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of an operaia (an INPS circular on art. 23 c. 5) and compute her base and that of a month not worked in full, then resolve this limitation.

### Without monetary impact

!!! note ""
    CNEL CODE A011 sourced from ilccnl.it and contratticcnl.it; unverified against CNEL archive (archive returned 404 at time of extraction). Code A014 belongs to a separate expired minority CCNL (ASNALI/FAGRI) — do not confuse.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.contratticcnl.it/agricoltura-florovivaisti/tabelle-retributive/ | tabella_retributiva | 2026-05-28 | [↗](https://www.contratticcnl.it/agricoltura-florovivaisti/tabelle-retributive/) |
| https://ciatreviso.it/contributi-inps-inail-2026-agricoli-aliquote-e-le-scadenze-per-operai-otd-e-oti/ | inps_circolare | 2026-01-01 | [↗](https://ciatreviso.it/contributi-inps-inail-2026-agricoli-aliquote-e-le-scadenze-per-operai-otd-e-oti/) |
| INPS Circolare n. 94 del 13/11/2024 — Allegato 1: minimi salariali mensili di area in vigore dall'1.1.2023 (Area1=1389.15, Area2=1266.90, Area3=944.62). Fonte primaria per periodi 2022-2025. | inps_circolare | 2024-11-13 | [↗](https://www.inps.it/content/dam/inps-site/it/scorporati/circolari-e-messaggi/2024/11/Circolare_14697/Allegati/15379_Circolare-numero-94-del-13-11-2024_Allegato-n-1.pdf) |
| Dottrinalavoro — Retribuzioni al 1° gennaio 2025: minimi OTI agricoltura (Area1=1458.61, Area2=1330.25, Area3=991.85). Confermato coerente con +5% su valori INPS Jan 2023. | tabella_retributiva | 2025-01-01 | [↗](https://www.dottrinalavoro.it/wp-content/uploads/2024/12/Retribuzioni-al-1_1_2025.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobated retribuzione tabellare minima (paga base + contingenza + EDR merged since 01/01/2009). Contingenza = 0.00 and EDR = 0.00 per ilccnl.it table. Single base_salary per area per period. Source: contratticcnl.it tabelle retributive, confirmed by research from ilccnl.it showing zero contingenza columns.
    
    RENEWAL: CCNL signed 23/05/2022 (valid 2022-2025), renewed 28/05/2026 (quadriennio 2026-2029, signed verbale). Art. 50: the provincial salari contrattuali in force on 28 May 2026 rise by 3.4% from 2026-06-01 and by 1.7% from 2027-01-01, not compounded; the minimi di area of Allegato n. 1 include both increases (base x 1.051) and apply from 2026-06-01 in the provinces without a CPL (see the cpl_minimi_timing limitation). The file models the minimi di area. No una tantum.
    
    LEVELS: Three national professional areas (OTI, Operai a Tempo Indeterminato, national minimums). Area1=Specializzati, Area2=Qualificati, Area3=Comuni. National table sets floor only; provincial contracts (contratti provinciali di lavoro) always exceed these minimums.
    
    HOURLY DIVISOR: 169 hours/month. Formula: 39 h/week × 52 weeks / 12 = 169.00 exactly. Confirmed by ilccnl.it divisore orario field (169) and daily divisor 26 (169 / 6.5).
    
    ADDITIONAL MONTHS: 14 (tredicesima Art. 52 + quattordicesima Art. 53 CCNL). Tredicesima paid at year-end; quattordicesima paid 30 April. Both equal one full monthly retribuzione globale.
    
    TAX SECTOR: AGRICOLTURA (new TaxSector). INPS rates: Gestione Previdenziale Speciale Agricola, OTI standard agriculture: employee 8.84%, employer 25.453% (of which IVS 21.66%) (2026). Source: ciatreviso.it citing INPS 2026 rates (review of 2026-10-30)
    
    CNEL CODE: A011. Confirmed from ilccnl.it page header and contratticcnl.it/ccnl/a011/. CNEL archive (cnel.it) returned 404 at time of extraction.
    
    HISTORICAL PERIODS ADDED (2026-09-09). Three salary periods now modelled per area: (1) 2023-01-01: INPS Circ. n.94/2024 Allegato 1 (primary source, Area1=1389.15, Area2=1266.90, Area3=944.62). (2) 2025-01-01: Dottrinalavoro Jan 2025 PDF (Area1=1458.61, Area2=1330.25, Area3=991.85). Cross-check: 2025 values / 2023 values = 1.050 (approx. +5% tranche per 2022-2025 CCNL). (3) 2026-06-01: minimi di area of the 2026-2029 renewal (Allegato n. 1, both increases included). 2023-01-01 is the earliest verified period; pre-2023 values not modelled.
    
    JANUARY 2027 TRANCHE: the minimi of area of Allegato n. 1 of the verbale of 28 May 2026, printed Area 1 1532,999, Area 2 1398,093, Area 3 1042,434 (the 28 May 2026 salary x 1.051) and paid to the cent: 1533.00 / 1398.09 / 1042.43. Until 14 October 2026 the bundle compounded the tranches (June 2026 x 1.017: 1533.84 / 1398.86 / 1043.00), 0.57 to 0.84 a month too much.
    

## Raw data

The contract file this page is generated from: [`agreement/operai-agricoli-florovivaisti.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/operai-agricoli-florovivaisti.json).

## Usage example

```python
--8<-- "docs/examples/agreement/operai-agricoli-florovivaisti/example.py"
```
