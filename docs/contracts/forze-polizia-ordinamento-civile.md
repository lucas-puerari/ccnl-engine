# DPR 24 marzo 2025, n. 53 — Forze di Polizia ad ordinamento civile (Triennio 2022-2024)

| | |
|---|---|
| **CNEL code** | `N/A` |
| **Sector** | Pubblica Sicurezza — Forze di Polizia ad ordinamento civile |
| **Family** | `forze-polizia` |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2025-03-24 |
| **Workers (est.)** | ~130k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Presidenza del Consiglio dei Ministri
    - SIULP
    - SAP
    - SIAP
    - FSP Polizia di Stato
    - Federazione COISP-MOSAP
    - SILP CGIL
    - SAPPE
    - SINAPPE
    - OSAPP
    - UILPA PP
    - USPP
    - CISL FNS

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

5 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 112 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-03-24 |
| **Last review** | 2026-11-10 |
| **Latest salary tranche** | 2024-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-11-10 | claude-opus-5-5 (ai) | Functional seniority allowance annual tables, targeted amendment and stipend conversion convention. | corrected | The allowance is paid on the thirteenth; the source does not print the installment divisor. Disciplinary and special-rank eligibility remains limited. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `COMM_CAPO` | Commissario Capo (param 150,50) | € 2,451.90 | 2024-01-01 |
| `SOST_COMM_COORD` | Sostituto Commissario Coordinatore (param 148,00) | € 2,411.17 | 2024-01-01 |
| `COMMISSARIO` | Commissario (param 148,00) | € 2,411.17 | 2024-01-01 |
| `SOST_COMM` | Sostituto Commissario (param 143,50) | € 2,337.85 | 2024-01-01 |
| `ISP_SUP_8A` | Ispettore Superiore con 8 anni di qualifica (param 140,00) | € 2,280.83 | 2024-01-01 |
| `ISP_SUPERIORE` | Ispettore Superiore (param 137,50) | € 2,240.10 | 2024-01-01 |
| `VICE_COMM` | Vice Commissario (param 136,75) | € 2,227.89 | 2024-01-01 |
| `ISP_CAPO` | Ispettore Capo (param 133,50) | € 2,174.94 | 2024-01-01 |
| `SOV_CAPO_COORD` | Sovrintendente Capo Coordinatore (param 131,00) | € 2,134.21 | 2024-01-01 |
| `ISPETTORE` | Ispettore (param 131,00) | € 2,134.21 | 2024-01-01 |
| `SOV_CAPO_4A` | Sovrintendente Capo con 4 anni di qualifica (param 125,75) | € 2,048.68 | 2024-01-01 |
| `VICE_ISP` | Vice Ispettore (param 124,75) | € 2,032.39 | 2024-01-01 |
| `SOV_CAPO` | Sovrintendente Capo (param 124,25) | € 2,024.24 | 2024-01-01 |
| `ASSISTENTE_CAPO_COORD` | Assistente Capo Coordinatore (param 121,50) | € 1,979.44 | 2024-01-01 |
| `SOVRINTENDENTE` | Sovrintendente (param 121,50) | € 1,979.44 | 2024-01-01 |
| `ASSISTENTE_CAPO_5A` | Assistente Capo con 5 anni di qualifica (param 117,00) | € 1,906.13 | 2024-01-01 |
| `VICE_SOV` | Vice Sovrintendente (param 116,75) | € 1,902.05 | 2024-01-01 |
| `ASSISTENTE_CAPO` | Assistente Capo (param 116,50) | € 1,897.98 | 2024-01-01 |
| `ASSISTENTE` | Assistente (param 112,00) | € 1,824.67 | 2024-01-01 |
| `AGENTE_SCELTO` | Agente Scelto (param 108,50) | € 1,767.65 | 2024-01-01 |
| `AGENTE` | Agente (param 105,25) | € 1,714.70 | 2024-01-01 |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "forze-polizia-ordinamento-civile/assegno_funzionale_conditions_and_special_ranks · seniority · impact yes · open"
    Functional seniority allowance at 17, 27 and 32 years: the tabular annual rate is divided by 12 and also affects the thirteenth monthly payment. The standard rank rows are modelled; commissioners require the promoted_from_lower_rank worker role. Entitlement depends on qualifying service without demerit.

    **Applies when:** `seniority` applies.

    **Remediation:** Validate disciplinary assessments over the two years preceding each threshold (D.P.R. 254/1999 art. 5(3)); distinguish eligible service from raw seniority, model special coordinator and intermediate ranks including D.P.R. 57/2022 art. 5 increments and four-year designation conditions, and determine commissioner origin. The sources do not state the allowance installment divisor; annual/12 plus a thirteenth is an explicitly stated convention inferred from the stipend table and D.L. 387/1987 art. 6(4)-(5).

