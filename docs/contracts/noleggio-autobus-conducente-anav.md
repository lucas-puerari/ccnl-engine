# CCNL Noleggio Autobus con Conducente (ANAV)

| | |
|---|---|
| **CNEL code** | `IC36` |
| **Sector** | Trasporti - Noleggio autobus con conducente |
| **Family** | `trasporti-logistica` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-05-23 |
| **Workers (est.)** | ~5422 |
| **Ruleset version** | `1.0.0` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANAV
    - FILT-CGIL
    - FIT-CISL
    - UILTRASPORTI

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | seniority, una_tantum |

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 35 verified / 33 derived / 3 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-05-23 |
| **Last review** | 2026-11-14 |
| **Latest salary tranche** | 2026-08-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-17 | claude-opus-5-5 (ai) | The tabellari, contingenza and EDR of the eleven levels against the ANAV tables of the accordo of 6 October 2022, and the tranches and the EDR 2025 of the renewal of 23 May 2025. | corrected | Allegato n. 2 of the accordo of 6 October 2022, published by ANAV (text layer): the tabellare of October 2023, the contingenza and the EDR of the eleven levels move from assumed to verified (33 values). The signed CCNL scan (Allegato n. 5, p. 83) prints the same table at low resolution.<br>The renewal of 23 May 2025 prints only the increments at C2 (60 EUR from July 2025, 100 EUR from August 2026, EDR 2025 of 40 EUR), to reparametrise on the scale 100-200: the tranches and the EDR 2025 of each level are derived (33 values), with the increment rounded once, as the Allegato n. 2 of 2022 adds the aumento a regime in its last column (C4: 729,09 + 67,16 = 796,25, not the 796,26 of the three rounded tranches).<br>The ruleset names the renewal published by ANAV, the employer signatory: source_type contracting_party; the aggregator sources (redigo.info, kitech.it) are dropped.<br>Corrected: C4 2024-01-01: 796.26 -> 796.25; B2 2024-01-01: 1289.93 -> 1289.92; A1 2024-01-01: 1592.49 -> 1592.50; Q2 2024-01-01: 1592.49 -> 1592.50; Q1 2024-01-01: 1592.49 -> 1592.50. |
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Articolo 48 - Tredicesima mensilità, comma 2 (p. 81): "il lavoratore non in prova avrà diritto a tanti dodicesimi dell'ammontare della tredicesima mensilità per quanti sono i mesi di servizio prestato. Le frazioni di mese non superiori ai 14 giorni non saranno calcolate, mentre saranno considerate come mese intero se superiori ai 14 giorni.". Added: more_than 14 (the file applied the engine default, at least 15 days). |
| 2026-11-01 | claude-opus-5-5 (ai) | The una tantum of the renewal of 23 May 2025 (p. 1, OCR). | corrected | Renewal of 23 May 2025, p. 1: 600 EUR at C2 in two installments (June 2025, January 2026) for 1 January 2024 to 31 May 2025, staff in service on 23 May 2025, months with more than 15 days, part time by hours, outside the TFR: parameters.una_tantum[UT_2025]. |
| 2026-11-08 | claude-opus-5-5 (ai) | The monthly values of the levels against the primary tables (text layer). | confirmed | 33 values found verbatim on the cited pages and marked verified; 3 left as they were (derived or not on a text page). |
| 2026-11-09 | claude-opus-5-5 (ai) | Una Tantum of the signed renewal, PDF p. 1. | confirmed | Confirmed the C2 installments, service-on-signing condition, proportional service and part time, and TFR and Priamo exclusions; narrowed the obsolete exclusion note to the unmodelled effective-work-months condition. |
| 2026-11-14 | claude-opus-5-5 (ai) | Art. 47 (seniority) and Art. 21 c. 9-10 (apprentice pay and credit) of the renewal of 6 October 2022, against the renewal of 23 May 2025. | confirmed | Read Art. 47 and Art. 21 on the page images: the nine amounts match the file; apprentices take no increment and the whole apprenticeship counts on continuation. Re-sourced the amounts, set the apprentice amount to zero with full credit, closed seniority_from_ic35 and apprentice_seniority, and recorded the c. 3 anticipation and c. 5 promotion rules, which the engine does not apply. |
| 2026-11-14 | claude-opus-5-5 (ai) | Allegato n. 5 (ott-23 column) and Art. 70 b) of the renewal of 6 October 2022, against the table before July 2025. | corrected | The eleven values from 1 January 2024 were already taken from the ANAV circular, not back-calculated: the limitation was stale and is closed. The signed annex prints C4 796,26 against the circular's 796,25; the file follows the annex. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q1` | Livello Q1 (quadro) | € 1,831.31 | 2026-08-01 |
| `Q2` | Livello Q2 (quadro) | € 1,831.31 | 2026-08-01 |
| `A1` | Livello A1 | € 1,831.31 | 2026-08-01 |
| `A2` | Livello A2 | € 1,721.42 | 2026-08-01 |
| `B1` | Livello B1 | € 1,556.61 | 2026-08-01 |
| `B2` | Livello B2 | € 1,483.35 | 2026-08-01 |
| `B3` | Livello B3 | € 1,419.26 | 2026-08-01 |
| `C1` | Livello C1 | € 1,391.79 | 2026-08-01 |
| `C2` | Livello C2 | € 1,226.97 | 2026-08-01 |
| `C3` | Livello C3 | € 1,144.55 | 2026-08-01 |
| `C4` | Livello C4 | € 915.65 | 2026-08-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 9 increments

