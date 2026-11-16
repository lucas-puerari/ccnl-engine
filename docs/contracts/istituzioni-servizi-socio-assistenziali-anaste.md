# CCNL Istituzioni e Servizi Socio-Assistenziali (ANASTE)

| | |
|---|---|
| **CNEL code** | `T131` |
| **Sector** | servizi socio-assistenziali |
| **Family** | `socio-sanitario` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-07-23 |
| **Workers (est.)** | ~120k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANASTE
    - FISASCAT-CISL
    - UILTuCS-UIL
    - UGL Terziario

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

0 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🟢 Verified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 66 verified / 12 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-07-23 |
| **Last review** | 2026-11-16 |
| **Latest salary tranche** | 2028-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 74 - Tredicesima mensilità (p. 57): "4. Le frazioni di mese pari o superiori ai 15 giorni saranno considerate come mese intero.". Match: at_least 15. The quattordicesima differs: Art. 75: no separate 14th; an equivalent amount is already included in the minimo conglobato of art. 68, so no fraction rule applies to it. |
| 2026-11-07 | claude-opus-5-5 (ai) | Art. 69 of the CCNL ANASTE 2026-2028 signed 9 October 2026: the tabellare from 1 October 2026, 1 January 2027 and 1 January 2028 (p. 64, page image). | corrected | Three tranches of the 2026-2028 renewal; the 'tabellare vigente' column equals the August 2025 values of the file. |
| 2026-11-08 | claude-opus-5-5 (ai) | The monthly values of the levels against the primary tables (text layer). | confirmed | 52 values found verbatim on the cited pages and marked verified; 6 left as they were (derived or not on a text page). |
| 2026-11-08 | claude-opus-5-5 (ai) | Art. 70(2), p. 55: automatic absorption of the nurse allowance against individual excess. | confirmed | The EUR 155 allowance for twelve months applies only to qualified nurses and is absorbed up to concurrence by individual pay exceeding the minimum. |
| 2026-11-08 | claude-opus-5-5 (ai) | Art. 70 c. 2 (p. 55), the declaratorie of levels 6 and 7 (p. 31), artt. 68, 74, 75 and 99 of the CCNL ANASTE 2023-2025. | confirmed | Art. 70 c. 2: 155 EUR a month for 12 months to the staff 'con qualifica e mansioni di infermiere', absorbable by an individual pay above the CCNL; no starting date of its own.<br>The infermiere is named in the declaratorie of levels 6 and 7; art. 99 does not exclude the allowance from the TFR. |
| 2026-11-08 | claude-opus-5-5 (ai) | Art. 45(23), PDF p. 43: holiday top-up during compulsory maternity. | confirmed | Verified the quoted clause against the cached PDF; encoded only the compulsory maternity holiday target. |
| 2026-11-08 | gpt-6-sol (ai) | The maternity holiday clause against the encoding, by a separate model session. | corrected | Confirmed the 100% target net of the INPS share on the holidays of the compulsory leave.<br>Recorded as limitation maternity_holiday_scope: the Sunday holidays, the patron saint and 4 October, the 20% of the 13th in the compulsory absence; the publication date of the consolidated text corrected to 3 November 2025. |
| 2026-11-09 | claude-opus-5-5 (ai) | Art. 45(23), cached consolidated PDF p. 43; local holiday listing in the same agreement. | corrected | Compulsory maternity holiday integration reaches 100% daily pay; the patron saint is a contractual holiday. The 20% thirteenth-month share is still unmodelled. |
| 2026-11-15 | claude-opus-5-5 (ai) | Hourly base, night, holiday and shift supplements, travel allowance: quotes located in the cited files by sha256, values read against the quotes. | corrected | Applied: hourly_base, bands[0:night_shift], bands[1:night], bands[2:holiday], bands[3:holiday_compensatory_rest], bands[4:sunday], bands[5:night_holiday], travel. |
| 2026-11-16 | claude-opus-5-5 (ai) | Number of monthly pays: the article on the additional months located in the cited file by sha256. | corrected | Sourced: 13 monthly pays. |
| 2026-11-16 | claude-opus-5-5 (ai) | Apprentice pay (Art. 27, comma 14, PDF p. 25): the elements the percentage applies to, read in the cited file by sha256. | corrected | apprenticeship_pct_relevant INDENNITA_FUNZIONE = false: La percentuale riguarda solo il minimo conglobato; indennità quadri esterna e non spettante ai livelli apprendibili.<br>apprenticeship_pct_relevant INDENNITA_PROFESSIONALE_INFERMIERI = false: Il profilo infermiere è espressamente escluso dall’apprendistato (art. 27 c. 4): indennità non dovuta.<br>Clause: 14. Il trattamento economico dell’apprendista è determinato in percentuale rispetto al minimo contrattuale mensile
conglobato previsto dall’art. 68 del presente CCNL, con riferimento al livello di inquadramento della qualifica da
conseguire, secondo le seguenti progressioni: |
| 2026-11-16 | claude-opus-5-5 (ai) | Art. 45 c. 23 and art. 55 cc. 1 and 5, read in the 2025 text by sha256 and checked against the text signed on 9 October 2026 (sha256 e02bac8a5fd3587d63518dda5547adf4ac1e01ea835c3cc23703506c47bfb381, PDF pp. 51, 55). | corrected | Applied: the 13th of the compulsory maternity leave at 20% (decision of the maintainer of 2026-11-16: a share only where the CCNL states it).<br>The Sunday holiday is paid by art. 55 c. 5 and 4 October is not a holiday of the CCNL: the existing model holds. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro (dirigente di struttura o coordinatore senior) | € 2,252.88 | 2028-01-01 |
| `10` | Livello 10 — Responsabile di area/servizio | € 2,085.75 | 2028-01-01 |
| `9` | Livello 9 — Coordinatore/Professionista senior | € 2,002.57 | 2028-01-01 |
| `8` | Livello 8 — Operatore specializzato senior | € 1,871.54 | 2028-01-01 |
| `7` | Livello 7 — Operatore specializzato | € 1,853.92 | 2028-01-01 |
| `6` | Livello 6 — Operatore qualificato senior | € 1,794.11 | 2028-01-01 |
| `5` | Livello 5 — Operatore qualificato | € 1,731.38 | 2028-01-01 |
| `4` | Livello 4 — Operatore | € 1,652.10 | 2028-01-01 |
| `3S` | Livello 3 Super — Operatore ausiliario specializzato | € 1,612.90 | 2028-01-01 |
| `3` | Livello 3 — Operatore ausiliario | € 1,573.68 | 2028-01-01 |
| `2` | Livello 2 — Addetto generico | € 1,470.22 | 2028-01-01 |
| `1` | Livello 1 — Addetto base (introdotto nel rinnovo 2025) | € 1,370.06 | 2028-01-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 35.12 |
| `10` | € 33.57 |
| `9` | € 30.99 |
| `8` | € 30.47 |
| `7` | € 29.95 |
| `6` | € 28.92 |
| `5` | € 28.41 |
| `4` | € 27.89 |
| `3S` | € 27.63 |
| `3` | € 27.37 |
| `2` | € 26.86 |
| `1` | € 25.31 |

