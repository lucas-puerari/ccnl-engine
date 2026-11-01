# CCNL Area Tessile-Moda e Chimica-Ceramica — Artigianato

| | |
|---|---|
| **CNEL code** | `V751` |
| **Sector** | tessile moda chimica ceramica artigianato |
| **Family** | `tessile-moda` |
| **Tax sector** | `artigianato` |
| **Last renewal** | 2024-07-16 |
| **Workers (est.)** | ~120k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CNA Federmoda
    - CNA Produzione
    - CNA Artistico e Tradizionale
    - CNA Servizi alla Comunità
    - Confartigianato Moda
    - Confartigianato Chimica
    - Confartigianato Ceramica
    - Casartigiani
    - CLAAI
    - Filctem CGIL
    - Femca CISL
    - Uiltec UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, inps_employer, seniority |

5 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 25 verified / 11 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-07-16 |
| **Last review** | 2026-10-31 |
| **Latest salary tranche** | 2026-10-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | base_salary of levels 1-6 and 6S, all four tranches (2024-07-01, 2025-01-01, 2025-10-01, 2026-10-01), against the Settore tessile abbigliamento table of the Verbale integrativo of 22 July 2024 published by Filctem CGIL (signatory). | corrected | Levels 1-6: all 24 periods match the 'Nuovi minimi contrattuali' table of the Settore tessile abbigliamento (Verbale integrativo 22 July 2024, p. 2, scanned PDF read by OCR and visual check) except level 5 from 2026-10-01: the table prints 1.813,56 (1.751,06 + the printed increment 62,50), the file had 1813.50.<br>Level 6S: the file stores the printed 6s minimo plus the quadri indennità di funzione of EUR 20,66 (art. 119 CCNL 14 Dec 2017; 6° super = quadri per art. 29). All four periods equal printed minimo + 20.66 and are recorded as derived on the CCNL text; the indennità is not repeated in the 2024 renewal and is assumed unchanged.<br>The minimi are conglobated tabellare amounts (single 'Retribuzione tabellare' column, no separate contingenza or EDR), consistent with the file's conglobated model.<br>The file models only the Settore tessile abbigliamento table. The same verbale prints distinct tables for calzaturiero (from 2026-10-01 and for level 6/6s already from 2024), lavorazioni a mano e su misura, pulitintolavanderie, occhialeria, chimica-concia-gomma-plastica-vetro and ceramica; those are not modelled.<br>Corrected to the printed table: 5 2026-10-01: 1813.50 -> 1813.56. |
| 2026-10-31 | claude-opus-5-5 (ai) | The sick pay and the comporto of the CCNL (work_rules.sickness_rules), read on the signed text. | corrected | Art. 109 (pp. 126-127), operai Tessile, Abbigliamento, Calzaturiero: 80% for days 1-7, the first 3 not paid for an illness under 8 days, 100% of the net pay for days 8-180; Art. 97 (p. 116): 12 months. The file had a flat 80% and no carenza: corrected. Art. 97 holds both a 21-month and a 24-month paragraph on several illnesses, so no window is stored (note). |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `6S` | Level 6S — senior manager / technical director (incl. function allowance EUR 20.66) | € 2,133.07 | 2026-10-01 |
| `6` | Level 6 — skilled technician / senior clerical employee | € 1,978.15 | 2026-10-01 |
| `5` | Level 5 — specialist operator / clerical employee | € 1,813.56 | 2026-10-01 |
| `4` | Level 4 — highly qualified operator | € 1,675.42 | 2026-10-01 |
| `3` | Level 3 — specialist operator | € 1,606.03 | 2026-10-01 |
| `2` | Level 2 — qualified operator | € 1,538.39 | 2026-10-01 |
| `1` | Level 1 — basic operator | € 1,454.41 | 2026-10-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 4 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 7.23 |
| `2` | € 7.75 |
| `3` | € 8.26 |
| `4` | € 9.30 |
| `5` | € 10.85 |
| `6` | € 12.91 |
| `6S` | € 15.49 |

## Apprenticeship

**gruppo_1_abb** (type: `percentage`)  
Destination levels: `4`, `5`, `6`, `6S`  
percentage: 1.00

**gruppo_2_abb** (type: `percentage`)  
Destination levels: `3`  
percentage: 1.00

