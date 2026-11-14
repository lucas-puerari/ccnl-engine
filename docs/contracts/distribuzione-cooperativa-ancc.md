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
| **Limits of this contract** | seniority |

2 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 26 verified / 48 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-03-29 |
| **Last review** | 2026-11-14 |
| **Latest salary tranche** | 2027-03-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 190 - Mensilita' supplementari (13a e 14a) (p. 202): "il lavoratore avrà diritto a tanti dodicesimi dell'ammontare della 13a mensilità, per quanti sono i mesi interi di servizio prestati nella cooperativa intendendosi per tali le frazioni di mese superiori ai 15 giorni.". Match: more_than 15. |
| 2026-10-18 | claude-opus-5-5 (ai) | The paga base nazionale of the 9 levels on the four modelled tranches of the renewal of 29 March 2024 (1/05/2025, 1/12/2025, 1/11/2026, 1/03/2027), derived from the paga base printed by the economic renewal of 19 February 2019 plus the Art. 185 increments printed by the 2024 renewal; all texts as deposited at CNEL. | corrected | Ipotesi 29 marzo 2024 (CNEL 183889, 73-page scan read on the page image of PDF p. 70): Art. 185 prints only the per-level increments (01/04/2023, 01/04/2024, 01/05/2025, 01/12/2025, 01/11/2026, 01/03/2027; IV livello 30, 70, 30, 35, 35, 40 = 240), not the resulting minimi. The level labels (quadro, 1, 2, 3S, 3, 4S, 4, 5, 6) are the file codes; each row's increments sum to the printed TOTALE (within one or two cents of rounding, e.g. quadro 425,01 against 425,00).<br>The base is the 'Paga Base Nazionale dal 01.07.2019' table of the economic renewal of 19 February 2019 (CNEL 100291, p. 3; 'III° Liv.Super' = 3S, 'IV° Liv. Super' = 4S). No minimi increase applied between 1.7.2019 and 31.3.2023: the 2019 accord ran to 31.12.2019 in ultrattività, and the Protocollo straordinario of 12 December 2022 (CNEL 161824) granted una tantum amounts plus the 30-euro acconto from 1/4/2023 that Art. 185 lists as its first tranche.<br>35 of the 36 file values equal paga base 1.7.2019 + cumulated Art. 185 increments to the cent; 4S on 1/03/2027 is 1411.61 in the file against 1153.29 + 32.29 + 75.35 + 32.29 + 37.67 + 37.67 + 43.06 = 1411.62 and is corrected. The file's base_salary is the paga base nazionale (conglobata) only, with contingenza and terzo elemento as fixed allowances; this matches the item both tables print.<br>The file's coverage note calls the 2026-11-01 and 2027-03-01 tranches 'derived' by per-level ratios; they are printed increments in Art. 185 and the note can be updated.<br>The ruleset now names the CNEL deposit of the text signed by ANCC-Coop, Confcooperative Consumo e Utenza, AGCI Agrital, Filcams-CGIL, Fisascat-CISL and Uiltucs: source_type contracting_party.<br>Corrected to the printed table: 4S 2027-03-01: 1411.61 -> 1411.62. |
| 2026-11-05 | claude-opus-5-5 (ai) | The hourly divisors of art. 187 (PDF p. 201) and the normal week of art. 113 (PDF pp. 151-152) of the 2011 official text, read by a separate research session and checked again on the text layer. | corrected | Art. 187 c. 2: 165 for 38 hours, 167 for 38.5, 168 for 40 and 39, 182 for 42, 184 from 42.5 to 44: work_rules.time_supplements.week_divisors, hourly_divisor_weekly_hours 38.<br>The coverage note cited art. 198 and a 195 divisor for 45 hours: art. 198 is the resignation for marriage and art. 187 sets no 45-hour divisor. |
| 2026-11-07 | claude-opus-5-5 (ai) | The monthly values of the levels against the primary tables (text layer). | confirmed | 10 values found verbatim on the cited pages and marked verified; 36 left as they were (derived or not on a text page). |
| 2026-11-07 | gpt-6-sol (ai) | Terzo elemento against art. 186 of the signed text and the later renewals. | corrected | The file paid 3.07 from a secondary table; art. 186 c. 4 prints 3,10 and no later renewal amends it (research .private/research/work/r-distr-coop). Corrected on all levels. |
| 2026-11-08 | claude-opus-5-5 (ai) | The monthly values of the levels against the primary tables (text layer). | confirmed | 19 values found verbatim on the cited pages and marked verified; 36 left as they were (derived or not on a text page). |
| 2026-11-08 | claude-opus-5-5 (ai) | Art. 187 c. 2 of the 2011 official text (PDF p. 201, text layer). | corrected | The divisors of the half-hour weeks (167 for 38.5, 184 from 42.5) are now expressible: added 38.5, 42.5 and 43.5 to time_supplements.week_divisors. |
| 2026-11-13 | claude-opus-5-5 (ai) | Art. 75 of the signed ipotesi di accordo of 29 March 2024 deposited at the CNEL (accordo 183889, PDF p. 43, OCR of the page image). | confirmed | The 2024 renewal keeps two levels below for the first 24 months and one below after for destinations 4 to 1, one below throughout for level 5: the encoded tracks hold; limitation apprenticeship_2024_text_unread removed. |
| 2026-11-14 | claude-opus-5-5 (ai) | Art. 182 of the testo ufficiale 2011 (seniority), against the renewals 2019 and 2024. | confirmed | Read Art. 182 in the text PDF (pp. 195-196): the seven amounts of the file match the table; the service counts from the 21st year of age, which the file did not apply. Upgraded the provenance from the aggregator to the signed text, added counted_from_age 21, and narrowed the proxy limitation to the 3S and 4S amounts, which the table does not print. |
| 2026-11-14 | claude-opus-5-5 (ai) | Artt. 61 C, 113, 115 and Allegato 13 of the testo ufficiale 2011; Art. 147 of the renewal of 29 March 2024. | corrected | The file had the ferie but no permit. Added the 104-hour pool with the 38-hour absorption that leaves 24 hours, the ramp of the hires after 22 December 2011 and the fixed 30 June deadline; recorded the imprese minori hours of Art. 147 (2024) as a limitation, the file having no input for them. |
| 2026-11-14 | claude-opus-5-5 (ai) | Art. 147 of the renewal of 29 March 2024 (imprese minori). | corrected | Added the hours of the small imprese minori (60, +6 from April 2025, +6 from April 2026) under the sub-sector piccola_impresa_minore and closed imprese_minori_permits; the other imprese minori work 40 hours and keep the 104. Recorded that the Art. 61 C ramp still applies to their new hires. |
| 2026-11-14 | claude-opus-5-5 (ai) | Art. 147 of the renewal of 29 March 2024 against the ramp of Art. 61 C. | corrected | The 60 hours of the small imprese minori are 'per tutti i lavoratori dipendenti': the ramp now excludes the sub-sector piccola_impresa_minore; closed small_cooperative_new_hire_ramp. |
| 2026-11-14 | claude-opus-5-5 (ai) | Ferie at termination and Art. 187 of the testo ufficiale 2011. | corrected | The file had no basis for the leave left at termination: added the twelfths (more than 15 days a month), the 1/26 indemnity and the hourly quota of the permits. |
| 2026-11-14 | claude-opus-5-5 (ai) | Art. 132 c. 2-3 - Lavoro festivo (holiday on a Sunday). | corrected | The file had no clause for a holiday falling on a Sunday, so its further daily quota was not paid: added the clause with the holidays the text lists and 4 November. |
| 2026-11-14 | claude-opus-5-5 (ai) | Artt. 121, 126, 128, 129 and 132 of the testo ufficiale 2011. | corrected | The overtime bands came from an aggregator (15/30/30/50%, premiums on the minimo): set the rates of Art. 126 (20/25/35/55%, highest when concurring) on the de facto hourly quota, the 48th-hour threshold, and the ordinary night, rest-day and holiday premiums. |
| 2026-11-14 | claude-opus-5-5 (ai) | Art. 16 of the renewal of 29 March 2024; Art. 58 and the pension fund clause of the testo ufficiale 2011. | corrected | The file had no fund: added Coopersalute (14 EUR a month from 2025), the quadri health cover (1,000 + 100 EUR a year) and Previcooper (1,55% employer, 0,55% worker minimum on the TFR base). |

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

