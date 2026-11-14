# CCNL Tessile-Abbigliamento-Moda PMI (Uniontessile-Confapi)

| | |
|---|---|
| **CNEL code** | `D018` |
| **Sector** | tessile abbigliamento moda PMI |
| **Family** | `tessile-moda` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-02-18 |
| **Workers (est.)** | ~48k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Uniontessile-Confapi
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
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, seniority |

7 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🧑 Manual | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 42 verified / 0 derived / 5 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟡 Needs review | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-02-18 |
| **Last review** | 2026-11-10 |
| **Latest salary tranche** | 2027-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-17 | maintainer (human) | Whole file. The values checked were not recorded. | flagged | The review recorded no list of the documents it read.<br>Confidence set to needs_review: values to re-check. |
| 2026-10-17 | claude-opus-5-5 (ai) | The minimi of the ten levels of the settore tessili e abbigliamento against the signed renewal of 18 February 2025. | confirmed | Settore tessili e abbigliamento (PDF p. 21 of the signed scan, checked on the page image): the 38 minimi of the file, from the minimi of 1/02/2022 to 1/01/2027, match and move from assumed to verified. Level 1 is a flat 1.558,00 from 2025 with no increment printed. The errata of 21/2/2025 (pp. 24-25) does not touch this table.<br>The ruleset names this source, published by FILCTEM-CGIL, a signatory: source_type contracting_party instead of estimated. |
| 2026-11-07 | claude-opus-5-5 (ai) | Art. 46 calzature table of the renewal 2024-2027 (p. 21, page image). | corrected | The calzature employers pay their own minimi (level 8 2,431.61 from 2025, not the tessile 2,421.56). |
| 2026-11-07 | claude-opus-5-5 (ai) | The giocattoli table of art. 46 (p. 22) and the occhiali and pelli e cuoio replacement tables of the verbale of 21 February 2025 (pp. 24-25), page images. | confirmed | Giocattoli (p. 22), occhiali (p. 24) and pelli e cuoio (p. 25): the 88 minimi, from the minimi of 1/02/2022 to 1/01/2027, read on the page images and added as the base_salary_by_subsector of levels 1-7 and the new sub-sector level 4s.<br>The verbale moves the last occhiali tranche to 1/01/2027 (p. 22 printed 1/02/2027) and corrects the pelli e cuoio level 6; pelli e cuoio level 1 is printed 1.557,00 in 2025 and 1.558,00 from 2026, kept as printed. |
| 2026-11-08 | claude-opus-5-5 (ai) | Art. 12 bis and 12 ter of the renewal of 24 January 2020 (CNEL deposito 118136, PDF p. 12), the renewal of 18 February 2025 (deposito 216349) for amendments. | corrected | Art. 12 bis: 240 EUR a year from 2017, with the June pay from 2021, to the worker in service on 1 January without company bargaining or individual treatment; twelfths of the year before, part-time proportional, all-inclusive including the TFR.<br>The text is silent on a termination before June: limitation egr_termination_before_june.<br>Art. 12 ter (110 EUR, firms without art. 12 C) left as limitation art_12_ter_element.<br>The renewal of 18 February 2025 does not amend art. 12, 12 bis or 12 ter.<br>An independent reading confirmed amount, months, part-time, exclusion and the termination limitation, and found that the text tests the company bargaining in the present ('aziende prive'), not in the year before: the element is closed by bargaining in force in the year of payment. |
| 2026-11-10 | claude-opus-5-5 (ai) | Art. 12 ter, CNEL deposito 118136, PDF page 12 | confirmed | Art. 12 ter pays EUR 110 with June pay from 2020, for the payment year's service in twelfths, to workers in service in June; part-time is proportional. A smaller company payment requires an unmodelled top-up. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `8` | Livello 8 — quadro | € 2,548.78 | 2027-01-01 |
| `7` | Livello 7 | € 2,403.51 | 2027-01-01 |
| `6` | Livello 6 | € 2,257.77 | 2027-01-01 |
| `5` | Livello 5 | € 2,116.84 | 2027-01-01 |
| `4s` | Livello 4s (pelli e cuoio, occhiali, giocattoli only) | € 2,074.87 | 2027-01-01 |
| `4` | Livello 4 | € 2,002.56 | 2027-01-01 |
| `3bis` | Livello 3 bis | € 1,955.72 | 2027-01-01 |
| `3` | Livello 3 | € 1,908.92 | 2027-01-01 |
| `2bis` | Livello 2 bis | € 1,850.15 | 2027-01-01 |
| `2` | Livello 2 | € 1,796.58 | 2027-01-01 |
| `1` | Livello 1 — base | € 1,558.00 | 2025-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 4 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 6.71 |
| `2` | € 7.23 |
| `2bis` | € 7.23 |
| `3` | € 7.75 |
| `3bis` | € 7.75 |
| `4` | € 8.26 |
| `5` | € 9.81 |
| `6` | € 10.33 |
| `7` | € 11.88 |
| `8` | € 12.91 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "tessile-pmi-uniontessile/other_subsectors_tables · base_salary · impact yes · open"
    SUB-SECTORS (Art. 46 of the renewal 2024-2027 signed 18 February 2025, pp. 21-22; verbale of 21 February 2025, pp. 24-25): the calzature, giocattoli, occhiali and pelli e cuoio tables are modelled as the base_salary_by_subsector calzature, giocattoli, occhiali and pelli_cuoio (EmployerProfile.subsector), the occhiali and pelli e cuoio ones from the replacement tables of the verbale; level 4s exists only in the last three. Not modelled: the penne, spazzole e pennarelli table (pp. 22 and 24, with a 4S level). The levels the tables of giocattoli, occhiali and pelli e cuoio do not print (2bis, 3bis and 8; 7 also for occhiali and pelli e cuoio) are paid the tessile table when requested with those sub-sectors, and every level of the four sub-sectors takes the tessile seniority amounts.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the penne, spazzole e pennarelli table, source the seniority of the sub-sectors and reject the levels their tables lack, then remove this note.

