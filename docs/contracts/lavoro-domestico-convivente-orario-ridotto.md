# CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (conviventi a orario ridotto, art. 14 c. 2)

| | |
|---|---|
| **CNEL code** | `H501` |
| **Sector** | lavoro domestico |
| **Family** | `lavoro-domestico` |
| **Tax sector** | `lavoro-domestico` |
| **Last renewal** | 2025-10-28 |
| **Workers (est.)** | — |
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
| **Limits of this contract** | assistance_contribution, base_salary, inps_employer, overtime |

8 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🧑 Manual | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 13 verified / 2 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-10-28 |
| **Last review** | 2026-10-16 |
| **Latest salary tranche** | 2026-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-12 | claude-opus-5-5 (ai) | Every payable rule of the file: minimums, hourly divisor, additional months, seniority, Cas.Sa.Colf, overtime, absences, leave and the accrual of the tredicesima, read in the signed text of 28 October 2025 and its 2026 table (p. 59); the sickness rule of Art. 27 stays derived (readings in its transformation). | corrected | Overtime: the file held 10% and 20%; Art. 15 c. 3 sets 25% by day, 50% by night and 60% on a holiday or Sunday. The 20% of Art. 14 c. 6 is the supplement of ordinary night work, not of overtime.<br>accrual_rule was missing: chiarimento a verbale 4 counts a fraction of a month of at least 15 calendar days as a whole month.<br>Citations moved from the DOMINA table and section labels without page to the signed text with page and quote.<br>Tabella B, level B: the file held 702,35 as printed in the signed text; the DOMINA table of 2026 and the table of the Commissione of 11 February 2026 print 702,25. Corrected to 702,25 and left derived; the seniority step (4%) is 28,09 either way. |
| 2026-10-16 | claude-opus-5-5 (ai) | Limitation hourly_inps_bracket_unvalidated: the band of the hourly INPS contribution up to 24 weekly hours against the worked quarters of a signatory of the CCNL (DOMINA) and INPS circ. 9/2026. | flagged | INPS circ. 9/2026 downloaded again on 2026-10-16: same sha256 as the bundle, no rectification in the text; the 2026 amounts of the file stand.<br>DOMINA states that the paga oraria effettiva includes the hourly share of the tredicesima and prints four quarters of 2026 (13 weeks): colf 10 h at 8.00 an hour, 1.70, 221.00 (worker 55.90); colf 10 h at 9.00, 1.92 because 9 x 13 / 12 = 9.75 is above 9.61, 249.60 (62.40); colf 25 h, 1.24, 403.00 (100.75); badante convivente 54 h, 1.24, 870.48 (217.62). The engine's effective pay and band match all four (tests/knowledge/ccnl_engine/contribution/domestic/services/test_effective_hourly_pay.py::test_the_band_of_the_published_quarters_of_a_signatory): the raise by 13/12 is validated.<br>Still unvalidated, so the limitation stays: the share of board and lodging in the effective pay of a convivente up to 24 weekly hours. DOMINA states it ('per chi ha vitto e alloggio, il loro valore convenzionale'), as the engine computes it, but prints no worked case with board and lodging, and no worked example of a convivente up to 24 hours was found. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `C` | Level C — specialised domestic worker / assistant caregiver (badante) | € 814.60 | 2026-01-01 |
| `BS` | Level BS — qualified domestic worker with seniority | € 737.39 | 2026-01-01 |
| `B` | Level B — qualified domestic worker (colf qualificata) | € 702.25 | 2026-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 7 increments

| Level | Increment (monthly) |
|---|---:|
| `B` | € 28.09 |
| `BS` | € 29.50 |
| `C` | € 32.58 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "lavoro-domestico-convivente-orario-ridotto/babysitter_and_certification_allowances · base_salary · impact yes · open"
    NOT MODELLED: students aged 16 to 40 (art. 14 c. 2) at levels other than C, B and B super, for whom Tabella B has no value; the Tabella H indennita of the baby sitter of level B super for children under six (art. 34 c. 3), 97,06 a month for Tabella B workers; the Tabella L indennita of art. 34 c. 7 for certified workers. None of them is paid.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the Tabella H indennita (97,06 for a B super baby sitter of children under six) and the Tabella L indennita of certified workers as role-gated allowances (Allowance.role); the Tabella L one applies at any level.

