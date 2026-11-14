# CCNL Logistica, Trasporto Merci e Spedizione (Confetra)

| | |
|---|---|
| **CNEL code** | `I100` |
| **Sector** | logistica |
| **Family** | `trasporti-logistica` |
| **Tax sector** | `industria` |
| **Last renewal** | 2024-12-06 |
| **Workers (est.)** | ~430k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - AITI
    - ASSOESPRESSI
    - ASSOLOGISTICA
    - FEDESPEDI
    - FEDIT
    - FISI
    - TRASPORTOUNITO FIAP
    - ANITA
    - Confetra
    - FILT-CGIL
    - FIT-CISL
    - UILTrasporti

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | absence, base_salary, overtime |

7 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 70 verified / 3 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-12-06 |
| **Last review** | 2026-11-14 |
| **Latest salary tranche** | 2027-06-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-11 | claude-opus-5-5 (ai) | Every payable rule of the file (55 records) read again in the signed testo unico of the renewal of 6 December 2024 (Verbale di accordo 25 September 2025), published by Confetra; the URLs the file cited return 404. | corrected | Corrected: every one of the 36 salary periods. The base salary is the minimo plus the EPA of the tables of pp. 80-81 for non-travelling staff; the file held values about 88-110 EUR too high. The printed Totale of the 1 January 2027 table already includes the minimo increase of 1 June 2027; the Legacoop circular of 19 December 2024 (p. 2) confirms that January 2027 is an EPA-only step, so the period holds minimo plus EPA.<br>Corrected: the Quadri receive the indennità di funzione of 51.65 EUR a month (Art. 6 c. 4, p. 17), which the file lacked.<br>Corrected: the daily quota is 1/22 (Art. 61 c. 3, Sezione prima, p. 86), not 1/26, which applies to a six-day week of non-travelling staff and to Sezione seconda (Art. 73 c. 5).<br>Verified: 14 monthly payments (Artt. 18-19), the accrual of fractions over 15 days (Art. 18 c. 2, Art. 19 c. 2), seniority (Art. 17) and 22 days of leave (Art. 24). Pages are PDF page numbers, equal to the printed ones.<br>Assumed: sickness. Art. 63 A) c. 7-12 keeps the job 245 or 365 days and pays 3 months in full and 5 at half (up to 5 years of service) or 5 and 7, counted over 24 or 30 months; the cumulation model holds one window in whole years for every band, so the rule is not expressible and the file's 100% for 180 days is wrong.<br>Left derived: the overtime rates (30%, 50%, 65%, 75%, Art. 13 c. 6) match, but their start of 2023-05-01 is not stated; the level descriptions are paraphrases.<br>Not modelled: the EDR of Art. 60 c. 8 (10 EUR at level 3S, re-parametrised) for workers in service on 26 January 2011, which affects every entitlement, and level 6J and travelling staff. |
| 2026-10-12 | claude-opus-5-5 (ai) | Sickness rule of art. 63 A), now expressible with a window and steps per seniority band; readiness of the file. | corrected | The sickness rule was assumed (100% for 180 days, not the CCNL's): it is now 90 days in full and 150 at half within 24 months, comporto 245 days, up to 5 years of seniority; 150 in full and 210 at half within 30 months, comporto 365 days, above.<br>With no assumed or missing payable rule left and the salary tables, additional months, divisor and seniority verified on 2026-10-11, the file is promoted to reviewed. |
| 2026-10-12 | claude-opus-5-5 (ai) | Malattie particolarmente gravi (art. 63 cc. 8 and 12). | corrected | The serious illnesses of INPS circ. 95/2016 were a limitation (grave_illness): now paid in full for 18 months and left out of the comporto when SicknessEpisode.serious_illness says so. |
| 2026-10-14 | claude-opus-5-5 (ai) | P1 audit: the salary tables of pp. 80-81 for every tranche, the overtime rates of Art. 13 c. 6 and the remaining derived records. | corrected | The minimo plus EPA of every level at 1.1.2025, 1.1.2026, 1.1.2027 and 1.6.2027 match the bundle.<br>Overtime 30/50/65/75%: verified from 1 January 2025 (the start of the salary series); the unsourced start of 2023-05-01 is dropped.<br>The 50% of the sixth day of a five-day week is not modelled: declared.<br>The EDR of 2011 (re-parametrisation by level not stated) and of 2021 (TFR treatment contradictory, pp. 54 and 83) stay derived. |
| 2026-10-15 | claude-opus-5-5 (ai) | Registry check: CNEL code, name, signatories and term against the 21st CNEL report of CCNLs in force (30 June 2025) and the term clause of the text read in the P1 review. | confirmed | CNEL I100 matches; the report lists the same associations and FILT, FIT, UILTRASPORTI.<br>Term: 'Il presente contratto scadrà il 31 dicembre 2027' (testo unico), the same in the report. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'scatti di anzianità, indennità e altri elementi fissi': the scatti and fixed allowances of the file against the text read in the P1 review. | confirmed | EDR ex accordo 18 maggio 2021 (p. 82, personale non viaggiante): the nine amounts match (Quadri 12,80 to 6° 8,26); 13 mensilità, no effect on other institutes (p. 83). Verified.<br>EDR of Art. 60 c. 8 (p. 85, 10 euro at 3° Super, staff in service on 26 January 2011): the eight amounts match (Quadro 12,89 to 6° 8,26) and the file gates it with in_service_on 2011-01-26. Verified. The 5-euro table of p. 93 belongs to another article and is not modelled here.<br>Scatti (Art. 17) were verified in the P1 review; IND_FUN verified. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'part-time, tempo determinato, apprendistato e periodo di prova': the apprenticeship tracks and the part-time supplementary hours of the file against the text read in the P1 review. | corrected | Tabella A (p. 75) matches the standard track. Tabella B, 90, 95 and 100% for the profili artigiani, was not modelled: added as a track; an apprentice now names it.<br>Part-time supplementary hours at 18% (40% past the annual limit, Art. 56, p. 71): declared. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'fondi sanitari, previdenza complementare, bilateralità e quote a carico di lavoratore e datore': the pension, health and bilateral contributions of the file against the text read in the P1 review. | corrected | Priamo (Art. 50, pp. 63-64): 1% of the employer and 1% of the worker; no pension fund was modelled: added as an employer fund on the TFR base, derived because the text names the monthly pay.<br>Sanilog (150 euro a year, employer) and Ebilog (3,50 euro a month employer, 0,50 worker, or an EAR of 8 euro): declared. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'confrontare lordo, netto e costo azienda con esempi indipendenti': a run of the engine against the cost table of the Ministry of Labour (DD 135 of 19 December 2025, impiegati non viaggianti, January 2026). | flagged | Impiegato 3S with 3 scatti, January 2026: minimo plus EPA 2000.37 ((23.644,44 + 360) / 12), scatti 74.37 and EDR 10.00 a month match the table (p. 9); the TFR of the month is the table's TFR base over 13.5 less the 0.5% IVS offset. Match.<br>Deviation: the table applies an employer INPS rate of 29.44%; the engine applies 29.06% from 16 to 50 employees and 29.36% from 51. Cause not established (the table does not state the class of employer and size); decision: flagged for the INPS review of the logistica contribution class. Sanilog (165 euro) and Ebilog (46,20 euro) of the table equal the declared 150 and 42 euro plus the 10% solidarity contribution. INAIL 0.404%: not computed by the engine. No independent net pay example. |
| 2026-10-15 | claude-opus-5-5 (ai) | Closure of the divergence left open by the review 2026-10-15-ai-cost-check: the employer INPS rate against the cost table of the Ministry of Labour (DD 135/2025). | flagged | The table prints 'Inps (29,44%)' on every row, operai and impiegati non viaggianti alike (30,68% for the personale viaggiante), with no composition and no class of employer. The 0.08 points above the 29.36% of the engine fit more than one composition (the whole 0.90% CIGS and a 0.24% maternità, for one), and a single rate for operai and impiegati does not fit the industria class of the file, where the operai pay the 2.22% malattia. The class is not established.<br>Divergence (source_context_missing): Employer INPS rate of an impiegato non viaggiante, January 2026: 29.44% in DD 135/2025 against 29.06% (16-50 employees) or 29.36% (51 and more) in the engine. Cause: The table does not state the INPS class of the employer nor the composition of its rate; the class of the file (industria) is not confirmed. |
| 2026-10-16 | claude-opus-5-5 (ai) | Follow-up of the source_context_missing divergence of 2026-10-15-ai-divergences: the composition of the 29.44% of DD 135/2025 for the personale non viaggiante. | flagged | The INPS rate tables of January 2023 (reproduced by GIA Parma) have no row of 29.44%: impiegati of class industria pay 29.06% from 16 to 50 employees and 29.36% above. The 30.68% of the personale viaggiante of the same decree is the class industria rate of operai up to 15 employees (review 2026-10-16-ai-inps-composition of logistica-trasporto-confetra-viaggiante).<br>The composition of 29.44% and the class of the employer remain unknown; the divergence stays open and its limitation keeps blocking the runs. |
| 2026-10-17 | claude-opus-5-5 (ai) | The INPS sector of the employers of the CCNL against the INPS classification manual, after the review 2026-10-16-ai-inps-composition left the class of the employer open. | corrected | The Manuale di classificazione dei datori di lavoro of INPS (May 2021, ATECO 2007) classifies the activities of this CCNL in two sectors: autotrasporto, traslochi, movimento merci and corrieri in the industria (CSC 11501, 11505, 11507), magazzini di custodia, spedizionieri, intermediari dei trasporti and servizi logistici in the terziario (CSC 70401). The file applied the industria to every employer.<br>Corrected: meta.inps_sectors lists industria and terziario; EmployerProfile.inps_sector states the sector of the employer and the run reads its INPS rates, sickness cover and every rule that follows the sector; a run without it reads the industria with a missing_fact inps_sector blocker.<br>INPS circ. 71/2025 adopted ATECO 2025 from 1 April 2025 and announced a new edition of the manual; that edition was not found: the classification above is the one of the 2021 edition.<br>The 29.44% of DD 135/2025 for the personale non viaggiante is still no INPS rate of either sector: industria impiegati 29.06% (16 to 50 employees) and 29.36% (above 50), terziario 29.31% to 30.11%. The table states neither the class nor the composition; the engine follows the classification of the employer.<br>Divergence (accepted_external_variance): Employer INPS rate of an impiegato non viaggiante, January 2026: 29.44% in DD 135/2025 against 29.06% or 29.36% (industria) and 29.31% to 30.11% (terziario) in the engine. Cause: The cost table of the Ministry of Labour applies one rate to operai and impiegati and states neither the INPS class of the employer nor the composition of the rate; no composition of the INPS rates of the industria or of the terziario of 2026 gives 29.44%. INPS rates follow the CSC of the employer (art. 49 L. 88/1989), which the employer now states. |
| 2026-10-17 | claude-opus-5-5 (ai) | The rate of the supplementary hours of the part-time workers. | corrected | Art. 56 of the testo unico (p. 71), read in review 2026-10-15-ai-contracts (the Confetra site was down on 2026-10-17): supplementary hours at 18%, 40% past the yearly limit. The 18% band is added for OvertimeKind.SUPPLEMENTARY; the 40% needs the yearly count and is not modelled. |
| 2026-11-01 | claude-opus-5-5 (ai) | The notice clause (Art. 36, lett. a–d; artt. 18–19, p. 53–54 (art. 36); 42 (artt. 18–19)). | corrected | Notice bands by level, category and service checked against the PDF by a separate session (delegated search and independent verification): work_rules.notice. |
| 2026-11-01 | claude-opus-5-5 (ai) | Hourly base of the time supplements (art. 13 c. 8, art. 61 c. 1) and the supplements of ordinary Sunday and holiday work (art. 12 c. 4), read in the text layer of the testo unico. AI review only: the same model extracted and checked the values. | corrected | hourly_base_method gross_incl_allowances (was minimo_tabellare), now verified: the retribuzione globale of art. 61 c. 1 divided by 168 (art. 13 c. 8), without the EDR of 2021; the engine derives the hourly rate of an event without one.<br>individual_elements included: art. 61 c. 1 punto 3 counts 'eventuali altri aumenti comunque denominati'.<br>Band FESTIVO added: 50% on holiday work within the ordinary hours (art. 12 c. 4). The night (20/15/25%) and Sunday (20% by day, 50% by night) rates of art. 12 c. 4 are left out: they depend on the guardian role, the shift and the hours of the Sunday, which the request does not carry. |
| 2026-11-05 | claude-opus-5-5 (ai) | The daily divisor of a six-day week of the non-travelling staff, art. 61 c. 3, p. 86 of the testo unico. | confirmed | Art. 61 c. 3 divides by 26 the monthly pay of the non-travelling staff on a six-day week, by 22 otherwise: week_days_methods 6 -> by_26, read when Employment.full_time_week_days is 6. |
| 2026-11-05 | claude-opus-5-5 (ai) | Artt. 51-52 (PDF pp. 64-65) of the Testo Unico of 25 September 2025, text layer. | corrected | Sanilog and Ebilog, owed for every worker of the CCNL, were not modelled: employer cost and worker share were short. |
| 2026-11-06 | claude-opus-5-5 (ai) | Apprentice seniority: artt. 17 and 57 of the testo unico of 25 September 2025 (pp. 40-41, 73, 75). | corrected | Apprentices accrue the level increments in full: art. 17 c. 1 (pp. 40-41 of the testo unico of 25 September 2025) gives 'Ai lavoratori, per l'anzianità di servizio maturata presso la stessa azienda' a fixed amount of the level each biennio; art. 57 c. 7 (p. 73) counts the apprentice's probation 'agli effetti dell'anzianità di servizio'; cc. 8-9 and tables A-B (pp. 73, 75) apply the percentage to the 'minimo contrattuale' only. |
| 2026-11-08 | gpt-6-sol (ai) | CCNL top-ups of maternity and work injury, read from the signed text by a separate model session; every quote found on the PDF text layer. | confirmed | Added work_rules.insured_absence.maternity.<br>Added work_rules.insured_absence.injury. |
| 2026-11-08 | claude-opus-5-5 (ai) | Art. 71(1)(b,c), (5), cached PDF p. 93; Art. 60(2-3), p. 85. | confirmed | National weekday holidays are within art. 71(b,c); reduced sickness pay reaches full daily actual pay. Injury, patron saint and art. 60 coincident-holiday payment remain outside this rule.<br>A separate review found art. 71 c. 5 restricted to the Sezione seconda (ex Magazzini Generali): the holiday target is removed and kept as a limitation. |
| 2026-11-08 | claude-opus-5-5 (ai) | Art. 64 c. 1(b), cached Confetra PDF p. 90; maternity integration periods. | corrected | The sixth-month target is 50% inclusive of statutory indemnity, not an additional payment. |
| 2026-11-08 | claude-opus-5-5 (ai) | Level 6 junior classification and pay, PDF pp. 25, 41, 80, 82. | corrected | The 2025 minimum is 1464.53, the biennial step is 18.78, the separate element is 7.58, and the level ceases at the end of 2025; promotion after twelve months applies to hires since 2020. |
| 2026-11-08 | claude-opus-5-5 (ai) | Junior hire cohorts and mandatory cutoff, cached PDF pp. 25, 41, 80, 82. | corrected | The junior minimum of 1464.53 ends with 2025; 2018/2019/2020 cohorts wait 24/18/12 months. Later junior salary values only mirror level 6 to satisfy the no-gap invariant and are never paid; prior-level matured increments and unfinished biennia must be preserved or affected runs refused. |
| 2026-11-08 | claude-opus-5-5 (ai) | Art. 64 c. 1(b), cached Confetra PDF p. 90; sixth-month parental leave after compulsory maternity. | corrected | The sixth month of absence targets 50% of global pay inclusive of statutory indemnity even when the leave after compulsory maternity is parental. |
| 2026-11-09 | claude-opus-5-5 (ai) | Art. 56 supplementary hours on either side of the annual limit. | corrected | Art. 56, PDF p. 71: 'non possono superare, annualmente, il 30% della prestazione già concordata' at 18%; 'oltre il limite massimo complessivo annuale ... maggiorazione ... del 40%'. The 18% band remains; the 40% requires caller-split hours with an explicit multiplier because annual cumulative hours are unavailable. Corrected the limitation status to open. |
| 2026-11-09 | claude-opus-5-5 (ai) | Art. 71(5), section-two eligibility, physical PDF pp. 92-93; sickness and injury holiday targets. | corrected | Only employers covered before 29 January 2005 by the previous agreement qualify for the holiday top-up. |
| 2026-11-10 | claude-opus-5-5 (ai) | Cached Confetra consolidated text pp. 92-93, section-two eligibility and art. 71(5) injury holiday top-up. | confirmed | The existing conditional injury holiday target reaches full actual daily pay; the separate art. 60 coincident-holiday payment remains unmodelled. |
| 2026-11-10 | claude-opus-5-5 (ai) | Art. 60(1)(b), (2-4) coincident national holiday quota, cached consolidated text pp. 84-85. | confirmed | The national letter (b) holiday quota is 1/22 of monthly global pay on Saturday, Sunday or another holiday; local patron holidays are not calendared. |
| 2026-11-14 | gpt-6-sol (ai) | Part-time supplementary work clause, read by a separate model session. | confirmed | Confirmed: 18% of the hourly quota of the retribuzione globale up to 30% of the agreed annual hours, 40% past it (art. 56 cc. 16-17, PDF p. 70-71). |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro — quadro with high directional and managerial expertise | € 2,681.12 | 2027-06-01 |
| `1` | Level 1 — management role / area manager | € 2,496.84 | 2027-06-01 |
| `2` | Level 2 — operational unit manager / junior management role | € 2,302.61 | 2027-06-01 |
| `3S` | Level 3 Super — reference technical/operational expert or process manager | € 2,070.37 | 2027-06-01 |
| `3` | Level 3 — highly specialised operator / department coordinator | € 2,016.54 | 2027-06-01 |
| `4` | Level 4 — specialist operator (CED operator) | € 1,912.80 | 2027-06-01 |
| `4J` | Level 4 Junior — recently graded senior operator | € 1,865.27 | 2027-06-01 |
| `5` | Level 5 — qualified operator (specialist warehouse worker) | € 1,817.10 | 2027-06-01 |
| `6` | Level 6 — worker assigned to generic operational support tasks | € 1,703.67 | 2027-06-01 |
| `6J` | Level 6 junior — simple tasks requiring practical training | € 1,703.67 | 2027-06-01 |

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
| `6J` | — |

## Apprenticeship

**standard** (type: `percentage`)  
Destination levels: `1`, `2`, `3`, `3S`, `4`, `4J`, `5`, `6`  
percentage: 1.00

**profili_artigiani** (type: `percentage`)  
Destination levels: `1`, `2`, `3`, `3S`, `4`, `4J`, `5`, `6`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! note "logistica-trasporto-confetra/holiday_during_injury · sickness · impact yes · resolved"
    Art. 71(5) tops up letter (b) and (c) holidays in reduced paid sickness or injury for eligible legacy-section employers when EmployerProfile.legacy_section_applicable is true; an unknown fact blocks the target. The separate art. 60 coincident-holiday quota is calculated for national letter (b) holidays; the local patron holiday and any locally substituted day are not calendared.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Resolved: art. 71(5) injury holidays reach full actual daily pay for eligible legacy-section employers; the national coincident-holiday quota is calculated separately; local patron holidays remain outside the calendar.

!!! warning "logistica-trasporto-confetra/edr_2021_in_daily_base · absence · impact unknown · open"
    EDR: the EDR of EUR 10.33/month (agreement 26 Jan 2001) is conglobated into the minimum pay tables (Art. 61 note). The EDR of art. 60 c. 8 (workers in service on 26 January 2011) and the EDR of the agreement of 18 May 2021 (13 mensilità, no effect on other institutes) are paid as allowances; the 2021 EDR may still enter the daily base of absences and sickness, which 'nessuna incidenza su alcun istituto contrattuale' excludes.

    **Applies when:** `absence` applies.

    **Remediation:** Exclude EDR_2021 from the daily base of absences and sickness (a relevance flag on the allowance), or source that it enters it.

!!! warning "logistica-trasporto-confetra/sixth_day_overtime · overtime · impact yes · open"
    SIXTH DAY: Art. 13 c. 6 (p. 39) pays 50% for the overtime of the sixth day of a non-travelling worker whose normal week is spread over five days; the overtime bands have no such kind, so that overtime takes the 30% of the weekday band.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a sixth-day kind to the overtime event and a 50% band, then remove this note.

!!! note "logistica-trasporto-confetra/health_and_bilateral_funds · bilateral_funds · impact yes · resolved"
    HEALTH AND BILATERAL FUNDS (artt. 51-52, pp. 64-65): Sanilog EUR 150 a year from the employer for the permanent workers with the 10% INPS solidarity, Ebilog EUR 3.50 + 0.50 a month, and the EAR of EUR 8 on 12 months of an employer that does not pay Ebilog, when it states so in EmployerProfile.contractual_funds. The artisan section (EBNA, FSBA) is not modelled.

    **Applies when:** `bilateral_funds` applies.

    **Remediation:** Resolved: parameters.health_funds sanilog and ebilog, read on 2026-11-05.

!!! note "logistica-trasporto-confetra/inps_employer_class_unconfirmed · inps_employer · impact unknown · resolved"
    INPS CONTRIBUTION CLASS: the file applies the rates of the industria (impiegati 29.06% from 16 to 50 employees and 29.36% from 51, operai 31.28% and 31.58% with the 2.22% malattia). The cost table of the Ministry of Labour for this CCNL (DD 135 of 19 December 2025) applies 29.44% to operai and impiegati alike, and states neither the INPS class of the employer nor the composition of the rate: the class of a logistica employer is not confirmed, and the employer and worker contributions may differ.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Resolved: the employer states its INPS sector (EmployerProfile.inps_sector, industria or terziario by the CSC of its ATECO in the INPS manual); without it the run has a missing_fact inps_sector blocker. Tested in tests/integration/ccnl_engine/api/test_engine_modes.py.

!!! warning "logistica-trasporto-confetra/level_6j_apprenticeship · base_salary · impact yes · open"
    Level 6J uses the 2018, 2019 and 2020 hire cohorts until the mandatory 1 January 2026 promotion. Pre-2018 hires and apprentices before the cutoff are refused without verified prior classification or apprentice progression. Promotions with matured seniority increments are refused unless the worker states earned increments at their original amounts; that fact preserves the unfinished biennium.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Implement the separate 24-month apprentice classification progression for level 6J.

!!! warning "logistica-trasporto-confetra/part_time_supplementary_rate · overtime · impact yes · open"
    PART-TIME SUPPLEMENTARY HOURS: Art. 56 pays 18% of the global hourly pay on supplementary hours up to 30% of agreed annual hours, and 40% on the excess. The rate past the yearly share is paid when the event states the supplementary hours worked earlier in the year and the agreed annual hours (OvertimeEvent.supplementary_hours_before, agreed_annual_hours); without them the base rate is paid and the run carries this limitation. Saturday work has separate Art. 13 rates.

    **Applies when:** `overtime` applies; the run takes the engine code path.

    **Remediation:** State OvertimeEvent.supplementary_hours_before and agreed_annual_hours on the supplementary hours.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "apprenticeship_pct_undeclared_components · base_salary · impact unknown · open"
    A percentage apprenticeship reduces every fixed allowance whose apprenticeship_pct_relevant flag the data leaves at its default, together with the base salary. Whether the CCNL applies the percentage to that allowance (an EDR, a contingenza, a function allowance) was not sourced. The run is affected when such an allowance is in the apprentice's pay.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source, for each CCNL, the elements the apprenticeship percentage applies to and set apprenticeship_pct_relevant on every allowance; the limitation then no longer applies to its runs.

!!! note "sickness_inps_daily_base · sickness · impact unknown · resolved"
    The INPS share of a sick day is computed on the INPS daily base of the episode, on the days INPS pays (the weekdays of an operaio, every day but the national holidays on a Sunday of an impiegato, point 7.3 of INPS circ. 134368/1981): the retribuzione media globale giornaliera of the month before the illness (INPS circ. 134368/1981 point 11; circ. 55/2024 Allegato 1), whole or partial month, impiegato or operaio, or for the lavoratori dello spettacolo the average pay of the last 40 daily contributions, capped for a fixed-term worker (INPS circ. 132/2021 par. 2.4). The base is a fact of the payroll history the episode states (SicknessEpisode.inps_base).

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Resolved: the INPS share is computed on the base of every regime of the bundle; an episode that states no base the engine can read has the missing_fact issue sickness_inps_base_unknown (fact inps_base), which blocks the run. Tests: tests/mutation/ccnl_engine/sickness/base/test_rules_wiring.py, tests/mutation/ccnl_engine/sickness/base/test_rules.py.

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax ruleset marked provisional: the sources of its year are not published yet (budget law of the year; regional and municipal surtax resolutions), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

!!! warning "provisional_inps_ruleset · inps_employer · impact unknown · open"
    The run reads an INPS ruleset marked provisional: the INPS circulars of its year are not published yet, so the rates, the massimale and the minimale (and the hourly contributions of domestic work) are those of the year before, carried over. The indexed amounts change every January: the carried-over values understate them.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional INPS ruleset of the year with the values of the INPS circulars of the year, drop its provisional flag, then resolve this limitation.

!!! warning "tfr_compensation_apprentice_guarantee_fund · inps_employer · impact yes · open"
    An apprentice whose TFR goes to a pension fund or to the Fondo Tesoreria takes the 0.28-point relief of D.L. 203/2005 art. 8, but not the exemption from the 0.20% Fondo di garanzia contribution of D.Lgs. 252/2005 art. 10 c. 2: no source found says whether the apprentice rate (10% of L. 296/2006 art. 1 c. 773 plus NASpI and the integration funds) holds a Fondo di garanzia share to exempt. The employer contributions of the run may be overstated by 0.20% of the INPS base.

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Find an INPS source on the Fondo di garanzia share of the apprentice rate, then exempt it with the other workers or record that none is due.

!!! note "maternity_daily_base · maternity_leave · impact unknown · resolved"
    The INPS indemnity of the leave is computed on the pay of the month before, as the sickness base (art. 23 D.Lgs. 151/2001): an operaio's pay over the days worked or paid with the monthly share of the extra months over 25, a month not worked in full over its days worked or paid; the pay of the month before, its days and the pay of a whole month are facts of the leave, missing when not stated. The run keeps its own pay only when the category or the monthly payments of the CCNL are unknown.

    **Applies when:** `maternity_leave` applies; the run takes the engine code path.

    **Remediation:** Resolved: the base of an operaio and of a partial month is the sickness base of the month before.

!!! note "paternity_daily_base · paternity_leave · impact unknown · resolved"
    The INPS indemnity of the leave is computed on the pay of the month before, as the sickness base (art. 23 D.Lgs. 151/2001): an operaio's pay over the days worked or paid with the monthly share of the extra months over 25, a month not worked in full over its days worked or paid; the pay of the month before, its days and the pay of a whole month are facts of the leave, missing when not stated. The run keeps its own pay only when the category or the monthly payments of the CCNL are unknown.

    **Applies when:** `paternity_leave` applies; the run takes the engine code path.

    **Remediation:** Resolved: the base of an operaio and of a partial month is the sickness base of the month before.

!!! note "parental_daily_base · parental_leave · impact unknown · resolved"
    The INPS indemnity of the leave is computed on the pay of the month before, as the sickness base (art. 23 D.Lgs. 151/2001): an operaio's pay over the days worked or paid with the monthly share of the extra months over 25, a month not worked in full over its days worked or paid; the pay of the month before, its days and the pay of a whole month are facts of the leave, missing when not stated. The run keeps its own pay only when the category or the monthly payments of the CCNL are unknown.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Resolved: the base of an operaio and of a partial month is the sickness base of the month before.

!!! warning "parental_income_condition · parental_leave · impact unknown · open"
    The days of parental leave beyond the indemnified months (three of each parent and three of the couple, nine of a sole parent) are paid nothing: art. 34 c. 3 D.Lgs. 151/2001 pays them 30% when the parent's income is below 2.5 times the trattamento minimo di pensione, an income test and a yearly amount the engine does not model.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the yearly trattamento minimo and the income the test reads, take the income as a fact of the leave and pay the further days at 30% when the condition holds, then resolve this limitation.

!!! warning "parental_month_split · parental_leave · impact unknown · open"
    When a counter of the parental leave (a rate band or the indemnified months) ends inside a calendar month of the leave that is not of thirty days, the engine pays the days of that month in order, one day of counter each and the last day what is left of the thirty: INPS counts the calendar month as one month (FAQ congedo parentale 2024, n. 10) but no source says which of its days fall in which band.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source how INPS splits a calendar month between two rates of the parental leave and apply it, then resolve this limitation.

!!! warning "parental_extra_month_share · parental_leave · impact unknown · open"
    The days of parental leave accrue the 13th and the other extra months in full at the employer's charge (art. 34 c. 5 D.Lgs. 151/2001: the leave does not reduce them), while the INPS indemnity is computed on a base that already holds their daily rateo (art. 23 c. 2, INPS circ. 122/2022): no source read settles whether the employer's extra month is reduced by the share INPS pays, so the rateo of a month on leave may be overstated.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source how the extra months of a parental leave are split between INPS and the employer and net the INPS share from the employer's rateo, then resolve this limitation.

!!! warning "parental_hourly_ccnl_rule · parental_leave · impact unknown · open"
    A parental leave by the hour takes half the average daily hours a day and counts two such days as one day of leave, the general criterion of art. 32 c. 1-ter D.Lgs. 151/2001 (INPS circ. 152/2015 par. 2.2); a collective agreement, also of the company, that sets other hours to a day of leave or other rules of cumulation prevails, and the bundle holds none.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the collective rules on the leave by the hour of the CCNL (hours of a day of leave, cumulation) and apply them, then resolve this limitation.

!!! warning "disability_permit_tfr · disability_permits · impact unknown · open"
    The days of permit under L. 104/1992 art. 33 c. 3 keep the TFR base, as payroll practice holds; art. 2120 c. 3 c.c. keeps in the TFR base only the absences of art. 2110 c.c. and the wage integration, and no primary source read says the permits are among them, so the TFR quota of a month with permits may be overstated.

    **Applies when:** `disability_permits` applies; the run takes the engine code path.

    **Remediation:** Source the TFR treatment of the permit days (an INPS or Ministry ruling, or case law of the Cassazione) and apply it, then resolve this limitation.

!!! warning "notice_indemnity_partial · termination_notice · impact unknown · open"
    A notice partly worked pays the share of its calendar days left of the indemnity the CCNL band gives in monthly pays; the CCNL clause read (Federmeccanica Sez. Quarta Tit. VIII Art. 1) states the indemnity of the whole notice only, and practice also measures the rest by 30ths or 26ths of the monthly pay.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source how the CCNL or case law measures the indemnity of a notice partly worked and apply it, then resolve this limitation.

!!! warning "notice_indemnity_extra_months · termination_notice · impact yes · open"
    The indemnity is the monthly pays of the CCNL band on the monthly pay of art. 2121 c.c.; the 13th and 14th the notice would have accrued are not added, although art. 2121 counts 'ogni altro compenso di carattere continuativo', so the indemnity may be understated.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source whether the indemnity carries the rateo of the extra months (CCNL clause or case law) and add it, then resolve this limitation.

!!! note "notice_indemnity_tfr · termination_notice · impact yes · resolved"
    The notice indemnity enters the TFR base only when the CCNL puts it there: the Cassazione holds that it is out of it, being referable to a period not worked after the end of the employment, and art. 2120 c. 2 c.c. leaves a different rule to the collective agreement.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Resolved: the indemnity is out of the TFR base unless the CCNL notice sets tfr_base true.

!!! warning "notice_indemnity_day_measure · termination_notice · impact unknown · open"
    A CCNL that sets the notice in calendar days measures the indemnity on the pay of those days: the engine takes a calendar day as a 30th of the monthly pay; Commercio art. 209 refers the monthly pay to all the days of the calendar month, but its art. 210 sets the daily quota at 1/26 'in tutti i casi', so the indemnity may be understated.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source the daily measure of the notice indemnity of the CCNL (an interpretation of the parties or case law) and apply it, then resolve this limitation.

!!! note "extraordinary_leave_daily_base · extraordinary_leave · impact unknown · resolved"
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year, over 365 days (366 in a leap year), as INPS circ. 64/2001 par. 4 sets for a month worked full time; for a vertical part time the circular divides the pay of the month by its paid days, rest days included, which ExtraordinaryLeaveEvent.last_month_paid_days states. A vertical or mixed part time that does not state them is paid on the full-time measure, so its indemnity may be misstated.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Resolved: ExtraordinaryLeaveEvent.last_month_paid_days divides the pay of a vertical part time by its paid days (INPS circ. 64/2001 par. 4); a leave that does not state them is paid on the full-time measure with the provisional issue extraordinary_paid_days_unknown, which names the fact.

!!! note "naspi_dismissal_exceptions · naspi_dismissal · impact unknown · resolved"
    The NASpI contribution of the end of an employment that does not state its case (EmploymentPeriod.naspi_case) is read from the cause, the just cause and the contract type alone: a resignation in the protected period of maternity and a mutual agreement before the labour office or on a transfer over 50 km would owe it (INPS circ. 44/2013 par. 1), a collective dismissal would owe 82% for an employer owing the CIGS contribution (L. 205/2017 art. 1 c. 137) and three times without union agreement (L. 92/2012 art. 2 c. 35), the changes of contractor with a social clause and the closures of a construction site of c. 34 would leave it out. The service counts the fixed-term periods before the open-ended contract and leaves out the leave of art. 42 c. 5 D.Lgs. 151/2001 only through EmploymentPeriod.started_on.

    **Applies when:** `naspi_dismissal` applies; the run takes the engine code path.

    **Remediation:** Resolved: EmploymentPeriod.naspi_case states the cases that owe, leave out or multiply the contribution; an end that could be one and does not state it is decided from its cause alone with the provisional issue naspi_dismissal_case_unknown, which names the fact.

!!! warning "personal_withholding_same_kind · personal_withholdings · impact unknown · open"
    Two garnishments of the same kind, or two salary assignments, share the measure of their kind (a fifth, or the tenth or seventh of the agente della riscossione) in the order of notification: art. 545 c. 4 c.p.c. sets 'un quinto per i tributi ... ed in eguale misura per ogni altro credito' and art. 5 DPR 180/1950 a cessione 'fino al quinto', but no text read says how two orders of the same kind split the measure, so the later order may be under- or overstated.

    **Applies when:** `personal_withholdings` applies; the run takes the engine code path.

    **Remediation:** Source how the employer splits the measure between two orders of the same kind (art. 499 c.p.c. on the intervention of creditors, case law of the Cassazione) and apply it, then resolve this limitation.

!!! warning "mid_month_level_change · base_salary · impact unknown · open"
    A promotion on a day other than the first of a month splits the monthly pay of the run between the level before and the new level by the payable days of the CCNL daily quota on each side of the promotion, component by component; the hourly quotas of the month (overtime, permits, absences) read the same split chain whatever the day of the event. The CCNL texts read (Commercio and Terziario art. 118, DMO art. 102) give the new level from the promotion but not how its month is split.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source how a month is split by a promotion inside it (a CCNL clause or an INPS or Ministry ruling) and price the events of the month at the terms of their day, then resolve this limitation.

!!! warning "arrears_unused_deductions · contract_renewal_arrears · impact yes · open"
    The engine computes the rate of the separate taxation of arrears from PriorYearTaxFacts.net_income_biennio (art. 21 cc. 1, 3 TUIR) and reduces the tax by ArrearsEvent.unused_deductions, the deductions of artt. 12 and 13 cc. 1-2 the worker did not use in the years the arrears refer to (art. 21 c. 4). An arrears event that does not state them, among which the una tantum the engine pays itself, is taxed without the reduction, so the tax may be overstated.

    **Applies when:** `contract_renewal_arrears` applies; the run takes the engine code path.

    **Remediation:** State ArrearsEvent.unused_deductions from the worker's declaration of the deductions used each year; for the una tantum, carry it into the events the engine generates.

!!! warning "una_tantum_readings · base_salary · impact unknown · open"
    The una tantum of a renewal is paid from the CCNL data with readings no text read settles in full: a month of service in the covered period counts with the days of the una tantum (15 when the text is silent), over the months of the period; the absences of a month do not reduce it, though a text may pay the months 'di effettiva prestazione'; a part time is paid in proportion to its hours; a run without the employment period is paid none; the share of the covered months of earlier years is taxed apart as arrears.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source the counting of the months, the part time and the taxation of each una tantum from its agreement, then resolve this limitation.

!!! warning "sunday_holiday_ccnl_clause · sunday_holiday · impact yes · open"
    L. 260/1949 art. 5 pays the workers with a fixed salary a further daily quota only for the civil holidays (25 April, 1 May, 2 June) falling on a Sunday; the other holidays of art. 2 (1 January, 6 January, Easter Monday, 15 August, 4 October, 1 November, 8 December, 25 and 26 December) give it only by CCNL clause, and the payment of 4 November is a CCNL institute. A run of a month with such a holiday on a Sunday, in a CCNL whose clause is not sourced (work_rules.sunday_holidays), pays the statutory holidays only; a public employment is paid none, its treatment not being sourced.

    **Applies when:** `sunday_holiday` applies; the run takes the engine code path.

    **Remediation:** Source the CCNL clause on the holidays falling on a Sunday and record it as work_rules.sunday_holidays.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.confetra.com/wp-content/uploads/Nuovo-Testo-Unico-del-CCNL-logistica-trasporto-e-spedizione_pulito.pdf | altro | 2024-12-06 | [↗](https://www.confetra.com/wp-content/uploads/Nuovo-Testo-Unico-del-CCNL-logistica-trasporto-e-spedizione_pulito.pdf) |

??? note "Coverage notes"
    Art. 60 c. 2-3: the letter (b) holidays falling on a Saturday, a Sunday or another holiday are paid a further 1/22 of the monthly pay, also in sickness, injury, maternity, leave and permits; the patron saint of the place of work (EmployerProfile.patron_saint_day, or its locally agreed replacement stated there) is one of them.
    
    STAFF: tables for non-travelling staff (clerical employees and sedentary workers). The travelling staff (personale viaggiante, drivers and riders: letters C3 to L of pp. 25-26, tables pp. 81-82) is modelled in logistica-trasporto-confetra-viaggiante.
    
    CONGLOBATED MINIMUMS: base_salary values are the conglobated monthly minimum pay (minimum pay table + contingenza per Art. 61 note + EPA). Primary check: Art. 61 of the consolidated text September 2025 — 'From 1.1.2001 the indennità di contingenza has been conglobated into the minimum pay tables together with the EDR of EUR 10.33 per month'. fixed_allowances is empty for all levels.
    
    HOURLY DIVISOR: 168 hours/month. Primary source: Art. 61 para. 3 consolidated text September 2025 — 'The hourly pay is obtained by dividing the monthly pay by 168'.
    
    TRANCHES: four tranches for level 3S: 1.1.2025 +120 (minimo 90 + EPA 30), 1.1.2026 +40 (minimo), 1.1.2027 +30 (EPA), 1.6.2027 +40 (minimo 10 + EPA 30). Source: the tables of pp. 80-81 of the testo unico of 25 September 2025 and the Legacoop circular of 19 December 2024 (p. 2).
    
    ICE: the Indennità di Copertura Economica (ICE) was a provisional element in force until 31.12.2024. It ceases from 1.1.2025 with the renewal taking effect. base_salary values do not include ICE (ceased element). The consolidated text cites net increases of EUR 230 at 3S compared to the previous pay including ICE — the difference from the algebraic sum of the tranches (EUR 290 from base without ICE) corresponds to the pre-existing ICE value for that level.
    
    ADDITIONAL MONTHS: 14 (tredicesima Art. 18 + quattordicesima Art. 19 consolidated text September 2025).
    
    SENIORITY INCREMENTS: biennial (24-month cadence), max 5 biennial periods. Amounts from Art. 17 consolidated text September 2025. Non-travelling staff.
    
    EPA: Elemento Professionale d'Area, a component introduced by the 6.12.2024 renewal. Included in base_salary values from 1.1.2025. Not shown separately because it forms an integral part of the minimum pay (it affects all contractual and statutory entitlements) — see Confetra circ283-2024.
    
    INPS: meta.inps_sectors lists industria (contribution/2026/industria.json) and terziario (contribution/2026/terziario.json); EmployerProfile.inps_sector chooses, and without it the run reads the industria with a missing_fact inps_sector blocker (see the INPS SECTOR OF THE EMPLOYER note) (review of 2026-10-30)
    
    APPRENTICESHIP: percentage type from TABELLA A consolidated text September 2025. 75% year 1 (m1-12), 85% year 2 (m13-24), 100% from m25. Eligible levels: 1, 2, 3, 3S, 4, 4J, 5, 6 (level Q excluded). Maximum duration 36 months. Source: Art. 106 + TABELLA A consolidated text 09/2025 (contrattotrasporti.it).
    
    APPRENTICESHIP TABELLA B (testo unico p. 75): the profili artigiani and equivalent profiles (addetti al magazzinaggio, alla manutenzione veicoli, alla movimentazione) are paid 90% in the first year, 95% in the second and 100% after, not the 75 and 85% of Tabella A. The profile, not the level, selects the table: track 'profili_artigiani' beside 'standard'; set Apprentice.track.
    
    INPS SECTOR OF THE EMPLOYER: INPS classifies an employer by the activity it carries out (art. 49 L. 88/1989), not by the CCNL it applies. The Manuale di classificazione dei datori di lavoro of May 2021 (ATECO 2007, PDF pp. 199-206) gives CSC 11501 (industria, trasporti) to 49.41.00 trasporto di merci su strada and 49.42.00 traslochi, 11505 (industria) to 52.24 movimento merci and 52.21.90, 11506 to 52.21.40 interporti, 11507 to 53.20.00 corrieri, and 70401 (terziario, intermediari) to 52.10.10 magazzini di custodia e deposito, 52.29.10 spedizionieri, 52.29.21 intermediari dei trasporti and 52.29.22 servizi logistici. The employers of this CCNL are therefore in the industria or in the terziario: meta.inps_sectors lists both and EmployerProfile.inps_sector chooses; without it the run reads the industria and has a missing_fact inps_sector blocker. INPS circ. 71/2025 moved the classification to ATECO 2025 from 1 April 2025 and announced a new edition of the manual, not found in this review: the CSC above are those of the 2021 edition.
    
    Art. 71(5), section two, PDF p. 93: a holiday listed in (b) or (c) during paid, reduced sickness or injury is topped up to the full daily actual remuneration only for employers covered by the carried-forward section (eligibility on p. 92). EmployerProfile.legacy_section_applicable selects the target; an unknown fact blocks the holiday top-up. The section-two daily quota and other section-specific treatment remain unmodelled.
    

## Raw data

The contract file this page is generated from: [`agreement/logistica-trasporto-confetra.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/logistica-trasporto-confetra.json).

## Usage example

```python
--8<-- "docs/examples/agreement/logistica-trasporto-confetra/example.py"
```
