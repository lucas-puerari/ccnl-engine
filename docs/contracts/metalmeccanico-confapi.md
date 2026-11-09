# CCNL Metalmeccanici Piccola Industria (Unionmeccanica-Confapi)

| | |
|---|---|
| **CNEL code** | `C018` |
| **Sector** | metalmeccanico |
| **Family** | `metalmeccanica` |
| **Tax sector** | `industria` |
| **Last renewal** | 2017-07-03 |
| **Workers (est.)** | ~350k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - Unionmeccanica-Confapi
    - FIM-CISL
    - FIOM-CGIL
    - UILM-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, leave, overtime, sickness |

14 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 69 verified / 10 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2017-07-03 |
| **Last review** | 2026-11-10 |
| **Latest salary tranche** | 2028-06-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule read in the signed texts: the CCNL of 3 July 2017, the verbali on the minimi of 11 June 2024, 19 June 2025 and 17 June 2026, the accordo of 24 July 2025 and the renewal of 4 June 2026, for the production tier. | corrected | 70 records verified, 8 derived; the salary tables and the work rules cited aggregator pages and now cite the signatories' texts. The scans have no text layer: their quotes are OCR.<br>September 2025 minimi: the file re-parametrised the tranche; the signed accordo of 24 July 2025 prints 1603.45, 1770.79, 1964.74, 2195.87, 2354.36, 3054.74 for levels 1, 2, 3, 5, 6, 9 (one to five cents above).<br>Added the June 2027 and June 2028 tranches of the renewal of 4 June 2026 (ratified 23 July 2026); June 2026 closed at 2027-06-01.<br>Left derived: level 1 June 2024 and levels 1, 2, 4, 5, 9 June 2025, where the verbale that set the tranche and the later restated tables differ by one to five cents; the daily divisor 1/26 (no clause on absences); the leave tiers, whose 'oltre 10 anni' and 'oltre i 18 anni' are read as 120 and 216 completed months.<br>Overtime per Art. 29 column 'non a turni': 20% day, 50% night, 55% holiday and rest day, 75% night holiday (were 15/40/50/60); the base is the retribuzione globale di fatto (gross_incl_allowances).<br>Leave per Art. 33: 20 days, 21 over 10 years, 25 over 18 years (was 22 flat); left derived for the reading of the seniority thresholds.<br>Sickness per Art. 55: full pay for 2/3/4 months and half for 4/6/8 more over a 3-year window, comporto 6/9/12 months, net basis (was 60%/75%/180 days).<br>Fondapi 2.0%/1.2% from 2021-06-01 (Art. 50), not 2026-01-01; hourly divisor 173 from 2021-06-01 (Art. 40).<br>Apprenticeship: the 30- and 24-month tracks of Art. 10 added (limitation apprenticeship_36_months_assumed closed); no seniority during the apprenticeship (Art. 10 p. 49, limitation apprentice_seniority closed).<br>Not modelled pay clauses gathered in the limitation confapi_unmodelled_pay_elements; fondapi_base_elements narrowed to the indennità di funzione of the quadri. |
| 2026-10-17 | claude-opus-5-5 (ai) | The minimi of 2025 and 2026 against the accordo of 24 July 2025 and the verbale of 17 June 2026, the derived minimi of 2024 and 2025, and a year and a termination of a 5th level impiegato against a hand oracle. | confirmed | 5th level (scans read by OCR): 2.195,87 from 1 September 2025 and 2.245,87 from 1 June 2026 in both documents. Match.<br>The 6 derived minimi of June 2024 and June 2025 stay derived: for each the verbale that set the tranche and the later accordo and renewal print amounts one to five cents apart (for example 1.752,96 against 1.752,97 at the 2nd level); the file keeps the verbale in force for the months it covers and records both. The derived absence and leave rules state their transformation of a cited text. No primary states any of them directly.<br>Hand oracle (tests/knowledge/ccnl_engine/period/sector, scenarios confapi-year and confapi-june): a 5th level impiegato hired on 1 January 2026 by an employer with 50 employees, across the tranche of June 2026; every payment and the year (gross, contributions, tax, net, TFR, employer cost) match the engine to the cent. The CCNL now covers every total of the definition of done. |
| 2026-10-19 | claude-opus-5-5 (ai) | Hourly base of the time supplements and the supplements of ordinary night, holiday, Sunday, rest-day and shift work, read in the cited articles of the national text (text layer, or OCR of the scanned pages). AI review only: the same model extracted and checked the values. | confirmed | hourly_base_method gross_incl_allowances (was gross_incl_allowances), now verified: the engine reads it to derive the hourly rate of an event without one.<br>Supplement bands added: CONFAPI_FESTIVO, CONFAPI_FESTIVO_RIPOSO.<br>Bands left out where the rate depends on facts the request does not carry or the text is unconfirmed; listed in the coverage note HOURLY RATE AND SUPPLEMENTS. |
| 2026-10-19 | claude-opus-5-5 (ai) | Leave accrual: the ferie twelfths and month rule, the hours of each permit bucket (ROL, ex festività or the pooled PAR), the new-hire ramps and the basis of the indemnity for the residual leave at termination, read on the text cited by each rule. An AI review: the extractor is also the verifier. | confirmed | The values stated are those of the quoted clauses; what the texts leave open (month fractions, termination divisors, schedules and shift patterns) is not modelled and is recorded in the coverage notes. |
| 2026-10-20 | claude-opus-5-5 (ai) | The pricing of the seniority increments matured before a change of level (Art. 41 - Aumenti periodici di anzianità). | corrected | Art. 41 - Aumenti periodici di anzianità (p. 116): the earlier increments take the amounts of the new level from the change: seniority_increments.on_promotion. |
| 2026-10-20 | claude-opus-5-5 (ai) | Whether the individual elements of the worker (superminimi, aumenti di merito, assegni ad personam) enter the hourly base of overtime and supplements (Art. 38 - Mensilizzazione). | corrected | Art. 38 - Mensilizzazione: individual elements included in the hourly base: work_rules.time_supplements.individual_elements. |
| 2026-10-31 | claude-opus-5-5 (ai) | The basis of the indemnity for the leave not taken at the end of the employment, searched for a divisor of the daily pay in the CCNL of 3 July 2017 (Artt. 15, 29, 32, 33, 40) and in the OCR of the 2025-2028 renewal. | confirmed | Art. 33 pays a day of ferie at the 'retribuzione giornaliera globale di fatto' and no text read divides the monthly pay into it for the generality of workers. No termination basis is recorded. |
| 2026-11-02 | claude-opus-5-5 (ai) | Art. 29 row h (PDF p. 101). | corrected | Art. 29 row h: notturno e festivo 60%, 55% for shift workers (role turnista). |
| 2026-11-02 | claude-opus-5-5 (ai) | Art. 29 row b (PDF p. 101). | corrected | Art. 29 row b: ordinary night 25% until 22 (NightShiftEvent.before_22) and 35% after for the workers not on shifts, 25% for shift workers (role turnista). |
| 2026-11-07 | claude-opus-5-5 (ai) | Art. 48 (PDF p. 122) and the renewals of 26 May 2021 and 4 June 2026 for amendments to it. | confirmed | Art. 48: 485 EUR a year with the June pay, to the workers in service on 1 January in firms without second-level bargaining with economic content, prorated by the months of the year before (a fraction above 15 days a month), reduced up to its amount by the pay above the CCNL, out of the TFR base, paid at the settlement on an earlier termination, of the competence of the year of payment.<br>The ipotesi of 26 May 2021 and the renewal of 4 June 2026 do not mention the element (OCR of their 23 and 41 pages). |
| 2026-11-08 | gpt-6-sol (ai) | CCNL top-ups of maternity and work injury, read from the signed text by a separate model session; every quote found on the PDF text layer. | confirmed | Added work_rules.insured_absence.maternity.<br>Added work_rules.insured_absence.injury. |
| 2026-11-08 | claude-opus-5-5 (ai) | Art. 98 (printed p. 182), Premesse p. 12 and the renewals of 26 May 2021, 24 July 2025 and 4 June 2026 for amendments to it. | corrected | Art. 98 sets 69.72 (quadri A) and 49.06 (quadri B) from 1 January 1991 and 32.75 for the quadri B of the oreficeria sector, without a date.<br>No renewal of 2021, 2025 or 2026 amends Art. 98 (an independent reading of the three signed texts found none).<br>Art. 50 p. 123 counts the indennità di funzione quadri in the 'retribuzione FONDAPI': added to the base of the fund.<br>An independent reading flagged that the 9th category also holds workers outside the declaratoria of the quadri A: the 69.72 is paid with the role 'quadro' on level 9 too; it confirmed Art. 50 (both contributions on the retribuzione FONDAPI) and found no absorption or 13th-month clause on Art. 98. |
| 2026-11-08 | gpt-6-sol (ai) | The conto ore of the PAR not taken, the hourly pay of art. 38 and the leave settlement code path, by a separate model session in two rounds. | flagged | Round 1 found the payout blocked by the missing termination basis: the deadline now values the hours by the hour (PermitDeadline.permits_hourly), the termination path unchanged.<br>Round 2 confirmed the year offset (December of the second year after), the hourly valuation as the general hourly pay 'ai fini dei vari istituti contrattuali', and the test amounts (C3 131.27, level 5 132.42).<br>Flagged: the hourly pay of art. 38 adds the hourly elements (incentivi, cottimo), which the engine leaves out; kept under par_conto_ore_hourly_elements. |
| 2026-11-08 | claude-opus-5-5 (ai) | Art. 32(a,b,c) and holiday-in-absence paragraph, cached PDF pp. 104-105. | confirmed | Art. 32 excludes letter a) (25 April, 1 May and 2 June); the national calendar includes these, so a blanket sickness holiday rule would overpay. Injury and patron saint also remain unmodelled. |
| 2026-11-08 | claude-opus-5-5 (ai) | Art. 32 and Art. 38 of the 2017 CCNL, physical PDF pages 104 and 112, former-worker holiday hours and December pay. | confirmed | The Sunday daily quota already exists. Former legal operai receive 80 minutes for weekday holidays and January weekend Epiphany, subject to company offset; former Part One workers in service on 2008-12-31 receive a non-absorbable 11h10 December annual payment. |
| 2026-11-08 | claude-opus-5-5 (ai) | Art. 32 p. 104 and Art. 38 p. 112: local patron, 2009 effective date and termination settlement. | confirmed | Local patron is letter c of Art. 32; the 80-minute entitlement starts in 2009. Art. 38 pays the annual amount with December wages, without an express earlier termination advance. Hourly cottimo and other hourly elements remain outside the computed base. |
| 2026-11-09 | claude-opus-5-5 (ai) | PAR supplements of Arts. 21, 22 and 24 of the 2017 PDF and Art. 22 of the 2026 renewal, checked against cached PDFs. | confirmed | General 104 hours; entire-workforce sectors and eligible rotations add eight hours each; all employers add four hours from 2029. Unit headcount, restricted production areas, steel monetisation and company offsets remain limitations. |
| 2026-11-09 | claude-opus-5-5 (ai) | Art. 32 pp. 104-105, letter b and c holidays during reduced sickness, maternity and injury pay. | confirmed | Letter a is excluded; 4 October is absent; letter c includes the stated local patron day. Maternity local patron and substitute days remain outside its holiday calendar. |
| 2026-11-09 | claude-opus-5-5 (ai) | Art. 23 and Art. 29 paragraph 2 of the cached 2017 CCNL, physical PDF pages 94 and 102; immediate banked overtime premium only. | confirmed | The bank election covers every overtime hour worked in a month; banked hours pay 50% of the applicable premium immediately, with rest and any residual payout deferred. Flexible hours are not overtime and need a separate schedule model. |
| 2026-11-09 | claude-opus-5-5 (ai) | Art. 10 p. 49 apprenticeship credit towards seniority increments. | corrected | Art. 10 counts the apprenticeship at 65% towards the increments of the worker kept on from 1 November 2018; added apprenticeship_credit_share 0.65 and resolved the limitation. |
| 2026-11-10 | claude-opus-5-5 (ai) | Art. 32(b,c), physical PDF pp. 104-105, maternity holiday and local holiday selection. | confirmed | The maternity holiday target exists; letters b and c cover reduced-pay pregnancy and puerperium holidays. The employer-stated patron date can denote the locally agreed substitute or 29 June in Rome; neither is inferred without the local fact. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `9` | Level 9 — highly qualified quadro | € 3,263.42 | 2028-06-01 |
| `8` | Level 8 — highly specialised technician, quadro | € 2,934.46 | 2028-06-01 |
| `7` | Level 7 — high technical or managerial expertise | € 2,698.38 | 2028-06-01 |
| `6` | Level 6 — specialist technician, department head, senior technical employee | € 2,515.19 | 2028-06-01 |
| `5` | Level 5 — specialist worker 2nd category, senior white-collar employee (CCNL reference level) | € 2,345.87 | 2028-06-01 |
| `4` | Level 4 — specialist worker 1st category, white-collar employee | € 2,189.93 | 2028-06-01 |
| `3` | Level 3 — skilled worker, clerical employee | € 2,098.96 | 2028-06-01 |
| `2` | Level 2 — standardised operations, simple executive duties | € 1,891.75 | 2028-06-01 |
| `1` | Level 1 — auxiliary duties, simple and repetitive operations | € 1,712.98 | 2028-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 18.49 |
| `2` | € 21.59 |
| `3` | € 25.05 |
| `4` | € 26.75 |
| `5` | € 29.64 |
| `6` | € 32.43 |
| `7` | € 36.41 |
| `8` | € 40.95 |
| `9` | € 45.96 |

