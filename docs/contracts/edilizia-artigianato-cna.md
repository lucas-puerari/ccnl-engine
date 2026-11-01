# CCNL Edilizia e Affini Artigianato

| | |
|---|---|
| **CNEL code** | `F015` |
| **Sector** | edilizia |
| **Family** | `edilizia` |
| **Tax sector** | `artigianato` |
| **Last renewal** | 2025-05-20 |
| **Workers (est.)** | ~350k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CNA Costruzioni
    - ANAEPA-Confartigianato
    - FIAE-Casartigiani
    - Feneal-UIL
    - Filca-CISL
    - Fillea-CGIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | bilateral_funds, inps_employer, pension_fund_contribution, seniority |

7 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 72 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-05-20 |
| **Last review** | 2026-09-18 |
| **Latest salary tranche** | 2028-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `7Q` | Quadro — manager with statutory Quadro status (Art. 2095 c.c., L. 190/1985) | € 2,358.36 | 2028-01-01 |
| `7` | Senior executive employee / site manager — site manager / senior technical staff | € 2,358.36 | 2028-01-01 |
| `6` | Technical employee / worker with supervisory duties — technical staff or team leader | € 2,097.48 | 2028-01-01 |
| `5` | Highly specialised worker — highly specialized worker | € 1,748.04 | 2028-01-01 |
| `4` | Specialised worker — specialized construction worker | € 1,628.40 | 2028-01-01 |
| `3` | First-category worker — skilled worker | € 1,515.12 | 2028-01-01 |
| `2` | Second-category worker — semi-skilled worker | € 1,358.35 | 2028-01-01 |
| `1` | Common worker — unskilled construction worker | € 1,165.30 | 2028-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 0.00 |
| `2` | € 9.86 |
| `3` | € 10.78 |
| `4` | € 11.54 |
| `5` | € 12.55 |
| `6` | € 15.92 |
| `7` | € 16.73 |
| `7Q` | € 16.73 |

## Apprenticeship

**standard_gruppo_4** (type: `percentage`)  
Destination levels: `4`  
percentage: 1.00

**standard_gruppi_1_3** (type: `percentage`)  
Destination levels: `3`, `4`, `5`  
percentage: 1.00

**specialistico_1sp** (type: `percentage`)  
Destination levels: `4`, `5`  
percentage: 1.00

**specialistico_2sp** (type: `percentage`)  
Destination levels: `3`, `4`  
percentage: 1.00

**specialistico_3sp** (type: `percentage`)  
Destination levels: `3`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "edilizia-artigianato-cna/seniority_cadence_unconfirmed · seniority · impact unknown · open"
    Seniority increment cadence (24 months) and maximum count (5) taken from general CCNL Edilizia Artigianato provisions; F015-specific text not independently confirmed. Level 1 scatto = EUR 0.00 as published in kitech.it.

    **Applies when:** `seniority` applies.

    **Remediation:** Confirm the 24-month cadence, the 5-scatti maximum and the level 1 amount against the F015 text.

!!! warning "edilizia-artigianato-cna/cassa_edile_accruals_missing · bilateral_funds · impact yes · open"
    For blue-collar workers in construction the Cassa Edile / EPR bilateral system provides additional accrual benefits (annual leave, Christmas bonus, seniority) that are separate from INPS seniority increments. These are not modelled; only the tabular seniority increments are implemented.

    **Applies when:** `bilateral_funds` applies; category in operaio.

    **Remediation:** Pass the Cassa Edile contributions as a bilateral fund event, or model the Cassa Edile system.

!!! warning "edilizia-artigianato-cna/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "edilizia-artigianato-cna/contractual_fund_uncovered · pension_fund_contribution · impact yes · open"
    The Prevedi table has no row for some levels of the bundle (a quadro level, or an operaio at a level the hourly table lacks): such a worker owes a contractual contribution the engine does not compute, and the run has the incomplete issue contractual_fund_not_computed.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Source the Prevedi amount of the levels without a row and add it, then remove this note.

!!! warning "edilizia-artigianato-cna/inps_sector_rates_unsourced · inps_employer · impact unknown · open"
    INPS RATES: the employer and worker INPS rates of the sector (artigianato) are totals no 2026 INPS or association table confirms: the only component split found is the INPS guide of 2012 and the 2026 totals come from a software house page that does not prove its year. The contributions of every run rest on them.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Source the artigianato rates of 2026 on an INPS or association table, mark the inps block of contribution/2026/artigianato.json derived, then remove this note.

