# CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (non conviventi)

| | |
|---|---|
| **CNEL code** | `H501` |
| **Sector** | lavoro domestico |
| **Family** | `lavoro-domestico` |
| **Tax sector** | `lavoro-domestico` |
| **Last renewal** | 2025-10-28 |
| **Workers (est.)** | ~900k |
| **Ruleset version** | `2026.3` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - DOMINA — Associazione Nazionale Famiglie Datori di Lavoro Domestico
    - FIDALDO — Federazione Italiana Datori di Lavoro Domestico
    - ASSINDATCOLF — Associazione Nazionale dei Datori di Lavoro Domestico
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL
    - FEDERCOLF

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | assistance_contribution, base_salary, inps_employer, seniority |

8 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 17 verified / 0 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-10-28 |
| **Last review** | 2026-10-15 |
| **Latest salary tranche** | 2026-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-12 | claude-opus-5-5 (ai) | Every payable rule of the file: minimums, hourly divisor, additional months, seniority, Cas.Sa.Colf, overtime, absences, leave and the accrual of the tredicesima, read in the signed text of 28 October 2025 and its 2026 table (p. 59); the sickness rule of Art. 27 stays derived (readings in its transformation). | corrected | Overtime: the file held 10% and 20%; Art. 15 c. 3 sets 25% by day, 50% by night and 60% on a holiday or Sunday. The 20% of Art. 14 c. 6 is the supplement of ordinary night work, not of overtime.<br>accrual_rule was missing: chiarimento a verbale 4 counts a fraction of a month of at least 15 calendar days as a whole month.<br>Citations moved from the DOMINA table and section labels without page to the signed text with page and quote.<br>Overtime of non conviventi: hours 41 to 44 by day at 10% (Art. 15 c. 4), beyond the 44th at 25% (hour_threshold_per_week 4). |
| 2026-10-14 | claude-opus-5-5 (ai) | P1 audit: Tabella C of the 2026 minimi (values from 1 January 2026) for the eight levels; the annual update of the minimi. | corrected | The eight hourly minimi of Tabella C (6,51 to 9,97) times 40 x 52 / 12 are the monthly amounts of the bundle.<br>The minimi are reset every 1 January (Art. 38): from 2027 the 2026 table would be paid as final. Declared as annual_minimi_not_updated on the three domestic CCNLs, review_due 2027-01-31. |
| 2026-10-15 | claude-opus-5-5 (ai) | Registry check: CNEL code, name, signatories and term against the 21st CNEL report of CCNLs in force (30 June 2025) and the term clause of the text read in the P1 review. | confirmed | CNEL H501 matches (FIDALDO, which groups ASSINDATCOLF, and DOMINA with FILCAMS, FISASCAT, UILTUCS, FEDERCOLF).<br>Term: the ipotesi of 28 October 2025 applies from 1 November 2025; its expiry is reported as 31 October 2028 (CNEL filing) or 31 December 2028 (press); not read in the text, left open. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'confrontare lordo, netto e costo azienda con esempi indipendenti': a run of the engine against the worked examples of a third-party guide (money.it, Costo colf e badanti 2026). | confirmed | Level CS, 2026: the hourly minimum 8,30 matches. 20 hours a week (effective hourly pay up to 9,61): 0,43 euro an hour of the worker and 1,27 of the employer; 30 hours a week (over 24 hours): 0,31 and 0,93. The engine applies the same bands. Match.<br>Deviation: the monthly pay of 20 hours is 719.34, half the rounded full-time 1438.67, against 8,30 x 20 x 52 / 12 = 719.33: one cent of rounding; decision: accepted and noted. The guide is a third-party page (hash of the copy read on 15 October 2026); Cas.Sa.Colf, tredicesima and TFR are not quantified there. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'ferie, permessi, festività, assenze, malattia e comporto': the sickness rule against the signed text of 28 October 2025. | confirmed | Art. 27 (p. 37): the three seniority bands, the 365-day count and the 50% / 100% pay match the file: verified. The +50% for oncological illness (c. 6) is declared. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `DS` | Level DS — senior caregiver / household manager with seniority | € 1,728.13 | 2026-01-01 |
| `D` | Level D — senior caregiver / household manager | € 1,658.80 | 2026-01-01 |
| `CS` | Level CS — specialised domestic worker with seniority | € 1,438.67 | 2026-01-01 |
| `C` | Level C — specialised domestic worker / assistant caregiver (badante) | € 1,362.40 | 2026-01-01 |
| `BS` | Level BS — qualified domestic worker with seniority | € 1,291.33 | 2026-01-01 |
| `B` | Level B — qualified domestic worker (colf qualificata) | € 1,215.07 | 2026-01-01 |
| `AS` | Level AS — domestic worker with seniority qualification | € 1,171.73 | 2026-01-01 |
| `A` | Level A — entry-level domestic worker (colf generica) | € 1,128.40 | 2026-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 7 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 45.14 |
| `AS` | € 46.87 |
| `B` | € 48.60 |
| `BS` | € 51.65 |
| `C` | € 54.50 |
| `CS` | € 57.55 |
| `D` | € 66.35 |
| `DS` | € 69.13 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "lavoro-domestico-non-convivente/tranches_from_2027 · base_salary · impact yes · open"
    SINGLE PERIOD 2026-01-01. Pre-2026 tranches out of scope. Post-2026 CCNL 2025-2028 tranches not yet modelled: +30 on BS from Jan 2027, +15 from Jan 2028, +15 from Sep 2028 (other levels proportional — exact amounts require official ASSINDATCOLF/DOMINA table for those periods).

    **Applies when:** `base_salary` applies; from 2027-01-01.

    **Remediation:** Add the 2027 and 2028 tranches from the official ASSINDATCOLF/DOMINA tables.