!!! note "forze-polizia-ordinamento-civile/ctps_rates_proxy · inps_employer · impact unknown · resolved"
    aliquote INPS/CTPS — dipendente 8,80%, datore 24,20% — proxy dal file 2026-pubblica-amministrazione.json già presente; verificare circolare INPS annuale per valori esatti (regime CTPS ex-INPDAP, identico a PA ordinaria).

    **Applies when:** `inps_employer` applies.

    **Remediation:** Resolved (review of 2026-10-30): the CTPS rates of the bundle (employer 24.20%, employee 8.80%) are read from the INPS page 'I contributi dei dipendenti pubblici' (contribution/2026/pubblica-amministrazione.json, inps.provenance, verified, checked on 2026-10-09 and 2026-10-17), as for funzioni-centrali-aran/ctps_rates_proxy.

!!! warning "forze-polizia-ordinamento-civile/renewal_2025_2027_pending_dpr · base_salary · impact yes · open"
    Accordo triennio 2025-2027 (Comparto Sicurezza-Difesa) firmato 2026-07-15 a Palazzo Vidoni. Tre nuovi valori del punto parametrale: 200,90 EUR/anno (decorrenza 2025-01-01), 205,40 EUR/anno (2026-01-01), 207,51 EUR/anno (2027-01-01), da T3=195,50. Incremento totale +12,01 punti pari al +6,14%. Retroattività 2025 e 2026 in forma di arretrati. DPR di recepimento (art. 2 D.Lgs. 195/1995) non ancora emanato al 2026-09-09; firma definitiva sospesa per il nodo della previdenza dedicata. I nuovi periodi non sono modellati in attesa del DPR. Fonte: UIL Polizia (uilpolizia.com), money.it.

    **Applies when:** `base_salary` applies; from 2025-01-01.

    **Remediation:** Add the punto parametrale 200.90 / 205.40 / 207.51 periods when the DPR is issued, then remove this limitation.

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

### Without monetary impact

!!! note ""
    cnel_code = 'N/A' — il CNEL non assegna codici agli accordi DPR-based (questo comparto è escluso dalla contrattazione collettiva ordinaria ex D.Lgs. 195/1995 e resta in regime di diritto pubblico). Il CNEL medesimo non include questo comparto nel proprio archivio contratti.