!!! warning "edilizia-artigianato-cna/apprentice_inps_rates_unsourced · inps_employer · impact unknown · open"
    APPRENTICE INPS RATES: the apprentice rates of the sector (artigianato) apply the 10% of L. 296/2006 art. 1 c. 773 plus the 1.61% NASpI, but no source found settles whether the 0.91 NASpI reduction of the artisan employers also applies to apprentices, nor the wage-integration contribution they owe (the FSBA is paid outside INPS). The contributions of an apprentice may differ.

    **Applies when:** `inps_employer` applies; contract type in apprentice.

    **Remediation:** Source the apprentice rates of artigianato (an INPS circular or an association table of 2026), mark the apprentice block of contribution/2026/artigianato.json derived, then remove this note.

!!! warning "edilizia-artigianato-cna/cigo_rate_by_activity · inps_employer · impact yes · open"
    CIGO: artisan builders are within the CIGO (D.Lgs. 148/2015 art. 13 c. 1 (Normattiva, text in force on 2026-10-14, https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2015-09-14;148~art13!vig=2026-10-14, snapshot sha256 3f7019a244e01d36ac8e7c9e25bcf058c777c8ed758418ba261d83867672c46a)): 4.70% for the 'operai delle imprese dell'industria e artigianato edile' (lett. c) and 1.70% / 2.00% for their impiegati and quadri (lett. e-f). The artigianato table charges no CIGO, so the employer contributions of every worker are understated.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Model the CIGO of D.Lgs. 148/2015 art. 13 c. 1 by activity (edile, lapidei) apart from the tax sector, then remove this note.

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

    **Remediation:** Resolved: the INPS share is computed on the base of every regime of the bundle; an episode that states no base the engine can read has the missing_fact issue sickness_inps_base_unknown (fact inps_base), which blocks the run. Tests: tests/integration/ccnl_engine/sickness/base/test_rules.py, tests/unit/ccnl_engine/sickness/base/test_rules.py.

!!! warning "sickness_cumulation_window · sickness · impact unknown · open"
    The CCNL tier and the comporto are counted on the days of one episode and the relapses it continues. A CCNL that sums the sickness of separate episodes over a window (a calendar year, the last three years) can reach a lower tier or the end of the comporto earlier than the engine shows. The run is affected when an earlier episode outside the relapse chain is recorded. A CCNL whose comporto the engine counts over the calendar year (Commercio Art. 186 and the others with comporto_calendar_year) is not affected.

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

!!! warning "tfr_compensation_apprentice_guarantee_fund · inps_employer · impact yes · open"
    An apprentice whose TFR goes to a pension fund or to the Fondo Tesoreria takes the 0.28-point relief of D.L. 203/2005 art. 8, but not the exemption from the 0.20% Fondo di garanzia contribution of D.Lgs. 252/2005 art. 10 c. 2: no source found says whether the apprentice rate (10% of L. 296/2006 art. 1 c. 773 plus NASpI and the integration funds) holds a Fondo di garanzia share to exempt. The employer contributions of the run may be overstated by 0.20% of the INPS base.

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Find an INPS source on the Fondo di garanzia share of the apprentice rate, then exempt it with the other workers or record that none is due.

!!! warning "maternity_daily_base · maternity_leave · impact unknown · open"
    The INPS maternity indemnity of an operaia, or of a leave whose month before was not worked in full, is computed on the pay of the run over 30 with the rateo of the extra months, not on the pay of the month before the leave: art. 23 c. 5 D.Lgs. 151/2001 divides the pay of an operaia by the days worked or paid (or by the hours, when fewer than the contract), and the divisor of her daily rateo of the 13th is not settled by a primary source. The base of another worker over a whole month is computed from MaternityLeaveEvent.maternity_base_pay.

    **Applies when:** `maternity_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of an operaia (an INPS circular on art. 23 c. 5) and compute her base and that of a month not worked in full, then resolve this limitation.

!!! warning "paternity_daily_base · paternity_leave · impact unknown · open"
    The INPS indemnity of the compulsory paternity leave of an operaio, or of a leave whose month before was not worked in full, is computed on the pay of the run over 30 with the rateo of the extra months, not on the pay of the month before the leave: art. 29 D.Lgs. 151/2001 applies art. 23, whose c. 5 divides the pay of a manual worker by the days worked or paid (or by the hours) with a daily rateo no primary source settles. The base of another worker over a whole month is computed from PaternityLeaveEvent.paternity_base_pay.

    **Applies when:** `paternity_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of a manual worker under art. 23 c. 5 and compute his base and that of a month not worked in full, then resolve this limitation.

