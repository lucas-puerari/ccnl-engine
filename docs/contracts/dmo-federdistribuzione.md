# Distribuzione Moderna Organizzata — Federdistribuzione

| | |
|---|---|
| **CNEL code** | `H008` |
| **Sector** | terziario |
| **Family** | `commercio` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-09-29 |
| **Workers (est.)** | ~460k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - Federdistribuzione
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
| **Limits of this contract** | base_salary, bilateral_funds, overtime, seniority, sickness, territorial_supplement |

10 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 88 verified / 3 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-09-29 |
| **Last review** | 2026-11-01 |
| **Latest salary tranche** | 2027-02-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule read again in the Testo Unico of 29 September 2025 (Federdistribuzione, 99 pages), for the production tier. | corrected | 90 records verified; the work rules cited an aggregator and now cite the Testo Unico. The 2025/01 URL of the sources returns 404: replaced by the 2026/04 one.<br>Night overtime 50%, not 30% (Art. 132 c. 3); added the 20% beyond the 48th weekly hour (c. 1). The premiums are on the normale retribuzione of Art. 189 (hourly_base_method gross_incl_allowances, which documents the rule: the caller states OvertimeEvent.hourly_rate).<br>Sickness: 75% for days 4-20 and 100% from day 21 of the net daily pay, carenza by event, apprentices excluded (Art. 170), not a flat 100%.<br>Seniority amounts in force since 1990 (Art. 188): the gap before 23 April 2024 removed.<br>Terzo elemento 2.07 due only without a provincial element (Art. 199): now gated.<br>Apprenticeship: second half of level VI at VII (Art. 46 c. 3); the 36-month end of levels II-V stated.<br>Added the payment days of the tredicesima and quattordicesima and Fon.Te. (Art. 95, 1.55% and 0.55%, apprentices 1.05%).<br>Night holiday overtime 0.50 stays derived: no clause sets it, Art. 132 c. 5 forbids cumulation.<br>No renewal after the Testo Unico through October 2026. |
| 2026-10-13 | claude-opus-5-5 (ai) | Scope of the declared limitations. | corrected | sickness_net_basis is recorded on every run with a sickness event (trigger run), not only documented. |
| 2026-10-17 | claude-opus-5-5 (ai) | The paga base, contingenza, terzo elemento, indennità di funzione and scatti of every level against the Testo Unico of 29 September 2025, and a year and a termination of a level IV worker against a hand oracle. | confirmed | Allegato 11 (PDF pp. 97-99): 47 of the 48 paghe base of the file are printed in the tables; the IV of 1 April 2023 prints 1112,46 in the paga base column, but its total 1646,68 less the contingenza 524,22 gives the 1122,46 of the file, which the CCNL Terziario Confesercenti also reaches (total 1646,68). The paga base column has a misprint; the file keeps 1122,46.<br>Contingenza + EDR of every level, the terzo elemento of 2,07 (Art. 195), the indennità di funzione of the Quadri (260,76) and of the VII (5,16) and the scatti (Quadri 25,46 to VII 19,47): match.<br>Art. 204 and 205 (PDF p. 59): tredicesima at Christmas, quattordicesima of the pay in force on 30 June paid on 1 July, in twelfths of the twelve months before. Match.<br>Hand oracle (tests/knowledge/ccnl_engine/period/sector, scenarios dmo-year and dmo-june): a level IV impiegato hired on 1 January 2026 by an employer with 50 employees where a provincial element is in force; every payment and the year (gross, contributions, tax, net, TFR, employer cost) match the engine to the cent. The CCNL now covers every total of the definition of done. |
| 2026-10-31 | claude-opus-5-5 (ai) | The basis of the indemnity for the leave not taken at the end of the employment, read in the Testo Unico of 29 September 2025 (Artt. 79, 141, 142, 191, 193, 194). | corrected | Art. 142 - Ferie, Chiarimento a verbale (p. 45): the indemnity of the ferie at the end of the employment is the retribuzione mensile di fatto divided by twenty-six: work_rules.leave_rules.termination; the accrual of the leave is not modelled, so the basis is not used yet. |
| 2026-10-31 | claude-opus-5-5 (ai) | The accrual of the ferie, the ex festività and the ROL read in the Testo Unico of 29 September 2025 (Artt. 141, 142, 145). | corrected | Art. 145 c.1 (p. 45): twelfths of the 26 days of Art. 142 per month of effective service, no month-fraction rule: work_rules.leave_rules.ferie_accrual.<br>Art. 141 cc.1, 3, 4, 7 (pp. 44-45): 32 hours of ex festività (4 festività in groups of 8 hours), 56 hours of permits up to 15 employees and 72 above, by whole months: work_rules.leave_rules.permits.<br>Art. 141 c.8 (p. 45): the 56/72 hours of a hire after 1 March 2011 at 0%, 50% after two years, 100% after four: permits[rol].ramp. |
| 2026-11-01 | claude-opus-5-5 (ai) | The indennità di cassa e maneggio denaro of Art. 202 (p. 59). | corrected | Art. 202 (p. 59): 5% of the paga base nazionale conglobata to the staff normally at the till with full responsibility for it: levels[*].fixed_allowances[IND_CASSA], role cassiere, one value per period of the base_salary. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Managers (Quadri) | € 2,313.29 | 2027-02-01 |
| `I` | First level | € 2,083.84 | 2027-02-01 |
| `II` | Second level | € 1,802.50 | 2027-02-01 |
| `III` | Third level | € 1,540.66 | 2027-02-01 |
| `IV` | Fourth level | € 1,332.46 | 2027-02-01 |
| `V` | Fifth level | € 1,203.83 | 2027-02-01 |
| `VI` | Sixth level | € 1,080.77 | 2027-02-01 |
| `VII` | Seventh level | € 925.31 | 2027-02-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 25.46 |
| `I` | € 24.84 |
| `II` | € 22.83 |
| `III` | € 21.95 |
| `IV` | € 20.66 |
| `V` | € 20.30 |
| `VI` | € 19.73 |
| `VII` | € 19.47 |