## Apprenticeship

**professionalizzante_36** (type: `under_classification`)  
Destination levels: `3`, `4`, `5`, `6`, `7`, `8`, `9`

**professionalizzante_30** (type: `under_classification`)  
Destination levels: `3`, `4`, `5`, `6`, `7`, `8`, `9`

**professionalizzante_24** (type: `under_classification`)  
Destination levels: `3`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "metalmeccanico-confapi/elemento_perequativo · base_salary · impact yes · open"
    Art. 48 (p. 122): the elemento perequativo of 485 EUR a year with the June pay to the worker in service on 1 January of a firm without second-level bargaining with economic content (EmployerProfile.second_level_premium false), for the months of the year before over twelve; the engine pays it (parameters.equalisation_element). Left open: the pay above the CCNL the worker received in the year before (superminimi, premi annui, other pay subject to contributions) has no field in the request; the engine reads it from the individual elements of the run, each amount on 31 December of the year before at the part-time fraction, for each month served, on twelve monthly payments, so an element agreed since, the share of the extra months or a yearly premium of the year before is not seen. A run without the employment period pays none; a second-level element the employer states counts when in force in the year before.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** State the pay above the CCNL of the year before as a fact of the run, or pass the element as a bonus and leave the employer flag true.

!!! warning "metalmeccanico-confapi/standby_and_travel · base_salary · impact yes · open"
    Art. 28: reperibilità (amounts by group of levels adjusted each June) and trasferta.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model standby and travel.

