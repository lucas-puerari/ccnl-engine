# CCNL Energia e Petrolio (Confindustria Energia)

| | |
|---|---|
| **CNEL code** | `B254` |
| **Sector** | energia |
| **Family** | `energia-utilities` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-04-16 |
| **Workers (est.)** | ~38k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Confindustria Energia
    - Filctem-CGIL
    - Femca-CISL
    - Uiltec-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ✅ |
| **Limits of this contract** | — |

1 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 115 verified / 56 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-04-16 |
| **Last review** | 2026-11-08 |
| **Latest salary tranche** | 2027-07-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-11-07 | claude-opus-5-5 (ai) | Values a primary-text verification found different from the printed tables (text layer). | corrected | 161 values corrected to the amounts printed on the cited pages. |
| 2026-11-08 | gpt-6-sol (ai) | CCNL top-ups of maternity and work injury, read from the signed text by a separate model session; every quote found on the PDF text layer. | confirmed | Added work_rules.insured_absence.maternity.<br>Added work_rules.insured_absence.injury. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1-5` | Quadro Gruppo 1/5 — manager, fifth CREA tier (highest) | € 3,761.90 | 2027-07-01 |
| `1-4` | Quadro Gruppo 1/4 — manager, fourth CREA tier | € 3,761.90 | 2027-07-01 |
| `1-3` | Quadro Gruppo 1/3 — manager, third CREA tier | € 3,761.90 | 2027-07-01 |
| `1-2` | Quadro Gruppo 1/2 — manager, second CREA tier | € 3,761.90 | 2027-07-01 |
| `1-1` | Quadro Gruppo 1/1 — manager, first CREA tier | € 3,761.90 | 2027-07-01 |
| `2-4` | Gruppo 2/4 — specialist workers, fourth function allowance tier | € 3,406.97 | 2027-07-01 |
| `2-3` | Gruppo 2/3 — specialist workers, third function allowance tier | € 3,406.97 | 2027-07-01 |
| `2-2` | Gruppo 2/2 — specialist workers, second function allowance tier | € 3,406.97 | 2027-07-01 |
| `2-1` | Gruppo 2/1 — specialist workers, first function allowance tier | € 3,406.97 | 2027-07-01 |
| `3-4` | Gruppo 3/4 — senior workers, fourth function allowance tier | € 3,085.42 | 2027-07-01 |
| `3-3` | Gruppo 3/3 — senior workers, third function allowance tier | € 3,085.42 | 2027-07-01 |
| `3-2` | Gruppo 3/2 — senior workers, second function allowance tier | € 3,085.42 | 2027-07-01 |
| `3-1` | Gruppo 3/1 — senior workers, first function allowance tier | € 3,085.42 | 2027-07-01 |
| `4-4` | Gruppo 4/4 — skilled workers, fourth function allowance tier | € 2,726.61 | 2027-07-01 |
| `4-3` | Gruppo 4/3 — skilled workers, third function allowance tier | € 2,726.61 | 2027-07-01 |
| `4-2` | Gruppo 4/2 — skilled workers, second function allowance tier | € 2,726.61 | 2027-07-01 |
| `4-1` | Gruppo 4/1 — skilled workers, first function allowance tier | € 2,726.61 | 2027-07-01 |
| `5-4` | Gruppo 5/4 — standard workers, fourth function allowance tier | € 2,391.09 | 2027-07-01 |
| `5-3` | Gruppo 5/3 — standard workers, third function allowance tier | € 2,391.09 | 2027-07-01 |
| `5-2` | Gruppo 5/2 — standard workers, second function allowance tier | € 2,391.09 | 2027-07-01 |
| `5-1` | Gruppo 5/1 — standard workers, first function allowance tier | € 2,391.09 | 2027-07-01 |
| `5-0` | Gruppo 5/0 — standard workers, base position (no function allowance) | € 2,391.09 | 2027-07-01 |
| `6-0` | Gruppo 6/0 — entry-level workers, basic routine operations | € 2,080.12 | 2027-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**livelli_2_3** (type: `percentage`)  
Destination levels: `2-1`, `2-2`, `2-3`, `2-4`, `3-1`, `3-2`, `3-3`, `3-4`  
percentage: 0.95

**livello_4** (type: `percentage`)  
Destination levels: `4-1`, `4-2`, `4-3`, `4-4`  
percentage: 0.95

**livello_5** (type: `percentage`)  
Destination levels: `5-0`, `5-1`, `5-2`, `5-3`, `5-4`  
percentage: 0.90

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! note "sickness_inps_daily_base · sickness · impact unknown · resolved"
    The INPS share of a sick day is computed on the INPS daily base of the episode, on the days INPS pays (the weekdays of an operaio, every day but the national holidays on a Sunday of an impiegato, point 7.3 of INPS circ. 134368/1981): the retribuzione media globale giornaliera of the month before the illness (INPS circ. 134368/1981 point 11; circ. 55/2024 Allegato 1), whole or partial month, impiegato or operaio, or for the lavoratori dello spettacolo the average pay of the last 40 daily contributions, capped for a fixed-term worker (INPS circ. 132/2021 par. 2.4). The base is a fact of the payroll history the episode states (SicknessEpisode.inps_base).

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Resolved: the INPS share is computed on the base of every regime of the bundle; an episode that states no base the engine can read has the missing_fact issue sickness_inps_base_unknown (fact inps_base), which blocks the run. Tests: tests/mutation/ccnl_engine/sickness/base/test_rules_wiring.py, tests/mutation/ccnl_engine/sickness/base/test_rules.py.

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
    A parental leave by the hour takes half the average daily hours a day and counts two such days as one day of leave, the general criterion of art. 32 c. 1-ter D.Lgs. 151/2001 (INPS circ. 152/2015 par. 2.2); a collective agreement, also of the company, that sets other hours to a day of leave or other rules of cumulation prevails, and the bundle holds none.

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

### Without monetary impact

!!! note ""
    APPRENTICESHIP LEVEL 6: percentages not found in any consulted source (previdenza-professionisti.it lists only tracks for levels 2-3, 4, 5). Level 6-0 omitted from apprenticeship tracks.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.redigo.info/2025/08/06/tabelle-retributive-ccnl-energia-e-petrolio/ | tabella_retributiva | 2025-04-16 | [↗](https://www.redigo.info/2025/08/06/tabelle-retributive-ccnl-energia-e-petrolio/) |
| https://www.previdenza-professionisti.it/diritto-del-lavoro/ccnl-energia-e-petrolio---scheda.html | altro | 2025-04-16 | [↗](https://www.previdenza-professionisti.it/diritto-del-lavoro/ccnl-energia-e-petrolio---scheda.html) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=B254 | tabella_retributiva | 2026-07-01 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=B254) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = paga_base (minimi tabellari) only. fixed_allowances per level include: (1) EDR_IPCA — Elemento Distinto della Retribuzione, group-specific TimeSeries from Jul 2025; (2) INDENNITA_FUNZIONE — level-specific function allowance (constant for groups 2-6, TimeSeries Jul 2025=190/Jan 2027=200 for group 1 quadri); (3) CREA — level-specific, constant, group 1 only. Total paga tabellare = base_salary + INDENNITA_FUNZIONE + CREA; verified against kitech at Jul 2026 (exact match 23/23 levels).
    
    MODELLED TRANCHES: 2025-07-01 (first tranche, new CCNL 2025-2027), 2025-12-01 (second), 2026-01-01 (third), 2026-07-01 (fourth), 2027-07-01 (fifth and final). Jan-Jun 2025 retroactive tranche (ipotesi signed 2025-04-16) not modelled — belongs to the transition period of the previous CCNL.
    
    EDR IPCA: introduced 2025-03-01 (pre-modelled). First modelled period from 2025-07-01 at increased amounts: G1=60.71, G2=54.98, G3=49.79, G4=44.00, G5=38.59, G6=33.57. Second period from 2026-01-01: G1=70.37, G2=63.73, G3=57.71, G4=51.00, G5=44.73, G6=38.91. Open-ended (no further increase published). Source: redigo.info.
    
    FUNCTION ALLOWANCE GROUP 1 (indennità di funzione quadri): 190 EUR/month for all 14 mensilità, valid 2025-07-01 to 2026-12-31; increases to 200 EUR from 2027-01-01. Source: contratticcnl.it (CCNL 2025-2027). Constant for groups 2-5; absent for group 6.
    
    CREA (Compenso per Risultato ed Eccellenza Aziendale): only for group 1 (quadri). Amounts from kitech Jul 2026 back-calculation: 1-1=90.65, 1-2=181.31, 1-3=271.96, 1-4=362.61, 1-5=453.26. Constant throughout the contract (no source indicates time variation).
    
    CATEGORY: group 1 levels (1-1 through 1-5) are Quadri under L. 190/1985. Groups 2-6 are impiegati/operai; category omitted as the CCNL does not publish a clean impiegato/operaio split by level.
    
    SENIORITY INCREMENTS: abolished from 2016-01-01 by the 2016 CCNL renewal. Amounts accrued up to 2015 are crystallised as a personal supplement. Modelled as maximum_count=0, amount_by_level={}, cadence_months=24 (historical biennial cadence).
    
    HOURLY DIVISOR: 174.5 h/month (confirmed from previdenza-professionisti.it and lavoro-economia.it for CCNL B254). The CCNL states EDR is 'omnicomprensivo' with no impact on other contractual institutes. The engine derives no hourly rate for this CCNL (no verified work_rules.time_supplements.hourly_base_provenance: overtime takes the caller's rate); when derived, hourly_base_method=minimo_tabellare leaves the EDR out. All monthly and annual figures are unaffected (review of 2026-10-30)
    
    ADDITIONAL MONTHS: 14 (tredicesima December + quattordicesima June). Source: previdenza-professionisti.it.
    
    INPS: uses 2026-industria.json (standard industry sector). CNEL code: B254.
    
    APPRENTICESHIP: percentage type, 3 tracks (livelli_2_3, livello_4, livello_5). Source: previdenza-professionisti.it (2025-04-16 CCNL). Livelli 2-3 max 24 months (90% for first 12m, 95% thereafter). Livello 4 max 36 months (90% for first 12m, 95% thereafter). Livello 5 max 36 months (80% for first 12m, 90% thereafter). Reference retribution per CCNL Art.: 'il minimo del livello di inquadramento e del relativo CREA'.
    
    APPRENTICESHIP REFERENCE BASE: per CCNL, reference is 'minimo tabellare e relativo CREA'. Modelled correctly: INDENNITA_FUNZIONE and INDENNITA_FUNZIONE_QUADRI set apprenticeship_pct_relevant=false (paid at full value, not reduced); EDR set apprenticeship_pct_relevant=false (omnicomprensivo, no impact on other institutes); CREA set apprenticeship_pct_relevant=true (explicitly in CCNL base for group 1).
    
    FUNCTION ALLOWANCE GROUPS 2-5: amounts assumed constant throughout 2025-2027 CCNL. No published text or renewal announcement indicates a change to these allowances. Values from kitech Jul 2026. In the energia-petrolio sector, INDENNITA_FUNZIONE is a fixed contractual element rarely changed mid-contract; constancy is consistent with historical pattern.
    
    CREA CONSTANCY: CREA amounts assumed constant throughout 2025-2027 (no source indicates time variation). Values from kitech Jul 2026. CREA is a fixed contractual element (Compenso per Risultato Aziendale Aggiuntivo) set at contract-level; constancy is standard for this type of element.
    

## Raw data

The contract file this page is generated from: [`agreement/energia-petrolio-confindustria.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/energia-petrolio-confindustria.json).

## Usage example

```python
--8<-- "docs/examples/agreement/energia-petrolio-confindustria/example.py"
```