## Apprenticeship

**standard_II_V** (type: `under_classification`)  
Destination levels: `II`, `III`, `IV`, `V`

**standard_VI** (type: `under_classification`)  
Destination levels: `VI`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "dmo-federdistribuzione/provincial_elements_missing · territorial_supplement · impact yes · open"
    Terzo elemento nazionale (Art. 199, PDF p. 59): EUR 2.07 a month only for the workers of firms in provinces with no provincial terzo elemento in force (Art. 198, frozen since 1973): gated by EmployerProfile.provincial_pay_element. The provincial amounts themselves are set by provincial agreements outside the Testo Unico and are not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the provincial terzi elementi of Art. 198 as a territorial supplement.

!!! warning "dmo-federdistribuzione/long_apprenticeship_profiles · base_salary · impact yes · open"
    APPRENTICESHIP: under-classification of Art. 46 and durations of Art. 57 (Testo Unico 29/09/2025, PDF pp. 24-25). Destinations II-VI (Art. 55: I and Q excluded). Levels II-V: 36 months, two levels below in the first half, one below in the second. Level VI: 24 months at level VII, the first half by Art. 46 c. 5 and the second by c. 3 (one level below), as the Commercio file. The 42 and 48 month profiles of Art. 61 are not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the 42 and 48 month tracks of Art. 61, selected by Apprentice.track.

!!! warning "dmo-federdistribuzione/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "dmo-federdistribuzione/sickness_net_basis · sickness · impact yes · open"
    SICKNESS (Art. 170): the CCNL integrates up to a share of the net daily pay ('retribuzione giornaliera netta') without saying how the net pay is computed. The engine grosses up the INPS indemnity by the worker's INPS rate and tops it up to the measure of the gross daily quota, as for the Commercio file. The exempt events of c. 3 are an input (SicknessEpisode.short_absence_exempt, read with carenza_by_event) (review of 2026-10-30).

    **Applies when:** `sickness` applies.

    **Remediation:** Model the net daily pay of Art. 170.