!!! warning "distribuzione-cooperativa-ancc/seniority_super_levels · seniority · impact unknown · open"
    SENIORITY OF LEVELS 3S AND 4S: the Art. 182 table has rows III and IV only, while the minimum table of the 2024 renewal (art. 185, p. 70) prints 3S and 4S apart; the file pays 3S the III amount (21,79) and 4S the IV amount (19,93), a reading the text does not state.

    **Applies when:** `seniority` applies; level in 3S, 4S.

    **Remediation:** Source the seniority amount of levels 3S and 4S (signed table or interpretation of the parties).

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

!!! warning "tfr_compensation_apprentice_guarantee_fund · inps_employer · impact yes · open"
    An apprentice whose TFR goes to a pension fund or to the Fondo Tesoreria takes the 0.28-point relief of D.L. 203/2005 art. 8, but not the exemption from the 0.20% Fondo di garanzia contribution of D.Lgs. 252/2005 art. 10 c. 2: no source found says whether the apprentice rate (10% of L. 296/2006 art. 1 c. 773 plus NASpI and the integration funds) holds a Fondo di garanzia share to exempt. The employer contributions of the run may be overstated by 0.20% of the INPS base.

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Find an INPS source on the Fondo di garanzia share of the apprentice rate, then exempt it with the other workers or record that none is due.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=H016 | tabella_retributiva | 2024-03-29 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=H016) |
| https://olympus.uniurb.it/index.php?option=com_content&view=article&id=31717:coop29324&catid=262&Itemid=139 | altro | 2024-03-29 | [↗](https://olympus.uniurb.it/index.php?option=com_content&view=article&id=31717:coop29324&catid=262&Itemid=139) |
| https://ilccnl.it/contratto/ccnl/cooperative-di-consumo | tabella_retributiva | 2024-03-29 | [↗](https://ilccnl.it/contratto/ccnl/cooperative-di-consumo) |
| Ipotesi di accordo di rinnovo del CCNL per i dipendenti da imprese della distribuzione cooperativa, Roma 29 marzo 2024 (deposito CNEL, accordo 183889, scansione firmata) | cnel | 2024-03-29 | [↗](https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/183889) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = minimo tabellare only. fixed_allowances per level: (1) CONTINGENZA frozen since January 1993, level-specific constant; (2) TERZO_ELEMENTO 3.07 EUR all levels, constant; (3) INDENNITA_FUNZIONE 250.76 EUR, Q only, constant since 2008. Total monthly = base_salary + CONTINGENZA + TERZO_ELEMENTO (+ INDENNITA_FUNZIONE for Q). Verified against kitech.it Dec 2025 table: Q=2985.20 (expected 2985.23), L1=2533.93 (expected 2533.96), L4=1763.99 (expected 1764.02). 3-cent gap = TERZO_ELEMENTO rounding (3.07 filcams vs 3.10 kitech); filcams used.
    
    MODELLED TRANCHES: 2025-05-01 (third tranche, source-confirmed from filcams.cgil.it and kitech.it), 2025-12-01 (fourth tranche, confirmed), 2026-11-01 (fifth, derived), 2027-03-01 (sixth and final, derived). April 2023 and April 2024 tranches not modelled — pre-signing period. Derivation method: per-level ratios from confirmed Dec 2025 L4 increments (35 EUR/tranche); validated by independent check pre-2023 Q minimo = 1,897.32 EUR matching search snippet.
    
    ADDITIONAL MONTHS: 14 (tredicesima December + quattordicesima June). Source: CCNL text (olympus.uniurb.it summary, kitech.it).
    
    SENIORITY (Art. 182 of the testo ufficiale 2011, PDF pp. 195-196): ten triennial scatti of the service 'a decorrere dal 21° anno di età' (counted_from_age 21, from SeniorityFact.birth_date; without it the service counts from the start; c. 2 is the transition of 1 July 1975, kept as the first hire the rule covers), fixed amounts 'Dal 1° aprile 1987': Q 27,82, I 26,64, II 24,52, III 21,79, IV 19,93, V 18,84, VI 16,51, paid from the month after the triennium (c. 5). The economic renewal 2019 (CNEL 100291) replaces only art. 185 and the 2024 renewal (CNEL 183889) does not amend art. 182.
    
    INPS: uses 2026-terziario.json (terziario sector). No bilateral fund substituting INPS contributions. CNEL code: H016.
    
    APPRENTICESHIP (2024 RENEWAL): art. 75 of the signed ipotesi of 29 March 2024 (CNEL 183889, p. 43, scanned page read by OCR) keeps the under-classification of the 2020 text: 'di due livelli inferiori [...] per i primi 24 mesi dal 4° livello al 1° livello e di un livello inferiore [...] per la restante durata dello stesso'; 'di un livello inferiore [...] per l'intera durata del percorso di apprendistato per il 5° livello'. Tracks livelli_1_a_4 (1, 2, 3S, 3, 4S, 4) and livello_5 unchanged.
    
    HOURLY DIVISOR: Art. 187 c. 2 (2011 official text, p. 201): 165 for the normal week of 38 hours (art. 113 c. 1), 167 for 38.5, 168 for 39 and 40, 182 for 42, 184 from 42.5 to 44. The engine keeps 165 and reads the others from Employment.full_time_weekly_hours (38.5, 39, 40, 42, 42.5, 43, 43.5, 44); for the life of that contract, the staff hired after its signature work 40 hours (art. 113 c. 5) and state it. The cooperative minori of title XV keep their own 40-hour week and divisor (art. 187 c. 3, art. 147): not told apart.
    
    MODELLED TRANCHES (Nov 2026 / Mar 2027): confirmed by studioagostini.org (secondary source, June 2024 commentary on the Mar 2024 renewal). L4 increments: +35.00 EUR (01/11/2026), +40.00 EUR (01/03/2027). L1 increments: +56.39 EUR (01/11/2026), +64.44 EUR (01/03/2027). All per-level values match the reparametrized ratio from confirmed prior tranches. Source: studioagostini.org/ccnl-distribuzione-cooperativa-aumenti-fino-a-240-euro/
    
    INDENNITA_FUNZIONE (Q): 250.76 EUR constant throughout 2023-2027 contract. Confirmed at Dec 2025 by kitech.it, unchanged since at least 2008. The 2024 renewal (IPSOA analysis, lavorofacile.it) modified Arts. 75 and 80-82 but did not alter the Q function allowance. Modelled with valid_from at the earliest salary period.
    
    UNA TANTUM: 350 EUR gross at L4 level (proportionally reparametrized per other levels), paid April 2024 and April 2025 to workers in service at 2024-03-29 signing date. One-off payment with no engine representation; deliberately excluded.
    
    PRE-SIGNING TRANCHES: April 2023 (retroactive) and April 2024 tranches not modelled. Coverage starts at 2025-05-01 (first source-confirmed post-signing tranche).
    
    TERZO ELEMENTO (art. 186 c. 4): 3,10 EUR a month in provinces without collective surpluses, as the signed text prints; the renewal of 29 March 2024 does not amend art. 186. A Filcams pay table 2025-2027 prints 3,07: a summary table, not a signed text, so the signed amount is used. Where collective surpluses are in force, the frozen provincial amounts apply instead (not modelled: they depend on local bargaining).
    
    PERMITS, LARGE COOPERATIVES (Allegato 13, Art. 113, Art. 115, Art. 61 C of the testo ufficiale 2011, signed 22 December 2011): a pool of 104 hours a year, 32 for the abolished holidays and 72 of reduction; the 38-hour week of Art. 113 c. 1 absorbs 96 of them and leaves 24 (8 plus 16 not absorbable, Art. 115 c. 1), the 40-hour week of the hires after the signing (Art. 113 c. 5) absorbs none (EmployerProfile/Employment full_time_weekly_hours); the hires after 22 December 2011 take the 72 hours at 50% after two years and 100% after four (Art. 61 C); a twelfth per whole month of service; not taken by 30 June of the next year, paid with the pay of that date, with no choice of the employer (Art. 115 c. 4). The 2019 and 2024 renewals do not amend these articles.
    
    PERMITS, IMPRESE MINORI (Title XV, Art. 147 as renewed on 29 March 2024, CNEL 183889 pp. 59-60): a 40-hour week for every worker (Employment full_time_weekly_hours 40: the 104 hours, not absorbed); in the small firms of one unit or up to 20 full-time staff a unit (EmployerProfile.subsector 'piccola_impresa_minore') 60 hours a year, read as the 32 of ex festività and 28 of reduction, plus 6 from 1 April 2025 and 6 from 1 April 2026 (72, aim 88). Their new hires take the hours in full: the ROL ramp of Art. 61 C does not reach this sub-sector.
    
    LEAVE AT TERMINATION (testo ufficiale 2011, p. 166 and Art. 187): ferie in twelfths, a fraction above fifteen days counting as a month, the indemnity 'dividendo per ventisei la retribuzione mensile di fatto'; the permit hours left at the hourly quota of Art. 187 (168 at 40 hours, 165 at 38).
    
    HOLIDAY ON A SUNDAY (Art. 132 c. 2-3 - Lavoro festivo, p. 164 (printed 162-163)): a listed holiday falling on a Sunday pays a further daily quota (1/26 of the monthly pay); 4 November, celebrated on the first Sunday of November, takes the same treatment.
    
    OVERTIME AND ORDINARY PREMIUMS (testo ufficiale 2011): overtime at the hourly quota of the retribuzione di fatto with 20% up to the 48th weekly hour, 25% beyond, 35% on holidays, 55% at night, the highest when several concur (Art. 126); ordinary night work 25% (Art. 121); work on the weekly rest day the premium of 35% alone (Art. 129); work on a holiday paid as holiday overtime (Art. 132 c. 1); ordinary Sunday work in an authorised opening takes no premium (Art. 128 c. 3). The bands previously came from an aggregator at 15/30/30/50%.
    
    FUNDS: Coopersalute (renewal 2024, art. 16): 14 EUR a month paid by the employer from January 2025 for the permanent workers, full or part time, and the apprentices, quadri excluded, with the 10% INPS solidarity contribution (the 30 EUR one-off enrolment fee is not modelled as a monthly charge); quadri (art. 58): 1,000 EUR a year by the employer and 100 EUR by the quadro; Previcooper: employer 1,55% and worker at least 0,55% of the TFR base for the enrolled worker (Employment.pension_fund). The employer names the health funds it pays (EmployerProfile.contractual_funds); none has an element in its place (Coopersalute is compulsory).
    

## Raw data

The contract file this page is generated from: [`agreement/distribuzione-cooperativa-ancc.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/distribuzione-cooperativa-ancc.json).

## Usage example

```python
--8<-- "docs/examples/agreement/distribuzione-cooperativa-ancc/example.py"
```
