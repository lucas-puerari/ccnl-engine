# CCNL Servizi di Pulizia e Servizi Integrati/Multiservizi (ANIP-Confindustria)

| | |
|---|---|
| **CNEL code** | `K511` |
| **Sector** | multiservizi |
| **Family** | `pulizia-multiservizi` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2021-06-08 |
| **Workers (est.)** | ~580k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANIP-Confindustria
    - Legacoop Lavoro e Servizi
    - Confcooperative Lavoro e Servizi
    - AGCI Servizi
    - Unionservizi Confapi
    - Filcams-CGIL
    - Fisascat-CISL
    - Uiltrasporti-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, overtime, pension_fund_contribution, seniority, sickness |

10 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 79 verified / 15 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2021-06-08 |
| **Last review** | 2026-11-10 |
| **Latest salary tranche** | 2025-07-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-13 | claude-opus-5-5 (ai) | Signatories of the renewals behind the salary periods from July 2025. | flagged | The renewal of 13 June 2025 (CNEL K511, deposits 234754 and 234752) is not signed by ANIP; the file pays its minima from July 2025. Declared as the limitation anip_unsigned_renewal; values left unchanged pending an ANIP amount. |
| 2026-10-13 | claude-opus-5-5 (ai) | Limited scope, tier unchanged: the rules that do not depend on the missing ANIP amounts, read in the CNEL K511 deposits 105782 (2011 text) and 139292 (2021 renewal); the salary periods from July 2025 stay as they are. | corrected | 66 records verified: the 2021-2024 tabellare, contingenza and EDR of levels 1-7 and Q, the quadri allowance, the levels 1, 2par115, 4par125, 7 and Q, the divisor 173, the 14 monthly payments and their accrual rule, the overtime rates and 22 days of leave.<br>Added the payment days of the tredicesima (20 December) and quattordicesima (15 July, window July to June), arts. 20-21.<br>The 2par115 and 4par125 tabellare is computed (April 2013 amount plus the parametric increments): derived, descriptions corrected to the notes a verbale of art. 10.<br>Closed cigs_threshold_16_to_50: terziario.json already charges the CIGS above 15 employees (D.Lgs. 148/2015 arts. 20 and 23).<br>Closed apprentice_seniority: apprentices are paid tabellare, contingenza and EDR only (art. 12), apprentice_amount 0 (derived).<br>Corrected the notes on the July 2025 values (the 2021 fifth tranche is the operative ANIP amount), on scatti recomputed at every tranche, on the apprenticeship durations, on the 2025 signatories and on the worker estimate.<br>Separate limitations remain for seniority maturation and worker category, sickness basis and bands, variable time premiums, duty allowances and EDAR, pension historical base, and apprenticeship destinations. The ordinary five-day daily divisor is /22, with /26 on a six-day week.<br>hourly_base_method gross_incl_allowances: the art. 38 premiums are on tabellare plus contingenza.<br>Left derived: the periods from July 2025 (renewal not signed by ANIP, re-cited to CNEL 234752), the seniority block, the contingenza of the parametric positions, levels 2 to 6 (mixed categories), absence and sickness rules.<br>The aggregator sources (oristano summary, redigo, kitech, ccnlportatili) are replaced by the CNEL deposits. |
| 2026-11-05 | claude-opus-5-5 (ai) | The ferie days of the six-day week, Art. 42 Ferie (PDF p. 61), read by a separate research session and checked again on the text layer. | corrected | Art. 42 Ferie: 22 working days in the five-day week, 26 in the six-day week: work_rules.leave_rules.week_days_annual_days 6/26, read when Employment.full_time_week_days is 6. |
| 2026-11-05 | claude-opus-5-5 (ai) | Ferie accrual, permits and their settlement: arts. 19 (PDF p. 40), 41 and 42 (pp. 60-61) of the 2011 definitive text, read by a separate research session and checked again on the text layer; the 2021 renewal read for amendments. | corrected | Art. 42: twelfths with the month over 15 days, 40 hours of reduced time a year: work_rules.leave_rules.ferie_accrual and permits.<br>Art. 41: the ex festività are compensatory permits for the days worked, not a yearly bank.<br>The 2025 renewal (72 hours according to the union summary) was not read in a primary text. |
| 2026-11-05 | claude-opus-5-5 (ai) | Art. 66 (PDF p. 29) of the ipotesi of 8 June 2021, OCR of the scan. | corrected | ONBSI was not modelled: the contractual funds held no reduced worker share; the model now has reduced_employee. |
| 2026-11-07 | claude-opus-5-5 (ai) | Values a primary-text verification found different from the printed tables (text layer). | corrected | 31 values corrected to the amounts printed on the cited pages. |
| 2026-11-08 | gpt-6-sol (ai) | CCNL top-ups of maternity and work injury, read from the signed text by a separate model session; every quote found on the PDF text layer. | confirmed | Added work_rules.insured_absence.maternity.<br>Added work_rules.insured_absence.injury. |
| 2026-11-08 | gpt-6-sol (ai) | Open limitations claimed to be no longer gaps: one session read the clauses and the data, a second independent session checked the claim. | confirmed | health_and_bilateral_funds: For modeled runs from July 2021, parameters.health_funds already contains ASIM employer EUR 4/month through 28 weekly hours and EUR 6 above, permanent workers only, and ONBSI EUR 0.25 per party under 20 weekly hours and EUR 0.50 per party otherwise, on ordinary months only (12, n |
| 2026-11-08 | claude-opus-5-5 (ai) | Cached CNEL 139292 PDF page 34, July 2025 tabellare for all eight printed levels; two parametric positions derived; later unsigned salary periods excluded. | corrected | Verified all eight printed monthly minima against PDF page 34; derived two unprinted parametric positions from prior signed periods and signed tranche increments.<br>Excluded all unsigned salary periods from May 2026 onward; the signed July 2025 tranche remains in force until further ANIP evidence. |
| 2026-11-09 | claude-opus-5-5 (ai) | Art. 19 daily pay and art. 30 ordinary working week, cached signed CNEL 105782; separate limitations for the remaining clauses in CNEL 105782 and 139292. | corrected | Art. 19 prints 22 for a five-day week and 26 for six days; art. 30 makes five days the normal distribution. The historical pension base and the missing signed 2012 apprenticeship accord prevent assuming current pay bases or durations. |
| 2026-11-10 | claude-opus-5-5 (ai) | CNEL 139292 art. 33 pp. 16-17 and CNEL 105782 art. 18 p. 40, art. 38 p. 57; supplementary and ordinary holiday/night supplements and percentage bases. | corrected | The 2021 ANIP-signed part-time amendment governs supplementary hours in 2026; elastic hours remain a limitation.<br>The 2011 art. 38 continues to set ordinary holiday and night rates, on base pay, with non-cumulation not automatically enforced. |
| 2026-11-10 | claude-opus-5-5 (ai) | Category-specific seniority amounts and remaining limitations, CNEL 105782 art. 22 pp. 41-42, 90. | corrected | The printed sector amounts include levels 5 and 6. Impiegati scatti are priced at maturation and kept after promotion; the automatic freeze and ceiling remain unsupported. |
| 2026-11-10 | claude-opus-5-5 (ai) | Art. 54 pension rates, frozen per-level bases and fund eligibility in CNEL 105782 pp. 69-70, 90; membership routing remains limited. | corrected | Verified all ten configured level bases against the page 90 table and the 1% shares and twelve payments against pp. 69-70.<br>The printed Q and 7 illustrative 1% amounts (12.28) differ from 1% of the printed 1222.75 base (12.23); applied the stated percentage and base, not the inconsistent illustrative amount.<br>Association-dependent fund choice and six-month calendar-year fixed-term eligibility remain open. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadri with high-responsibility managerial duties | € 1,572.70 | 2025-07-01 |
| `7` | Employees with managerial functions | € 1,436.88 | 2025-07-01 |
| `6` | Workers with specialist duties / Senior white-collar employees | € 1,243.86 | 2025-07-01 |
| `5` | Expert workers / White-collar employees | € 1,000.81 | 2025-07-01 |
| `4` | Specialist workers / Junior clerical employees | € 915.03 | 2025-07-01 |
| `4par125` | Skilled workers on painting booths and lines in service on 1 June 2001: level IV at parameter 125, closed group (nota a verbale) | € 893.60 | 2025-07-01 |
| `3` | Skilled workers / Clerical employees | € 843.55 | 2025-07-01 |
| `2par115` | Common workers on auxiliary support activities in school and healthcare settings: level 2 at parameter 115 (nota a verbale, profile 1.9) | € 822.11 | 2025-07-01 |
| `2` | General workers / Clerical employees (first 18 months) | € 779.21 | 2025-07-01 |
| `1` | General labourers | € 714.87 | 2025-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `5` | € 80.03 |
| `6` | € 95.22 |
| `7` | € 107.28 |
| `Q` | € 115.77 |

## Apprenticeship

**destinazione_5** (type: `under_classification`)  
Destination levels: `5`

**destinazione_4** (type: `under_classification`)  
Destination levels: `4`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "multiservizi-anip/anip_unsigned_renewal · base_salary · impact yes · open"
    LATER UNSIGNED TRANCHES: the May 2026 and later minima of the renewal of 13 June 2025 (CNEL K511, deposits 234754 and 234752) were not signed by ANIP and are excluded. The signed July 2025 fifth tranche of the 2021 renewal (CNEL 139292 p. 34) is applied; no subsequent ANIP minimum or actual IPCA adjustment has been verified.

    **Applies when:** `base_salary` applies; from 2026-05-01.

    **Remediation:** Source an ANIP-signed later minimum or verified IPCA adjustment before adding subsequent tranches.

!!! warning "multiservizi-anip/multiservizi_sickness_by_category_and_basis · sickness · impact yes · open"
    SICKNESS (CNEL 139292 art. 51, pp. 22-24): operai receive a top-up to 100% of net global pay on days 1-180, then 50% of gross global pay on days 181-270. Impiegati receive 100% of stipendio plus contingenza for five months and 50% for seven; both are subject to a twelve-month comporto in a rolling 36-month window. The existing rule ends pay at day 180, uses gross throughout and does not route by category; the rolling comporto alone is represented.

    **Applies when:** `sickness` applies.

    **Remediation:** Apply separate category rules and day-dependent net/gross bases to operai; apply the separate stipendio-plus-contingenza impiegati bands.

!!! warning "multiservizi-anip/multiservizi_variable_time_premiums · overtime · impact yes · open"
    OVERTIME AND NIGHT WORK (CNEL 105782 art. 38, p. 57): ordinary overtime hours use global pay, whereas percentage supplements use base pay (tabellare and contingenza). Holiday work attracts 50%; ordinary night work attracts 20% in rotating shifts or 30% otherwise. The four overtime bands, the ordinary holiday band and the two night bands use the printed rates, with a separate tabellare-plus-contingenza premium base. The engine cannot automatically enforce the non-cumulation of simultaneous holiday and night premiums or the incidence of continuous night supplements on deferred pay.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Do not stack simultaneous holiday and night premiums; account for continuous night premiums in deferred pay where applicable.

!!! warning "multiservizi-anip/multiservizi_part_time_supplements · overtime · impact yes · open"
    PART-TIME SUPPLEMENTS (CNEL 139292 art. 33): supplementary hours and elastic clauses have distinct rates and eligibility. OT_SUPPLEMENTARE covers additional hours at ordinary global hourly pay plus 28% of tabellare and contingenza. The engine does not defer the 28% to the following month or include its incidence in indirect and deferred pay including TFR; it does not route the distinct elastic-clause hours, enforce part-time eligibility or the full-time ceiling.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Route elastic clauses separately (10% on global pay for shifted hours, plus 1.5% for additional hours); enforce part-time eligibility and the full-time ceiling, next-month settlement and incidence on deferred pay including TFR.

!!! warning "multiservizi-anip/multiservizi_duty_allowances_and_edar · base_salary · impact yes · open"
    VARIABLE ALLOWANCES (CNEL 105782 art. 24): hardship, cash-handling and collection duties require separate daily, hourly or percentage bases and qualifying work events. The retained personal EDAR is absorbed at the next qualifying seniority increment (art. 22 pp. 41-42). No amounts for work not evidenced by the source are inferred.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model each evidenced allowance on its own qualifying duty and base; track the individual EDAR and absorption at the first subsequent increment.

!!! warning "multiservizi-anip/multiservizi_apprenticeship_destinations · base_salary · impact yes · open"
    APPRENTICESHIP (19 July 2012 accord): destination 5 is configured for 30 months rather than 36; destinations 2, 3, 6 and 7 are not configured. The cited duration schedule has not been verified on the cached signed 2011 or 2021 PDF and must not be inferred from a third-party copy.

    **Applies when:** `base_salary` applies.

    **Remediation:** Obtain and verify the signed 2012 apprenticeship accord before changing durations or adding destinations.

!!! warning "multiservizi-anip/renewal_not_signed_by_anip · base_salary · impact yes · open"
    SIGNATORIES: ANIP is not among the original signatories of the 13 June 2025 renewal and the 6 August 2025 tables (CNEL 234754, 234752); a later ANIP accession or a separate ANIP agreement was not found but is not excluded. From July 2025 the file applies the ANIP-signed fifth tranche of the 8 June 2021 renewal (CNEL 139292 p. 34); with an accession the 2025 renewal minima (level 2 819.21 from July 2025) would apply instead.

    **Applies when:** `base_salary` applies; from 2025-07-01.

    **Remediation:** Source an ANIP accession or an ANIP-signed later agreement before adding later minima.

!!! warning "multiservizi-anip/anip_ipca_consuntivo · base_salary · impact unknown · open"
    IPCA CONSUNTIVO: CNEL 139292 p. 34 makes the July 2025 table provisional, subject to the 2021-2024 IPCA consuntivo of June 2025 (and pp. 35-36 provide the 2025-2026 IPCA mechanism). No consuntivo adjustment has been found, so the printed provisional amounts are paid from July 2025.

    **Applies when:** `base_salary` applies; from 2025-07-01.

    **Remediation:** Source the IPCA consuntivo of June 2025 and any later IPCA adjustment for ANIP and adjust the July 2025 minima.

!!! warning "multiservizi-anip/multiservizi_seniority_maturation · seniority · impact yes · open"
    SENIORITY (CNEL 105782 art. 22, pp. 41-42, 90): Category-specific amounts now pay operai at levels 1-6 after four years (including levels 5 and 6), with at most one quota; levels 5-7 and Q pay impiegati up to eight biennial scatti. No current series for impiegati at levels 2-4 is verified. Without an EarnedIncrements worker fact, matured scatti are still repriced at the run date, including after promotion; the 50% ceiling of tabellare plus EUR 279.60 is not enforced. The worker must supply recognised sector service across contract changes and the correct category at mixed levels.

    **Applies when:** `seniority` applies.

    **Remediation:** Source the current impiegati scatto amounts for levels 2-4; supply earned amounts and recognised sector service from worker records, and implement automatic maturation-date pricing and the 50% ceiling.

!!! warning "multiservizi-anip/multiservizi_pension_membership_eligibility · pension_fund_contribution · impact yes · open"
    COMPLEMENTARY PENSION (CNEL 105782 art. 54, pp. 69-70): The frozen 1 January 2001 tabellare and contingenza bases, 1% employer and member shares and twelve monthly payments are modelled for enrolled workers. Fund eligibility still depends on the employer association (Previambiente for FISE, Fondapi for CONFAPI, Cooperlavoro for cooperatives, with a choice for non-affiliated employers); fixed-term membership requires six months of work within the calendar year. These eligibility facts are not established by the enrolment alone. ASIM and ONBSI are addressed by the separate health_and_bilateral_funds limitation.

    **Applies when:** `pension_fund_contribution` applies.

    **Remediation:** Verify the employer association and accumulated calendar-year fixed-term work before accepting the caller-selected fund and enrolment. No eligibility is inferred from the level or the fund code.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! note "sickness_inps_daily_base · sickness · impact unknown · resolved"
    The INPS share of a sick day is computed on the INPS daily base of the episode, on the days INPS pays (the weekdays of an operaio, every day but the national holidays on a Sunday of an impiegato, point 7.3 of INPS circ. 134368/1981): the retribuzione media globale giornaliera of the month before the illness (INPS circ. 134368/1981 point 11; circ. 55/2024 Allegato 1), whole or partial month, impiegato or operaio, or for the lavoratori dello spettacolo the average pay of the last 40 daily contributions, capped for a fixed-term worker (INPS circ. 132/2021 par. 2.4). The base is a fact of the payroll history the episode states (SicknessEpisode.inps_base).

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Resolved: the INPS share is computed on the base of every regime of the bundle; an episode that states no base the engine can read has the missing_fact issue sickness_inps_base_unknown (fact inps_base), which blocks the run. Tests: tests/mutation/ccnl_engine/sickness/base/test_rules_wiring.py, tests/mutation/ccnl_engine/sickness/base/test_rules.py.

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
| https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/139292 | cnel | 2021-06-08 | [↗](https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/139292) |
| https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/105782 | cnel | 2011-05-31 | [↗](https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/105782) |
| https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/234754 | cnel | 2025-06-13 | [↗](https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/234754) |
| https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/234752 | cnel | 2025-08-06 | [↗](https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/234752) |

??? note "Coverage notes"
    Salary model: SPLIT. The tabellare is a time series; contingenza and EDR are frozen fixed_allowances. Tranches of July 2021 to July 2024: art. 73 tables of the renewal of 8 June 2021 (CNEL 139292, pp. 32-34, signed by ANIP). From July 2025: the ANIP-signed fifth tranche of CNEL 139292 p. 34. Later unsigned tables of 6 August 2025 (CNEL 234752) are excluded (see anip_unsigned_renewal). No table prints the tabellare of 2par115 and 4par125 after April 2013: it is the April 2013 amount (CNEL 105782 pp. 30-31) plus the parametric increments.
    
    hourly_divisor 173: 'Ai fini della determinazione della retribuzione oraria, il divisore mensile è 173' (art. 19, CNEL 105782 p. 40).
    
    additional_months 14: tredicesima by 20 December (art. 20) and quattordicesima by 15 July (art. 21), each one retribuzione globale mensile (CNEL 105782 p. 41). The quattordicesima accrues from 1 July to 30 June.
    
    Contingenza of 2par115 and 4par125: no text prints one. The notes a verbale of art. 10 (CNEL 105782 p. 30) classify these workers at level 2 with parameter 115 and at level IV with parameter 125, so the file applies the contingenza of levels 2 and 4.
    
    Apprenticeship: two levels below the destination for the first half and one below for the second, destination II at level I throughout (art. 12, CNEL 105782 p. 37; the parametric positions are skipped). Durations come from the accord of 19 July 2012, read only in a third-party copy of the 2021 text: II 24, III 30, IV 30, V 36, VI 36, VII 36 months. The file models destinations 4 and 5 with 30 months each: destination 5 should last 36 and the other destinations are missing. The 2012 duration schedule has not been verified on the signed cached PDFs; declared in multiservizi_apprenticeship_destinations.
    
    July 2025 values: the renewal of 8 June 2021 (CNEL 139292, signed by ANIP) sets a fifth tranche from 1 July 2025 (level 2 +10.00, tabellare 779.21, p. 34), provisional under the art. 73 consuntivo. The renewal of 13 June 2025 (CNEL 234754) and its tables of 6 August 2025 (CNEL 234752) raise level 2 to 819.21 from the same date, but ANIP signed neither. The file applies the ANIP-signed 2021 fifth tranche from July 2025 and excludes the later unsigned tranches (see anip_unsigned_renewal). No ANIP amount for the art. 73 consuntivo or the IPCA increments of art. 73-bis and 73-ter was found.
    
    ANIP CONTRACT STATUS (2025): the renewal of 13 June 2025 (CNEL 234754) and its tables of 6 August 2025 (CNEL 234752) are signed by AGCI Servizi, Confcooperative Lavoro e Servizi, Legacoop Produzione e Servizi and Unionservizi Confapi with Filcams-CGIL, Fisascat-CISL and Uiltrasporti-UIL; ANIP-Confindustria signed neither. ANIP companies keep the renewal of 8 June 2021 (this file). A separate file would cover the 2025-2028 renewal (levels 1-7 and Q, retribuzione base 1,296.39 to 2,256.14 EUR from May 2026, 14 mensilità).
    
    INPS: terziario regime. Cleaning contractors are CIGS employers above 15 employees: D.Lgs. 148/2015 art. 20 c. 1 d) ('imprese appaltatrici di servizi di pulizia, anche se costituite in forma di cooperativa, che subiscano una riduzione di attività') and, from 1 January 2022, art. 20 c. 3-bis and art. 23 c. 1-bis ('a carico dei datori di lavoro che, nel semestre precedente la data di presentazione della domanda, abbiano occupato mediamente più di quindici dipendenti [...] è stabilito un contributo ordinario nella misura dello 0,90 per cento'). contribution/2026/terziario.json already charges the CIGS 0.90% (0.30% on the worker, INPS circ. 117/2022 all. 1) above 15 employees and the FIS of art. 29 below.
    
    Workers covered: no sourced figure. The earlier note (~403,000, INPS-UNIEMENS 2025) and meta.workers_estimate (~580k) disagree and neither cites a document.
    
    LEAVE (artt. 19, 41, 42 of the 2011 text): 22 days of ferie on five days, 26 on six (Employment.full_time_week_days), in twelfths with the month over 15 days; 40 hours a year of reduced time (art. 42). At termination a day of ferie is the monthly pay over 22 (26 on six days), an hour of permits over 173. The ex festività are compensatory permits for the abolished holidays worked (art. 41): not a bank, not accrued. The 2025 renewal (72 hours of permits according to the union summary) is not read in a primary text.
    
    Seniority, impiegati: biennial scatti of 6.25% of the tabellare in force when each scatto matures plus the contingenza at 1/8/1983 (EUR 279.60), at most 8 and up to 50% of tabellare + 279.60 (art. 22, CNEL 105782 p. 41). A matured scatto keeps its amount: it is not recomputed at later tranches. Levels 5, 6, 7 and Q have derived 2021-2025 amounts; levels 2-4 have no current scatto series. For an identified impiegato, declare EarnedIncrements for amounts matured before the run, including before a promotion. Otherwise the engine reprices matured scatti at the run date. Declared in multiservizi_seniority_maturation.
    
    Seniority, operai: one fixed sector amount after four years (art. 22, CNEL 105782 pp. 41-42; table p. 90), now routed by declared worker category at levels 1-6, including level 5 EUR 66.77 and level 6 EUR 82.99. Sector seniority continuity across employers must be stated as recognised service. Declared in multiservizi_seniority_maturation.
    

## Raw data

The contract file this page is generated from: [`agreement/multiservizi-anip.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/multiservizi-anip.json).

## Usage example

```python
--8<-- "docs/examples/agreement/multiservizi-anip/example.py"
```