!!! warning "lavoro-domestico-non-convivente/seniority_frozen_at_2026 · seniority · impact unknown · open"
    Seniority amounts frozen at 2026 base. Future ISTAT adjustments will raise base_salary but amount_by_level will need manual update.

    **Applies when:** `seniority` applies; from 2027-01-01.

    **Remediation:** Update the seniority amounts with each ISTAT adjustment of the minimum tables.

!!! warning "lavoro-domestico-non-convivente/meal_indennity · base_salary · impact unknown · open"
    A non-convivente on 6 or more hours a day with continuous presence is owed the meal or, when it is not given, an indennita equal to its valore convenzionale (Art. 14 c. 8; Tabella F 2026: 2,33 per meal). The request carries no fact on daily hours, presence or meals given, so the engine pays none.

    **Applies when:** `base_salary` applies; run kind in regular, termination.

    **Remediation:** Add a fact for the days owed a meal not given and pay the Tabella F value for them.

!!! warning "lavoro-domestico-non-convivente/extra_month_hours · assistance_contribution · impact unknown · open"
    The INPS contributions of the tredicesima are paid on the hours of the year: INPS bands them on the paga oraria effettiva, which spreads the tredicesima over the hours, so the tredicesima run charges no INPS hours. The Cas.Sa.Colf contribution of Art. 54 c. 2 is charged on the contributable hours the run states, a tredicesima run too: no bundled source says whether the tredicesima carries hours of its own for it.

    **Applies when:** `assistance_contribution` applies; run kind in thirteenth.

    **Remediation:** Source from the Cas.Sa.Colf rules whether the tredicesima carries contributable hours and set them for extra-month runs.

!!! note "lavoro-domestico-non-convivente/oncological_comporto · sickness · impact unknown · resolved"
    Art. 27 c. 6: the comporto is 50% longer for an oncological illness certified by the ASL. The episode can state a serious illness (SicknessEpisode.serious_illness), but the domestic sickness rules have no serious-illness rule, so the engine keeps the ordinary comporto (review of 2026-10-30).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Resolved: the bands carry the comporto of an oncological illness (serious_comporto_days 15, 68 and 270 days, the periods of c. 4 raised by 50%), applied when the episode states SicknessEpisode.serious_illness; 45 x 1.5 = 67.5 is read as 68, the 68th day being still in part within the period.

!!! warning "lavoro-domestico-non-convivente/hourly_inps_bracket_unvalidated · inps_employer · impact unknown · open"
    INPS BAND: the band of up to 24 weekly hours is chosen on the paga oraria effettiva of INPS (circ. 9/2026; INPS page Contributi e agevolazioni fiscali per chi assume un lavoratore domestico): the monthly pay with board and lodging over the hours of the employment (weekly hours x 52 / 12), raised by the tredicesima (x 13 / 12).

    **Applies when:** `inps_employer` applies.

    **Remediation:** Validate the hourly INPS bracket lookup for weekly hours up to 24 against the INPS domestic table, as for the convivente files.