!!! warning "parental_daily_base · parental_leave · impact unknown · open"
    The INPS indemnity of the parental leave of an operaio or operaia, or of a leave whose month before was not worked in full, is computed on the pay of the run over 30 with the rateo of the extra months, not on the pay of the month before the leave: art. 34 c. 1 D.Lgs. 151/2001 applies art. 23, whose c. 5 divides the pay of a manual worker by the days worked or paid (or by the hours) with a daily rateo no primary source settles. The base of another worker over a whole month is computed from ParentalLeaveEvent.parental_base_pay.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of a manual worker under art. 23 c. 5 and compute his base and that of a month not worked in full, then resolve this limitation.

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

!!! warning "extraordinary_leave_daily_base · extraordinary_leave · impact unknown · open"
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year over 365: art. 42 c. 5-ter D.Lgs. 151/2001 and INPS messaggio 30/2024 set the pay and its rateo of the extra months, and the INPS table of the yearly maximum divides it by 365 (2026: 43,486.00 / 365 = 119.14), but no source read states the divisor of the worker's own pay.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily divisor INPS applies to the last pay (circ. INPS 64/2001 or 32/2012) and apply it, then resolve this limitation.

!!! warning "naspi_dismissal_exceptions · naspi_dismissal · impact unknown · open"
    The NASpI contribution of the end of an employment is read from the cause, the just cause and the contract type alone. The request states none of the cases that change it: a resignation in the protected period of maternity and a mutual agreement before the labour office or on a transfer over 50 km owe it (INPS circ. 44/2013 par. 1); a collective dismissal without union agreement owes it three times (L. 92/2012 art. 2 c. 35); the changes of contractor with a social clause and the closures of a construction site of c. 34, and the reductions agreed under artt. 4 and 24 L. 223/1991, leave it out; the service counts the fixed-term periods before the open-ended contract and leaves out the leave of art. 42 c. 5 D.Lgs. 151/2001 only through EmploymentPeriod.started_on.

    **Applies when:** `naspi_dismissal` applies; the run takes the engine code path.

    **Remediation:** Add the facts of these cases to the end of the employment (EmploymentPeriod) and apply them, then resolve this limitation.

!!! warning "personal_withholding_same_kind · personal_withholdings · impact unknown · open"
    Two garnishments of the same kind, or two salary assignments, share the measure of their kind (a fifth, or the tenth or seventh of the agente della riscossione) in the order of notification: art. 545 c. 4 c.p.c. sets 'un quinto per i tributi ... ed in eguale misura per ogni altro credito' and art. 5 DPR 180/1950 a cessione 'fino al quinto', but no text read says how two orders of the same kind split the measure, so the later order may be under- or overstated.

    **Applies when:** `personal_withholdings` applies; the run takes the engine code path.

    **Remediation:** Source how the employer splits the measure between two orders of the same kind (art. 499 c.p.c. on the intervention of creditors, case law of the Cassazione) and apply it, then resolve this limitation.

!!! warning "mid_month_level_change · base_salary · impact unknown · open"
    A promotion on a day other than the first of a month splits the monthly pay of the run between the level before and the new level by the payable days of the CCNL daily quota on each side of the promotion, component by component; the hourly quotas of the month (overtime, permits, absences) read the same split chain whatever the day of the event. The CCNL texts read (Commercio and Terziario art. 118, DMO art. 102) give the new level from the promotion but not how its month is split.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source how a month is split by a promotion inside it (a CCNL clause or an INPS or Ministry ruling) and price the events of the month at the terms of their day, then resolve this limitation.

!!! warning "arrears_unused_deductions · contract_renewal_arrears · impact yes · open"
    The engine computes the rate of the separate taxation of arrears from PriorYearTaxFacts.net_income_biennio (art. 21 cc. 1, 3 TUIR) but does not reduce the tax by the deductions of artt. 12 and 13 cc. 1-2 the worker did not use in the years the arrears refer to (art. 21 c. 4): the request does not state them, so the tax may be overstated.

    **Applies when:** `contract_renewal_arrears` applies; the run takes the engine code path.

    **Remediation:** Add the deductions the worker declares as unused for each year of the arrears and reduce the tax by them, then resolve this limitation.

