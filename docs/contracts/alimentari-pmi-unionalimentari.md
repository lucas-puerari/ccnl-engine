# CCNL Dipendenti Piccola e Media Industria Alimentare (Unionalimentari-Confapi)

| | |
|---|---|
| **CNEL code** | `E018` |
| **Sector** | Alimentare |
| **Family** | `alimentare` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-05-28 |
| **Workers (est.)** | ~35k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - UNIONALIMENTARI-CONFAPI
    - FAI-CISL
    - FLAI-CGIL
    - UILA-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ✅ |
| **Limits of this contract** | overtime |

1 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 273 verified / 38 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-05-28 |
| **Last review** | 2026-11-16 |
| **Latest salary tranche** | 2028-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Art. 48 - Tredicesima mensilità (p. 127): "Nel caso di inizio o di cessazione del rapporto di lavoro durante il corso dell’anno, il lavoratore ha diritto a tanti dodicesimi della gratifica natalizia quanti sono i mesi di anzianità di servizio presso l’azienda. La frazione di mese superiore ai 15 giorni viene considerata a questi effetti mese intero.". Added: more_than 15 (the file applied the engine default, at least 15 days). |
| 2026-11-07 | claude-opus-5-5 (ai) | Art. 47 of the verbale of 28 May 2025 (p. 26, page image): the minimi from 1 April 2027 and 1 January 2028. | corrected | Two tranches of 70 EUR at parametro 137, reparametrised per level; the 2025 and 2026 columns equal the file. |
| 2026-11-07 | claude-opus-5-5 (ai) | The monthly values of the levels against the primary tables (text layer). | confirmed | 54 values found verbatim on the cited pages and marked verified; 18 left as they were (derived or not on a text page). |
| 2026-11-08 | gpt-6-sol (ai) | Art. 36 sickness rules of the CCNL 2024-2028 (alimentare): proposal by one session, field-by-field check of the text by a second independent session. | corrected | Comporto as a sum over the 17 months (up to 5 years of seniority, 180 days) or 24 months (over 5 years, 365 days) before the day, 'anche in caso di diverse malattie': modelled as cumulation; 180 days at full net pay, then 50%.<br>The second session confirmed 15 fields; the window_years fallback and the band boundaries are schema conventions, not contractual windows. |
| 2026-11-14 | claude-opus-5-5 (ai) | Art. 47 table of the consolidated text signed on 18 March 2026 (PDF p. 144), read on the page image, against the file and the verbale of 28 May 2025 (p. 26). | corrected | 21 minimi of 2026-2028 differed by one or two cents from the later signed text and were corrected.<br>Both signed documents set four tranches of EUR 70: the 2027 and 2028 tranches are confirmed. |
| 2026-11-14 | claude-opus-5-5 (ai) | Panificazione industriale pay of the text signed on 18 March 2026 (PDF p. 145, 147-148, 153-154, 160), read on the page images, against the research of a separate model session on the CCNL 2021. | corrected | Added the seven panificazione industriale levels with paga base, contingenza, premio di produzione, premio per obiettivi and scatti.<br>The contingenza of the sector (art. 47 bis) is new in the 2026 text; the CCNL 2021 had none for these levels. |
| 2026-11-14 | claude-opus-5-5 (ai) | Art. 29 tables of the text signed on 18 March 2026 (PDF p. 109-119), read on the page images, against the Federalimentare art. 31 bands. | corrected | The file had unverified overtime rates of 40%, 45% and 50% for everyone; the signed tables pay 45% for weekday overtime in every sub-sector and differ by sub-sector and category.<br>The sub-sector tables equal those of Federalimentare art. 31; the first also covers the prodotti da forno; the panificazione has its own table. |
| 2026-11-16 | claude-opus-5-5 (ai) | Parental leave by the hour (art. 32 c. 1-bis D.Lgs. 151/2001): the clause located in the cited file by sha256. | corrected | Applied: work_rules.parental_hourly. |
| 2026-11-16 | claude-opus-5-5 (ai) | Hourly base, night, holiday and shift supplements, travel allowance: quotes located in the cited files by sha256, values read against the quotes. | corrected | Applied: travel. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `P1` | Panificazione industriale 1° livello: preposti ai servizi commerciale, amministrativo, tecnico e chimico con discrezionalità di poteri | € 2,047.17 | 2028-01-01 |
| `P2` | Panificazione industriale 2° livello: funzioni di concetto con compiti di controllo e di coordinamento | € 1,886.71 | 2028-01-01 |
| `P3A` | Panificazione industriale 3A livello: guidano, controllano, coordinano squadre di altri lavoratori | € 1,737.12 | 2028-01-01 |
| `P3B` | Panificazione industriale 3B livello: impastatore, infornatore con responsabilità diretta, conduttore di forni | € 1,616.40 | 2028-01-01 |
| `P4` | Panificazione industriale 4° livello: attività tecniche qualificate nella produzione, confezione, distribuzione | € 1,364.56 | 2028-01-01 |
| `P5` | Panificazione industriale 5° livello: attività semplici o di esclusivo ausilio | € 1,216.31 | 2028-01-01 |
| `P6` | Panificazione industriale 6° livello: lavori di semplice manovalanza | € 1,024.10 | 2028-01-01 |
| `Q` | Quadri (executive staff) | € 3,105.90 | 2028-01-01 |
| `1` | 1st level — senior specialists and team leaders | € 3,005.90 | 2028-01-01 |
| `2` | 2nd level — skilled specialists | € 2,613.80 | 2028-01-01 |
| `3` | 3rd level — intermediate skilled workers | € 2,156.43 | 2028-01-01 |
| `4` | 4th level — qualified workers | € 1,895.05 | 2028-01-01 |
| `5` | 5th level — semi-skilled workers | € 1,698.98 | 2028-01-01 |
| `6` | 6th level — standard production workers | € 1,568.26 | 2028-01-01 |
| `7` | 7th level — basic production workers | € 1,437.59 | 2028-01-01 |
| `8` | 8th level — entry-level workers, simple repetitive tasks | € 1,306.90 | 2028-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 54.62 |
| `1` | € 51.42 |
| `2` | € 44.71 |
| `3` | € 36.89 |
| `4` | € 32.42 |
| `5` | € 29.06 |
| `6` | € 26.83 |
| `7` | € 24.59 |
| `8` | € 22.35 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "alimentari-pmi-unionalimentari/bakery_premium_cumulation · overtime · impact yes · open"
    BAKERY PREMIUM CUMULATION (art. 29, PANIFICAZIONE, PDF p. 119): the premiums marked * are 'Cumulabile con le altre maggiorazioni in misura non superiore al 55%'; the engine applies the higher premium alone, as for the other tables, so overtime at night or on holidays of the panificazione is underpaid.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Cumulate the panificazione premiums marked * up to 55% above the highest one.