!!! warning "lavoro-domestico-convivente-orario-ridotto/hourly_inps_bracket_unvalidated · inps_employer · impact unknown · open"
    INPS BAND: the engine chooses the band of up to 24 weekly hours on the paga oraria effettiva of INPS (circ. 9/2026; INPS page Contributi e agevolazioni fiscali per chi assume un lavoratore domestico): the monthly pay with board and lodging over the hours of the employment (weekly hours x 52 / 12), raised by the tredicesima (x 13 / 12). That reading of the circular is not yet checked against a worked example of the INPS domestic table (review of 2026-10-30).

    **Applies when:** `inps_employer` applies.

    **Remediation:** Validate the hourly INPS bracket lookup for weekly hours up to 24 against the INPS domestic table.

!!! note "lavoro-domestico-convivente-orario-ridotto/board_lodging_substitute · base_salary · impact unknown · resolved"
    The cash indennita sostitutiva of board and lodging is not paid for the days the convivente does not take them: ferie (Art. 17 c. 7), sospensioni extraferiali (Art. 18 c. 1), congedo matrimoniale (Art. 24 c. 2), malattia and infortunio outside hospital (Art. 27 c. 9, Art. 29 c. 7). The request states those days with BoardLodgingEvent, and the engine pays the value in kind over 30 for each of them.

    **Applies when:** `base_salary` applies; run kind in regular, termination.

    **Remediation:** Resolved: BoardLodgingEvent states the days without board and lodging of the month; the engine pays the value in kind over 30 times the days (Art. 36 c. 3).

!!! warning "lavoro-domestico-convivente-orario-ridotto/extra_month_hours · assistance_contribution · impact unknown · open"
    The INPS contributions of the tredicesima are paid on the hours of the year: INPS bands them on the paga oraria effettiva, which spreads the tredicesima over the hours, so the tredicesima run charges no INPS hours. The Cas.Sa.Colf contribution of Art. 54 c. 2 is charged on the contributable hours the run states, a tredicesima run too: no bundled source says whether the tredicesima carries hours of its own for it.

    **Applies when:** `assistance_contribution` applies; run kind in thirteenth.

    **Remediation:** Source from the Cas.Sa.Colf rules whether the tredicesima carries contributable hours and set them for extra-month runs.

!!! note "lavoro-domestico-convivente-orario-ridotto/oncological_comporto · sickness · impact unknown · resolved"
    Art. 27 c. 6: the comporto is 50% longer for an oncological illness certified by the ASL. The episode can state a serious illness (SicknessEpisode.serious_illness), but the domestic sickness rules have no serious-illness rule, so the engine keeps the ordinary comporto (review of 2026-10-30).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Resolved: the bands carry the comporto of an oncological illness (serious_comporto_days 15, 68 and 270 days, the periods of c. 4 raised by 50%), applied when the episode states SicknessEpisode.serious_illness; 45 x 1.5 = 67.5 is read as 68, the 68th day being still in part within the period.

!!! note "lavoro-domestico-convivente-orario-ridotto/sick_board_lodging · sickness · impact unknown · resolved"
    Art. 27 c. 9: the conventional value of board and lodging is added to the sick pay only when the worker is not in hospital or in the employer's home. The sick pay is thirtieths of the cash monthly pay, without the value in kind; the sick days spent elsewhere are stated with BoardLodgingEvent, which pays that value in cash.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Resolved: the sick pay leaves the value in kind out, and BoardLodgingEvent pays it for the sick days outside hospital and the employer's home.

!!! warning "lavoro-domestico-convivente-orario-ridotto/hours_within_arrangement · overtime · impact yes · open"
    Art. 14 c. 2: hours beyond the agreed ones within the agreed time arrangement are paid at the plain hourly retribuzione globale di fatto, only those outside it with the supplements of Art. 15. The request does not say where an hour falls, so the overtime bands of Art. 15 apply to every overtime hour stated.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a fact for the extra hours within the agreed time arrangement and pay them without a supplement.

!!! warning "lavoro-domestico-convivente-orario-ridotto/annual_minimi_not_updated · base_salary · impact yes · open"
    ANNUAL MINIMI: the minimi of the CCNL are updated every year from 1 January by the Commissione nazionale (Art. 38, ISTAT variation of the consumer prices); the bundle holds the table of 2026. From 1 January 2027 the amounts are those of 2026 until the 2027 table is published and added, so a 2027 run is not payable.

    **Applies when:** `base_salary` applies; from 2027-01-01.

    **Remediation:** Add the minimi of 2027 set by the Commissione nazionale with their source, then remove this note.

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
| https://lavorodomestico.assindatcolf.it/wp-content/uploads/2026/04/CCNL.pdf | altro | 2025-10-28 | [↗](https://lavorodomestico.assindatcolf.it/wp-content/uploads/2026/04/CCNL.pdf) |