!!! warning "tessile-pmi-uniontessile/level_8_function_allowance · base_salary · impact yes · open"
    LEVEL 8 IDF: indennità di funzione 51.65 EUR modelled as fixed_allowance (unverified for period before Jan 2026). Function-conditional, not automatic for all L8 workers.

    **Applies when:** `base_salary` applies; level in 8.

    **Remediation:** Gate IND_FUN by a role (function holders) and source the pre-Jan 2026 amount, or record the limitation.

!!! warning "tessile-pmi-uniontessile/level_4s_seniority · seniority · impact yes · unsourced"
    LEVEL 4s (pelli e cuoio, occhiali, giocattoli): the seniority table of the file has no 4s row and the art. 46 tables read do not set one, so a 4s worker accrues no seniority increments. No fixed allowance is modelled for it (the tables read set none), and its category is left to Employment.category.

    **Applies when:** `seniority` applies; level in 4s.

    **Remediation:** Source the seniority increment of level 4s, add it to amount_by_level, then remove this note.

!!! warning "tessile-pmi-uniontessile/egr_termination_before_june · base_salary · impact yes · open"
    Art. 12 bis: the elemento di garanzia retributiva is owed to the worker in service on 1 January and paid with the June pay; the text does not say whether a worker who leaves between January and June is paid it with the final settlement. The engine pays it only in the regular run of June.

    **Applies when:** `base_salary` applies; run kind in termination.

    **Remediation:** Read an authoritative interpretation of art. 12 bis for a termination before June and settle the element there if owed.

!!! warning "tessile-pmi-uniontessile/art_12_ter_top_up · base_salary · impact yes · open"
    Art. 12 ter: the EUR 110 June element from 2020 is modelled for workers in service in June, in twelfths of the payment year and proportional to part-time hours, when EmployerProfile.second_level_premium is false. Not modelled: a company agreement paying less than EUR 110 must be topped up; no amount of that company payment is available to calculate the difference. The second-level premium flag does not distinguish agreements implementing art. 12 C from other company agreements.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Record the amount paid under a company agreement below EUR 110 and distinguish art. 12 C implementation before calculating the difference.

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