!!! warning "una_tantum_readings · base_salary · impact unknown · open"
    The una tantum of a renewal is paid from the CCNL data with readings no text read settles in full: a month of service in the covered period counts with the days of the una tantum (15 when the text is silent), over the months of the period; the absences of a month do not reduce it, though a text may pay the months 'di effettiva prestazione'; a part time is paid in proportion to its hours; a run without the employment period is paid none; the share of the covered months of earlier years is taxed apart as arrears.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source the counting of the months, the part time and the taxation of each una tantum from its agreement, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| Apprenticeship Allegato D — semester percentages by group, standard professionalizzante and specialistico tracks | altro | 2025-05-20 | [↗](https://www.ediltecnico.it/ccnl-edilizia-artigianato-novita-su-campo-di-applicazione-classificazione-personale-e-apprendistato/) |
| Hourly divisor 173, additional months 13 (tredicesima 173 ore), salary tranches | altro | 2025-05-20 | [↗](https://www.ilccnl.it/ccnl-edilizia-artigianato/) |
| January 2026 paga base per level and seniority (scatti) amounts | altro | 2026-01-01 | [↗](https://www.kitech.it/ccnl/edilizia-artigianato) |
| Contingenza frozen values per level | altro | 2023-07-01 | [↗](https://lexplain.it/ccnl-edilizia-artigianato-tabelle-retributive/) |

??? note "Coverage notes"
    Split salary model: paga base (TimeSeries, 4 tranches May 2025/Jan 2026/Jan 2027/Jan 2028) + contingenza (frozen since July 1992 Protocol) + EDR (frozen EUR 10.33 since 1992).
    
    Paga base May 2025 and Jan 2026 verified directly against published salary tables (ilccnl.it, kitech.it). Jan 2026 cross-checked across all 8 levels.
    
    Jan 2027 and Jan 2028 paga base values confirmed from CCNL F015 renewal text (signed 2025-05-20): 4 tranches totalling +178 EUR at parametro 100 — May 2025 +75, Jan 2026 +35, Jan 2027 +35, Jan 2028 +33 (all at parametro 100 / L1). Parametro coefficients (L1=100, L2=115, L3=130, L4=139, L5=150, L6=180, L7=L7Q=205) applied proportionally; all 8 levels for all 4 periods cross-checked against Jan 2026 published figures (ilccnl.it, kitech.it); max deviation < 0.01 EUR. Source: confartigianatomarcatrevigiana.it citing F015 renewal.
    
    Level 7Q has the same paga base as level 7, plus a fixed indennita di funzione of EUR 140.00/month (F015 Art. on Quadri, L. 190/1985). Modelled at order 8 (above level 7 order 7).
    
    Apprenticeship standard professionalizzante Group 4 (Art. 7, Allegato D, renewal May 2025): 36 months / 6 semesters, destination level 4, 74/76/79/86/91/96% per semester, track 'standard_gruppo_4'. Source: ediltecnico.it citing F015 Allegato D.
    
    INPS contribution rates from 2026-artigianato.json (artigianato sector). No Cassa Edile contribution substitution modelled in the INPS rate; employer Cassa Edile contributions are additional and are out of scope.
    
    Layer 3: overtime is modelled (work_rules.time_supplements.overtime_bands); the Cassa Edile contributions, the premiums on ordinary night and holiday hours and the accruals managed bilaterally are out of scope (review of 2026-10-30)
    
    Apprenticeship specialistico tracks (Allegato D, verbale 05/09/2023, Art. 9): 1 Sp (54m, livelli 4-5): 0-12=78%, 12-24=80%, 24-36=86%, 36-42=91%, 42-54=96%. 3 Sp (42m, livello 3): 0-12=78%, 12-24=80%, 24-36=86%, 36-42=91%. SIMPLIFICATION: 2 Sp (45m, livelli 3-4): last 8th sem.=3m (not 6m) to reach 45m (the exact boundary of the last period is not published in textual form by any secondary source; total duration of 45m is confirmed). Source: studiodalmaschio.it; fareapprendistato.it; cdltorino.it.
    

## Raw data

The contract file this page is generated from: [`agreement/edilizia-artigianato-cna.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/edilizia-artigianato-cna.json).

## Usage example

```python
--8<-- "docs/examples/agreement/edilizia-artigianato-cna/example.py"
```