| Level | Increment (monthly) |
|---|---:|
| `Q1` | € 33.10 |
| `Q2` | € 33.10 |
| `A1` | € 33.10 |
| `A2` | € 32.19 |
| `B1` | € 30.36 |
| `B2` | € 29.57 |
| `B3` | € 29.39 |
| `C1` | € 29.23 |
| `C2` | € 27.17 |
| `C3` | € 26.61 |
| `C4` | € 25.35 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `Q1`, `Q2`, `A1`, `A2`, `B1`, `B2`, `B3`, `C1`, `C2`, `C3`, `C4`  
percentage: 0.95

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "noleggio-autobus-conducente-anav/una_tantum_effective_work_months · una_tantum · impact yes · open"
    The two una tantum installments are paid, but the agreement counts months of effective work; the engine counts months of employment, without reducing for months with no effective work. An absence spanning a covered month can overstate the payment.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Provide the covered months of effective work for this payment and count only those months when prorating each installment.

!!! warning "noleggio-autobus-conducente-anav/seniority_month_and_promotion · seniority · impact yes · open"
    Art. 47 c. 3 and 5: an increment is paid from the first day of the month in which the biennium is completed when more than 15 days of that month remain, and on a promotion 'il dipendente mantiene l'importo in cifra fissa degli aumenti maturati nel livello di provenienza'. The engine pays from the month after the biennium and prices all the increments at the current level.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Bring the increment forward when more than 15 days of the month remain, and keep the matured increments at the amounts of the level they matured in.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "apprenticeship_pct_undeclared_components · base_salary · impact unknown · open"
    A percentage apprenticeship reduces every fixed allowance whose apprenticeship_pct_relevant flag the data leaves at its default, together with the base salary. Whether the CCNL applies the percentage to that allowance (an EDR, a contingenza, a function allowance) was not sourced. The run is affected when such an allowance is in the apprentice's pay.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source, for each CCNL, the elements the apprenticeship percentage applies to and set apprenticeship_pct_relevant on every allowance; the limitation then no longer applies to its runs.

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

