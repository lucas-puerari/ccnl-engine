# CCNL per i dipendenti da aziende dei settori Pubblici Esercizi, Ristorazione Collettiva e Commerciale e Turismo - Ristorazione collettiva (aziende dell'art. 1 c. 1 par. II)

| | |
|---|---|
| **CNEL code** | `H05Y` |
| **Sector** | turismo |
| **Family** | `turismo` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-06-26 |
| **Workers (est.)** | ~350k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🏭 Production |

[← Contracts index](index.md)

??? note "Signatories"
    - FIPE-Confcommercio
    - Legacoop Produzione e Servizi
    - Confcooperative Lavoro e Servizi
    - AGCI-Servizi
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTuCS

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, overtime |

5 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 65 verified / 6 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 🏭 Production | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-06-26 |
| **Last review** | 2026-11-15 |
| **Latest salary tranche** | 2027-12-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-11 | claude-opus-5-5 (ai) | Inherited from pubblici-esercizi-fipe-angem, of which this file is a copy: the review covered that file's levels; here it stands for the shared rules (work rules, parameters) only. Every payable rule of the file (72 records) and the hourly divisor read again in the signed texts: the CCNL of 8 February 2018, the renewal of 5 June 2024 and its accordo integrativo of 26 June 2024 with the final salary tables. | corrected | All 50 salary periods and the 10 level rows match the accordo integrativo of 26 June 2024 (pp. 1-2) and are verified, with the Quadri allowances (Art. 154), the 14 monthly payments (Artt. 183-184), seniority (Art. 182), overtime 30% and 60% (Art. 126), the daily quota 1/26 (Art. 159), leave (Art. 134) and the hourly divisor 172 (Art. 160). Pages are PDF page indexes.<br>Corrected: sickness (Art. 190, Art. 194). INPS pays 80% for the whole sickness in this sector (regime pubblici_esercizi, funded by the 0.77% supplement) and the CCNL adds no top-up, so the target is 80%; the three days of carenza are paid in full only when the sickness lasts more than five days; the comporto is 180 days a calendar year.<br>Assumed: the overtime bands for holidays (30%) and holiday nights (60%). The CCNL sets only 30% by day and 60% by night (Art. 126) and 20% for ordinary work on a holiday (Art. 132); the two bands are inferences, not cited values.<br>Left derived: the Fon.Te. rates, read in the fund's information sheet, not in the CCNL.<br>Not modelled: the quattordicesima excludes the seniority increments (Art. 184), the collective catering companies move the June 2025 and June 2026 tranches to September (accordo integrativo p. 3), and the conditions of Art. 190 beyond the carenza.<br>FIPE and the Turismo CCNLs are two agreements: FIPE was renewed on 5 June 2024 (level 4 at 1,692.69 from June 2026), the Turismo CCNL of Federalberghi and Faita on 5 July 2024 (1,695.69 from May 2026). |
| 2026-10-12 | claude-opus-5-5 (ai) | Quattordicesima and seniority, holiday overtime, September tranches of the ristorazione collettiva: follow-ups of the review of 2026-10-11. | corrected | Quattordicesima: art. 184 c. 1 excludes the matured seniority increments; the engine paid them. Now excluded.<br>Holiday overtime: the 30% and 60% are art. 126 itself (by time of day), not an analogy: derived from p. 99; whether art. 132's 20% is added is left open (outside_input note).<br>Ristorazione collettiva: the 2025 and 2026 tranches start in September for the companies of art. 1 c. 1 par. II (accordo integrativo 26.6.2024, p. 3); still the limitation contract_catering_tranche_dates.<br>This file was created from pubblici-esercizi-fipe-angem for the collective catering companies: same rules and review history, with the 2025 and 2026 tranches from 1 September (accordo integrativo of 26 June 2024, p. 3). |
| 2026-10-12 | claude-opus-5-5 (ai) | Accrual of the tredicesima and quattordicesima (artt. 183 c. 2 and 184 c. 4). | corrected | The accrual rule was missing (engine default of 15 days per month): the CCNL cumulates the fractions of month, a rateo for each 30 days and one for a remainder of 15 days or more, now modelled (cumulated_fractions). |
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule not yet verified, the apprenticeship (arts. 68 and 72), the limitations and the L2 values, for the production tier. | corrected | 22 records verified on the signed texts (salary periods on the accordo integrativo of 26 June 2024, accrual rule and Fon.Te. on the CCNL of 8 February 2018).<br>Fon.Te.: 0.55% employer and worker on the TFR base, art. 185 c. 3; valid from 29 November 1996 (the fund table), not from 2026.<br>Apprenticeship: level 1 is not a destination; level 6 lasts 24 months (art. 72 c. 1), now its own track; the 42 and 48 month profiles stay a limitation.<br>Holiday overtime: whether the 20% of art. 132 adds to the 30%/60% of art. 126 is not stated; the two bands stay derived with the limitation.<br>L2: INPS terziario verified (circ. 117/2022 allegato accepted on 2026-10-13), with the 0.77% sickness supplement of the pubblici esercizi (CCNL art. 190 c. 3); TFR art. 217, the scatti included since 1 November 2021.<br>No renewal after the accordo integrativo of 26 June 2024 changes gross pay. |
| 2026-10-16 | claude-opus-5-5 (ai) | Checklist item 'confrontare lordo, netto e costo azienda con esempi indipendenti': a run of the engine against the cost table of the Ministry of Labour for the comparto ristorazione collettiva (DD 63 of 10 July 2025, national table of January 2026, D.Lgs. 36/2023 art. 41 c. 13). | flagged | Level 4, January 2026: paga base conglobata 19.832,28 a year over 12 equals the 1652.69 of the file (tranche of 1 September 2025); the quattordicesima of the table, 1.652,69, is that month. Match: reference case pubblici-esercizi-fipe-angem-ristorazione-collettiva_4_2026_ministry.json.<br>Employer contributions: the table prints Inps 29,75%, FIS 0,53% and CIGS 0,60%, 30.88% in all; the engine applies 30.8833% to an impiegato of a company of 51 employees (the FIS employer share 0.80% x 2/3 = 0.5333%, printed rounded). The CIGS line places the table above 50 employees (D.Lgs. 148/2015 art. 20, commercial companies with more than fifty employees). Match within the rounding of the printed rate; a rate, not a total, so no output is credited.<br>Deviations, with cause and decision: INAIL 1,09% is not computed by the engine (documented); the health fund (158,40 a year) is the owed limitation health_and_bilateral_funds, which leaves the employer cost incomplete on every run (checked: is_employer_cost_complete false); the EBT contribution, the complementary pension at a 30% enrolment and the three seniority increments of row A are averages of the table, not facts of one worker: not compared. No independent net pay example: not compared. |
| 2026-10-17 | claude-opus-5-5 (ai) | The paga base and contingenza of every level from June 2024 against the accordo integrativo of 26 June 2024, the quattordicesima against the CCNL of 8 February 2018, and a year and a termination of a 4th level worker against a hand oracle. | confirmed | Accordo integrativo of 26 June 2024 (pp. 1-3): the 50 totals of contingenza and paga base of the ten levels from June 2024 to December 2027 match the file, with the tranches of 2025 and 2026 in September.<br>Art. 184 of the CCNL of 8 February 2018 (p. 128, scan read by OCR): quattordicesima of the pay in force on 30 June, paid with the July pay, in ratei of the twelve months before 1 July. Match.<br>Hand oracle (tests/knowledge/ccnl_engine/period/sector, scenarios ristorazione-year and ristorazione-june): a 4th level impiegato hired on 1 January 2026 by an employer with 10 employees, with the terziario rates up to 15 employees and the 0.77% sickness supplement of the pubblici esercizi taken apart; every payment and the year (gross, contributions, tax, net, TFR, employer cost) match the engine to the cent. The CCNL now covers every total of the definition of done. |
| 2026-10-31 | claude-opus-5-5 (ai) | The basis of the indemnity for the leave not taken at the end of the employment, searched in the OCR of the signed text of 2018 (Artt. 114, 134, 135, 159, 160). | corrected | Art. 159 - Determinazione della retribuzione giornaliera (p. 116): the daily pay is the monthly pay divided by 26 for every contractual purpose: work_rules.leave_rules.termination; the accrual of the leave is not modelled, so the basis is not used yet. |
| 2026-11-01 | claude-opus-5-5 (ai) | The notice of Artt. 208-209 (PDF pp. 143-144), checked by a separate session on the rendered pages. | confirmed | Art. 208 (PDF pp. 143-144, sha256 32a2831b... matched, page images read): 15 bands, A e B / 1 / 2 e 3 / 4 e 5 / 6S, 6 e 7 over the three service bands, the same for dismissal and resignation, no start day: work_rules.notice.<br>Art. 209 (p. 144): the indemnity is the normale retribuzione of the period (the ratei of the extra months follow art. 2121 c. 1 c.c.); the exception of Art. 179 for the pubblici esercizi does not concern this file. |
| 2026-11-05 | claude-opus-5-5 (ai) | The hourly divisor of the 44-hour week, Articolo 160 (PDF p. 116, printed p. 114), checked by a separate session on the page rendered at 200 and 400 dpi. | confirmed | Art. 160 c.1 (sha256 32a2831b... matched): 190 for a normal week of 44 hours, 172 for 40: work_rules.time_supplements.week_divisors 44/190.<br>The renewal of 5 June 2024 amends arts. 114, 135, 161, 183-184 and 199-202, not art. 160. |
| 2026-11-05 | claude-opus-5-5 (ai) | Art. 186 (p. 17) of the renewal of 5 June 2024, OCR of the signed scan. | corrected | Art. 186 covers every sector of the CCNL: the Fondo Est of the Pubblici esercizi file applies to ristorazione collettiva, which had no health fund. |
| 2026-11-08 | gpt-6-sol (ai) | Art. 13 commi 5-13 (renewal of 5 June 2024 pp. 7-8, CCNL 2018 p. 29), the encoding checked against the signed pages by a separate model session. | flagged | Confirmed the amounts by level and their mapping, the November 2027 payment, the part-time of comma 6 and the exclusion of comma 7.<br>Flagged: the quote condensed the table (now verbatim up to the table, the table in the transformation); the eligibility date of comma 5 is a reading, not stated; commi 8 (pre-1993 exception) and 12 (Fon.Te.) were missing from the limitation: added.<br>Kept as approximations under the limitation: trigger of comma 10, days worked, absorption. |
| 2026-11-15 | claude-opus-5-5 (ai) | Hourly base, night, holiday and shift supplements, travel allowance: quotes located in the cited files by sha256, values read against the quotes. | corrected | Applied: hourly_base, bands[0:night], bands[1:holiday], none.shift_work.<br>Left out: bands[2:sunday]: quote skipped; none.rest_day: skipped. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Qa` | Quadri A — managerial functions with a high level of management responsibility | € 2,578.07 | 2027-12-01 |
| `Qb` | Quadri B — managerial functions with continuous responsibility over a complex unit | € 2,375.56 | 2027-12-01 |
| `1` | Level 1 — staff with high professional content and operational autonomy | € 2,201.85 | 2027-12-01 |
| `2` | Level 2 — staff with initiative and operational autonomy (coordination) | € 1,999.36 | 2027-12-01 |
| `3` | Level 3 — staff with specialist technical knowledge (conceptual work) | € 1,877.00 | 2027-12-01 |
| `4` | Level 4 — staff with executive autonomy (specialised technical-administrative duties) | € 1,762.69 | 2027-12-01 |
| `5` | Level 5 — staff with qualified technical-practical knowledge and skills | € 1,643.50 | 2027-12-01 |
| `6s` | Level 6 super — staff with adequate technical-practical skills (formerly qualified commis or experienced staff) | € 1,574.42 | 2027-12-01 |
| `6` | Level 6 — staff with standard practical training and basic professional knowledge | € 1,549.78 | 2027-12-01 |
| `7` | Level 7 — general assistants, cleaning staff (simple manual tasks) | € 1,442.45 | 2027-12-01 |

## Seniority increments

**Cadence:** every 48 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `Qa` | € 40.80 |
| `Qb` | € 39.25 |
| `1` | € 37.70 |
| `2` | € 36.15 |
| `3` | € 34.86 |
| `4` | € 33.05 |
| `5` | € 32.54 |
| `6s` | € 31.25 |
| `6` | € 30.99 |
| `7` | € 30.47 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `2`, `3`, `4`, `5`, `6s`  
percentage: 1.00

**professionalizzante_24_mesi** (type: `percentage`)  
Destination levels: `6`  
percentage: 1.00

**professionalizzante_48_mesi** (type: `percentage`)  
Destination levels: `2`, `3`  
percentage: 1.00

**professionalizzante_42_mesi** (type: `percentage`)  
Destination levels: `4`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "pubblici-esercizi-fipe-angem-ristorazione-collettiva/holiday_overtime_cumulation · overtime · impact unknown · unsourced"
    HOLIDAY OVERTIME: Art. 126 (PDF p. 99) gives 30% by day and 60% by night for every overtime hour; Art. 132 (p. 103) gives 20% for the hours worked on a festività. No clause links them: art. 126 c. 3 excludes cumulation only with ordinary night work, art. 130 c. 2 only Sunday work with the festività, and the special parts (arts. 246-247, 263-264) and the 2024 renewal repeat or leave them. The engine pays holiday overtime at 30%/60% without the 20%.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Confirm whether the 20% of art. 132 is added to the overtime rate on a festività; if so set the bands to 0.5 and 0.8, else close this note.

!!! warning "pubblici-esercizi-fipe-angem-ristorazione-collettiva/guarantee_premium_2027 · base_salary · impact yes · open"
    Art. 13 c. 10 of the renewal of 5 June 2024 (p. 7), with commi 5-8 of the CCNL 2018 (p. 29): the amounts of November 2027 (A and B 186, 1-3 158, 4-5 140, 6S-7 112) are parameters.equalisation_element. Approximated: the trigger, read from the second-level facts of 2026 where the text asks whether an agreement on the premio di risultato was defined by 31 October 2026 after a platform was presented; the eligibility of comma 5, read as in service in October 2027 with six months of service; the proportion to the days actually worked in 2026, counted in months of more than 15 days; the absorption of comma 8, which takes any individual or collective treatment granted after 1 June 2024 except the fixed amounts of collective agreements signed before 1 July 1993, the engine deducting only the individual elements. Not modelled: the welfare alternative of comma 11, the worker's choice to pay the amount to Fon.Te. (comma 12) and the crisis exemption of comma 13. Unlike the Federalberghi clause, art. 13 has no territorial floor.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** State the comma 10 condition, the eligibility date and the days worked in 2026 as facts, take every treatment granted after 1 June 2024 (but the pre-1993 fixed amounts) into the absorption, and model commi 11, 12 and 13.

!!! note "pubblici-esercizi-fipe-angem-ristorazione-collettiva/health_and_bilateral_funds · bilateral_funds · impact yes · resolved"
    HEALTH FUND (art. 186): Fondo Est EUR 11/12 (15 from 2027) a month from the employer for the permanent non-quadri, and the element of EUR 16 on 14 months of an employer that does not pay it, as in the Pubblici esercizi file.

    **Applies when:** `bilateral_funds` applies.

    **Remediation:** Resolved: parameters.health_funds fondo_est, read on 2026-11-05.

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

!!! note "pension_extra_deduction_first_employed · pension_fund_contribution · impact unknown · resolved"
    A worker first employed after D.Lgs. 252/2005 came into force may deduct, in the twenty years after the fifth year of membership, the contributions above the annual cap within the room the first five years left, up to half the annual cap (art. 8 c. 6). The withholding agent applies it (AdE circ. 70/E/2007: the employer excludes the deductible contributions from the income of the ritenute): the worker states the deduction of the year as PensionFundEnrolment.extra_deduction, and contributions above the cap left with none stated carry the missing fact extra_deduction.

    **Applies when:** `pension_fund_contribution` applies; the run takes the engine code path.

    **Remediation:** Resolved: the extra deduction is an input of the enrolment.

### Without monetary impact

!!! note ""
    SALARY MODEL: the contractual pay structure provides for a separate national base pay and contingenza. For engine purposes they are consolidated into base_salary (monthly total per tranche). The totals are read in the accordo integrativo of 26 June 2024 (pp. 1-2), the same as the FIPE pay tables. fixed_allowances models the function allowance for quadri: Qa=75 EUR and Qb=70 EUR, from Art. 154 of the CCNL of 8 February 2018 (CCNL 2024-2027).

!!! note ""
    APPRENTICESHIP (CCNL 8 February 2018, arts. 68 and 72, PDF pp. 74-75, read on the signed scan): the professionalizzante apprentice is paid 80%, 85% and 90% of the qualified pay of the level in the first three years (art. 68 c. 1). Durations (art. 72 c. 1): 36 months for levels 2, 3, 4, 5 and 6s, 24 months for level 6. Level 1, level 7 and the quadri are not apprenticeship destinations. Art. 75 (apprenticeship for qualification or diploma) is out of scope.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.confcommerciomilano.it/export/sites/unione/doc/contratti_lavoro/contrattazione_collettiva/ACCORDO-INTEGRATIVO_Tabelle-Retributive_CCNL_P_E_Risto_Collettiva_Commerciale_Turismo.pdf | tabella_retributiva | 2024-06-26 | [↗](https://www.confcommerciomilano.it/export/sites/unione/doc/contratti_lavoro/contrattazione_collettiva/ACCORDO-INTEGRATIVO_Tabelle-Retributive_CCNL_P_E_Risto_Collettiva_Commerciale_Turismo.pdf) |
| https://www.fipe.it/wp-content/uploads/2024/06/Contratto-CCNL-05_06_24.pdf | altro | 2024-06-05 | [↗](https://www.fipe.it/wp-content/uploads/2024/06/Contratto-CCNL-05_06_24.pdf) |
| https://www.confcommerciomilano.it/export/sites/unione/doc/contratti_lavoro/contrattazione_collettiva/ccnl_ristorazione_2018.pdf | altro | 2018-02-08 | [↗](https://www.confcommerciomilano.it/export/sites/unione/doc/contratti_lavoro/contrattazione_collettiva/ccnl_ristorazione_2018.pdf) |

??? note "Coverage notes"
    SUB-SECTOR: collective catering companies of art. 1 c. 1 par. II (ristorazione collettiva). Same rules as pubblici-esercizi-fipe-angem; the 2025 and 2026 tranches apply from 1 September (accordo integrativo 26 June 2024, p. 3: 'Per le aziende di cui all'art. 1 comma 1 paragrafo II, le Parti stabiliscono incrementi dei valori di paga base nazionale mensile nelle modalità di seguito indicate').
    
    2024 RENEWAL: CCNL signed 5 June 2024, validity 1 June 2024 – 31 December 2027 (CNEL H05Y, ~592,364 workers Uniemens 2022 / over 1 million according to FIPE). Pay table source: fipe.it/wp-content/uploads/2025/02/Tabelle-retributive-2024.pdf.
    
    SENIORITY INCREMENTS: 6 quadrennial increments (48 months). Per-level amounts from FIPE pay tables (fipe.it/wp-content/uploads/2025/02/Tabelle-retributive-2024.pdf). Paid over 14 monthly instalments.
    
    MONTHLY PAYMENTS: 14, the tredicesima of Art. 183 and the quattordicesima of Art. 184 of the CCNL of 8 February 2018 (PDF pp. 127-128). The quattordicesima excludes the matured seniority increments (seniority_increments.excluded_from_extra_months).
    
    HOURLY DIVISOR: 172 for a 40-hour week (Art. 160 of the CCNL of 8 February 2018, PDF p. 116; 190 for a 44-hour week, not modelled).
    
    INPS: uses 2026-terziario.json (tax_sector terziario, same as commercio-confcommercio and turismo-federalberghi).
    
    APPRENTICESHIP PROFILES: art. 72 c. 2 (PDF p. 75) gives 48 months to named profiles of levels 2 and 3 and 42 months to named profiles of level 4, and art. 68 c. 1 (p. 74) pays them 95% in the fourth year: tracks professionalizzante_48_mesi and professionalizzante_42_mesi. An apprentice of levels 2, 3 and 4 states Apprentice.track: professionalizzante for the 36 months of the other profiles.
    
    TRATTAMENTO INTEGRATIVO SPECIALE (L. 199/2025 art. 1 cc. 18-21): for the work of 1 January - 30 September 2026 of a worker who asked for it (PriorYearTaxFacts.special_supplement_requested) with 2025 employment income up to 40,000 EUR, in an employer of food service, tourism or thermal establishments (EmployerProfile.activity), the engine pays 15% of the gross pay of the night hours and of the holiday overtime (AdE circ. 26/E/2023 par. 2: 'calcolata sulla retribuzione lorda'), outside income, as a credit the employer recovers in F24 (capability special_supplement).
    

## Raw data

The contract file this page is generated from: [`agreement/pubblici-esercizi-fipe-angem-ristorazione-collettiva.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/pubblici-esercizi-fipe-angem-ristorazione-collettiva.json).

## Usage example

```python
--8<-- "docs/examples/agreement/pubblici-esercizi-fipe-angem-ristorazione-collettiva/example.py"
```