!!! warning "lavoro-domestico-non-convivente/annual_minimi_not_updated · base_salary · impact yes · open"
    ANNUAL MINIMI: the minimi of the CCNL are updated every year from 1 January by the Commissione nazionale (Art. 38, ISTAT variation of the consumer prices); the bundle holds the table of 2026. From 1 January 2027 the amounts are those of 2026 until the 2027 table is published and added, so a 2027 run is not payable.

    **Applies when:** `base_salary` applies; from 2027-01-01.

    **Remediation:** Add the minimi of 2027 set by the Commissione nazionale with their source, then remove this note.

!!! note "lavoro-domestico-non-convivente/domestic_oncological_comporto · sickness · impact yes · resolved"
    ONCOLOGICAL ILLNESS: the periods of Art. 27 c. 4 rise by 50% for an oncological illness documented by the ASL (c. 6, p. 37); the file applies the ordinary periods and the request does not state the illness.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Resolved as a duplicate of lavoro-domestico-non-convivente/oncological_comporto, resolved in turn: both track the 50% longer comporto of Art. 27 c. 6 for an oncological illness.

!!! note "sickness_inps_daily_base · sickness · impact unknown · resolved"
    The INPS share of a sick day is computed on the INPS daily base of the episode, on the days INPS pays (the weekdays of an operaio, every day but the national holidays on a Sunday of an impiegato, point 7.3 of INPS circ. 134368/1981): the retribuzione media globale giornaliera of the month before the illness (INPS circ. 134368/1981 point 11; circ. 55/2024 Allegato 1), whole or partial month, impiegato or operaio, or for the lavoratori dello spettacolo the average pay of the last 40 daily contributions, capped for a fixed-term worker (INPS circ. 132/2021 par. 2.4). The base is a fact of the payroll history the episode states (SicknessEpisode.inps_base).

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Resolved: the INPS share is computed on the base of every regime of the bundle; an episode that states no base the engine can read has the missing_fact issue sickness_inps_base_unknown (fact inps_base), which blocks the run. Tests: tests/integration/ccnl_engine/sickness/base/test_rules.py, tests/unit/ccnl_engine/sickness/base/test_rules.py.

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax ruleset marked provisional: the sources of its year are not published yet (budget law of the year; regional and municipal surtax resolutions), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

!!! warning "provisional_inps_ruleset · inps_employer · impact unknown · open"
    The run reads an INPS ruleset marked provisional: the INPS circulars of its year are not published yet, so the rates, the massimale and the minimale (and the hourly contributions of domestic work) are those of the year before, carried over. The indexed amounts change every January: the carried-over values understate them.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional INPS ruleset of the year with the values of the INPS circulars of the year, drop its provisional flag, then resolve this limitation.

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
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year over 365: art. 42 c. 5-ter D.Lgs. 151/2001 and INPS messaggio 30/2024 set the pay and its rateo of the extra months, and the INPS table of the yearly maximum divides it by 365 (2026: 43,486.00 / 365 = 119.14), but no source read states the divisor of the worker's own pay.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily divisor INPS applies to the last pay (circ. INPS 64/2001 or 32/2012) and apply it, then resolve this limitation.

!!! warning "naspi_dismissal_exceptions · naspi_dismissal · impact unknown · open"
    The NASpI contribution of the end of an employment is read from the cause, the just cause and the contract type alone. The request states none of the cases that change it: a resignation in the protected period of maternity and a mutual agreement before the labour office or on a transfer over 50 km owe it (INPS circ. 44/2013 par. 1); a collective dismissal without union agreement owes it three times (L. 92/2012 art. 2 c. 35); the changes of contractor with a social clause and the closures of a construction site of c. 34, and the reductions agreed under artt. 4 and 24 L. 223/1991, leave it out; the service counts the fixed-term periods before the open-ended contract and leaves out the leave of art. 42 c. 5 D.Lgs. 151/2001 only through EmploymentPeriod.started_on.

    **Applies when:** `naspi_dismissal` applies; the run takes the engine code path.

    **Remediation:** Add the facts of these cases to the end of the employment (EmploymentPeriod) and apply them, then resolve this limitation.