!!! note "dmo-federdistribuzione/cashier_allowance · base_salary · impact yes · resolved"
    Art. 202: the indennità di cassa of 5%.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Resolved: every level carries IND_CASSA, 5% of its paga base nazionale conglobata, for the role cassiere of Employment.roles.

!!! warning "dmo-federdistribuzione/ordinary_hours_premiums · overtime · impact yes · open"
    Art. 134, 136 and 139: the premiums on ordinary night (15%), Sunday (30%) and weekly rest day (30%) work.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the premiums on ordinary hours.

!!! warning "dmo-federdistribuzione/sales_operators · base_salary · impact yes · open"
    The pay rows of the operatori di vendita.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the operatori di vendita levels.

!!! warning "dmo-federdistribuzione/employment_support_contract · base_salary · impact yes · open"
    Art. 70: the sostegno all'occupazione contract.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the pay of the Art. 70 contract.

!!! warning "dmo-federdistribuzione/commission_guarantee · base_salary · impact yes · open"
    Art. 201: the guarantee of the commission-paid staff. The una tantum of Art. 197 (July 2024 and 2025) is historic and outside the TFR base (c. 6).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the guarantee of commission-paid staff.

!!! warning "dmo-federdistribuzione/health_and_bilateral_funds · bilateral_funds · impact yes · open"
    HEALTH AND BILATERAL FUNDS: E.Bi.Di.M. (Art. 18), Fondo EST (Art. 19) and, for the quadri, Cassa QuAS (Art. 20) are owed for every worker, with their worker shares; an employer that does not pay them owes the worker instead the EDR of 0.30% of paga base and contingenza (14 months), EUR 16.00 x 14 and EUR 37.00 x 14. Neither is modelled: the net pay and the employer cost are short of them.

    **Applies when:** `bilateral_funds` applies.

    **Remediation:** Model the contributions per worker, with a fact for an employer that pays the worker the alternative element instead, then remove this note.

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
| https://www.federdistribuzione.it/app/uploads/2026/04/Testo-Unico-CCNL-DMO.pdf | altro | 2025-09-29 | [↗](https://www.federdistribuzione.it/app/uploads/2026/04/Testo-Unico-CCNL-DMO.pdf) |

??? note "Coverage notes"
    Salary tables: 6 tranches from 01/04/2023 through 01/02/2027, Allegato 11 (PDF p. 98) of the Testo Unico CCNL DMO of 29/09/2025 (Federdistribuzione), Art. 196 for the tranche dates. Level IV on 01/04/2023 is printed 1112,46 in the PDF itself: the total 1646,68 less the contingenza 524,22, and 1192,46 less the 70,00 of Art. 196, give 1122.46, the value kept.
    
    Split model confirmed: total / 168 at L1 = 14.905, L4 = 10.605, L7 = 8.309 — all non-integer. Source: Art. 194 (divisore 168 for 40h/week), Allegato 11.
    
    Contingenza: frozen values from Allegato 11 column. EDR (lire 20,000 = 10.33 EUR) conglobated into contingenza on 01/01/1995 per Art. 190 — no separate EDR allowance modelled.
    
    Indennità di funzione Quadri (Art. 113): EUR 260.76/month for 14 months (cumulative increments: 51.65+77.47+51.65+70.00+10.00=260.77; 0.01 rounding from lire). Allegato 11 shows 260.76.
    
    Altri elementi of level VII: EUR 5.16/month (lire 10,000), column 'altri elementi' of Allegato 11 (PDF p. 98); the Testo Unico names no article for it.
    
    Seniority: 10 scatti triennali (Art. 188), amounts of the Art. 188 table, in force since 1 January 1990; paid from the month after the triennium (c. 4).
    
    Additional months: 14 (tredicesima Art. 204 + quattordicesima Art. 205).
    

## Raw data

The contract file this page is generated from: [`agreement/dmo-federdistribuzione.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/dmo-federdistribuzione.json).

## Usage example

```python
--8<-- "docs/examples/agreement/dmo-federdistribuzione/example.py"
```