!!! note "parental_month_split · parental_leave · impact unknown · resolved"
    When a rate band or the indemnified months of the parental leave end inside a calendar month, the days of that month are paid in order at the rate of the period each falls in, one day of counter each, the last day what is left of the thirty. INPS attributes the rates to the periods of leave by day, within a month too: circ. 57/2024, example A, gives 30% to 21-31 December 2023 and 80% to 1-20 January 2024, and counts '10 giorni residui' of the further month after 20 days taken.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Resolved: the rates follow the days of each period, as INPS circ. 57/2024.

!!! note "parental_extra_month_share · parental_leave · impact unknown · resolved"
    The days of parental leave accrue the 13th and the other extra months in full at the employer's charge: the leave does not reduce them (art. 34 c. 5 D.Lgs. 151/2001), and no source sets a netting of the share the INPS indemnity holds in its base (art. 23 c. 2); by the maintainer's decision of 2026-11-15 the employer pays the whole rateo, as the text reads.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Resolved by the decision of 2026-11-15: the employer pays the whole rateo of the extra months.

!!! warning "parental_hourly_ccnl_rule · parental_leave · impact unknown · open"
    A parental leave by the hour follows the national CCNL rule on the hours of a day of leave (art. 32 c. 1-bis D.Lgs. 151/2001, work_rules.parental_hourly), or without one the general criterion of art. 32 c. 1-ter: half the average daily hours a day, two such days a day of leave, no cumulation with the nursing rests on the same day (INPS circ. 152/2015 par. 2.1-2.2). The run records this limitation while the bundle does not record the rule of the CCNL; a company or territorial agreement is the fact local_hourly_agreement of the event.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the collective rules on the leave by the hour of the CCNL (hours of a day of leave, cumulation) and apply them, then resolve this limitation.

!!! note "disability_permit_tfr · disability_permits · impact unknown · resolved"
    The days of permit under L. 104/1992 art. 33 c. 3 keep the TFR base. Art. 33 c. 4 refers to art. 43 D.Lgs. 151/2001, which applies art. 34 c. 5: the days are paid and counted in the seniority; no primary source states their TFR base, and by the maintainer's decision of 2026-11-15 they stay in it, as payroll practice holds.

    **Applies when:** `disability_permits` applies; the run takes the engine code path.

    **Remediation:** Resolved by the decision of 2026-11-15: the permit days stay in the TFR base.

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

!!! note "notice_indemnity_day_measure · termination_notice · impact unknown · resolved"
    A notice in calendar days is paid at the monthly pay over 30 for each calendar day ('la retribuzione che sarebbe spettata', art. 2118 c. 2 c.c.): no law sets a daily measure, and by the maintainer's decision of 2026-11-15 a calendar day is a thirtieth of the month unless the CCNL sets its own. A CCNL whose daily quota differs records its own limitation.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Resolved by the decision of 2026-11-15: a calendar day of notice is a thirtieth of the monthly pay.

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

!!! note "mid_month_level_change · base_salary · impact unknown · resolved"
    A promotion on a day other than the first of a month splits the monthly pay of the run between the level before and the new level by the payable days of the CCNL daily quota on each side of the promotion, component by component, as a month of hire or termination; the hourly quotas of the month read the same split chain. No source sets the split (art. 2103 c.c. gives the higher pay from the assignment): by the maintainer's decision of 2026-11-15 the partial-month rule of the CCNL applies.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Resolved by the decision of 2026-11-15: the month is split by the partial-month rule of the CCNL.

