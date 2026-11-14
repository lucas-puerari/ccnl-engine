# CCNL Cooperative e Consorzi Agricoli

| | |
|---|---|
| **CNEL code** | `A016` |
| **Sector** | cooperative e consorzi agricoli — impiegati e operai agricoli |
| **Family** | `agricoltura` |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2024-07-19 |
| **Workers (est.)** | ~60k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - AGCI-Agrital
    - Confcooperative-Fedagripesca
    - Legacoop-Agroalimentare
    - FLAI-CGIL
    - FAI-CISL
    - UILA-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary |

2 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 34 verified / 8 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-07-19 |
| **Last review** | 2026-11-15 |
| **Latest salary tranche** | 2027-02-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-14 | claude-opus-5-5 (ai) | Second review of the agricoltura group: minimi conglobati of the eight levels in the four tranches, monthly payments, fixed-term operai and scatti, against the signed verbale of 19 July 2024. | corrected | The 32 minimi match the signed All. n. 1 (p. 19, a scanned page read from the image; each tranche equals the one before plus the printed aumento): verified.<br>14 monthly payments: the verbale names the 13ma and 14ma for the operai a tempo indeterminato (p. 14) but restates no clause for the impiegati: derived, no longer assumed.<br>Fixed-term operai are owed a terzo elemento of 30.44% instead of the monthly payments (p. 14): not modelled and not declared; now a limitation.<br>Scatti are not in the verbale: derived. The file applies the impiegati maximum of 12 to the operai, whose maximum is 5; the note said so but did not block: now a limitation from the 6th biennale. |
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 34 - 13ma e 14ma mensilita' (p. 52): "La frazione di mese superiore a 15 giorni viene considerata come mese intero.". Match: more_than 15. |
| 2026-11-05 | claude-opus-5-5 (ai) | The seniority increments of the apprentices, Art. 24 - Apprendistato (PDF p. 40), found by a separate research session and checked again on the page. | corrected | The apprentice has the treatment of the permanent staff: seniority_increments.apprentice_level_amount. |
| 2026-11-05 | claude-opus-5-5 (ai) | Artt. 49 and 61 (PDF pp. 67, 81) of the stesura of 3 August 2022, text layer. | corrected | Operai: at most 5 increments, not the 12 of the impiegati; impiegati of levels 3, 4, 6, 7: 26.86, 24.79, 23.76, 22.21, not the operai amounts the file paid them. |
| 2026-11-08 | gpt-6-sol (ai) | Open limitations claimed to be no longer gaps: one session read the clauses and the data, a second independent session checked the claim. | confirmed | operai_seniority_over_five: Art. 61 caps permanent operai at five biennial increments, not six at 144 months. The agreement already specifies cadence_months=24, maximum_count_by_category.operaio=5 and the 2006-07-01 category-specific amounts for levels 3–7. compensation/element/services.py passes worker_cat |
| 2026-11-08 | claude-opus-5-5 (ai) | Art. 60 of the verbale of 19 July 2024 (scanned pp. 14-15, read on the page images). | corrected | Added parameters.fixed_term_pay for the OTD: hourly pay with the 30.44% terzo elemento and twelve monthly payments.<br>Added the 8.63% TFR of art. 66 (stesura 2019-2023, p. 85) and took the terzo elemento out of the TFR base.<br>Chiarimento a verbale p. 86: the overtime hours worked with 'costanza e continuità' accrue the TFR at the 8.63% of art. 66 (no other rate; an independent reading found no reference to the 10% of the CCNL operai agricoli): parameters.fixed_term_pay.overtime_tfr_rate 0.0863. |
| 2026-11-14 | claude-opus-5-5 (ai) | Art. 24 apprenticeship of the text signed 3 August 2022 (PDF p. 40), against the research of a separate model session. | corrected | The file paid apprentices 100% of the destination level; art. 24 pays by under-classification. Tracks added; the impiegati skip of the 5th level and the seasonal track remain a limitation. |
| 2026-11-15 | claude-opus-5-5 (ai) | Comporto of several illnesses, against the research of a separate model session; quote checked on the source text. | corrected | Added the comporto window of the CCNL. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1` | Livello 1° | € 2,303.40 | 2027-02-01 |
| `2` | Livello 2° | € 2,070.77 | 2027-02-01 |
| `3` | Livello 3° | € 1,906.06 | 2027-02-01 |
| `4` | Livello 4° | € 1,772.31 | 2027-02-01 |
| `5` | Livello 5° | € 1,685.38 | 2027-02-01 |
| `6` | Livello 6° | € 1,636.55 | 2027-02-01 |
| `7` | Livello 7° | € 1,518.40 | 2027-02-01 |
| `np` | Area non professionalizzati | € 1,280.82 | 2027-02-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 12 increments

| Level | Increment (monthly) |
|---|---:|
| `np` | € 0.00 |
| `2` | € 29.44 |
| `1` | € 33.05 |

## Apprenticeship

**professionalizzante (livelli 1-5)** (type: `under_classification`)  
Destination levels: `1`, `2`, `3`, `4`, `5`

**professionalizzante (livello 6)** (type: `under_classification`)  
Destination levels: `6`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "cooperative-consorzi-agricoli/apprenticeship_passthrough · base_salary · impact yes · open"
    APPRENTICESHIP (art. 24, text signed 3 August 2022 p. 40, unchanged by the renewal of 19 July 2024): destinations 1st-6th by under-classification (two levels below, one below, destination; the 6th after the first 12 months). Not modelled: the impiegati skip the 5th level, reserved to operai ('la progressione dei livelli sarà ad esempio la seguente: 7°-6°-4°, 6°-4°-3°'), so an impiegato apprentice destined to the 4th or 3rd is paid one level too high in the first or second period; and the apprentices of seasonal cycles, one level below for half the period and then the destination.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Skip the 5th level for impiegati apprentices and model the seasonal-cycle track of art. 24.

!!! warning "cooperative-consorzi-agricoli/otd_terzo_elemento_missing · base_salary · impact yes · open"
    OTD (Art. 60, verbale 19 July 2024, pp. 14-15; Art. 66 of the stesura 2019-2023, p. 85): a fixed-term operaio is paid the hours worked (PeriodFacts.ordinary_hours_worked, minimo over 169) with the terzo elemento of 30.44% on them and on the overtime hours, outside the TFR base; TFR 8.63% of the minimo, and of the minimo of the overtime hours worked with 'costanza e continuità' (OvertimeEvent.non_occasional; p. 86); no extra month and no leave pay accrue (parameters.fixed_term_pay). Not modelled: the terzo elemento and the TFR on the salario integrativo of the second level, which the bundle does not hold; the balance of the ferie the OTD still takes, unpaid ('mera anticipazione economica').

    **Applies when:** `base_salary` applies; contract type in fixed_term; category in operaio.

    **Remediation:** Model the salario integrativo and the TFR of the non-occasional overtime hours.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

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

!!! warning "inps_minimum_base_exempt_category · inps_employer · impact unknown · open"
    D.L. 463/1983 art. 7 c. 5 keeps the operai agricoli out of the 9.50% minimum daily base, and the run applies no minimum to them. Tabella A of INPS circ. 6/2026 still lists 51.70 for the operai agricoli, 'non soggetto all'adeguamento' of art. 7 c. 1; no source found says whether it is a floor of their contribution base. A base below it may understate the contributions.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Source the role of the 51.70 of the operai agricoli (INPS circ. 43/2026 on the agricultural contributions, or the minimum daily wages of art. 1 L. 389/1989), then apply it as their minimum or record that none applies.

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
| Verbale di accordo 19/07/2024 All. n.1: tabelle retributive conglobate per 8 livelli (1-7+np), 4 tranches 2024-2027. Seniority: Art. 61 (operai) e Art. 49 (impiegati). Indennità funzione quadri Art. 45 rivisitata dal 01/08/2024. | tabella_retributiva | 2024-07-19 | [↗](https://www.flai.it/wp-content/uploads/2018/11/CCNL-Cooperative-e-consorzi-agricoli-2024-2027.pdf) |

??? note "Coverage notes"
    CCNL A016 — Cooperative e Consorzi Agricoli. Conglobated model. 8 livelli: np-7-6-5-4-3-2-1. Divisore 169, 14 mesi. 4 tranches: apr-2024, mag-2025, mag-2026, feb-2027.
    
    Quadri: i livelli 1Q e 2Q del precedente impianto corrispondono a livello 1° e 2° con aggiunta dell'indennità di funzione quadri (Art. 45): 1Q +EUR 180→230/mese, 2Q +EUR 125→160/mese dal 01/08/2024. Modellata come fixed_allowance a 14 mensilità su ciascun livello.
    
    APPRENTICE SENIORITY (Art. 24 - Apprendistato, p. 40 of https://www.uila.eu/web/wp-content/uploads/2022/04/03_08_2022-STESURA-CCNL-COOPERATIVE-AGRICOLE-2019-2023.pdf, sha256 586ec86c279b9cf2484217d15e0e663985d32c3ed31a4e649e1574a1f594004b): 'A tutti gli apprendisti operai, in quanto lavoratori a tempo indeterminato si applicano le norme del CCNL relative a tale categoria pertanto agli stessi gli istituti contrattuali saranno corrisposti alle normali scadenze e non attraverso il terzo elemento. Analogamente agli apprendisti impiegati sarà garantito lo stesso trattamento previsto per gli altri impiegati a tempo indeterminato.' Reading: the apprentice matures the increments of the level, at its amounts (seniority_increments.apprentice_level_amount). The renewal of 19 July 2024 does not amend art. 24.
    
    APPRENTICE INPS RATES (contribution/2026/agricoltura.json): employer 10% plus NASpI 1.61% (INPS circ. 108/2018 par. 3.2, applied to the agricultural contribution by circ. 116/2013 par. 1) plus CISOA 1.50% (circ. 1/2023; 'CIS operai agricoli 1,5000' of circ. 43/2026 allegato 1) = 13.11% (4.61% and 6.11% in the first two years up to nine employees); worker 5.84%.
    
    COMPORTO OF SEVERAL ILLNESSES (Conservazione del posto, operai agricoli a tempo indeterminato, PDF p. 113, https://www.flai.it/wp-content/uploads/2018/11/CCNL-per-i-lavoratori-dipendenti-di-cooperative-e-consorzi-agricoli-2024-2027.pdf, sha256 2a3ccfd23d9545f5614e7af245eb51f60e89c323b1797b81b336d2d2d79e153e): 'L'operaio agricolo a tempo indeterminato, nel caso di malattia o di infortunio non sul lavoro, ha diritto alla conservazione del posto per un periodo di 180 giorni, anche per più eventi, nell'arco degli ultimi 12 mesi.' Modelled as sickness_rules.comporto_windows: 180 days within the 12 months before the day; the 12 months of a grave oncological illness in 18 are not modelled.
    

## Raw data

The contract file this page is generated from: [`agreement/cooperative-consorzi-agricoli.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/cooperative-consorzi-agricoli.json).

## Usage example

```python
--8<-- "docs/examples/agreement/cooperative-consorzi-agricoli/example.py"
```
