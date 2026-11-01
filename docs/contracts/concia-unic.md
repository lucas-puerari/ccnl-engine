# CCNL per i lavoratori dell'industria conciaria (UNIC)

| | |
|---|---|
| **CNEL code** | `B101` |
| **Sector** | industria |
| **Family** | `pelli-calzature` |
| **Tax sector** | `industria` |
| **Last renewal** | 2024-03-07 |
| **Workers (est.)** | ~22.6k |
| **Ruleset version** | `2026.1` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - UNIC
    - FILCTEM-CGIL
    - FEMCA-CISL
    - UILTEC-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | leave, overtime, seniority |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🟢 Verified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 57 verified / 1 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-03-07 |
| **Last review** | 2026-10-12 |
| **Latest salary tranche** | 2026-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-10 | claude-opus-5-5 (ai) | Whole file. The values checked were not recorded; no value was marked verified. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-11 | claude-opus-5-5 (ai) | Every payable rule of the file (98 records) read again in the signed texts: the renewal of 7 March 2024 and the CCNL testo definitivo of 21 January 2021 deposited at CNEL (B101), which the 2024 renewal leaves unchanged for these articles. | corrected | 96 records match their source and are verified; the two corrected rules below are verified too. The 34 records that cited the mysolution.it summary sheet now cite the CNEL testo definitivo. Pages are physical PDF pages (the printed page of the CNEL text is two lower).<br>Corrected: the leave tiers of Art. 42 start after the 10th and the 15th year (120 and 180 months), not 132 and 192.<br>Corrected: Art. 51 b) deducts unworked hours by the ratio 173 / working hours of the month, and Art. 50 keeps 1/25 for Sunday holidays, so the absence rule is by_month_hours instead of by_25.<br>Not modelled, each underpaying: night overtime after the first hour (76%), the 25% and 35% bands for daytime overtime beyond 48 hours, and the sickness tiers of 10 and 12 months for longer service.<br>The IND_FUNZIONE clause is Art. 46 g), not Art. 47.<br>No renewal signed after 7 March 2024; the contract expired on 30 June 2026 and a renewal is under negotiation. |
| 2026-10-12 | claude-opus-5-5 (ai) | Overtime bands of art. 35 and the sickness rule of art. 60, follow-ups of the review of 2026-10-11. | corrected | Overtime: the 25% (49th weekly hour), 35% (beyond) and 76% (night after the first hour) bands were missing; added, the night threshold read per day.<br>Sickness: only the band up to 3 years was modelled, per episode and on the gross pay; now three seniority bands within 36 months, on the net pay, with the restart after 4 months without sickness (derived: months of 30 days, band edges read on completed months). |
| 2026-10-12 | claude-opus-5-5 (ai) | Special cases of the comporto (art. 60 B as rewritten on 7 March 2024). | corrected | The longer comporto of the malattie invalidanti (+2, +3, +4 months) and the hospital stays over 5 days left out of the comporto (60 days at most) are now modelled; the restart from the 16th day of a hospital stay and the periodic checks stay a limitation. |
| 2026-10-12 | claude-opus-5-5 (ai) | Restart of the sickness treatment from the 16th day of a hospital stay (art. 60 C). | corrected | From the 16th day of a hospital stay the treatment starts anew (full pay again): modelled with hospital_restart_day 16. |
| 2026-10-12 | claude-opus-5-5 (ai) | Restart 12 months after the end of the full pay and periodic checks (art. 60). | corrected | The last special cases of art. 60 are modelled: the restart 12 months after the full pay ended and the periodic checks out of the comporto; the limitation sickness_special_cases is closed. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A` | Livello A — quadri, direttivi con elevata autonomia decisionale | € 2,937.60 | 2026-01-01 |
| `B1` | Livello B1 — operai e impiegati con elevata specializzazione | € 2,494.04 | 2026-01-01 |
| `B2` | Livello B2 — operai e impiegati specializzati | € 2,494.04 | 2026-01-01 |
| `C1` | Livello C1 — operai e impiegati qualificati con funzioni di coordinamento | € 2,234.82 | 2026-01-01 |
| `C2` | Livello C2 — operai e impiegati qualificati | € 2,234.82 | 2026-01-01 |
| `D1` | Livello D1 — operai e impiegati con mansioni di concetto specializzate | € 2,041.99 | 2026-01-01 |
| `D2` | Livello D2 — operai e impiegati con mansioni di concetto | € 2,041.99 | 2026-01-01 |
| `E1` | Livello E1 — operai e impiegati qualificati con mansioni operative specializzate | € 1,783.71 | 2026-01-01 |
| `E2` | Livello E2 — operai e impiegati con mansioni operative qualificate | € 1,783.71 | 2026-01-01 |
| `E3` | Livello E3 — operai e impiegati con mansioni operative generiche specializzate | € 1,783.71 | 2026-01-01 |
| `F1` | Livello F1 — lavoratori in periodo di prima formazione (parametro 100) | € 1,689.30 | 2026-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 19.63 |
| `B1` | € 19.63 |
| `B2` | € 17.56 |
| `C1` | € 14.46 |
| `C2` | € 13.94 |
| `D1` | € 13.94 |
| `D2` | € 12.65 |
| `E1` | € 11.88 |
| `E2` | € 11.88 |
| `E3` | € 10.33 |
| `F1` | € 10.33 |

## Apprenticeship

**professionalizzante_A_B1_B2** (type: `under_classification`)  
Destination levels: `A`, `B1`, `B2`

**professionalizzante_C1_C2** (type: `under_classification`)  
Destination levels: `C1`, `C2`

**professionalizzante_D1** (type: `under_classification`)  
Destination levels: `D1`

**professionalizzante_D2** (type: `under_classification`)  
Destination levels: `D2`

**professionalizzante_E1** (type: `under_classification`)  
Destination levels: `E1`

**professionalizzante_E2** (type: `under_classification`)  
Destination levels: `E2`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "concia-unic/higher_overtime_bands · overtime · impact yes · open"
    OVERTIME: every band of art. 35 is modelled: 15% to the 48th weekly hour, 25% the 49th, 35% beyond; night 61% the first hour, 76% after (first hour read per day); holiday 71%. The percentages do not add up ('la maggiore assorbe la minore', p. 57). The engine pays the first tier of an overtime event and flags the bands past a threshold (overtime_tier_not_applied): the caller passes the multiplier for the hours past a threshold.

    **Applies when:** `overtime` applies.

    **Remediation:** Pass the multiplier on the overtime event for the hours past a threshold; the engine does not split an event by weekly or daily hours.

!!! warning "concia-unic/rol_not_accrued · leave · impact yes · open"
    LEAVE: Art. 42 of the CCNL testo definitivo 21/01/2021 (CNEL B101, physical p. 62): 4 weeks (20 days) up to the 10th year of service completed; 4 weeks + 2 days beyond the 10th year (120 months); 4 weeks + 3 days beyond the 15th (180 months); 5 weeks (25 days) beyond the 18th (216 months). ROL 68 ore/anno not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a rol bucket of 68 hours a year to leave_rules with its accrual and payout (Art. 42 / ROL article).

!!! warning "concia-unic/apprentice_seniority · seniority · impact unknown · open"
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

### Without monetary impact

!!! note ""
    DAILY DIVISOR: Art. 51 b) of the CCNL testo definitivo 21/01/2021 (CNEL B101, physical pp. 69-70) deducts the normal hours not worked by the ratio 173 / working hours of the month; Art. 50 keeps the quota of 1/25 for the holidays falling on a Sunday. Modelled as by_month_hours: one share per Monday to Friday out of the Mondays to Fridays of the month.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.filctemcgil.it/images/download/CONTRATTI/concia/240307_CONCIA_RINNOVO%20CCNL%202023-2026.pdf | altro | 2024-03-07 | [↗](https://www.filctemcgil.it/images/download/CONTRATTI/concia/240307_CONCIA_RINNOVO%20CCNL%202023-2026.pdf) |
| https://az-apim-cne-sa-0002-lgc-we.azure-api.net/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/148617 | altro | 2021-01-21 | [↗](https://az-apim-cne-sa-0002-lgc-we.azure-api.net/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/148617) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = minimo tabellare (Allegato n. 1, CCNL 07/03/2024). EDR = 10.33 EUR (Accordo 31/07/1992, all levels). IPO = Indennità di posizione organizzativa, level-specific time series per tranche (levels B1, C1, D1, E1, E2). IND_FUNZIONE = 25.82 EUR (level A only, Indennità di funzione, art. 47 CCNL 2017). Back-calculation: D1 total 01/01/2026 = 2041.99+123.67+10.33 = 2175.99; kitech confirms 2176.00 (rounding). B1 total = 2494.04+222.01+10.33 = 2726.38; kitech confirms 2726.38. A total = 2937.60+25.82+10.33 = 2973.75; kitech confirms 2973.75.
    
    DECORRENZA: economic decorrenza 01/07/2023; first tranche 01/03/2024. Arretrati for 2023-07-01 to 2024-03-01 paid as lump sum. Series starts at 2024-03-01. SIMPLIFICATION: pre-tranche salary not modeled.
    
    HOURLY DIVISOR: contract states 'quota oraria = retribuzione mensile / 173' (Allegato n. 1). Cross-check: 40h/week × 52 / 12 = 173.3; divisor 173 verified. Source: primary CCNL PDF filctemcgil.it.
    
    IPO CROSS-CHECK: MySolution 2017 IPO at 01/05/2019: B1=182.63, C1=91.62, D1=103.98, E1=128.23, E2=73.02. Allegato n.1 pre-renewal (30/06/2023): B1=192.63, C1=96.62, D1=108.98, E1=135.73, E2=75.52. Deltas B1+10.00, C1+5.00, D1+5.00, E1+7.50, E2+2.50 — all clean round figures consistent with 2019-2023 renewal cycle.
    
    APPRENTICESHIP: under_classification per MySolution sintesi 2017 p. 5 (Allegato apprendistato). 6 tracks by destination level, all with levels_below 2 → 1 → 0. D1 period-2: source table prints E2, but 10 of 11 destination tracks are monotone 2->1->0; E2 (order 3) below D1 (order 6) would cut pay mid-track, so D2 (order 5, exactly 1 below D1) is the only consistent reading. Max 36 months per D.Lgs. 167/2011 as amended 26/04/2012 (footnote in source).
    
    SICKNESS: seniority bands of art. 60 modelled as a cumulation (8, 10, 12 months of comporto within 36 months; 3, 4, 5 months in full and the rest at half, on the net pay); restarts after 4 months without sickness, from the 16th day of a hospital stay (within the episode) and 12 months after the end of the full pay; comporto 2, 3, 4 months longer for an invalidating disease; hospital stays over 5 days (60 at most) and periodic checks of an oncological illness left out of the comporto.
    
    SENIORITY: biennial (cadence_months=24), maximum 5 increments, amounts per level from Art. 48 of the CCNL testo definitivo 21/01/2021 (CNEL B101, physical p. 67), which the 2024 renewal leaves unchanged.
    

## Raw data

The contract file this page is generated from: [`agreement/concia-unic.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/concia-unic.json).

## Usage example

```python
--8<-- "docs/examples/agreement/concia-unic/example.py"
```