!!! warning "metalmeccanico-confapi/ordinary_hours_premiums · overtime · impact yes · open"
    Art. 29 row i and the shift-worker column of the overtime rows: night holiday work with compensatory rest (35%, 30%), night overtime 40%/45% and night holiday overtime 65% of shift workers. The ordinary night (25% until 22, 35% after; 25% for shift workers), holiday (55%), compensatory-rest (10%) and night holiday (60%, 55%) premiums are modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model row i and the shift-worker column of the Art. 29 overtime rows.

!!! warning "metalmeccanico-confapi/sunday_holiday_and_ex_operai · base_salary · impact yes · open"
    The Sunday holiday quota is modelled. Art. 32 former legal operai hours cover national and stated local patron weekday holidays from 2009; Art. 38 December annual payment is separate. Unstated patron days, hourly elements beyond fixed monthly pay and nonstandard company holiday arrangements not specified by the caller remain outside the calculation.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** State the local patron day and company holiday offset when applicable; supply non-monthly hourly elements when available.

!!! warning "metalmeccanico-confapi/six_day_leave · base_salary · impact yes · open"
    Art. 33: leave on a 6-day week and the transitional extra day.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the leave of a 6-day week.

!!! warning "metalmeccanico-confapi/sickness_rules · sickness · impact yes · open"
    Sickness: comporto prolungato (9/13.5/18 months) and its treatment, short absences counted double from the eighth in the triennio, hospital stays over 10 days and sickness over 21 days left out of the limits (60/75/90 days, at most 120), the 2026 disability extension at 50% (renewal p. 27). The net-pay gross-up is modelled (sickness_rules.net_basis) (review of 2026-10-30).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the residual sickness rules of Art. 55.

