# CCNL Telecomunicazioni — Assotelecomunicazioni (Asstel)

| | |
|---|---|
| **CNEL code** | `K411` |
| **Sector** | telecomunicazioni |
| **Family** | `ict-telecomunicazioni` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-11-11 |
| **Workers (est.)** | ~110k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Assotelecomunicazioni-Asstel
    - SLC-CGIL
    - Fistel-CISL
    - Uilcom-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | inps_employer, seniority |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 2 verified / 44 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-11-11 |
| **Last review** | 2026-10-31 |
| **Latest salary tranche** | 2028-12-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 42 - 13ª mensilità (p. 83): "Nel caso di inizio o di cessazione del rapporto di lavoro durante il corso dell'anno, il lavoratore non in prova ha diritto a tanti dodicesimi dell'ammontare della tredicesima mensilità quanti sono i mesi di anzianità di servizio presso l’azienda. La frazione di mese superiore a quindici giorni va considerata a questi effetti come mese intero.". Match: more_than 15. |
| 2026-10-31 | claude-opus-5-5 (ai) | The comporto and the sick pay of the CCNL counted over several illnesses (work_rules.sickness_rules), read on the signed text. | corrected | Art. 36 (pp. 73-75) of the CCNL 12.11.2020: 180 days at the whole pay and 185 at 50%, summed over the three years before each new episode. The file kept 180 days of one illness: corrected to a cumulation over three years. A 2025 carenza reduction by event was seen only in a non-primary transcription and is not stored. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `D1` | D1 — Quadri, maximum managerial and professional responsibility | € 2,814.86 | 2028-12-01 |
| `C4` | C4 — Grade 7, managerial functions of high organisational complexity | € 2,814.86 | 2028-12-01 |
| `C3` | C3 — Grade 6, high and consolidated professional and managerial expertise | € 2,559.28 | 2028-12-01 |
| `C2` | C2 — Grade 5S, specialist profiles with a high degree of specialisation | € 2,263.82 | 2028-12-01 |
| `C1` | C1 — Grade 5, advanced professional and managerial capabilities with high-level knowledge | € 2,186.73 | 2028-12-01 |
| `B2` | B2 — Grade 4, qualified specialist knowledge | € 2,020.45 | 2028-12-01 |
| `B1` | B1 — Grade 3, theoretical and practical knowledge of medium complexity | € 1,862.81 | 2028-12-01 |
| `A2` | A2 — Grade 2, basic professional knowledge | € 1,701.25 | 2028-12-01 |
| `A1` | A1 — Grade 1, predominantly manual tasks requiring no professional knowledge | € 1,518.96 | 2028-12-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 7 increments

| Level | Increment (monthly) |
|---|---:|
| `A1` | € 21.54 |
| `A2` | € 21.54 |
| `B1` | € 23.24 |
| `B2` | € 24.38 |
| `C1` | € 25.56 |
| `C2` | € 25.56 |
| `C3` | € 28.10 |
| `C4` | € 30.73 |
| `D1` | € 30.73 |

## Apprenticeship

**professionalizzante** (type: `under_classification`)  
Destination levels: `B1`, `B2`, `C1`, `C2`, `C3`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "telecomunicazioni-asstel/seniority_adjacent_level_amounts · seniority · impact unknown · open"
    SENIORITY biennale (24 months), max 7 scatti, amounts from Art. 41 CCNL 12/11/2020: 6 of 9 levels confirmed (A2, B1, B2, C1, C3, C4); A1=A2 (21.54), C2=C1 (25.56) and D1=C4 (30.73) by adjacent-level approximation (1° livello, 5°S and Quadri absent from the Art. 41 table).

    **Applies when:** `seniority` applies; level in A1, C2, D1.

    **Remediation:** Source the Art. 41 amounts of 1° livello, 5°S and Quadri and replace the adjacent-level values.