!!! note "sickness_inps_daily_base · sickness · impact unknown · resolved"
    The INPS share of a sick day is computed on the INPS daily base of the episode, on the days INPS pays (the weekdays of an operaio, every day but the national holidays on a Sunday of an impiegato, point 7.3 of INPS circ. 134368/1981): the retribuzione media globale giornaliera of the month before the illness (INPS circ. 134368/1981 point 11; circ. 55/2024 Allegato 1), whole or partial month, impiegato or operaio, or for the lavoratori dello spettacolo the average pay of the last 40 daily contributions, capped for a fixed-term worker (INPS circ. 132/2021 par. 2.4). The base is a fact of the payroll history the episode states (SicknessEpisode.inps_base).

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Resolved: the INPS share is computed on the base of every regime of the bundle; an episode that states no base the engine can read has the missing_fact issue sickness_inps_base_unknown (fact inps_base), which blocks the run. Tests: tests/mutation/ccnl_engine/sickness/base/test_rules_wiring.py, tests/mutation/ccnl_engine/sickness/base/test_rules.py.

!!! warning "provisional_ruleset · irpef · impact unknown · awaiting_publication"
    The run reads a tax ruleset marked provisional: the sources of its year are not published yet (budget law of the year; regional and municipal surtax resolutions), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

!!! warning "provisional_inps_ruleset · inps_employer · impact unknown · awaiting_publication"
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

!!! warning "parental_income_condition · parental_leave · impact unknown · awaiting_publication"
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