!!! warning "metalmeccanico-confapi/child_sickness_and_oncological_permits · sickness · impact yes · open"
    Art. 58 bis and Art. 55 bis: the child sickness indemnity from 2027 and the oncological permits.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the indemnity of Art. 58 bis and the permits of Art. 55 bis.

!!! note "metalmeccanico-confapi/apprentice_seniority_credit · base_salary · impact yes · resolved"
    Art. 10 p. 49: 65% of the apprenticeship counts towards the seniority increments of the worker kept on (from 1 November 2018), modelled by apprenticeship_credit_share with the stated SeniorityFact.apprenticeship_months. The text does not say how a fractional credited month is rounded; the engine compares the exact credit with the increment threshold.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Resolved: apprenticeship_credit_share 0.65 on the stated apprenticeship months, read on 2026-11-09.

!!! warning "metalmeccanico-confapi/ipca_top_up · base_salary · impact yes · open"
    Renewal of 4 June 2026: the IPCA top-up of June 2027 and 2028 above 2.653% and 2.729%.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the IPCA top-up when the index is published.

!!! warning "metalmeccanico-confapi/par_sector_shift_and_renewal_hours · leave · impact yes · open"
    LEAVE, PAR (Artt. 21-22, 24 and renewal of 4 June 2026, p. 18): the engine adds 8 hours for the whole-workforce sectors of Art. 21(b), 8 for qualifying rotating shifts outside steel, and 4 for all workers from 2029. Not modelled: the Art. 21(a) production/maintenance-area restriction (and southern auto shift exception), the steel shift permit paid with the Christmas bonus instead of credited, the 2027–28 four hours restricted to production units of at least 50 workers (employer headcount is not unit headcount), and absorption by company-level reductions. The 104-hour base remains payable for all workers.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model worker production area and unit headcount, steel shift monetisation and company-level offsets; the 2027–28 four hours cannot use employer headcount as unit headcount.

