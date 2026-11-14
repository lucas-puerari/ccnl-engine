# CCNL Comunicazione, Informatica e Servizi Innovativi PMI — Settore Informatico

| | |
|---|---|
| **CNEL code** | `G029` |
| **Sector** | informatica-servizi-innovativi |
| **Family** | `ict-telecomunicazioni` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-04-14 |
| **Workers (est.)** | ~20k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Unigec Confapi
    - Unimatica Confapi
    - SLC-CGIL
    - Fistel-CISL
    - Uilcom-UIL

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
| **Rule provenance** | 2 verified / 39 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-04-14 |
| **Last review** | 2026-11-14 |
| **Latest salary tranche** | 2027-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 80 - Tredicesima mensilità (impiegati) (p. 123): "Nel caso di inizio o di cessazione del rapporto durante il corso dell'anno, l'impiegato non in prova avrà diritto a tanti dodicesimi dell'ammontare della 13ª mensilità per quanti sono i mesi di servizio prestato. La frazione di mese non superiore ai 15 giorni non sarà considerata, mentre sarà considerata come mese intero la frazione di mese superiore a 15 giorni.". Match: more_than 15. |
| 2026-10-31 | claude-opus-5-5 (ai) | The comporto and the sick pay of the CCNL counted over several illnesses (work_rules.sickness_rules), read on the signed text. | corrected | Art. 70 (pp. 113-114): comporto 12 months within 36 months (1095 days), 180 days of 100% of the net pay and 6 months of 50%, counted over the 36 months before each day of absence, from day 1. The file kept 180 days of one illness: corrected to a cumulation over three years. |
| 2026-11-14 | claude-opus-5-5 (ai) | Art. 30 of the renewal of 9 July 2018 (CNEL 90438, scanned pp. 35, 39, 40) and the renewals of 2021 (CNEL 133946) and 2025 (CNEL 216350). | corrected | Added the 30 and 24 month tracks; the apprentice accrues no seniority increment (art. 30 p. 40); limitations apprenticeship_duration_by_agreement and apprentice_seniority removed. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro — manager, exceptional leadership and innovative thinking (PAR 248 + indennità funzione 51.65) | € 2,889.92 | 2027-01-01 |
| `1` | Livello 1 — top professional, full strategic responsibility (PAR 247) | € 2,827.50 | 2027-01-01 |
| `2` | Livello 2 — expert professional, strategic solutions, wide autonomy (PAR 209) | € 2,468.03 | 2027-01-01 |
| `3` | Livello 3 — senior professional, leads in complex environments (PAR 195) | € 2,336.94 | 2027-01-01 |
| `4` | Livello 4 — senior specialist, responsible for team performance (PAR 182) | € 2,218.03 | 2027-01-01 |
| `5` | Livello 5 — reference level (PAR 169); experienced specialist with consultancy role | € 2,095.18 | 2027-01-01 |
| `6` | Livello 6 — senior technician, coordinates others in limited contexts (PAR 150) | € 1,967.68 | 2027-01-01 |
| `7` | Livello 7 — technical specialist, independent in structured contexts (PAR 133) | € 1,776.03 | 2027-01-01 |
| `8` | Livello 8 — qualified technical worker, applies skills to defined problems (PAR 125) | € 1,678.58 | 2027-01-01 |
| `9` | Livello 9 — basic technical tasks, limited autonomy (PAR 114) | € 1,575.27 | 2027-01-01 |
| `10` | Livello 10 — entry-level worker, simple tasks under close supervision (PAR 100) | € 1,444.33 | 2027-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 16.01 |
| `1` | € 16.01 |
| `2` | € 16.01 |
| `3` | € 14.46 |
| `4` | € 13.94 |
| `5` | € 13.43 |
| `6` | € 13.17 |
| `7` | € 12.91 |
| `8` | € 12.39 |
| `9` | € 11.88 |
| `10` | € 11.62 |

## Apprenticeship

**professionalizzante_36** (type: `under_classification`)  
Destination levels: `1`, `2`, `3`, `4`, `5`, `6`, `7`

**professionalizzante_30** (type: `under_classification`)  
Destination levels: `1`, `2`, `3`, `4`, `5`, `6`, `7`

**professionalizzante_24** (type: `under_classification`)  
Destination levels: `1`, `2`, `3`, `4`, `5`, `6`, `7`

**automatico_it** (type: `under_classification`)  
Destination levels: `8`, `9`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

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

### Without monetary impact