!!! note "pension_extra_deduction_first_employed · pension_fund_contribution · impact unknown · resolved"
    A worker first employed after D.Lgs. 252/2005 came into force may deduct, in the twenty years after the fifth year of membership, the contributions above the annual cap within the room the first five years left, up to half the annual cap (art. 8 c. 6). The withholding agent applies it (AdE circ. 70/E/2007: the employer excludes the deductible contributions from the income of the ritenute): the worker states the deduction of the year as PensionFundEnrolment.extra_deduction, and contributions above the cap left with none stated carry the missing fact extra_deduction.

    **Applies when:** `pension_fund_contribution` applies; the run takes the engine code path.

    **Remediation:** Resolved: the extra deduction is an input of the enrolment.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.unionalimentari.com/ | tabella_retributiva | 2025-05-28 | [↗](https://www.unionalimentari.com/) |
| https://www.lavorofacile.it/ | altro | 2021-04-01 | [↗](https://www.lavorofacile.it/) |
| CCNL Alimentari PMI Unionalimentari Confapi, verbale di accordo di rinnovo 28 maggio 2025 (con rettifica 6 giugno 2025) | associazione | 2025-05-28 | [↗](https://www.uila.eu/web/wp-content/uploads/2022/04/CCNL-Unionalimentari-Confapi-Verbale-di-rettifica-28-06-25.pdf) |
| CCNL piccola e media industria alimentare Unionalimentari-Confapi 2024-2028, testo firmato Roma 18 marzo 2026 (scansione, copia UILA) | associazione | 2026-03-18 | [↗](https://www.uila.eu/web/wp-content/uploads/2022/04/CCNL-piccola-e-media-industria-alimentare-28-05-2025q.pdf) |

??? note "Coverage notes"
    Salary model: split. base_salary = paga base (changes each tranche); fixed_allowances = contingenza (per-level, frozen since 1993 Protocol) + EDR 10.33 (all levels, per Protocol 31/07/1992 Art. 1.1).
    
    Hourly divisor 173 confirmed from primary source: Art. 4.3 CCNL text (lavorofacile.it). Cross-check: level 8 Jan 2026 total = 1204.73 + 514.74 + 10.33 = 1729.80; 1729.80 / 173 = 10.00 EUR/h exactly. Art. 4.4 sets the normal workweek at 39h; computing 39 x 52 / 12 = 169h/month, not 173. The CCNL resolves this by stating the coefficient explicitly in Art. 4.3 — the arithmetic cross-check confirms 173 is the operative value.
    
    Additional months: 14 confirmed from Art. 4.1 CCNL text (mensilita: 14). Art. 5.3 = tredicesima, Art. 5.4 = quattordicesima.
    
    Seniority: 5 biennali per Art. 5.5 CCNL text (settore alimentare). Fixed EUR amounts from 2021 CCNL; 2025 Unionalimentari circular (28/05/2025) makes no mention of changes to scatti amounts.
    
    Salary tranches: 01/06/2025, 01/01/2026, 01/04/2027 and 01/01/2028, EUR 70 each at parametro 137 (art. 47 of the verbale of 28 May 2025 and of the consolidated text signed on 18 March 2026).
    
    Apprenticeship: Art. 8.1 CCNL — under-classification model, levels 1 through 7, multi-period per destination level. Complex schedule not publicly parsed in full. layer_2 = out_of_scope.
    
    Headcount: ~34,646 workers (CNEL archive, E018).
    
    PANIFICAZIONE INDUSTRIALE (text signed 18 March 2026): levels P1, P2, P3A, P3B, P4, P5, P6 (1°, 2°, 3A, 3B, 4°, 5°, 6°) only for an employer of the sub-sector panificazione_industriale, on a ladder of their own: paga base (4 tranches of EUR 70 at 3B), contingenza of art. 47 bis, premio di produzione nazionale (14 months, out of the TFR by the exhaustive list of art. 59), premio per obiettivi of the sector in place of art. 53 (12 months) and five biennial scatti frozen at the 1997 amounts. No EDR: the signed text names none for the sector.
    
    TRANCHES 2027-2028 (art. 47): 70.00 EUR at parametro 137 from 1 April 2027 and again from 1 January 2028, as in the verbale signed 28 May 2025 (p. 26) and the consolidated text signed 18 March 2026 (PDF p. 144). The association circular's prose giving 32 EUR for the third tranche is wrong. Where the two signed tables differ by a cent the later text is used: it adds each increment to the previous minimo exactly (e.g. 3rd level 1,987.81 from 1 January 2026, 1,987.80 in the verbale).
    
    OVERTIME AND PREMIUMS (art. 29, text signed 18 March 2026, PDF p. 109-119): the tables by EmployerProfile.subsector (carni, dolciari, alimenti_zootecnici, lattiero_caseari, prodotti_da_forno, vini_liquori, bevande_gassate, acque_minerali, distillatori, birra_malto, conserve_vegetali, alimentari_varie, risiera, molitoria_pastificazione, conserve_ittiche, avicoli, panificazione_industriale), by category (the operai column; the impiegati column for impiegati and quadri), equal to the Federalimentare art. 31 tables. The intermedi column and the rows of overtime of shift workers and festive night overtime beyond 8 hours are not modelled: the caller states those rates. The 90% Sunday of the bread staff takes the role 'addetto_pane'.
    

## Raw data

The contract file this page is generated from: [`agreement/alimentari-pmi-unionalimentari.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/alimentari-pmi-unionalimentari.json).

## Usage example

```python
--8<-- "docs/examples/agreement/alimentari-pmi-unionalimentari/example.py"
```