## Apprenticeship

**professionalizzante_12** (type: `percentage`)  
Destination levels: `5`, `4`, `3S`, `3`, `2`, `1`  
percentage: 1.00

**professionalizzante_32** (type: `percentage`)  
Destination levels: `Q`, `10`, `9`, `8`, `7`, `6`  
percentage: 1.00

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
| https://snalv.it/docs/anaste25/pdf6.pdf | altro | 2025-07-23 | [↗](https://snalv.it/docs/anaste25/pdf6.pdf) |
| CCNL ANASTE 2026-2028, testo sottoscritto il 9 ottobre 2026 | associazione | 2026-10-09 | [↗](https://www.anaste.com/download/?wpdmdl=11171) |

??? note "Coverage notes"
    UNA TANTUM 2025 (Art. 71 of the CCNL 2023-2025, consolidated text of 3 November 2025, pp. 55-56): EUR 300, 200 or 100 by hire year to the workers in service on 23 July 2025, reduced for part-time, paid in three instalments with the pay of September, October and November 2025, outside every institute and the TFR. Paid in 2025: no tax year the engine computes.
    
    CONGLOBATED (Art. 69): minimo contrattuale conglobato includes base wage, contingenza and EDR. No separate contingenza or EDR column.
    
    HOURLY DIVISOR (Art. 72): 164 h/month for 38h/week. Verified: 1696.37/10.34=164.06 (lvl 6), 1893.48/11.55=163.94 (lvl 9), 2130.15/12.99=163.98 (lvl Q).
    
    ADDITIONAL MONTHS (Art. 74): tredicesima only (paid December). Art. 75 states the quattordicesima equivalent is already embedded in the monthly conglobated minimum.
    
    SENIORITY (Art. 73): scatti triennali, max 10 scatti. Per-level amounts confirmed from Art. 73 table.
    
    LEVEL Q ALLOWANCE (Art. 70): indennita di funzione 77.47 EUR/month paid 13 months/year.
    
    LEVEL 1 PRE-2025: level 1 introduced ex-novo in 2025 renewal. Pre-2025 salary set equal to 2025-08-01 value (1295.43 EUR) — no historical data available.
    
    APPRENTICESHIP (Art. 22 c. 12-15, p. 19): levels 1-5 apprentice 12 months at 90% for months 1-6 and 95% after; levels 6-10 32 months at 90% for months 1-28 and 95% after; the full pay of the qualification from the end (c. 13). The first clause of c. 12 says 'fino a 32 mesi' for levels 1-5 too, against the 12 months of c. 15: c. 15 sets the duration. Level Q, in neither list, keeps the 32-month track.
    
    APPRENTICE SENIORITY (Apprendistato c. 12, p. 19 of the CCNL ANASTE, https://snalv.it/docs/anaste25/pdf6.pdf, sha256 0104ada3fe1307dce987c275b55e962e6db6230c0bc94d4182e406bb395c8c98): 'Il periodo di apprendistato è considerato utile ai fini della maturazione degli scatti di anzianità previsti dall’art. 73 del CCNL.' Reading: the scatti matured during the apprenticeship are those of art. 73 at the amounts of the level (seniority_increments.apprentice_level_amount).
    
    Art. 70 c. 2 (p. 55): the indennità professionale of the infermieri, 155 EUR a month on 12 payments, is a fixed allowance of levels 6 and 7 with the role 'infermiere'. The allowance is offset up to its full amount against paid Employment.individual_elements above the minimum. The TFR counts it: art. 99 does not exclude it.
    
    Art. 45 c. 23 (PDF p. 43): the holidays of the compulsory leave are topped up to 100% of the daily pay, a stated weekday patron day included; the 13th of the compulsory leave is paid 'limitatamente all'aliquota corrispondente al 20%' (extra_month_share 0.20, the months only the leave makes accrue counted at that share). A holiday falling on a Sunday is paid by its own amount of art. 55 c. 5, not by this top-up. 4 October is not among the holidays of art. 55 c. 1, nor in the text signed on 9 October 2026, so the CCNL top-up does not cover it.
    

## Raw data

The contract file this page is generated from: [`agreement/istituzioni-servizi-socio-assistenziali-anaste.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/istituzioni-servizi-socio-assistenziali-anaste.json).

## Usage example

```python
--8<-- "docs/examples/agreement/istituzioni-servizi-socio-assistenziali-anaste/example.py"
```