!!! note ""
    APPRENTICESHIP — QUADRO (Q) NOT MODELLED AS DESTINATION: Art. 52 and Art. 64 contain no affirmative listing of Q as an apprendistato professionalizzante destination. Following repo precedent (telecomunicazioni-asstel, gomma-plastica) where Quadri are excluded from apprenticeship destinations when no explicit contractual text lists them, Q is omitted from destination_levels of the general track.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.cdltorino.it/ccnl-informatica-piccola-industria-rettifica-tabelle-retributive/ | tabella_retributiva | 2025-04-14 | [↗](https://www.cdltorino.it/ccnl-informatica-piccola-industria-rettifica-tabelle-retributive/) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=302 | tabella_retributiva | 2025-04-14 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=302) |
| https://slc.cgil.it/ccnl/20210309-CCNL_CONFAPI_UNIGEC_UNIMATICA.pdf | altro | 2021-03-09 | [↗](https://slc.cgil.it/ccnl/20210309-CCNL_CONFAPI_UNIGEC_UNIMATICA.pdf) |
| CCNL informatica PMI (Unimatica-Confapi), accordo di rinnovo 9 luglio 2018 (deposito CNEL, accordo 90438, scansione firmata) | cnel | 2018-07-09 | [↗](https://az-apim-cne-sa-0002-lgc-we.azure-api.net/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/90438) |

??? note "Coverage notes"
    SCOPE: models the SETTORE INFORMATICO E SERVIZI INNOVATIVI sub-sector of G029 only (levels Q, 1–10). The SETTORE GRAFICO-EDITORIALE and SETTORE CARTARIO-CARTOTECNICO sub-sectors of G029 are NOT modelled here. Applicable to ICT companies covered by Art. 1 of the CCNL.
    
    SALARY MODEL — CONGLOBATED: base_salary values are the total contractual retribuzione mensile (paga base + contingenza + EDR + indennità di funzione for Q) at each tranche date. Contingenza per level is frozen since 1994 and sourced from Allegato 24 of the G029 CCNL 09/03/2021 PDF. EDR = EUR 10.33 (all levels). Q level includes indennità di funzione = EUR 51.65 introduced from 01/01/2025 (sourced from kitech.it April 2025 tables, component-level breakdown). fixed_allowances is empty for all levels.
    
    CONGLOBATED CHECK (non-circular): paga_base values from the April 14 2025 corrected tables (cdltorino.it) plus frozen contingenza (Allegato 24 PDF) plus EDR 10.33 independently sum to the kitech Jan 2026 totals to within EUR 0.01 on all 11 levels. Example at Jan 2026: level 5 paga_base 1529.38 + contingenza 525.47 + EDR 10.33 = 2065.18 (kitech ✓); level 10: 903.38 + 512.87 + 10.33 = 1426.58 (kitech ✓); Q: 2242.26 + 541.65 + 10.33 + 51.65 = 2845.89 (kitech ✓). The kitech values ARE the conglobated total, not paga_base only.
    
    HOURLY DIVISOR = 169. Source: Art. 113 G029 CCNL 2021 PDF ('dal 1° gennaio 2019 si dividerà per 169'). Independent cross-check: contractual weekly hours = 39 h from 01/01/2019 (same Art. text); 39 × 52 / 12 = 169.00 exactly.
    
    PAR COEFFICIENTS from Art. 116 G029 CCNL 2021 PDF (Settori Grafico-Editoriale, Informatico-Servizi Innovativi): Q=248, 1=247, 2=209, 3=195, 4=182, 5=169, 7=133, 8=125, 9=114, 10=100. CORRECTION: level 6 PAR was changed from 156 (2021 CCNL) to 150 in the April 14 2025 verbale integrativo corrected tables. This is confirmed by cdltorino.it rettifica article (PAR=150 shown explicitly) and is consistent with the kitech Jan 2026 total for level 6 (1407.71 + 523.01 + 10.33 = 1941.05). All base_salary values are computed from official paga_base (cdltorino April 2025) + frozen contingenza (Allegato 24 CCNL PDF) + EDR 10.33.
    
    TRANCHE DATES: 01/01/2025 (first, effective retroactively from April 2025 per verbale); 01/01/2026 (second); 01/01/2027 (third). Reference level 5 increases: +60, +60, +30 EUR paga base. Confirmed by search results (bollettinoadapt.it, fiscoetasse.com).
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: Art. 97 G029 CCNL 2021 PDF (tredicesima mensilità). No quattordicesima article exists in G029.
    
    SENIORITY: 5 scatti biennali (cadence 24 months). Source: Art. 45 G029 CCNL 2021 PDF ('per ogni biennio, e fino ad un massimo di 5 bienni'). Per-level amounts from same article (effective from 01/01/2002 update). kitech April 2025 table confirms same amounts unchanged in the 2025 renewal.
    
    INPS: reuses 2026-industria.json (Confapi/industria sector). Unimatica-Confapi belongs to industria. CIGO applies (D.Lgs. 148/2015). No Cassa Edile or bilateral fund substituting INPS contributions.
    
    APPRENTICESHIP GENERAL TRACK (Art. 52 CCNL, para. C Apprendistato professionalizzante): first period 2 levels below destination; second period 1 level below; third period classification stays 1 below but retribuzione is at destination level (levels_below=0 in engine, which models pay, not classification). Duration options: 36, 30 or 24 months by agreement. The 36-month (12+12+12) track is modelled as representative.
    
    APPRENTICESHIP DURATION (art. 30, renewal of 9 July 2018, scanned p. 35): 36, 30 or 24 months in three equal periods (two levels below, then one below, then the pay of the destination level), the duration agreed by the parties: tracks professionalizzante_36, _30 and _24, stated by Apprentice.track. The renewals of 2021 and 2025 do not change the durations.
    
    APPRENTICESHIP AUTOMATICO TRACK (Art. 52 CCNL, settore informatico-servizi innovativi Area Tecnica): destination level 8 → entry at level 9 (1 below), 18 months; destination level 9 → entry at level 10 (1 below), 18 months. After permanent hire, destination-level 8 apprentices spend 6 months at level 9 before final assignment (this post-apprenticeship transition is not modelled; it occurs outside the apprendistato period).
    
    EDR ROLL-UP: rolling EDR (EUR 10.33) into base_salary is safe for G029 because G029 uses under_classification apprenticeship, meaning the apprentice pay is determined by the classified level's base_salary directly. The EDR percentage-of-base exemption (Art. 3 L. 537/1993) does not apply to under_classification.
    

## Raw data

The contract file this page is generated from: [`agreement/informatica-pmi-unimatica.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/informatica-pmi-unimatica.json).

## Usage example

```python
--8<-- "docs/examples/agreement/informatica-pmi-unimatica/example.py"
```
