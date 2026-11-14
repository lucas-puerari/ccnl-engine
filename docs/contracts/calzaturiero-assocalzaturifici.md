# CCNL per i lavoratori addetti all'industria delle calzature

| | |
|---|---|
| **CNEL code** | `D121` |
| **Sector** | industria |
| **Family** | `pelli-calzature` |
| **Tax sector** | `industria` |
| **Last renewal** | 2024-07-17 |
| **Workers (est.)** | ~75k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Assocalzaturifici
    - FILCTEM-CGIL
    - FEMCA-CISL
    - UILTEC-UIL

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
| **Rule provenance** | 32 verified / 6 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-07-17 |
| **Last review** | 2026-11-15 |
| **Latest salary tranche** | 2026-08-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-11-06 | claude-opus-5-5 (ai) | CCNL Calzaturiero, text of 17 July 2024: art. 46 seniority (p. 97). | corrected | Four biennial increments and a fifth after four years, not five triennial; the amounts per level match. |
| 2026-11-08 | claude-opus-5-5 (ai) | The monthly values of the levels against the primary tables (text layer). | confirmed | 32 values found verbatim on the cited pages and marked verified; 0 left as they were (derived or not on a text page). |
| 2026-11-14 | claude-opus-5-5 (ai) | Art. 23 apprenticeship pay of the text of 17 July 2024 (p. 52). | corrected | The percentage applies to the minimo contrattuale only: the quadri function allowance is not reduced.<br>The lower rates of the Objective 1 areas were not recorded: now a limitation. |
| 2026-11-15 | claude-opus-5-5 (ai) | Comporto of several illnesses, against the research of a separate model session; quote checked on the source. | corrected | Added the comporto window of the CCNL; the pay bands across episodes stay under the engine limitation sickness_cumulation_window. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `8` | 8th level - Managers and workers with high-responsibility functions | € 2,509.13 | 2026-08-01 |
| `7` | 7th level - Workers with managerial functions | € 2,355.70 | 2026-08-01 |
| `6` | 6th level - Workers with high specialisation | € 2,163.79 | 2026-08-01 |
| `5` | 5th level - Workers with coordination duties | € 2,054.43 | 2026-08-01 |
| `4` | 4th level - Workers with intermediate duties | € 1,980.50 | 2026-08-01 |
| `3S` | 3rd level Super - Specialist workers with higher-grade duties | € 1,933.07 | 2026-08-01 |
| `3` | 3rd level - Specialist workers | € 1,891.45 | 2026-08-01 |
| `2S` | 2nd level Super - Qualified workers with higher-grade duties | € 1,832.71 | 2026-08-01 |
| `2` | 2nd level - Qualified workers | € 1,796.40 | 2026-08-01 |
| `1` | 1st level - Entry-level workers | € 1,557.00 | 2026-08-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

## Apprenticeship

**prof_L6_L8** (type: `percentage`)  
Destination levels: `6`, `7`, `8`  
percentage: 1.00

**prof_L3_L5** (type: `percentage`)  
Destination levels: `3`, `3S`, `4`, `5`  
percentage: 1.00

**prof_L2** (type: `percentage`)  
Destination levels: `2`, `2S`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! note "calzaturiero-assocalzaturifici/seniority_secondary_source · seniority · impact unknown · resolved"
    SENIORITY (Art. 46, p. 97 of the text of 17 July 2024): five increments, 'i primi quattro con cadenza biennale ed il quinto dopo un quadriennio', of 6.89 (1st) to 12.24 (8th) EUR a month.

    **Applies when:** `seniority` applies.

    **Remediation:** Resolved: cadence and amounts read in art. 46 of the 2024 text on 2026-11-06.

!!! warning "calzaturiero-assocalzaturifici/objective_one_apprentice_rates · base_salary · impact yes · open"
    OBJECTIVE 1 AREAS (art. 23, p. 52): 'Nelle aree di cui all'obiettivo 1 del regolamento 93/2081/CEE ... la retribuzione degli apprendisti è stabilita nelle seguenti misure: 70% ... 80% ... 90% del minimo contrattuale del livello assegnato'; the Protocollo sul Mezzogiorno names Basilicata, Calabria, Campania, Puglia, Sardegna and Sicilia. The request has no workplace region, so every apprentice takes 80/90/100%.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** State whether the workplace is in an Objective 1 region and pay the apprentice 70/80/90% there.

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