!!! warning "telecomunicazioni-asstel/industria_tax_sector_unverified · inps_employer · impact unknown · open"
    INPS: reuses the industria contribution table. SIMPLIFICATION: tax_sector='industria' is a modelling choice. Supporting facts: (a) Asstel is a Confindustria federation; (b) large TLC operators (Telecom Italia, etc.) have historically accessed CIGO/CIGS; (c) the CCNL itself (Art. 58 rinnovo 11/11/2025) describes the Fondo di Solidarietà Bilaterale TLC as 'in aggiunta' (supplementary), not as a CIG substitute. Counterargument: D.Lgs. 148/2015 Art. 26 bilateral funds are formally for sectors without CIG coverage; this was not verified against an INPS circular. The employer rate of the terziario table is about 1.2 points lower than the industria one in each headcount band of the bundle. The Fondo di Solidarietà Bilaterale (0.20% datore + 0.10% lavoratore) is NOT modelled in either case (review of 2026-10-30).

    **Applies when:** `inps_employer` applies.

    **Remediation:** Verify the INPS classification of TLC employers and model the Fondo di Solidarieta Bilaterale TLC.

!!! warning "telecomunicazioni-asstel/apprentice_seniority · seniority · impact unknown · open"
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
    APPRENTICESHIP professionalizzante, under_classification (Art. 20 CCNL 12/11/2020): 36 months, first 18 months two levels below the destination, next 18 months one level below, then the destination. Track covers destinations B1, B2, C1, C2, C3; A1/A2 (no level two steps below), C4 and D1 (funzioni direttive/Quadri) are not destinations.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.asstel.it/lavoro-e-relazioni-industriali/ccnl-tlc/ | altro | 2025-11-11 | [↗](https://www.asstel.it/lavoro-e-relazioni-industriali/ccnl-tlc/) |
| https://www.asstel.it/wp-content/uploads/2023/05/CCNL-TLC-Slc-Cgil-Fistel-Cisl-Uilcom-Uil-12-novembre-2020-nuovo.pdf | altro | 2020-11-12 | [↗](https://www.asstel.it/wp-content/uploads/2023/05/CCNL-TLC-Slc-Cgil-Fistel-Cisl-Uilcom-Uil-12-novembre-2020-nuovo.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (TEM = minimo tabellare + ex-contingenza + EDR + Elemento Retributivo di Settore), confirmed by footnote in rinnovo PDF (11/11/2025), tabelle retributive p.99-100. Back-calculation: C1(01/01/2026)=1988.73/173=11.50 EUR/h; A1=1399.68/173=8.09 EUR/h; C3=2317.44/173=13.39 EUR/h — all consistent with divisor 173. base_salary = TEM; fixed_allowances=[] for levels A1-C3.
    
    FIXED ALLOWANCES: C4 (7° livello) carries Elemento Retributivo di Settore EUR 59.39/month separate from TEM (rinnovo PDF p.97). D1 (Quadri) carries Indennità di Funzione EUR 98.13/month inclusive of the 59.39 ERS (rinnovo PDF + CCNL 12/11/2020 sezione Quadri). Both use TEM parametro=228, identical base_salary. The validator checks base_salary only so the equal values are valid.
    
    SALARY TRANCHES: four tranches from rinnovo 11/11/2025 — 01/01/2026, 01/12/2026, 01/07/2027, 01/12/2028. Pre-rinnovo salary tables (CCNL 12/11/2020) not modelled; engine scope starts from first 2026 tranche.
    
    NEW CLASSIFICATION SYSTEM: rinnovo 11/11/2025 Art. 23 introduces Professional Areas A-D (effective 01/07/2026). Old→new mapping: 1°→A1, 2°→A2, 3°→B1, 4°→B2, 5°→C1, 5°S→C2, 6°→C3, 7°→C4, Q→D1. TEM values are identical regardless of which code system is in use; engine uses new codes throughout.
    
    HOURLY DIVISOR: 173 (Art. 40, CCNL 12/11/2020: 'dividendo per 173'; 40h/week standard).
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: Art. 42, CCNL 12/11/2020. Quattordicesima not provided by this CCNL.
    

## Raw data

The contract file this page is generated from: [`agreement/telecomunicazioni-asstel.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/telecomunicazioni-asstel.json).

## Usage example

```python
--8<-- "docs/examples/agreement/telecomunicazioni-asstel/example.py"
```
