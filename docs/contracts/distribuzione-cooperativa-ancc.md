# CCNL Distribuzione Cooperativa (ANCC-Coop / Confcooperative Consumo)

| | |
|---|---|
| **CNEL code** | `H016` |
| **Sector** | distribuzione-cooperativa |
| **Family** | `commercio` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-03-29 |
| **Workers (est.)** | ~63k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANCC-Coop
    - Confcooperative Consumo e Utenza
    - AGCI Agrital
    - Filcams-CGIL
    - Fisascat-CISL
    - Uiltucs-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, seniority, workplace_injury |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 62 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-03-29 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2027-03-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 190 - Mensilita' supplementari (13a e 14a) (p. 202): "il lavoratore avrà diritto a tanti dodicesimi dell'ammontare della 13a mensilità, per quanti sono i mesi interi di servizio prestati nella cooperativa intendendosi per tali le frazioni di mese superiori ai 15 giorni.". Match: more_than 15. |
| 2026-10-18 | claude-opus-5-5 (ai) | The paga base nazionale of the 9 levels on the four modelled tranches of the renewal of 29 March 2024 (1/05/2025, 1/12/2025, 1/11/2026, 1/03/2027), derived from the paga base printed by the economic renewal of 19 February 2019 plus the Art. 185 increments printed by the 2024 renewal; all texts as deposited at CNEL. | corrected | Ipotesi 29 marzo 2024 (CNEL 183889, 73-page scan read on the page image of PDF p. 70): Art. 185 prints only the per-level increments (01/04/2023, 01/04/2024, 01/05/2025, 01/12/2025, 01/11/2026, 01/03/2027; IV livello 30, 70, 30, 35, 35, 40 = 240), not the resulting minimi. The level labels (quadro, 1, 2, 3S, 3, 4S, 4, 5, 6) are the file codes; each row's increments sum to the printed TOTALE (within one or two cents of rounding, e.g. quadro 425,01 against 425,00).<br>The base is the 'Paga Base Nazionale dal 01.07.2019' table of the economic renewal of 19 February 2019 (CNEL 100291, p. 3; 'III° Liv.Super' = 3S, 'IV° Liv. Super' = 4S). No minimi increase applied between 1.7.2019 and 31.3.2023: the 2019 accord ran to 31.12.2019 in ultrattività, and the Protocollo straordinario of 12 December 2022 (CNEL 161824) granted una tantum amounts plus the 30-euro acconto from 1/4/2023 that Art. 185 lists as its first tranche.<br>35 of the 36 file values equal paga base 1.7.2019 + cumulated Art. 185 increments to the cent; 4S on 1/03/2027 is 1411.61 in the file against 1153.29 + 32.29 + 75.35 + 32.29 + 37.67 + 37.67 + 43.06 = 1411.62 and is corrected. The file's base_salary is the paga base nazionale (conglobata) only, with contingenza and terzo elemento as fixed allowances; this matches the item both tables print.<br>The file's coverage note calls the 2026-11-01 and 2027-03-01 tranches 'derived' by per-level ratios; they are printed increments in Art. 185 and the note can be updated.<br>The ruleset now names the CNEL deposit of the text signed by ANCC-Coop, Confcooperative Consumo e Utenza, AGCI Agrital, Filcams-CGIL, Fisascat-CISL and Uiltucs: source_type contracting_party.<br>Corrected to the printed table: 4S 2027-03-01: 1411.61 -> 1411.62. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro — middle managers with coordination and responsibility (L. 190/1985) | € 2,322.33 | 2027-03-01 |
| `1` | Livello 1 — senior specialists and team coordinators | € 2,112.86 | 2027-03-01 |
| `2` | Livello 2 — highly qualified workers, responsible for complex processes | € 1,839.64 | 2027-03-01 |
| `3S` | Livello 3S — senior skilled workers, multi-competency roles | € 1,639.29 | 2027-03-01 |
| `3` | Livello 3 — skilled workers, complex tasks requiring specific competencies | € 1,520.91 | 2027-03-01 |
| `4S` | Livello 4S — intermediate between 4 and 3, specialised operations | € 1,411.62 | 2027-03-01 |
| `4` | Livello 4 — qualified workers with autonomous task execution | € 1,311.43 | 2027-03-01 |
| `5` | Livello 5 — semi-skilled workers, routine operations with basic training | € 1,183.91 | 2027-03-01 |
| `6` | Livello 6 — entry-level workers, basic operations | € 910.71 | 2027-03-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 27.82 |
| `1` | € 26.64 |
| `2` | € 24.52 |
| `3S` | € 21.79 |
| `3` | € 21.79 |
| `4S` | € 19.93 |
| `4` | € 19.93 |
| `5` | € 18.84 |
| `6` | € 16.51 |

## Apprenticeship

**livelli_1_a_4** (type: `under_classification`)  
Destination levels: `1`, `2`, `3S`, `3`, `4S`, `4`  
under-level: `1`

**livello_5** (type: `under_classification`)  
Destination levels: `5`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "distribuzione-cooperativa-ancc/apprenticeship_2024_text_unread · base_salary · impact unknown · open"
    APPRENTICESHIP (2024 RENEWAL): Modelled from the 2020 CCNL text (CCNL-Utilia2020 PDF, 'Apprendistato accordo 13 giugno 2012'): levels 1-4 start 2 levels below for first 24 months then 1 level below; level 5 stays 1 level below throughout. The 2024 renewal (signed 2024-03-29) amended Arts. 75 and 80-82 but the updated text is not publicly accessible. Rules assumed unchanged from 2020 source.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Read the apprenticeship articles of the 2024 renewal (Arts. 75, 80-82) and update the tracks, then remove this limitation.