!!! note "arrears_unused_deductions · contract_renewal_arrears · impact yes · resolved"
    The engine computes the rate of the separate taxation of arrears from PriorYearTaxFacts.net_income_biennio (art. 21 cc. 1, 3 TUIR) and reduces the tax by ArrearsEvent.unused_deductions, the deductions of artt. 12 and 13 cc. 1-2 the worker did not use in the years the arrears refer to (art. 21 c. 4). An arrears event that does not state them, among which the una tantum the engine pays itself, is taxed without the reduction, so the tax may be overstated.

    **Applies when:** `contract_renewal_arrears` applies; the run takes the engine code path.

    **Remediation:** Resolved: art. 21 c. 4 TUIR (Normattiva, https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art21!vig=, sha256 aafc3e5d5cd7254c7eb52e74051e86f1243b3a7b3cbadcd951daf7bc5e113fc6): 'Gli aventi diritto agli arretrati devono dichiarare al soggetto che li corrisponde l'ammontare delle detrazioni fruite per ciascuno degli anni cui si riferiscono'. The deductions are a fact the worker declares: ArrearsEvent.unused_deductions, and PriorYearTaxFacts.arrears_unused_deductions for the una tantum the engine pays as arrears; unstated, the run carries the missing-fact issue arrears_unused_deductions_unknown. Read on 2026-11-14.

!!! warning "una_tantum_readings · base_salary · impact unknown · open"
    The una tantum of a renewal is paid from the CCNL data with readings no text read settles in full: a month of service in the covered period counts with the days of the una tantum (15 when the text is silent), over the months of the period; the absences of a month do not reduce it, though a text may pay the months 'di effettiva prestazione'; a part time is paid in proportion to its hours; a run without the employment period is paid none; the share of the covered months of earlier years is taxed apart as arrears.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source the counting of the months, the part time and the taxation of each una tantum from its agreement, then resolve this limitation.

!!! warning "sunday_holiday_ccnl_clause · sunday_holiday · impact yes · open"
    L. 260/1949 art. 5 pays the workers with a fixed salary a further daily quota only for the civil holidays (25 April, 1 May, 2 June) falling on a Sunday; the other holidays of art. 2 (1 January, 6 January, Easter Monday, 15 August, 4 October, 1 November, 8 December, 25 and 26 December) give it only by CCNL clause, and the payment of 4 November is a CCNL institute. A run of a month with such a holiday on a Sunday, in a CCNL whose clause is not sourced (work_rules.sunday_holidays), pays the statutory holidays only; a public employment is paid as a private one (art. 5 names the "Stato, enti pubblici e datori privati").

    **Applies when:** `sunday_holiday` applies; the run takes the engine code path.

    **Remediation:** Source the CCNL clause on the holidays falling on a Sunday and record it as work_rules.sunday_holidays.

!!! note "pension_extra_deduction_first_employed · pension_fund_contribution · impact unknown · resolved"
    A worker first employed after D.Lgs. 252/2005 came into force may deduct, in the twenty years after the fifth year of membership, the contributions above the annual cap within the room the first five years left, up to half the annual cap (art. 8 c. 6). The withholding agent applies it (AdE circ. 70/E/2007: the employer excludes the deductible contributions from the income of the ritenute): the worker states the deduction of the year as PensionFundEnrolment.extra_deduction, and contributions above the cap left with none stated carry the missing fact extra_deduction.

    **Applies when:** `pension_fund_contribution` applies; the run takes the engine code path.

    **Remediation:** Resolved: the extra deduction is an input of the enrolment.

### Without monetary impact

