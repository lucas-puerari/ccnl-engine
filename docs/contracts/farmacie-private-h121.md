# CCNL Dipendenti delle Farmacie Private

| | |
|---|---|
| **CNEL code** | `H121` |
| **Sector** | Farmacie private |
| **Family** | `farmacie` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2021-09-07 |
| **Workers (est.)** | ~60k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - FEDERFARMA
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS

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
| **Rule provenance** | 13 verified / 42 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2021-09-07 |
| **Last review** | 2026-11-16 |
| **Latest salary tranche** | 2021-11-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Titolo XVIII - Anzianità di servizio, Art. 51 (p. 23): "Le frazioni di anno sono computate a tutti gli effetti contrattuali per dodicesimi, computando come mese intero le frazioni di mese superiori a 15 giorni.". Added: more_than 15 (the file applied the engine default, at least 15 days). |
| 2026-10-31 | claude-opus-5-5 (ai) | The basis of the indemnity for the leave not taken at the end of the employment, read in the CCNL of 7 September 2021 (Artt. 24, 26, 28, 29, 55, 57). | corrected | Art. 57 (p. 24): the daily quota of the retribuzione di fatto is the monthly pay divided by 26 and the hourly quota by 173: work_rules.leave_rules.termination; the accrual of the leave is not modelled, so the basis is not used yet. |
| 2026-10-31 | claude-opus-5-5 (ai) | The measure and accrual of the ferie, the ex festività and the permits read in the CCNL of 7 September 2021 (Artt. 24, 26, 29, 51). | corrected | Art. 26 (p. 17): 26 working days of ferie for every worker; the 28 days after 36 months of the earlier pay-table source are not in the text: entitlement_tiers corrected to one tier of 26.<br>Art. 29 (p. 17): twelfths of the ferie per month of effective service: work_rules.leave_rules.ferie_accrual.<br>Art. 24 (p. 16): 32 hours of ex festività and 40 further hours of permits a year: work_rules.leave_rules.permits.<br>Art. 24 (p. 16): the 40 hours of a hire from 1 November 2021 by a pharmacy of up to 40 employees at 0%, 50% after three years, 100% after six: permits[rol].ramp with headcount_max 40. |
| 2026-11-01 | claude-opus-5-5 (ai) | The notice clause (Art. 73, p. 27). | corrected | Notice bands by level and service checked against the PDF by a separate session (delegated search and independent verification): work_rules.notice. |
| 2026-11-06 | claude-opus-5-5 (ai) | Art. 3 Area Q and Tabella C (p. 59) of the CCNL of 7 September 2021. | corrected | Q2 and Q3 get 130 EUR after 12 years in level 1 and Area Q, 100 EUR before. |
| 2026-11-08 | gpt-6-sol (ai) | Open limitations claimed to be no longer gaps: one session read the clauses and the data, a second independent session checked the claim. | confirmed | isq_twelve_year_tier: The existing Q2 and Q3 fixed allowances are EUR 100 below 144 completed months and EUR 130 from 144 months, effective 2021-11-01. Both use career_service; the engine selects supplied SeniorityFact.career_months and applies mutually exclusive <144 / >=144 gates. With qualifying mo |
| 2026-11-14 | claude-opus-5-5 (ai) | Apprentice seniority increments against art. 53 of the CCNL, from the targeted research of a separate model session; text layer. | confirmed | Art. 53 grants the increments to the lavoratore qualificato: none during the apprenticeship. |
| 2026-11-15 | claude-opus-5-5 (ai) | Holidays falling on a Sunday: the clause proposed by a separate model from the targeted research, its quote checked on the downloaded text. | confirmed | work_rules.sunday_holidays: 01-01, 01-06, easter_monday, 04-25, 05-01, 06-02, 08-15, 11-01, 12-08, 12-25, 12-26, patron, 11-04 |
| 2026-11-15 | claude-opus-5-5 (ai) | Hourly base, night, holiday and shift supplements, travel allowance: quotes located in the cited files by sha256, values read against the quotes. | corrected | Applied: hourly_base, bands[4:night_holiday], bands[5:sunday], bands[6:rest_day], bands[7:holiday].<br>Left out: bands[0:night]: more night bands the engine cannot tell apart; bands[1:night]: more night bands the engine cannot tell apart; bands[2:night]: more night bands the engine cannot tell apart; bands[3:night]: more night bands the engine cannot tell apart; none.shift_work: skipped. |
| 2026-11-16 | claude-opus-5-5 (ai) | Hourly base, night, holiday and shift supplements, travel allowance: quotes located in the cited files by sha256, values read against the quotes. | corrected | Applied: the four night bands of art. 19 by service (doors open or closed, the first 8 hours or beyond).<br>Left out: bands[4:night_holiday]: the bundle already has a night_holiday band; bands[5:sunday]: the bundle already has a sunday band; bands[6:rest_day]: the bundle already has a rest_day band; bands[7:holiday]: the bundle already has a holiday band; none.shift_work: skipped. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q1` | Area Q1 - Direttore responsabile di farmacia | € 1,668.97 | 2021-11-01 |
| `Q2` | Area Q2 - Farmacista collaboratore specializzato | € 1,499.19 | 2021-11-01 |
| `Q3` | Area Q3 - Farmacista collaboratore con 24+ mesi in qualifica | € 1,429.19 | 2021-11-01 |
| `1` | 1o livello - Farmacista collaboratore | € 1,429.19 | 2021-11-01 |
| `2` | 2o livello - Lavoratori di concetto con funzioni di coordinamento | € 1,215.92 | 2021-11-01 |
| `3` | 3o livello - Lavoratori di concetto con conoscenze tecniche | € 1,130.17 | 2021-11-01 |
| `4` | 4o livello - Lavoratori con compiti operativi e conoscenze tecnico-pratiche | € 1,017.02 | 2021-11-01 |
| `5` | 5o livello - Lavoratori qualificati con normali conoscenze | € 898.97 | 2021-11-01 |
| `6` | 6o livello - Lavoratori di pulizia e operazioni semplici | € 807.81 | 2021-11-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 15 increments

| Level | Increment (monthly) |
|---|---:|
| `Q1` | € 25.82 |
| `Q2` | € 25.30 |
| `Q3` | € 25.30 |
| `1` | € 25.30 |
| `2` | € 23.24 |
| `3` | € 22.72 |
| `4` | € 20.65 |
| `5` | € 20.14 |
| `6` | € 19.62 |

## Apprenticeship

**farmacista_collaboratore** (type: `under_classification`)  
Destination levels: `1`

**professionalizzante** (type: `under_classification`)  
Destination levels: `4`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! note "farmacie-private-h121/apprentice_seniority · seniority · impact unknown · resolved"
    APPRENTICE SENIORITY: art. 53 of the CCNL 7 September 2021 (PDF p. 23, https://uiltucs.it/wp-content/uploads/2023/07/CCNL-per-i-Dipendenti-da-Farmacia-Privata-7-settembre-2021.pdf, sha256 dfc1fc57234cb43fb5ab7a4a7e22d89c464b7784b344cedd288de560f170cea4) grants the 15 biennial increments to the 'lavoratore qualificato' ('Per l'anzianità maturata presso la stessa farmacia il lavoratore qualificato ha diritto a 15 scatti biennali'), so no increment is paid during the apprenticeship (apprentice_amount 0). The service still runs from the hire (art. 51): the bienni of the apprenticeship count once the worker is qualified.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: art. 53 read on 2026-11-14.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

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
| https://www.mnlf.it/documenti/ContrattoCollettivoNazionalediLavorodeidipendentidafarmaciaprivata2021.pdf | altro | 2021-09-07 | [↗](https://www.mnlf.it/documenti/ContrattoCollettivoNazionalediLavorodeidipendentidafarmaciaprivata2021.pdf) |

??? note "Coverage notes"
    Salary model: split. base_salary = retribuzione base nazionale conglobata (Tabella A, Art. 58). fixed_allowances = contingenza (per-level, frozen since 1977 per settore commercio) + EDR 10.33 (all levels, accordo 31/07/1992) + ISQ (Q levels, Tabella C).
    
    Divisore convenzionale 173 confirmed from Art. 57 of primary CCNL text.
    
    Additional months: 14. Art. 62 (13a mensilita) and Art. 63 (14a mensilita) confirmed from primary source.
    
    Seniority: 15 scatti biennali (Art. 53). Amounts from Tabella D (1.2.1996 column) of primary CCNL PDF.
    
    Contract expired 31/08/2024 (Art. 102). No successor signed as of 2026-09-09 (INPS-CNEL spreadsheet updated 25/07/2026 shows Periodo finale=null for H121). Tables valid open-ended under ultrattività.
    
    SIMPLIFICATION resolved: The CCNL rinnovo 07/09/2021 (Tabella A confirmed from UILTUCS primary PDF) established ONE salary tranche from 01/11/2021 — not three separate tranches. Increases vs. Dec 2012 base: Q1=+89.97, Q2=+150.00 (incl. 70 Area Q2), Q3=+80.00, L1=+80.00, L2=+70.98, L3=+67.39, L4=+62.65, L5=+57.72, L6=+53.90. These are fully modelled in this file. The '3 tranches / +113 EUR' figure cited in some secondary sources refers to the separate CCNL farmacie speciali/municipalizzate (Assofarm H122), not this contract.
    
    Apprenticeship from Accordo 14 giugno 2012 (Allegato II). Farmacista collaboratore (dest 1o) stays at level 1o for all 36 months. Commesso/Magazziniere/Contabile (dest 4o): months 0-12 at level 6o, months 13-36 at level 5o.
    
    Headcount: 77,146 workers in 16,324 companies (INPS-CNEL archive, H121).
    
    TABLE: Tabella A, the urban and non-subsidised rural pharmacies; the Farmacie rurali sussidiate (Tabella B) are the sibling farmacie-rurali-sussidiate-h121.
    
    SIMPLIFICATION: Tabella D groups Q2, Q3, and 1o into a single scatto amount of 25.30 EUR. Q1 uses 25.82 EUR.
    

## Raw data

The contract file this page is generated from: [`agreement/farmacie-private-h121.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/farmacie-private-h121.json).

## Usage example

```python
--8<-- "docs/examples/agreement/farmacie-private-h121/example.py"
```