!!! warning "metalmeccanico-confapi/par_conto_ore_payout · leave · impact yes · open"
    LEAVE, CONTO ORE (Art. 22, p. 94): the residual PAR of a year are paid with the December pay two years later (work_rules.leave_rules.permit_deadline). Not modelled: 'L’attivazione del Conto ore individuale avverrà previo accertamento presso gli Enti previdenziali competenti' of the contributions on the hours set aside; the engine treats the conto ore as active.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** State whether the conto ore of the firm is active (the INPS check of art. 22) and, if not, pay the residual PAR at the end of their year.

!!! warning "metalmeccanico-confapi/par_conto_ore_hourly_elements · leave · impact yes · open"
    LEAVE, CONTO ORE: the PAR paid at the end of the conto ore are valued at the monthly pay of the run over 173; the hourly pay of art. 38 also adds the hourly elements of the pay (incentivi, indennità orarie, cottimo), which the engine does not add. A worker leaving before the expiry is paid nothing for them (no basis for the leave at termination).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the hourly elements of art. 38 to the hourly pay of the PAR, and source the PAR left at the end of the employment.

!!! warning "metalmeccanico-confapi/flexibility_and_hours_bank · overtime · impact yes · open"
    Art. 23 flexible hours above 40 per week (15% weekday, 20% Saturday) remain outside the model: they are not overtime. Art. 29 banked overtime pays half the applicable overtime premium now; the elected rest balance and eventual payout at current pay are not tracked. The election covers all overtime in the month and must be declared by the next month; callers must supply a consistent banked choice for each month's events.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model flexible schedule hours and compensation windows separately from overtime, and track elected overtime rest balances and their later liquidation.