**gruppo_3_abb** (type: `percentage`)  
Destination levels: `2`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "tessile-moda-artigianato-confartigianato/chimica_ceramica_subsectors · base_salary · impact yes · open"
    Only tessile-abbigliamento sub-sector modelled. Chimica-ceramica sub-sectors (different salary tables) are not modelled. CNEL code V751 covers all three sub-sectors.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the chimica-ceramica salary tables with a sub-sector input.

!!! warning "tessile-moda-artigianato-confartigianato/apprentice_seniority_hire_date · seniority · impact yes · open"
    APPRENTICE SENIORITY treated as uniform 6.00 EUR from 2025-01-01 regardless of hire date. Strictly, only workers hired after 17 Jul 2024 get 6.00 from Jan 2025; workers hired before that date remain at 5.16. For new hires this model is correct.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the 5.16 EUR apprentice increment for workers hired before 17 July 2024 with a hire-date input.

!!! warning "tessile-moda-artigianato-confartigianato/level_category_unconfirmed · inps_employer · impact unknown · open"
    LEVEL CATEGORY: all levels left null (no primary-source text confirming operaio/impiegato split). The 2026-artigianato.json tier applies the impiegato rate (0.2471) for category='impiegato'/'quadro' vs. default 0.2693. Employer cost for higher levels (5, 6, 6S) may be slightly overestimated until categories are confirmed from primary CCNL text.

    **Applies when:** `inps_employer` applies; level in 5, 6, 6S.

    **Remediation:** Confirm the operaio/impiegato category of each level from the CCNL text.

!!! warning "tessile-moda-artigianato-confartigianato/inps_sector_rates_unsourced · inps_employer · impact unknown · open"
    INPS RATES: the employer and worker INPS rates of the sector (artigianato) are totals no 2026 INPS or association table confirms: the only component split found is the INPS guide of 2012 and the 2026 totals come from a software house page that does not prove its year. The contributions of every run rest on them.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Source the artigianato rates of 2026 on an INPS or association table, mark the inps block of contribution/2026/artigianato.json derived, then remove this note.

!!! warning "tessile-moda-artigianato-confartigianato/apprentice_inps_rates_unsourced · inps_employer · impact unknown · open"
    APPRENTICE INPS RATES: the apprentice rates of the sector (artigianato) apply the 10% of L. 296/2006 art. 1 c. 773 plus the 1.61% NASpI, but no source found settles whether the 0.91 NASpI reduction of the artisan employers also applies to apprentices, nor the wage-integration contribution they owe (the FSBA is paid outside INPS). The contributions of an apprentice may differ.

    **Applies when:** `inps_employer` applies; contract type in apprentice.

    **Remediation:** Source the apprentice rates of artigianato (an INPS circular or an association table of 2026), mark the apprentice block of contribution/2026/artigianato.json derived, then remove this note.

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

!!! warning "mid_month_level_change · base_salary · impact unknown · open"
    A promotion on a day other than the first of a month splits the monthly pay of the run between the level before and the new level by the payable days of the CCNL daily quota on each side of the promotion, component by component; the hourly quotas of the month (overtime, permits, absences) read the same split chain whatever the day of the event. The CCNL texts read (Commercio and Terziario art. 118, DMO art. 102) give the new level from the promotion but not how its month is split.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source how a month is split by a promotion inside it (a CCNL clause or an INPS or Ministry ruling) and price the events of the month at the terms of their day, then resolve this limitation.