!!! warning "sunday_holiday_ccnl_clause · sunday_holiday · impact yes · open"
    L. 260/1949 art. 5 pays the workers with a fixed salary a further daily quota only for the civil holidays (25 April, 1 May, 2 June) falling on a Sunday; the other holidays of art. 2 (1 January, 6 January, Easter Monday, 15 August, 4 October, 1 November, 8 December, 25 and 26 December) give it only by CCNL clause, and the payment of 4 November is a CCNL institute. A run of a month with such a holiday on a Sunday, in a CCNL whose clause is not sourced (work_rules.sunday_holidays), pays the statutory holidays only; a public employment is paid none, its treatment not being sourced.

    **Applies when:** `sunday_holiday` applies; the run takes the engine code path.

    **Remediation:** Source the CCNL clause on the holidays falling on a Sunday and record it as work_rules.sunday_holidays.

### Without monetary impact

!!! note ""
    VV.PP. (Venditori Viaggiatori e Piazzisti) levels excluded; only Jan-2026 data available from primary sources, historical tranches not found.

!!! note ""
    APPRENTICESHIP: not modelled (set to []). Primary source for post-2024 apprenticeship rules not identified.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| Tabelle retributive CCNL Abbigliamento Moda Tessili PMI Uniontessile Confapi — KITech | tabella_retributiva | — | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=501) |
| CCNL Tessili PMI (Uniontessile - Confapi) — lavoro-economia.it | tabella_retributiva | — | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=500) |
| CCNL Uniontessile Confapi: rinnovo 2025 — farecontrattazione.adapt.it | rivista | — | [↗](https://farecontrattazione.adapt.it/ccnl-uniontessile-confapi-relazioni-industriali-e-sostegno-ai-dipendenti-al-centro-del-rinnovo-2025/) |
| CCNL tessile PMI Confapi: tabelle retributive 2025-2027 — FISCOeTASSE | tabella_retributiva | — | [↗](https://www.fiscoetasse.com/approfondimenti/16754-ccnl-tessile-abbigliamento-moda-pmi-tabelle-retributive-2025-2027.html) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (single minimo mensile, no separate contingenza or EDR). Source: lavoro-economia.it explicitly divides monthly by 173 to derive hourly rate, no separate component columns.
    
    LEVEL 1: jumps to 1558.00 EUR/month at Jan 2025 (9.006 EUR/h, exceeds 9 EUR/h floor per CCNL art. 33bis). Frozen in Jan 2026 and Jan 2027 — excluded from standard tranche mechanism.
    
    FONDAPI: the contributions are computed on the contractual minimum of the level; the Fondapi base also counts the EDR, not in the bundle pay.
    
    FONDAPI BASE: Fondapi reads its rate on the 'elemento retributivo nazionale' (minimo tabellare + EDR, scheda 'I destinatari e i contributi' 2026, p. 2). The CCNL conglobated minimum, contingenza and EDR confederale into the ERN from 1 January 1996 (CNEL archive, agreement 610: 'il conglobamento sotto la voce "elemento retributivo nazionale" [...] minimo contrattuale, indennità di contingenza, EDR confederale (L.20.000), che pertanto non saranno più presenti in busta paga'), and the renewal of 2025 (art. 46, scanned p. 20) defines the ERN by its tables, which are the base salaries of this file (level 4: 1.962,56 from January 2026, p. 21): the fund base is the base salary, with no EDR to add.
    

## Raw data

The contract file this page is generated from: [`agreement/tessile-pmi-uniontessile.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/tessile-pmi-uniontessile.json).

## Usage example

```python
--8<-- "docs/examples/agreement/tessile-pmi-uniontessile/example.py"
```