!!! warning "distribuzione-cooperativa-ancc/long_week_divisors · workplace_injury · impact unknown · open"
    HOURLY DIVISOR: 165 h/month used, per ilccnl.it (38h/week standard, all levels). Art. 198 of the CCNL also references 168 for 40h/week and higher divisors for extended shifts. Conflict: ilccnl.it states 165 as the contract divisor; Art. 198 lists 168 for 40h/week. Dominant workforce (post-2011 hires in a high-turnover retail sector on the 38h standard) is served by 165. 42h/week (182) and 45h/week (195) schedules not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Source Art. 198 and add the 168, 182 and 195 divisors of the 40, 42 and 45 hour weeks with hourly_divisor_weekly_hours=38, so other weeks are not derived from 165.

!!! warning "distribuzione-cooperativa-ancc/seniority_amounts_proxy_source · seniority · impact unknown · open"
    SENIORITY AMOUNTS: from kitech.it only (proxy source). No independent primary-source confirmation. Cadence (36 months) and maximum (10) confirmed from CCNL text via olympus.uniurb.it.

    **Applies when:** `seniority` applies.

    **Remediation:** Confirm the seniority amounts against a primary CCNL source.

!!! warning "distribuzione-cooperativa-ancc/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

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
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year, over 365 days (366 in a leap year), as INPS circ. 64/2001 par. 4 sets for a month worked full time. For a vertical part time the circular divides the pay of the month by its paid days, rest days included, which the request does not state: the engine applies the full-time measure, so the indemnity of a vertical or mixed part time may be misstated.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Take the paid days of the month before the leave of a vertical or mixed part time as a fact of the leave and divide its pay by them, then resolve this limitation.

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
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=H016 | tabella_retributiva | 2024-03-29 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=H016) |
| https://olympus.uniurb.it/index.php?option=com_content&view=article&id=31717:coop29324&catid=262&Itemid=139 | altro | 2024-03-29 | [↗](https://olympus.uniurb.it/index.php?option=com_content&view=article&id=31717:coop29324&catid=262&Itemid=139) |
| https://ilccnl.it/contratto/ccnl/cooperative-di-consumo | tabella_retributiva | 2024-03-29 | [↗](https://ilccnl.it/contratto/ccnl/cooperative-di-consumo) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = minimo tabellare only. fixed_allowances per level: (1) CONTINGENZA frozen since January 1993, level-specific constant; (2) TERZO_ELEMENTO 3.07 EUR all levels, constant; (3) INDENNITA_FUNZIONE 250.76 EUR, Q only, constant since 2008. Total monthly = base_salary + CONTINGENZA + TERZO_ELEMENTO (+ INDENNITA_FUNZIONE for Q). Verified against kitech.it Dec 2025 table: Q=2985.20 (expected 2985.23), L1=2533.93 (expected 2533.96), L4=1763.99 (expected 1764.02). 3-cent gap = TERZO_ELEMENTO rounding (3.07 filcams vs 3.10 kitech); filcams used.
    
    MODELLED TRANCHES: 2025-05-01 (third tranche, source-confirmed from filcams.cgil.it and kitech.it), 2025-12-01 (fourth tranche, confirmed), 2026-11-01 (fifth, derived), 2027-03-01 (sixth and final, derived). April 2023 and April 2024 tranches not modelled — pre-signing period. Derivation method: per-level ratios from confirmed Dec 2025 L4 increments (35 EUR/tranche); validated by independent check pre-2023 Q minimo = 1,897.32 EUR matching search snippet.
    
    ADDITIONAL MONTHS: 14 (tredicesima December + quattordicesima June). Source: CCNL text (olympus.uniurb.it summary, kitech.it).
    
    SENIORITY: triennial (cadence_months=36), maximum 10 scatti. Per-level amounts from kitech.it Dec 2025 (proxy, label SIMPLIFICATION). Q=27.82, L1=26.64, L2=24.52, L3S=21.79, L3=21.79, L4S=19.93, L4=19.93, L5=18.84, L6=16.51 EUR/scatto. L3S=L3 and L4S=L4 duplication confirmed plausible in Terziario family.
    
    INPS: uses 2026-terziario.json (terziario sector). No bilateral fund substituting INPS contributions. CNEL code: H016.
    
    MODELLED TRANCHES (Nov 2026 / Mar 2027): confirmed by studioagostini.org (secondary source, June 2024 commentary on the Mar 2024 renewal). L4 increments: +35.00 EUR (01/11/2026), +40.00 EUR (01/03/2027). L1 increments: +56.39 EUR (01/11/2026), +64.44 EUR (01/03/2027). All per-level values match the reparametrized ratio from confirmed prior tranches. Source: studioagostini.org/ccnl-distribuzione-cooperativa-aumenti-fino-a-240-euro/
    
    INDENNITA_FUNZIONE (Q): 250.76 EUR constant throughout 2023-2027 contract. Confirmed at Dec 2025 by kitech.it, unchanged since at least 2008. The 2024 renewal (IPSOA analysis, lavorofacile.it) modified Arts. 75 and 80-82 but did not alter the Q function allowance. Modelled with valid_from at the earliest salary period.
    
    UNA TANTUM: 350 EUR gross at L4 level (proportionally reparametrized per other levels), paid April 2024 and April 2025 to workers in service at 2024-03-29 signing date. One-off payment with no engine representation; deliberately excluded.
    
    PRE-SIGNING TRANCHES: April 2023 (retroactive) and April 2024 tranches not modelled. Coverage starts at 2025-05-01 (first source-confirmed post-signing tranche).
    

## Raw data

The contract file this page is generated from: [`agreement/distribuzione-cooperativa-ancc.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/distribuzione-cooperativa-ancc.json).

## Usage example

```python
--8<-- "docs/examples/agreement/distribuzione-cooperativa-ancc/example.py"
```
