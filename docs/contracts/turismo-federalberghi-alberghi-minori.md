# CCNL Turismo — Federalberghi/Faita - Alberghi a una e due stelle e campeggi minori

| | |
|---|---|
| **CNEL code** | `H052` |
| **Sector** | Turismo |
| **Family** | `turismo` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-07-05 |
| **Workers (est.)** | ~220k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federalberghi
    - Faita (L'Ospitalità Italiana)
    - Filcams-CGIL
    - Fisascat-CISL
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
| **Limits of this contract** | base_salary, sickness |

10 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 69 verified / 1 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-07-05 |
| **Last review** | 2026-11-10 |
| **Latest salary tranche** | 2027-11-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule read again in the signed texts: the ipotesi of 5 July 2024 (scan, Federalberghi copy), the renewal of 18 January 2014 and the CCNL of 20 February 2010. (copied from turismo-federalberghi: covers the rules the two tables share, not the paga base of Art. 152 c. 2) | corrected | 82 records verified. The salary periods cited the 2010 text: the 2016 values are in the 2014 renewal (p. 17), the 2024-2027 values in the 2024 ipotesi (p. 42). The 2024 text has no text layer: its quotes are OCR, checked on the page images.<br>Level B is quadro (art. 48 c.1), not impiegato; levels 1-7 have no category of their own (art. 50, by mansione): null.<br>Added the Quadri function allowance of art. 145: A 75.00, B 70.00 from January 2009.<br>Sickness: 75% for days 4-20 and 100% from day 21 of the net daily pay, 180 days a calendar year (art. 228), not a flat 100%.<br>Accrual: hotels and campsites counted twenty-sixths before 2024 too (artt. 225, 277): the cumulated-fractions clause dropped.<br>Seniority from 1 May 1990 (art. 158 c.4); Fon.Te. from 29 November 1996 (art. 162), no longer from 2026; ruleset and validity from the decorrenza of 1 July 2024 (art. 199); the ruleset source is the 2024 ipotesi.<br>Holiday overtime 30% stays derived from art. 219 c.1: the CCNL sets no festive overtime rate.<br>Overtime is paid on the retribuzione of art. 148 divided by 172 (art. 151): hourly_base_method gross_incl_allowances.<br>Production blocked: no signed copy of the accordo apprendistato of 17 April 2012 (base durations, art. 13) in the CNEL archive of H052 or at the signatories; only art. 14 bis is read in the 2014 renewal.<br>No renewal after the ipotesi of 5 July 2024 through October 2026. |
| 2026-10-13 | claude-opus-5-5 (ai) | Scope of the declared limitations. (copied from turismo-federalberghi: covers the rules the two tables share, not the paga base of Art. 152 c. 2) | corrected | sickness_net_basis is recorded on every run with a sickness event (trigger run), not only documented.<br>The apprenticeship durations without a signed source are now a limitation on every apprentice run (apprenticeship_durations_unsourced); with every remaining gap flagged on the runs it concerns, the file moves to production. |
| 2026-10-17 | claude-opus-5-5 (ai) | Periodic review due 2026-12-01: the paga base nazionale of every level and tranche from July 2024, the extra months against the ipotesi of 5 July 2024, the scatti and the hourly divisor against the CCNL of 20 February 2010, and a year and a termination of a 4th level worker against a hand oracle. (copied from turismo-federalberghi: covers the rules the two tables share, not the paga base of Art. 152 c. 2) | confirmed | Art. 152 c. 1 as replaced in 2024 (p. 42, scan read by OCR): the 50 amounts of the ten levels from July 2024 to November 2027 match the file.<br>Art. 160 (p. 45): tredicesima of one monthly pay at Christmas; art. 161 (p. 46): quattordicesima of the pay in force on 30 June, paid with the July pay, in twelfths of the twelve months before 1 July. Match with the fourteen payments of the file.<br>Art. 158 c. 4 of the 2010 text (pp. 140-141): six scatti, A 40,80 to 7 30,47. Match. Hourly divisor 172 for a 40-hour week. Match.<br>Hand oracle (tests/knowledge/ccnl_engine/period/sector, scenarios turismo-year and turismo-june): a 4th level impiegato hired on 1 January 2026 by an employer with 10 employees, across the tranche of May 2026; every payment and the year (gross, contributions, tax, net, TFR, employer cost) match the engine to the cent.<br>apprenticeship_durations_unsourced stays open: no signed or CNEL copy of the accord of 17 April 2012 as amended in 2014 was found in this review. |
| 2026-10-19 | claude-opus-5-5 (ai) | Hourly base of the time supplements and the supplements of ordinary night, holiday, Sunday, rest-day and shift work, read in the cited articles of the national text (text layer, or OCR of the scanned pages). AI review only: the same model extracted and checked the values. (copied from turismo-federalberghi: covers the rules the two tables share, not the paga base of Art. 152 c. 2) | confirmed | hourly_base_method gross_incl_allowances (was gross_incl_allowances), now verified: the engine reads it to derive the hourly rate of an event without one.<br>Supplement bands added: TUR_NOTTURNO, TUR_NOTTURNO_QUALIFICA, TUR_FESTIVO.<br>Bands left out where the rate depends on facts the request does not carry or the text is unconfirmed; listed in the coverage note HOURLY RATE AND SUPPLEMENTS. |
| 2026-10-19 | claude-opus-5-5 (ai) | Leave accrual: the ferie twelfths and month rule, the hours of each permit bucket (ROL, ex festività or the pooled PAR), the new-hire ramps and the basis of the indemnity for the residual leave at termination, read on the text cited by each rule. An AI review: the extractor is also the verifier. (copied from turismo-federalberghi: covers the rules the two tables share, not the paga base of Art. 152 c. 2) | confirmed | The values stated are those of the quoted clauses; what the texts leave open (month fractions, termination divisors, schedules and shift patterns) is not modelled and is recorded in the coverage notes. |
| 2026-10-20 | claude-opus-5-5 (ai) | The treatment of the compulsory maternity leave and of a work injury. (copied from turismo-federalberghi: covers the rules the two tables share, not the paga base of Art. 152 c. 2) | corrected | work_rules.insured_absence added from the articles cited in its provenance; statutory measures in absence/insured/rates.json (D.Lgs. 151/2001 artt. 22-23, D.P.R. 1124/1965 artt. 68, 73, 116-117). |
| 2026-10-20 | claude-opus-5-5 (ai) | The pricing of the seniority increments matured before a change of level (Art. 158 c. 6 - Scatti di anzianità). (copied from turismo-federalberghi: covers the rules the two tables share, not the paga base of Art. 152 c. 2) | corrected | Art. 158 c. 6 - Scatti di anzianità (p. 141): the earlier increments are repriced at the new level when the next one matures: seniority_increments.on_promotion. |
| 2026-10-20 | claude-opus-5-5 (ai) | Whether the individual elements of the worker (superminimi, aumenti di merito, assegni ad personam) enter the hourly base of overtime and supplements (Art. 148 c. 1 - Elementi della retribuzione). (copied from turismo-federalberghi: covers the rules the two tables share, not the paga base of Art. 152 c. 2) | corrected | Art. 148 c. 1 - Elementi della retribuzione: individual elements excluded in the hourly base: work_rules.time_supplements.individual_elements. |
| 2026-10-31 | claude-opus-5-5 (ai) | The basis of the indemnity for the leave not taken at the end of the employment, searched in the signed text of 2010 (Artt. 111, 129, 130, 150, 151), the 2014 version and the OCR of the 2024 ipotesi. (copied from turismo-federalberghi: covers the rules the two tables share, not the paga base of Art. 152 c. 2) | corrected | Art. 150 - Determinazione della retribuzione giornaliera (p. 134): the daily pay is the monthly pay divided by 26 for every contractual purpose: the residual ferie are paid at it, and the ROL at the hourly pay of Art. 151: work_rules.leave_rules.termination. |
| 2026-11-01 | claude-opus-5-5 (ai) | The hourly divisors of the 44 and 45 hour weeks, Art. 151 c.1 (p. 135), checked by a separate session on the rendered page. (copied from turismo-federalberghi: covers the rules the two tables share, not the paga base of Art. 152 c. 2) | confirmed | Art. 151 c.1 (PDF p. 135, sha256 47f71f5f... matched; the page rendered and read, the OCR 't 92' and 'L 90' are 192 and 190): 192 for a normal week of 45 hours, 190 for 44, 172 for 40: work_rules.time_supplements.week_divisors 44/190, 45/192.<br>No later source of the file states another divisor; the notes of the file hold Art. 151 unchanged by the renewals of 2014 and 2024, whose PDFs were not opened. |
| 2026-11-06 | claude-opus-5-5 (ai) | Apprentice seniority: artt. 58, 148 and 158 of the 2010 text (pp. 90, 134, 140, OCR). | corrected | APPRENTICE SENIORITY (CCNL Turismo of 20 February 2010: art. 58 c. 1, p. 90; art. 148 c. 1 d), p. 134; art. 158, p. 140): the apprentice is paid a percentage of 'la normale retribuzione dei lavoratori qualificati di pari livello', whose voci include 'eventuali scatti di anzianità', and the six triennial increments count 'l'anzianità di servizio prestata senza interruzione': the level increments, scaled by the percentage. |
| 2026-11-07 | claude-opus-5-5 (ai) | The monthly values of the levels against the primary tables (text layer). | confirmed | 2 values found verbatim on the cited pages and marked verified; 50 left as they were (derived or not on a text page). |
| 2026-11-07 | gpt-6-sol (ai) | Monthly values on scanned pages, each read twice from the page image by two independent sessions of another model, the second without being told the expected value. | confirmed | 50 values read identically by both readings and equal to the file. |
| 2026-11-08 | gpt-6-sol (ai) | Art. 13 commi 5-14 of the ipotesi of 5 July 2024 (scanned pp. 10-12), the encoding checked against the page images by a separate model session. | flagged | Confirmed the amounts by level, the November 2027 payment, the eligibility of comma 5 and the part-time of comma 6.<br>Flagged as approximations, kept under the limitation: the trigger of comma 10, the days worked of comma 5, the absorption of comma 8. |
| 2026-11-10 | claude-opus-5-5 (ai) | Art. 155(3) replacement table on PDF p. 44; each row and date read from the cached page image. | confirmed | Verified five levels and five effective monthly columns; territorial precedence, minimum service, and all-inclusive settlement remain limitations. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A` | Level A | € 2,483.86 | 2027-11-01 |
| `B` | Level B | € 2,299.78 | 2027-11-01 |
| `1` | Level 1 | € 2,141.99 | 2027-11-01 |
| `2` | Level 2 | € 1,958.42 | 2027-11-01 |
| `3` | Level 3 | € 1,847.57 | 2027-11-01 |
| `4` | Level 4 | € 1,743.98 | 2027-11-01 |
| `5` | Level 5 | € 1,635.65 | 2027-11-01 |
| `6s` | Level 6 super | € 1,573.04 | 2027-11-01 |
| `6` | Level 6 | € 1,550.67 | 2027-11-01 |
| `7` | Level 7 | € 1,453.26 | 2027-11-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 40.80 |
| `B` | € 39.25 |
| `1` | € 37.70 |
| `2` | € 36.15 |
| `3` | € 34.86 |
| `4` | € 33.05 |
| `5` | € 32.54 |
| `6s` | € 31.25 |
| `6` | € 30.99 |
| `7` | € 30.47 |

## Apprenticeship

**standard** (type: `percentage`)  
Destination levels: `2`, `3`, `4`, `5`, `6s`, `6`  
percentage: 0.95

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "turismo-federalberghi-alberghi-minori/sickness_net_basis · sickness · impact yes · open"
    SICKNESS (art. 228, 2010 text p. 184): the CCNL integrates up to a share of the net daily pay without saying how the net pay is computed; the engine grosses up the INPS indemnity by the worker's INPS rate, as for the Commercio file. For fixed-term and seasonal workers no integration is due past the end of the contract (c.2).

    **Applies when:** `sickness` applies.

    **Remediation:** Model the net daily pay of art. 228 and the end of a fixed-term contract.

!!! warning "turismo-federalberghi-alberghi-minori/guarantee_element_2027 · base_salary · impact yes · open"
    Art. 13 c. 10 (ipotesi 5 July 2024, pp. 11-12, read on the page images): the amounts of November 2027 (A and B 186, 1-3 158, 4-5 140, 6s-7 112) are parameters.equalisation_element. Approximated: the trigger, read from the second-level facts of 2026 where the text asks whether an integrative agreement was defined by 31 October 2026 after a platform was presented; the proportion to the days actually worked in 2026, counted in months of more than 15 days; the absorption of comma 8, which takes any individual or collective treatment granted after 1 July 2024, the engine deducting only the individual elements. Not modelled: the welfare alternative of comma 11, the crisis exemption of comma 13 and the territorial agreements of comma 14.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** State the comma 10 condition and the days worked in 2026 as facts, take every treatment granted after 1 July 2024 into the absorption, and model commi 11, 13 and 14.

!!! warning "turismo-federalberghi-alberghi-minori/extras_hourly_table · base_salary · impact yes · open"
    The caller-selected extra hourly table is encoded for the five levels and dated tranches printed on p. 44 of the 2024 renewal. Art. 155(1),(3) of the 2010 agreement gives priority to territorial bargaining and better conditions and requires a minimum four-hour service; the table is all-inclusive of extra months and TFR. Those precedence, minimum-service, and all-inclusive accrual treatments are not yet implemented.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model territorial precedence, the four-hour service minimum and avoid separate extra-month and TFR accrual for all-inclusive rates.

!!! warning "turismo-federalberghi-alberghi-minori/quadri_absorption · base_salary · impact yes · open"
    Art. 145: the absorption of the Quadri allowance into individual treatments.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the absorption of Art. 145.

!!! warning "turismo-federalberghi-alberghi-minori/apprentice_net_cap · base_salary · impact yes · open"
    Art. 58 c. 3: the net cap of the apprentice pay.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Cap the apprentice net pay.

!!! warning "turismo-federalberghi-alberghi-minori/extra_months_during_leave · base_salary · impact yes · open"
    Artt. 160 c. 4 and 161 c. 6 (ipotesi of 5 July 2024, pp. 45-46): from 1 July 2024 the maternity, paternity and parental leave count 'ai fini dell'integrale maturazione e corresponsione' of the tredicesima, and maternity and paternity of the quattordicesima; the engine accrues every extra month in full during these leaves, as D.Lgs. 151/2001 art. 34 c. 5 does for the tredicesima. Not settled: the quattordicesima during the parental leave before 1 December 2027, which the renewal guarantees only from that date ('Solo dal 1° dicembre 2027'); the engine accrues it in full.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Read whether the parental leave reduces the quattordicesima before 1 December 2027 and, if it does, take its days out of the accrual.

!!! warning "turismo-federalberghi-alberghi-minori/hires_2016_ramp · base_salary · impact yes · open"
    Verbale of 30 November 2016: the lower ramp of the hires of 14 November 2016. The caller pays these amounts as variable items.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the 2016 ramp.

!!! warning "turismo-federalberghi-alberghi-minori/apprenticeship_durations_unsourced · base_salary · impact yes · open"
    APPRENTICESHIP DURATIONS: the durations of the professionalizzante come from the accord of 17 April 2012 as amended in 2014, of which no signed or CNEL copy was found (only aggregator copies); the percentages of art. 58 are verified. Every apprentice run carries this limitation.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Read a signed copy of the accord of 17 April 2012 and its 2014 amendment.

!!! note "turismo-federalberghi-alberghi-minori/balneari_reduction_hours · leave · impact yes · resolved"
    LEAVE, STABILIMENTI BALNEARI (Art. 111 c.2, p. 114): 108 hours of reduction a year instead of the 104 of alberghi, pubblici esercizi, campeggi, alberghi diurni and agenzie di viaggi, for an employer whose EmployerProfile.subsector is 'stabilimenti_balneari'.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Resolved: rol annual_hours tier of 108 hours for the sub-sector stabilimenti_balneari, read on 2026-11-06.

!!! warning "turismo-federalberghi-alberghi-minori/small_hotel_legacy_award · base_salary · impact unknown · open"
    Art. 227 of the cached 2010 hotel-sector scan (PDF p. 183) abolishes the former seniority prize effective 31 May 1986 but preserves acquired rights of workers then in service. The referenced Annex G is missing from the cached scan, so its amounts cannot be verified for smaller hotels; the different Federturismo agreement cannot establish them. No legacy prize is encoded.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Obtain Annex G and verify current applicability and cohort amounts for smaller hotels before modelling.

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
| Ipotesi di accordo 5 luglio 2024 (scan, also CNEL id 194291): art. 152 tranches lug 2024 - nov 2027, artt. 48, 160, 161, 199. | altro | 2024-07-05 | [↗](https://intranet.federalberghi.it/pubblicazioni/CCNL%20Turismo/CCNL%20Turismo%205%20luglio%202024/ccnl%20turismo%20-%20ipotesi%20di%20accordo%205%20luglio%202024.pdf) |
| Renewal of 18 January 2014 (also CNEL id 20): art. 152 table in force from 1 April 2016; art. 14 bis of the apprenticeship accord. | altro | 2014-01-18 | [↗](https://intranet.federalberghi.it/pubblicazioni/CCNL%20Turismo/CCNL%20Turismo%2018%20gennaio%202014/ccnl%20turismo%2018%2001%2014%20versione%20guida.pdf) |
| CCNL Turismo 20 febbraio 2010: the articles not replaced in 2014 and 2024 (58, 129, 145, 150, 151, 158, 162, 219, 220, 228). | altro | 2010-02-20 | [↗](http://www.uiltucs.it/pdf/turismo/CCNL_Turismo_Confcommercio_2010.pdf) |

??? note "Coverage notes"
    CNEL code H052 is shared with CCNL Agenzie di Viaggio Fiavet: the engine allows duplicates.
    
    SENIORITY FROM AGE 18 (Art. 158 c. 2, p. 140): a worker hired from 1 June 1986 accrues the scatti only from the eighteenth birthday (SeniorityFact.birth_date; without it the service counts from the start). The rules of the workers in service on 1 June 1986 are not modelled.
    
    HOURLY RATE AND SUPPLEMENTS (artt. 148, 151, 216, 220 of the 2010 text): without a caller value the engine derives the hourly base (the art. 148 retribuzione over 172), the 25% on ordinary night hours from 24 to 6 (art. 216 c.1; 12% for the role qualifica_notturna, c.2: Employment.roles must be stated) and the 20% on the hours worked on a festività (art. 220). The night window of the lavoratori notturni (23:30-6:30, art. 218) only changes which hours the caller declares. Art. 220 also pays the festività hours themselves on top of the monthly pay: the engine posts the 20% only and the run is provisional. Not derived: the Sunday allowance of art. 126 (10% of the hourly paga base and contingenza: the bundle does not record that base_salary holds exactly those two voci), holiday overtime (art. 219 sets no rate). The divisors 190 and 192 of the 44- and 45-hour weeks are derived from Employment.full_time_weekly_hours; another week than 40, 44 or 45 is not derived.
    
    LEAVE AT TERMINATION: no clause of the texts read (2010, 2014 version, 2024 ipotesi) names the indemnity for the ferie and permits not taken; the daily pay of Art. 150 (monthly pay / 26, 'valido a tutti i fini contrattuali', p. 134) prices a residual day of ferie, and the hourly pay of Art. 151 (/ 172) a residual hour of ROL, the measure Art. 111 c.7 uses for the permits left at the deadline.
    
    INSURED ABSENCES: compulsory maternity leave (INPS 80% advanced, top-up to 100% of the net daily pay for five months, Art. 179) and work injury (injury day in full, carenza at 60%, INAIL advanced to permanent workers, no top-up, Artt. 170 and 172) as work_rules.insured_absence.
    
    SUB-SECTOR: the paga base of Art. 152 c. 2 (renewal of 5 July 2024, p. 43) for the alberghi a una e due stelle and the campeggi with up to 1200 presenze-licenza, from July 2024; the other rules are those of turismo-federalberghi. The reduction does not apply to the cuoco, cameriere and barista of level 5, nor to the staff of ostelli, bed and breakfast and affittacamere: they take turismo-federalberghi.
    
    TRATTAMENTO INTEGRATIVO SPECIALE (L. 199/2025 art. 1 cc. 18-21): for the work of 1 January - 30 September 2026 of a worker who asked for it (PriorYearTaxFacts.special_supplement_requested) with 2025 employment income up to 40,000 EUR, in an employer of food service, tourism or thermal establishments (EmployerProfile.activity), the engine pays 15% of the gross pay of the night hours and of the holiday overtime (AdE circ. 26/E/2023 par. 2: 'calcolata sulla retribuzione lorda'), outside income, as a credit the employer recovers in F24 (capability special_supplement).
    
    SALARY TABLES: the 1 April 2016 values from art. 152 c.1 of the renewal of 18 January 2014 (p. 17); the five tranches lug 2024, giu 2025, mag 2026, apr 2027 and nov 2027 from art. 152 c.1 of the ipotesi of 5 July 2024 (p. 42).
    
    APPRENTICESHIP: 80%, 85%, 90% and 95% from the fourth year (art. 58 c.1, 2010 text p. 90), to which art. 152 c.4 of the 2024 text still refers. Destination levels 2, 3, 4, 5, 6s and 6. The durations of art. 54 of the 2010 text were replaced by the accordo apprendistato of 17 April 2012 and its art. 14 bis (renewal of 18 January 2014, p. 12: 2 and 3 34 months, 6 22 months with prior learning); no signed copy of the 2012 accord was found, so its base durations are not sourced. The 95% band is open-ended.
    
    HOURLY DIVISOR: 172 for the 40-hour week (art. 151 c.1, 2010 text p. 135); 190 and 192 for 44 and 45 hours in work_rules.time_supplements.week_divisors, read from Employment.full_time_weekly_hours.
    
    MONTHLY PAYMENTS: 14, art. 160 (tredicesima) and art. 161 (quattordicesima, paid with the July pay) as replaced by the renewal of 5 July 2024 (pp. 45-46).
    
    SENIORITY: six scatti triennali (art. 158, 2010 text pp. 140-141), fixed amounts per level from 1 May 1990.
    

## Raw data

The contract file this page is generated from: [`agreement/turismo-federalberghi-alberghi-minori.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/turismo-federalberghi-alberghi-minori.json).

## Usage example

```python
--8<-- "docs/examples/agreement/turismo-federalberghi-alberghi-minori/example.py"
```