!!! note ""
    SIMPLIFICATION: Overtime bands not modeled (no standard rates found in public sources; article-specific complexity).

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://anav.it/wp-content/uploads/2025/05/accordo-nazionale-di-rinnovo-del-ccnl-noleggio-autobus-con-conducente-e-le-relativie-attivita-correlate-23-maggio-2025.pdf | altro | 2025-05-23 | [↗](https://anav.it/wp-content/uploads/2025/05/accordo-nazionale-di-rinnovo-del-ccnl-noleggio-autobus-con-conducente-e-le-relativie-attivita-correlate-23-maggio-2025.pdf) |
| https://anav.it/wp-content/uploads/2022/10/aumentoretributivonoleggio-07102022.pdf | tabella_retributiva | 2022-10-06 | [↗](https://anav.it/wp-content/uploads/2022/10/aumentoretributivonoleggio-07102022.pdf) |
| https://www.redigo.info/2025/05/27/ccnl-noleggio-autobus-con-conducente-laccordo-di-rinnovo-2024-2026/ | altro | 2025-05-23 | [↗](https://www.redigo.info/2025/05/27/ccnl-noleggio-autobus-con-conducente-laccordo-di-rinnovo-2024-2026/) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=548 | tabella_retributiva | 2025-05-23 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=548) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = retribuzione tabellare; fixed_allowances per level: CONTINGENZA (frozen) + EDR (10.33, frozen since Protocollo 1992) + EDR_RINNOVO (new EDR from 2025-07-01, per level, 14 mensilita) + INDENNITA_FUNZIONE (Q1=67.00, Q2=51.00 only).
    
    SALARY TABLE: 2024-2026 contract signed 23/05/2025, validity 01/01/2024-31/12/2026. Two salary tranches: T1 from 01/07/2025 (+60 EUR at C2, riparametrate), T2 from 01/08/2026 (+100 EUR at C2, riparametrate). New EDR (EDR_RINNOVO) introduced from 01/07/2025: 40.00 EUR at C2, riparametrate per level, paid for 14 mensilita.
    
    TABLE BEFORE JULY 2025: the retribuzione tabellare from 1 January 2024 to 30 June 2025 is the ott-23 column of Allegato n. 5 of the signed renewal of 6 October 2022 (p. 83, read on the page image), the last increase of Art. 70 b) (p. 75); the renewal of 23 May 2025 raises the table only from July 2025 and pays January 2024-May 2025 as una tantum. C4 is 796,26 as in the signed annex (the ANAV circular of 7 October 2022 prints 796,25).
    
    SENIORITY (Art. 47 of the signed renewal of 6 October 2022, CNEL 154242, pp. 79-80, kept by the renewal of 23 May 2025): an increment for every two years of service, up to nine, Q1, Q2 and A1 33,10, A2 32,19, B1 30,36, B2 29,57, B3 29,39, C1 29,23, C2 27,17, C3 26,61, C4 25,35; paid from the month after the biennium (c. 2). The amounts were first taken from the IC35 tables, which print the same figures.
    
    HOURLY DIVISOR: 173, consistent with 40h/week x 52/12 = 173.33 convention; ADDITIONAL MONTHS: 14 (tredicesima + quattordicesima).
    
    TAX SECTOR: terziario (same classification as IC35 autorimesse; bus rental companies fall under ATECO division 49 which uses terziario INPS rates).
    
    SALARY TABLES: the minimums of October 2023 are those of the signed CCNL of 6 October 2022 (allegato 5, PDF p. 83; the same column of ANAV's Allegato n. 2 of 7 October 2022); the renewal of 23 May 2025 (ANAV, signed, pp. 1-2) adds 60 EUR at C2 from July 2025 and 100 EUR from August 2026, re-proportioned by the parameters (100/134 for C4 and so on). The agreement does not state the rounding of the re-proportioned amounts: the file rounds the whole increase once, as the 2022 Allegato n. 2 adds the aumento a regime to the old tabellare (a cent may differ from rounding each tranche, e.g. C4 915,65 against 915,66).
    
    APPRENTICE SENIORITY (Art. 21 c. 9-10, p. 37): the apprentice pay lists 'la retribuzione tabellare, l'ex indennità di contingenza + e.d.r.' and named allowances, no increment; on continuation 'l'intero periodo di apprendistato professionalizzante è utile [...] ai fini degli aumenti periodici di anzianità'. apprentice_amount 0 during the apprenticeship and apprenticeship_credit_share 1 after it.
    

## Raw data

The contract file this page is generated from: [`agreement/noleggio-autobus-conducente-anav.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/noleggio-autobus-conducente-anav.json).

## Usage example

```python
--8<-- "docs/examples/agreement/noleggio-autobus-conducente-anav/example.py"
```