!!! warning "arrears_unused_deductions · contract_renewal_arrears · impact yes · open"
    The engine computes the rate of the separate taxation of arrears from PriorYearTaxFacts.net_income_biennio (art. 21 cc. 1, 3 TUIR) but does not reduce the tax by the deductions of artt. 12 and 13 cc. 1-2 the worker did not use in the years the arrears refer to (art. 21 c. 4): the request does not state them, so the tax may be overstated.

    **Applies when:** `contract_renewal_arrears` applies; the run takes the engine code path.

    **Remediation:** Add the deductions the worker declares as unused for each year of the arrears and reduce the tax by them, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| SOURCE: kitech.it cited as accessible URL proxy; primary source is FEMCA CISL Bergamo salary sheet (local PDF, 4 tranches Jul 2024–Oct 2026) against which all values were verified. | tabella_retributiva | 2024-07-16 | [↗](https://www.kitech.it/ccnl/tessile-abbigliamento-artigianato) |
| SOURCE: EBER Allegato 2 'Sintesi codifica contratti INPS e CNEL' — CNEL code V751, INPS code 003. Cross-validated: acconciatura H515 matches repo. | altro | — | [↗](https://www.eber.org) |
| SOURCE: Rinnovo signed 16 luglio 2024. Confirms Art. 68 Section 7 retribution 'Omissis' (unchanged from 2017 base). Apprentice seniority raised to 6.00 from 2025-01-01 for hires after 17 Jul 2024. | altro | 2024-07-16 | [↗](https://olympus.uniurb.it) |
| SOURCE: CNA PDF base CCNL 2017-12-14 — Art. 67 seniority amounts (per-level), Art. 68 apprenticeship percentages (3 gruppi, unchanged in 2024 rinnovo). Signatories from signature page. | altro | 2017-12-14 | [↗](https://www.cna.it) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (minimi tabellari conglobati). Back-calculation: L3 Jan 2025 = 1502.03/173 = 8.68 EUR/h; L4 Jan 2025 = 1566.69/173 = 9.05 EUR/h; L6 Jan 2025 = 1849.57/173 = 10.69 EUR/h — consistent divisor 173 across levels confirms conglobated model.
    
    CNEL CODE: V751 confirmed from EBER (Ente Bilaterale Emilia-Romagna) 'Allegato 2 — Sintesi codifica contratti INPS e CNEL', INPS code 003. D025 found on lavoro-economia.it refers to the older separate 'Area Tessile-Moda' pre-unification entry; V751 covers the current unified area contract (tessile+chimica+ceramica).
    
    TRANCHE DATES: four tranches — 2024-07-01 (retroactive from renewal 16 Jul 2024), 2025-01-01, 2025-10-01, 2026-10-01. Source: FEMCA CISL Bergamo salary sheet, cross-checked kitech.it.
    
    HOURLY DIVISOR: 173, derived from 40-hour work week (Art. 9 CCNL tessile-moda artigianato). Formula: 40 h/week × 52/12 = 173.33 rounded to 173 per contract.
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: ilccnl.it / CNA PDF art. mensilità aggiuntive.
    
    SENIORITY: biennale (every 24 months), maximum 4 scatti. Per-level amounts from Art. 67 CNA PDF 2017 (primary source): 6S=15.49, 6=12.91, 5=10.85, 4=9.30, 3=8.26, 2=7.75, 1=7.23 EUR. Unchanged in 2024 rinnovo.
    
    APPRENTICE SENIORITY: raised from 5.16 to 6.00 EUR by 2024 rinnovo (Art. 25), effective 2025-01-01 for new hires after 17 Jul 2024. Modelled as uniform 6.00 from 2025-01-01 (pre-Jul-2024 hires staying at 5.16 not separately tracked — minor simplification for new engagements).
    
    APPRENTICESHIP: 3 gruppi (Art. 68 CNA PDF 2017, Section 7 retribution marked 'Omissis' in 2024 rinnovo = unchanged). Gruppo 1 (destination levels 4-6S, max 54 months), Gruppo 2 (destination level 3, max 42 months), Gruppo 3 (destination level 2, max 24 months). Level 1 has no apprenticeship track.
    
    Level 6S indennità di funzione (EUR 20.66) confirmed fixed across all four tranches. Verification 2026-09-09: web sources show L6S minimi (without indennità) as 1922.59/1975.32/2039.91/2112.41 (Jul 2024/Jan 2025/Oct 2025/Oct 2026); file stores 1943.25/1995.98/2060.57/2133.07 — difference exactly 20.66 EUR at every tranche (kitech.it Oct 2025 confirmation plus back-check against all 4 tranches). Indennità conglobata in base_salary (no separate fixed_allowances entry).
    
    INPS: reuses 2026-artigianato.json (ARTIGIANATO sector).
    

## Raw data

The contract file this page is generated from: [`agreement/tessile-moda-artigianato-confartigianato.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/tessile-moda-artigianato-confartigianato.json).

## Usage example

```python
--8<-- "docs/examples/agreement/tessile-moda-artigianato-confartigianato/example.py"
```