!!! note "tfr_compensation_apprentice_guarantee_fund · inps_employer · impact yes · resolved"
    An apprentice whose TFR goes to a pension fund or to the Fondo Tesoreria takes the 0.28-point relief of D.L. 203/2005 art. 8 and no Fondo di garanzia exemption: the 10% apprentice rate of L. 296/2006 art. 1 c. 773 is split by the D.M. 28 marzo 2007 among FPLD 9.01, CUAF 0.11, malattia 0.53, maternità 0.05 and INAIL 0.30, with no Fondo di garanzia share to exempt.

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the apprentice rate holds no Fondo di garanzia share, so none is exempted.

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
    The days of parental leave beyond the indemnified months are paid 30% when the parent's individual income (ParentalLeaveEvent.individual_income) is below 2.5 times the yearly trattamento minimo di pensione (art. 34 c. 3 D.Lgs. 151/2001); a year whose minimum the INPS has not published yet (2027) pays them nothing.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Add the trattamento minimo of each new year to the parental rates when the INPS circular publishes it.

!!! warning "parental_month_split · parental_leave · impact unknown · unsourced"
    When a counter of the parental leave (a rate band or the indemnified months) ends inside a calendar month of the leave that is not of thirty days, the engine pays the days of that month in order, one day of counter each and the last day what is left of the thirty: INPS counts the calendar month as one month (FAQ congedo parentale 2024, n. 10) but no source says which of its days fall in which band.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source how INPS splits a calendar month between two rates of the parental leave and apply it, then resolve this limitation.

!!! warning "parental_extra_month_share · parental_leave · impact unknown · unsourced"
    The days of parental leave accrue the 13th and the other extra months in full at the employer's charge (art. 34 c. 5 D.Lgs. 151/2001: the leave does not reduce them), while the INPS indemnity is computed on a base that already holds their daily rateo (art. 23 c. 2, INPS circ. 122/2022): no source read settles whether the employer's extra month is reduced by the share INPS pays, so the rateo of a month on leave may be overstated.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source how the extra months of a parental leave are split between INPS and the employer and net the INPS share from the employer's rateo, then resolve this limitation.

!!! warning "parental_hourly_ccnl_rule · parental_leave · impact unknown · open"
    A parental leave by the hour takes half the average daily hours a day and counts two such days as one day of leave, the general criterion of art. 32 c. 1-ter D.Lgs. 151/2001 (INPS circ. 152/2015 par. 2.2). A national CCNL rule that sets other hours to a day of leave or other rules of cumulation prevails (art. 32 c. 1-bis), and the bundle holds none; a company or territorial agreement is the fact local_hourly_agreement of the event. Same-day cumulation with the other permits and rests of the decree, which the criterion excludes, is not checked.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the collective rules on the leave by the hour of the CCNL (hours of a day of leave, cumulation) and apply them, then resolve this limitation.

!!! warning "disability_permit_tfr · disability_permits · impact unknown · unsourced"
    The days of permit under L. 104/1992 art. 33 c. 3 keep the TFR base, as payroll practice holds; art. 2120 c. 3 c.c. keeps in the TFR base only the absences of art. 2110 c.c. and the wage integration, and no primary source read says the permits are among them, so the TFR quota of a month with permits may be overstated.

    **Applies when:** `disability_permits` applies; the run takes the engine code path.

    **Remediation:** Source the TFR treatment of the permit days (an INPS or Ministry ruling, or case law of the Cassazione) and apply it, then resolve this limitation.