!!! warning "metalmeccanico-confapi/holiday_outside_calendar · sickness · impact yes · open"
    Art. 32(b,c) holiday top-ups are modelled for sickness, compulsory maternity and injury, excluding letter a) and 4 October. A stated patron_saint_day covers the local patron day, its locally agreed substitute, or Rome-only 29 June when applicable. Without the applicable local date from the employer, these holidays cannot be calculated.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** State the applicable local patron holiday date (including a locally agreed substitute or Rome-only 29 June) as employer.patron_saint_day.

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
| https://www.fim-cisl.it/wp-content/uploads/2021/03/CCNL-Unionmeccanica.pdf | altro | 2017-07-03 | [↗](https://www.fim-cisl.it/wp-content/uploads/2021/03/CCNL-Unionmeccanica.pdf) |
| https://www.fim-cisl.it/wp-content/uploads/2021/03/Ipotesi-CCNL-TESTO-firme-accordo-26-maggio-2021.pdf | altro | 2021-05-26 | [↗](https://www.fim-cisl.it/wp-content/uploads/2021/03/Ipotesi-CCNL-TESTO-firme-accordo-26-maggio-2021.pdf) |
| https://www.uilmnazionale.it/wp-content/uploads/2024/06/20240611-UNIONMECCANICA-Verbale-accordo-minimi-2024.pdf | tabella_retributiva | 2024-06-11 | [↗](https://www.uilmnazionale.it/wp-content/uploads/2024/06/20240611-UNIONMECCANICA-Verbale-accordo-minimi-2024.pdf) |
| https://www.uilmnazionale.it/wp-content/uploads/2025/06/20250619-Unionmeccanica-Confapi-Verbale-di-accordo-adeguamento-IPCA-2024.pdf | tabella_retributiva | 2025-06-19 | [↗](https://www.uilmnazionale.it/wp-content/uploads/2025/06/20250619-Unionmeccanica-Confapi-Verbale-di-accordo-adeguamento-IPCA-2024.pdf) |
| https://www.uilmnazionale.it/wp-content/uploads/2025/07/2025-07-24-CCNL-Unionmeccanica-accordo-aumenti-minini-2025-26.pdf | altro | 2025-07-24 | [↗](https://www.uilmnazionale.it/wp-content/uploads/2025/07/2025-07-24-CCNL-Unionmeccanica-accordo-aumenti-minini-2025-26.pdf) |
| https://www.uilmnazionale.it/wp-content/uploads/2026/06/20260604-CCNL-Unionmeccanica-Confapi-2025-2028.pdf | altro | 2026-06-04 | [↗](https://www.uilmnazionale.it/wp-content/uploads/2026/06/20260604-CCNL-Unionmeccanica-Confapi-2025-2028.pdf) |
| https://www.uilmnazionale.it/wp-content/uploads/2026/06/20260617-Unionmeccanica-Confapi-Verbale-accordo-minimi-1-giugno-2026-IPCA-signed.pdf | tabella_retributiva | 2026-06-17 | [↗](https://www.uilmnazionale.it/wp-content/uploads/2026/06/20260617-Unionmeccanica-Confapi-Verbale-accordo-minimi-1-giugno-2026-IPCA-signed.pdf) |