??? note "Coverage notes"
    SALARY MODEL: TABELLA B of the CCNL of 28/10/2025, conviventi hired under art. 14 c. 2 (levels C, B and B super, up to 30 weekly hours, written act of c. 3). The monthly minimum is paid 'qualunque sia l'orario di lavoro osservato nel limite massimo delle 30 ore settimanali', so it is not proportioned to the hours and more than 30 weekly hours are rejected; board and lodging are due in full ('fermo restando l'obbligo di corresponsione dell'intera retribuzione in natura'). Values of 2026: B 702,25 (the signed text prints 702,35, the DOMINA and Commissione tables 702,25), BS 737,39, C 814,60.
    
    HOURLY DIVISOR: 130 = 30 x 52 / 12 in the file; a run uses the weekly hours of the employment x 52 / 12 (flat_pay_max_weekly_hours), since the Tabella B pay does not change with the hours: B super at 10 weekly hours is 737,39 / 43,33 = 17,02 an hour. Work beyond the agreed hours is paid at the hourly retribuzione globale di fatto (art. 14 c. 2), with the art. 15 supplements outside the agreed time arrangement; the overtime bands are those of the convivente file.
    
    SENIORITY: biennale, 4% of the Tabella B minimum (art. 37 c. 1: 'sulla retribuzione minima contrattuale'), maximum 7 scatti: B 28,09, BS 29,50, C 32,58.
    
    TAX SECTOR: lavoro-domestico (TaxSector.LAVORO_DOMESTICO). Flat per-hour INPS contributions from INPS Circ. 9/2026. A household employer is not a withholding agent: it is not among the sostituti d'imposta of art. 23 c. 1 D.P.R. 600/1973 (art. 33 c. 1 D.Lgs. 33/2025 from 2027), so the engine withholds no IRPEF or surtax and pays no trattamento integrativo, ulteriore detrazione or somma esente.
    
    ADDITIONAL MONTHS: 13 (tredicesima mensilita, Art. 39 CCNL 28/10/2025). No quattordicesima for domestic workers.
    
    APPRENTICESHIP: none. Domestic workers are excluded from D.lgs. 81/2015 Art. 47 apprenticeship provisions.
    
    BOARD AND LODGING: every level carries the allowance vitto_alloggio, the valore convenzionale of board and lodging provided in kind (Art. 36 c. 3, Tabella F 2026: 2,33 + 2,33 + 2,00 per day, x 30 = 199,80 per month). A regular run pays no cash for it and counts it in the TFR base (Art. 41 c. 1); the tredicesima pays it in cash (Art. 39 c. 1, chiarimento a verbale 5). It is not reduced for reduced hours (Art. 14 c. 2: intera retribuzione in natura).
    
    CAS.SA.COLF: contributi di assistenza contrattuale of Art. 54 c. 2, 0,06 EUR per paid hour, 0,02 withheld from the worker and 0,04 paid by the employer, charged on the contributable hours of the run.
    
    SICKNESS (Art. 27): INPS pays no indemnity to domestic workers; the employer pays 50% of the retribuzione globale di fatto up to the third day and 100% from the fourth, for at most 8, 10 or 15 days in the 365 days that end on the sick day, within a comporto of 10, 45 or 180 days, for up to 6 months of seniority, up to 2 years and over 2 years. A sick day is a thirtieth of the monthly pay (chiarimento a verbale 2).
    
    NIGHT WORK (Art. 14 c. 6): ordinary work between 22.00 and 6.00 is paid with a 20% supplement of the hourly retribuzione globale di fatto; the engine takes its amount as a NightShiftEvent stated by the caller. The overtime bands are those of Art. 15 c. 3 (25% by day, 50% by night, 60% on a holiday or Sunday); night overtime on a holiday has no band of its own and a run that states it is rejected.
    

## Raw data

The contract file this page is generated from: [`agreement/lavoro-domestico-convivente-orario-ridotto.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/lavoro-domestico-convivente-orario-ridotto.json).

## Usage example

```python
--8<-- "docs/examples/agreement/lavoro-domestico-convivente-orario-ridotto/example.py"
```