!!! note "notice_indemnity_partial · termination_notice · impact unknown · resolved"
    A notice partly worked pays the share of its calendar days left of the indemnity the CCNL band gives in monthly pays; the CCNL clause read (Federmeccanica Sez. Quarta Tit. VIII Art. 1) states the indemnity of the whole notice only, and practice also measures the rest by 30ths or 26ths of the monthly pay.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Resolved: art. 2118 c. 2 c.c. (https://www.normattiva.it/atto/caricaArticolo?art.versione=1&art.idGruppo=267&art.flagTipoArticolo=2&art.codiceRedazionale=042U0262&art.idArticolo=2118&art.idSottoArticolo=1&art.idSottoArticolo1=10&art.dataPubblicazioneGazzetta=1942-04-04&art.progressivo=0&, sha256 834213e542e77f0f1079835b14c444432e208be59a9d3d4c859ff5ede6c8e11d): 'un'indennità equivalente all'importo della retribuzione che sarebbe spettata per il periodo di preavviso'; a notice partly worked owes the pay of the days left, as the engine computes. How a day of that pay is measured stays the declared residual notice_indemnity_day_measure. Read on 2026-11-15.

!!! note "notice_indemnity_extra_months · termination_notice · impact yes · resolved"
    The indemnity is the monthly pays of the CCNL band on the monthly pay of art. 2121 c.c.; the 13th and 14th the notice would have accrued are not added, although art. 2121 counts 'ogni altro compenso di carattere continuativo', so the indemnity may be understated.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Resolved: art. 2121 c. 1 c.c. (Normattiva, https://www.normattiva.it/atto/caricaArticolo?art.versione=2&art.idGruppo=267&art.flagTipoArticolo=2&art.codiceRedazionale=042U0262&art.idArticolo=2121&art.idSottoArticolo=1&art.idSottoArticolo1=10&art.dataPubblicazioneGazzetta=1942-04-04&art.progressivo=0, sha256 d0e0175efc4dd4c7e4cc4d8431ed107547531932ccfc6dc5e078b94f0a45e7ec): 'L'indennità di cui all'articolo 2118 deve calcolarsi computando [...] ogni altro compenso di carattere continuativo'. The indemnity carries the rateo of the extra months; read on 2026-11-15.

!!! note "notice_indemnity_tfr · termination_notice · impact yes · resolved"
    The notice indemnity enters the TFR base only when the CCNL puts it there: the Cassazione holds that it is out of it, being referable to a period not worked after the end of the employment, and art. 2120 c. 2 c.c. leaves a different rule to the collective agreement.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Resolved: the indemnity is out of the TFR base unless the CCNL notice sets tfr_base true.

!!! warning "notice_indemnity_day_measure · termination_notice · impact unknown · unsourced"
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

!!! note "personal_withholding_same_kind · personal_withholdings · impact unknown · resolved"
    Two garnishments of the same kind, or two salary assignments, share the measure of their kind (a fifth, or the tenth or seventh of the agente della riscossione) in the order of notification: art. 545 c. 4 c.p.c. sets 'un quinto per i tributi ... ed in eguale misura per ogni altro credito' and art. 5 DPR 180/1950 a cessione 'fino al quinto', but no text read says how two orders of the same kind split the measure, so the later order may be under- or overstated.

    **Applies when:** `personal_withholdings` applies; the run takes the engine code path.

    **Remediation:** Resolved: art. 553 c. 1 c.p.c. (Normattiva, https://www.normattiva.it/atto/caricaArticolo?art.versione=4&art.idGruppo=93&art.flagTipoArticolo=1&art.codiceRedazionale=040U1443&art.idArticolo=553&art.idSottoArticolo=1&art.idSottoArticolo1=10&art.dataPubblicazioneGazzetta=1940-10-28&art.progressivo=0&, sha256 b41bf831e63fcaacfe95231f9595da5d0e5619c162cc455a80632bba90c147cd): the judge 'le assegna in pagamento [...] ai creditori concorrenti' and 'L'obbligo di pagamento decorre, per il terzo, dalla notifica dell'ordinanza di assegnazione'. The amount each garnishment takes is the fact of its ordinanza: PersonalWithholding.installment, and two garnishments of one kind without it give the missing-fact issue personal_withholding_unassigned. Read on 2026-11-15.

!!! warning "mid_month_level_change · base_salary · impact unknown · unsourced"
    A promotion on a day other than the first of a month splits the monthly pay of the run between the level before and the new level by the payable days of the CCNL daily quota on each side of the promotion, component by component; the hourly quotas of the month (overtime, permits, absences) read the same split chain whatever the day of the event. The CCNL texts read (Commercio and Terziario art. 118, DMO art. 102) give the new level from the promotion but not how its month is split.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source how a month is split by a promotion inside it (a CCNL clause or an INPS or Ministry ruling) and price the events of the month at the terms of their day, then resolve this limitation.

!!! note "arrears_unused_deductions · contract_renewal_arrears · impact yes · resolved"
    The engine computes the rate of the separate taxation of arrears from PriorYearTaxFacts.net_income_biennio (art. 21 cc. 1, 3 TUIR) and reduces the tax by ArrearsEvent.unused_deductions, the deductions of artt. 12 and 13 cc. 1-2 the worker did not use in the years the arrears refer to (art. 21 c. 4). An arrears event that does not state them, among which the una tantum the engine pays itself, is taxed without the reduction, so the tax may be overstated.

    **Applies when:** `contract_renewal_arrears` applies; the run takes the engine code path.

    **Remediation:** Resolved: art. 21 c. 4 TUIR (Normattiva, https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art21!vig=, sha256 aafc3e5d5cd7254c7eb52e74051e86f1243b3a7b3cbadcd951daf7bc5e113fc6): 'Gli aventi diritto agli arretrati devono dichiarare al soggetto che li corrisponde l'ammontare delle detrazioni fruite per ciascuno degli anni cui si riferiscono'. The deductions are a fact the worker declares: ArrearsEvent.unused_deductions, and PriorYearTaxFacts.arrears_unused_deductions for the una tantum the engine pays as arrears; unstated, the run carries the missing-fact issue arrears_unused_deductions_unknown. Read on 2026-11-14.

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
| https://www.consulenza.it/Contenuti/News/news/9409/calzaturieri-industria-e-minimi-retributivi | tabella_retributiva | 2024-07-17 | [↗](https://www.consulenza.it/Contenuti/News/news/9409/calzaturieri-industria-e-minimi-retributivi) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=173 | tabella_retributiva | 2024-07-17 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=173) |
| https://www.businessonline.it/articoli/scatti-anzianita-contratto-calzaturiero-tabella-ogni-quanto-ci-sono-e-stipendio-di-quanto-aumenta.html | tabella_retributiva | 2024-07-17 | [↗](https://www.businessonline.it/articoli/scatti-anzianita-contratto-calzaturiero-tabella-ogni-quanto-ci-sono-e-stipendio-di-quanto-aumenta.html) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (minimi retributivi include paga base, contingenza, and EDR). Modeled as base_salary with fixed_allowances: [] for all levels, level 8 included (the IND_FUN of the quadri is not modelled). Confirmed by stable coefficient ratios across all tranche dates (review of 2026-10-30).
    
    LEVEL 1 SPECIAL TRANCHE: separate wage correction from 1 January 2025 (EUR 1,502.46, up from EUR 1,315.70 at Aug 2024), independent of standard tranche dates Aug 2024/Aug 2025/Aug 2026. Confirmed by fiscoetasse.com (rinnovo 2024) and web search: Jan 2025=1502.46, Aug 2025=1530.00, Aug 2026=1557.00. Modeled as a four-period series for level 1 only.
    
    Workers covered: approximately 75,000 (Assocalzaturifici member companies). Agreement signed 2024-07-17; valid 2024-01-01 to 2026-12-31.
    
    INPS rates from 2026-industria.json (same sector as metalmeccanico). IRPEF 2026 brackets applied (L. 199/2025).
    
    APPRENTICESHIP (professionalizzante): 80/90/100% in three periods. Total duration 36 months per Art. apprendistato. Period splits by level group: L6-L8=10/10/16m, L3-L5=11/11/14m, L2-L2S=12/12/12m. L1 not eligible as destination. Source: CCNL 2024-07-17 Assocalzaturifici (D121), circolare apprendistato; businessonline.it article 2024; kitech.it scheda D121.
    
    APPRENTICE SENIORITY (Art. 23 Apprendistato, p. 52 of the CCNL industria delle calzature 17 July 2024, https://www.falc.biz/wp-content/uploads/2025/03/CCNL-contratto-collettivo-nazionale-di-lavoro-calzaturiero-2024.pdf, sha256 fd48de9dd4aa81fd5ca97c3dd94099d085ac61666831e6da37fe2fbab19558cf): 'L’anzianità durante il rapporto di apprendistato è utile per la maturazione e per la corresponsione degli aumenti periodici di anzianità. Gli aumenti saranno commisurati alle stesse percentuali del minimo contrattuale': the level increments, reduced by the apprenticeship percentage (seniority_increments.apprentice_level_amount and apprentice_pct_scaled).
    
    APPRENTICESHIP PERCENTAGE (art. 23, p. 52 of the text of 17 July 2024): '80% [90%, 100%] del minimo contrattuale del livello assegnato', the increments 'commisurati alle stesse percentuali del minimo contrattuale': the percentage reduces the minimo only, so the quadri function allowance is not reduced (apprenticeship_pct_relevant false).
    
    COMPORTO OF SEVERAL ILLNESSES (Art. 58 B - Malattia, conservazione del posto e chiarimento a verbale, PDF p. 16, https://az-apim-cne-sa-0002-lgc-we.azure-api.net/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/194333, sha256 b9fd63ceec2324fdcf4b96702f89ab5ce1b31df489027e81b81caca4c4132866): 'L'obbligo di conservazione del posto per l'azienda cesserà comunque ove nell'arco di 30 mesi si raggiungano i limiti predetti anche con più malattie con esclusione, per entrambi i limiti, dei periodi di ricovero ospedaliero. [...] il periodo di conservazione del posto si considera nell'ambito di un periodo mobile da determinare con riferimento ai 909 giorni di calendario immediatamente precedenti. Il periodo di conservazione del posto di 13 mesi è pari a 394 giorni di calendario' Modelled as sickness_rules.comporto_windows: 394 days within 909 days before the day, hospital stays left out. The pay bands of the operai count by day of each illness; those of the impiegati and quadri (6 months in full, then half to the end of the comporto) say nothing on several episodes and are counted per illness.
    

## Raw data

The contract file this page is generated from: [`agreement/calzaturiero-assocalzaturifici.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/calzaturiero-assocalzaturifici.json).

## Usage example

```python
--8<-- "docs/examples/agreement/calzaturiero-assocalzaturifici/example.py"
```