!!! warning "personal_withholding_same_kind · personal_withholdings · impact unknown · open"
    Two garnishments of the same kind, or two salary assignments, share the measure of their kind (a fifth, or the tenth or seventh of the agente della riscossione) in the order of notification: art. 545 c. 4 c.p.c. sets 'un quinto per i tributi ... ed in eguale misura per ogni altro credito' and art. 5 DPR 180/1950 a cessione 'fino al quinto', but no text read says how two orders of the same kind split the measure, so the later order may be under- or overstated.

    **Applies when:** `personal_withholdings` applies; the run takes the engine code path.

    **Remediation:** Source how the employer splits the measure between two orders of the same kind (art. 499 c.p.c. on the intervention of creditors, case law of the Cassazione) and apply it, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://associazionedomina.it/wp-content/uploads/2026/02/TABELLA-minimi-retributivi-2026.pdf | tabella_retributiva | 2026-01-01 | [↗](https://associazionedomina.it/wp-content/uploads/2026/02/TABELLA-minimi-retributivi-2026.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobated retribuzione globale (TABELLA C - Lavoratori Non Conviventi, Art. 14 c. 1 lett. b CCNL 28/10/2025). Hourly rates from the official Domina salary table PDF (TABELLA-minimi-retributivi-2026.pdf, effective 01/01/2026). Monthly base_salary = hourly rate x 40 x 52 / 12 (chiarimento a verbale 1). Source is signatory employer association - primary source.
    
    TAX SECTOR: lavoro-domestico (TaxSector.LAVORO_DOMESTICO). Flat per-hour INPS contributions from INPS Circ. 9/2026. A household employer is not a withholding agent: it is not among the sostituti d'imposta of art. 23 c. 1 D.P.R. 600/1973 (art. 33 c. 1 D.Lgs. 33/2025 from 2027), so the engine withholds no IRPEF or surtax and pays no trattamento integrativo, ulteriore detrazione or somma esente.
    
    HOURLY DIVISOR: 173.33 = 40 x 52 / 12 to the cent: 40 h/week contractual maximum for non conviventi (Art. 14 c. 1 lett. b CCNL 28/10/2025) and chiarimento a verbale 1. Convivente and non-convivente are independent pay scales (different tables, different hourly divisors).
    
    BASE SALARY: computed as hourly_rate x 40 x 52 / 12, rounded to the cent. Dividing it by the hourly divisor 173.33 recovers the Tabella C hourly rate to the cent.
    
    ADDITIONAL MONTHS: 13 (tredicesima mensilita, Art. 39 CCNL 28/10/2025). No quattordicesima.
    
    SENIORITY: biennale (24 months), maximum 7 scatti (Art. 37). Per-level amounts = 4% x the monthly minimum (hourly x 40 x 52 / 12). Amounts frozen at 2026 values - future ISTAT tranches require manual update.
    
    APPRENTICESHIP: none. Domestic workers excluded from D.lgs. 81/2015 Art. 47 apprenticeship.
    
    D/DS function allowance: not applicable for non-convivente (TABELLA C shows only hourly rates, no separate indennità column). D/DS hourly rates already reflect the seniority grade.
    
    CNEL code H501 confirmed: lavoro-economia.it explicitly lists 'CCNL Lavoro Domestico (Colf e Badanti) [Cnel: H501]'. Also confirmed via kitech.it. CNEL archive verification not attempted (had returned 404 previously).
    
    Livello Unico (hourly 5.83) is a special sub-under-18 level excluded from this model.
    
    CAS.SA.COLF: contributi di assistenza contrattuale of Art. 54 c. 2, 0,06 EUR per paid hour, 0,02 withheld from the worker and 0,04 paid by the employer, charged on the contributable hours of the run.
    
    SICKNESS (Art. 27): INPS pays no indemnity to domestic workers; the employer pays 50% of the retribuzione globale di fatto up to the third day and 100% from the fourth, for at most 8, 10 or 15 days in the 365 days that end on the sick day, within a comporto of 10, 45 or 180 days, for up to 6 months of seniority, up to 2 years and over 2 years. A sick day is a thirtieth of the monthly pay (chiarimento a verbale 2).
    
    NIGHT WORK (Art. 14 c. 6): ordinary work between 22.00 and 6.00 is paid with a 20% supplement of the hourly retribuzione globale di fatto; the engine takes its amount as a NightShiftEvent stated by the caller. The overtime bands are those of Art. 15 c. 3 (25% by day, 50% by night, 60% on a holiday or Sunday); night overtime on a holiday has no band of its own and a run that states it is rejected.
    

## Raw data

The contract file this page is generated from: [`agreement/lavoro-domestico-non-convivente.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/lavoro-domestico-non-convivente.json).

## Usage example

```python
--8<-- "docs/examples/agreement/lavoro-domestico-non-convivente/example.py"
```