??? note "Coverage notes"
    CONSOLIDATED MINIMUMS: base_salary holds the 'minimi tabellari conglobati della classificazione unica' (Art. 38 p. 112 and Art. 40 p. 113 of the CCNL of 3 July 2017), which absorb paga base, contingenza and EDR; fixed_allowances is empty for all levels.
    
    TRANCHES: June 2024 from the signed verbale of 11 June 2024; June 2025 from the verbale of 19 June 2025; September 2025 from the printed minimi of the accordo of 24 July 2025; June 2026 from the verbale of 17 June 2026 (IPCA 2025 absorbed); June 2027 and June 2028 from the renewal of 4 June 2026 (p. 5, ratified 23 July 2026), raised in those Junes only for the IPCA above 2.653% and 2.729%. The accordo of 24 July 2025 and the renewal restate the minimo at 31 December 2024 of level 1 as 1566.94 (verbale 1566.89) and the June 2025 minimi of levels 1, 2, 4, 5, 9 one to five cents apart from the verbale of 19 June 2025: the verbale values are kept, as derived.
    
    PRE-JUNE 2024 TRANCHES (CCNL in force since 26 May 2021) are outside the modelled window.
    
    SENIORITY INCREMENTS: Art. 41 (pp. 115-116 of the CCNL of 3 July 2017): five biennial increments, amounts in force from 1 January 2001 (1a=18.49 2a=21.59 3a=25.05 4a=26.75 5a=29.64 6a=32.43 7a=36.41 8a=40.95 9a=45.96), from the month after the biennio. None during the apprenticeship (Art. 10 p. 49).
    
    APPRENTICESHIP: Art. 10 (pp. 45-48). Destinations 3rd to 9th category (8th and 9th for high specialisation). Pay two levels below, then one below, then of the destination in three equal periods: 36 months (12/12/12), 30 months for holders of a relevant diploma (10/10/10), 24 months for assembly-line figures of the 3rd category (8/8/8). Choose the track by name.
    
    HOURLY DIVISOR: 173 (Art. 40 p. 113, Art. 38 p. 112; Art. 10 p. 48 for apprentices).
    
    MONTHLY PAYMENTS: 13 (Art. 42 p. 119). The CCNL provides no fourteenth month.
    
    INPS: industria rates (contribution/2026/industria.json); the CCNL sets no contribution regime of its own. Installation firms classified in another INPS sector are outside this file.
    
    SICKNESS (Art. 55 pp. 136-139): integration up to the normal net pay, full for 2/3/4 months and half for 4/6/8 more by seniority, over the sickness of the three years before each episode; comporto breve 6/9/12 months. The INPS share is grossed up by the worker's INPS rate (net_basis), a payroll practice the CCNL does not spell out.
    
    The Fondapi base ('retribuzione FONDAPI', Art. 50 p. 123) counts, besides the minimi conglobati, the EDR, the indennità di funzione of the quadri and the elemento retributivo of the 8th and 9th categories. The CCNL text sets no EDR amount and no elemento retributivo; the indennità di funzione (Art. 98 p. 182: 69.72 quadri A, 49.06 quadri B, 32.75 quadri B oreficeria) is paid on levels 8 and 9 and counted in the Fondapi base (minimum_allowances).
    
    HOURLY RATE AND SUPPLEMENTS (Art. 29 of the CCNL of 3 July 2017 (rates untouched by the renewals of 2021 and 2026)): without a caller value the engine derives the hourly base (minimi, scatti and fixed allowances over 173) and the supplements on holiday hours (55%) and on holiday hours with a compensatory rest (10%), equal in both columns. Whether those hours are also paid on top of the monthly pay is not settled: a derived holiday supplement is provisional. Not derived, the caller states the amount: ordinary night work (25% until 22 and 35% after (shift column 25%)), because its window starts 12 hours after the morning shift of each work group and its rate depends on the hour and on the shift column, facts the request does not carry; night holiday work and Sunday work. Individual elements (merito, superminimi, cottimi) are not in the hourly base. Absences: no clause sets the divisor of an absence deduction (work_rules.absence_rules is derived from the 1/26 of art. 32): the caller states AbsenceEvent.hourly_rate.
    
    LEAVE AT TERMINATION (Art. 33, p. 106 of the CCNL of 3 July 2017): 'Per ogni giornata di ferie la retribuzione dovuta al lavoratore è costituita dalla retribuzione giornaliera globale di fatto'. No clause of the 2017 text or of the 2025-2028 renewal (OCR) defines that daily pay as a fraction of the monthly pay: the 1/26 of the retribuzione mensile fissa (Art. 32, p. 104) is the pay of a festività falling on a Sunday, the 1/6 of the weekly pay (Art. 15, p. 87) is the ferie of the discontinuous workers only, and the divisor 173 gives the hourly pay. The engine pays no residual (termination_residual_leave incomplete, termination_basis_not_sourced).
    
    Art. 98: the indennità di funzione of the quadri is paid as a fixed allowance with the role 'quadro': 69.72 on the 9th category (quadri A), 49.06 on the 8th category (quadri B); 32.75 with the role 'quadro_oreficeria' on the 8th category. The 32.75 has no starting date in Art. 98: the series starts at the CCNL of 3 July 2017 that prints it. Art. 98 does not say whether superminimi absorb it: the caller states a superminimo net of any part an individual agreement absorbs.
    

## Raw data

The contract file this page is generated from: [`agreement/metalmeccanico-confapi.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/metalmeccanico-confapi.json).

## Usage example

```python
--8<-- "docs/examples/agreement/metalmeccanico-confapi/example.py"
```