!!! note ""
    valori mensili arrotondati col metodo a due passi (annual = round(param × punto, 2); monthly = round(annual / 12, 2)) per allineamento con le tavole dell'ipotesi di accordo 18/12/2024. Differenza massima da calcolo diretto: 1 centesimo.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| DPR 24 marzo 2025 n. 53, GU n. 91 del 18/04/2025 SO n. 12. Recepimento accordi sindacali triennio 2022-2024 per personale Forze di polizia ad ordinamento civile e militare. In vigore dal 03/05/2025. Testo normativo di riferimento; tavole retributive Art. 6 non direttamente estratte da questo atto — verificare allegati DPR per conferma. I valori sono stati estratti dall'ipotesi di accordo 18/12/2024 (seconda fonte). | altro | 2025-03-24 | [↗](https://www.normattiva.it/atto/caricaDettaglioAtto?atto.dataPubblicazioneGazzetta=2025-04-18&atto.codiceRedazionale=25G00046&atto.articolo.numero=0&atto.articolo.sottoArticolo=1&atto.articolo.sottoArticolo1=0&qId=1ede7c71-4666-4c74-b496-2391fce88e7f) |
| Ipotesi di accordo sindacale Forze di Polizia ad ordinamento civile triennio 2022/2024 sottoscritta il 18/12/2024 (fonte Autonomi di Polizia). Tavole retributive Art. 6 usate per estrazione dei parametri e valori mensili. | altro | 2024-12-18 | [↗](https://nazionale.autonomidipolizia.it/wp-content/uploads/2024/12/ipotesi-accordo-18-12-2024.pdf) |

??? note "Coverage notes"
    Primo accordo DPR-based nel repository. Il Comparto Sicurezza-Difesa è disciplinato dal D.Lgs. 195/1995 — non da ARAN né da CCNL. Gli accordi sindacali sono recepiti con DPR (non con CCNL). DPR 53/2025 copre Polizia di Stato (97.931 effettivi, fonte poliziadistato.it 2024) e Corpo di Polizia Penitenziaria (~31.000 effettivi, fonte Rapporto Antigone 2025 / DAP): totale ~129.000 dipendenti.
    
    Perimetro DPR 53/2025 — Art. 1: personale non dirigente delle Forze di polizia ad ordinamento civile (Polizia di Stato) e militare (Polizia Penitenziaria). Forze Armate (Esercito, Marina, Aeronautica), Carabinieri e Guardia di Finanza non rientrano.
    
    Modello parametrico. Stipendio mensile = param × punto_parametrale_annuo / 12. Punto parametrale: T1 183,6993 €/anno (1/4/2022), T2 184,0659 €/anno (1/7/2022–31/12/2023), T3 195,50 €/anno (1/1/2024–). Fonte: Art. 6 DPR 53/2025 e ipotesi di accordo 18/12/2024.
    
    Confirmed consolidated base salary: IIS was incorporated from 1 January 2005 (D.Lgs. 193/2003). The functional seniority allowance is separate from the consolidated base salary and is recorded in fixed_allowances for the sourced standard ranks.
    
    `order` assegnato per parametro crescente, non per gerarchia di carriera. Tre inversioni strutturali: Vice Sovrintendente (116,75) > Assistente Capo (116,50); Vice Ispettore (124,75) > Sovrintendente Capo (124,25); Vice Commissario (136,75) < Sostituto Commissario (143,50). Tre parità: SOVRINTENDENTE/ASSISTENTE_CAPO_COORD (121,50), ISPETTORE/SOV_CAPO_COORD (131,00), COMMISSARIO/SOST_COMM_COORD (148,00).
    
    divisore orario 156 (36h/settimana) — DPR 18 giugno 2002 n. 164 (orario di lavoro Polizia di Stato), 36h × 52 / 12 = 156. Stessa derivazione degli altri contratti PA.
    
    Tredicesima mensilità prevista — additional_months = 13.
    
    Apprendistato assente — il reclutamento avviene per concorso pubblico (D.Lgs. 195/1995 art. 6). apprenticeship: [].
    
    validity.valid_from = 2022-01-01 (inizio periodo normativo ex Art. 1 DPR 53/2025). Gli effetti retributivi iniziano il 2022-04-01 (prima tranche stipendiale), che coincide con la data valid_from del primo periodo base_salary.
    
    Firmatari Polizia di Stato: SIULP, SAP, SIAP, FSP Polizia di Stato (ES-LS-CONSAP-M.P.), Federazione COISP-MOSAP, SILP CGIL. Firmatari Polizia Penitenziaria: SAPPE, SINAPPE, OSAPP, UILPA PP, USPP, CISL FNS. Fonte: testo DPR 53/2025.
    
    ASSICURAZIONE SOCIALE VITA. The employers of this CCNL are Amministrazioni dello Stato (the State schools; the forze di polizia), which INPS circ. 104/2014 leaves out of the Assicurazione Sociale Vita (ex ENPDEP): meta.public_life_insurance is false.
    

## Raw data

The contract file this page is generated from: [`agreement/forze-polizia-ordinamento-civile.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/forze-polizia-ordinamento-civile.json).

## Usage example

```python
--8<-- "docs/examples/agreement/forze-polizia-ordinamento-civile/example.py"
```
