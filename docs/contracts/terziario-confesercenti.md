# CCNL Terziario Distribuzione e Servizi — Confesercenti

| | |
|---|---|
| **CNEL code** | `H012` |
| **Sector** | Terziario distribuzione e servizi |
| **Family** | `commercio` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-03-22 |
| **Workers (est.)** | ~230k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - Confesercenti
    - Filcams-CGIL
    - Fisascat-CISL
    - UILTuCS-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, leave, overtime, seniority, sickness, territorial_supplement, una_tantum |

14 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 92 verified / 2 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-03-22 |
| **Last review** | 2026-11-01 |
| **Latest salary tranche** | 2027-02-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule of the file read again in the signed texts, for the production tier: the Testo Unico of 12 December 2019, the renewal of 22 March 2024, its accordo integrativo of 28 March 2024 and the Protocollo of 12 December 2022. | corrected | 86 records verified against the Testo Unico of 12 December 2019 (text layer) and the Accordo integrativo of 28 March 2024 (CNEL 20279, scan read on the page image; quotes are the OCR-verbatim fragments).<br>Corrected 17 base_salary periods (Q 6, I 4, II 6, VI 1) by 1-5 cents: the file carried the ipotesi increases of 22 March 2024, the accordo integrativo of 28 March 2024 fixed their rounding and printed the official tables.<br>Sickness: 75% for days 4-20 and 100% from day 21 of the net daily pay, carenza by event, comporto in the calendar year, apprentices excluded (Artt. 186-187), not a flat 75%.<br>Added the terzo elemento nazionale of EUR 2.07, gated by the provincial element (Art. 215), the payment days of the tredicesima and quattordicesima (Artt. 220-221) and Fon.Te. (Art. 107, 1.55% and 0.55%, apprentices 1.05% by Art. 57).<br>Overtime premiums are on the normale retribuzione of Art. 206 (hourly_base_method gross_incl_allowances, was minimo_tabellare).<br>Apprenticeship: the second period closes at 36 months (II-V) and 24 months (VI), as Art. 53 pays the destination level at the end.<br>The una tantum of 2024-2025 is owed at every level, not only at level IV: limitation lump_sum_2024_2025 rescoped to July 2024 and July 2025.<br>The source documents had three ids and a tabella_retributiva kind for the same Testo Unico URL: unified. The 22 March 2024 ipotesi and the twin UGL texts (CNEL 20270, 19968) agree with the tables.<br>No renewal after the accordo integrativo of 28 March 2024 changes pay through October 2026 (CNEL H012 deposits through 20522 of 4 November 2024, training profiles only). |
| 2026-10-13 | claude-opus-5-5 (ai) | Scope of the declared limitations. | corrected | sickness_net_basis is recorded on every run with a sickness event (trigger run), not only documented. |
| 2026-10-19 | claude-opus-5-5 (ai) | Hourly base of the time supplements and the supplements of ordinary night, holiday, Sunday, rest-day and shift work, read in the cited articles of the national text (text layer, or OCR of the scanned pages). AI review only: the same model extracted and checked the values. | confirmed | hourly_base_method gross_incl_allowances (was gross_incl_allowances), now verified: the engine reads it to derive the hourly rate of an event without one.<br>Supplement bands added: CONF_NOTTURNO, CONF_FESTIVO, CONF_DOMENICA, CONF_DOMENICA_AUTOSTRADE, CONF_RIPOSO.<br>Bands left out where the rate depends on facts the request does not carry or the text is unconfirmed; listed in the coverage note HOURLY RATE AND SUPPLEMENTS. |
| 2026-10-19 | claude-opus-5-5 (ai) | Leave accrual: the ferie twelfths and month rule, the hours of each permit bucket (ROL, ex festività or the pooled PAR), the new-hire ramps and the basis of the indemnity for the residual leave at termination, read on the text cited by each rule. An AI review: the extractor is also the verifier. | confirmed | The values stated are those of the quoted clauses; what the texts leave open (month fractions, termination divisors, schedules and shift patterns) is not modelled and is recorded in the coverage notes. |
| 2026-10-20 | claude-opus-5-5 (ai) | The pricing of the seniority increments matured before a change of level (Art. 205 - Scatti di anzianità). | corrected | Art. 205 - Scatti di anzianità (p. 153): the earlier increments are repriced at the new level when the next one matures: seniority_increments.on_promotion. |
| 2026-10-20 | claude-opus-5-5 (ai) | Whether the individual elements of the worker (superminimi, aumenti di merito, assegni ad personam) enter the hourly base of overtime and supplements (Art. 149 - Maggiorazione lavoro straordinario; Artt. 206 and 208). | corrected | Art. 149 - Maggiorazione lavoro straordinario; Artt. 206 and 208: individual elements hour only in the hourly base: work_rules.time_supplements.individual_elements. |
| 2026-10-31 | claude-opus-5-5 (ai) | The basis of the indemnity for the leave not taken at the end of the employment (work_rules.leave_rules.termination) read again in the cited text. | confirmed | Art. 159 - Chiarimento a verbale (p. 127): the indemnity of the ferie at the end of the employment is the retribuzione mensile di fatto divided by twenty-six, as recorded; the basis is now verified. |
| 2026-11-01 | claude-opus-5-5 (ai) | The indennità di cassa e maneggio denaro of Art. 218 (p. 158). | corrected | Art. 218 (p. 158): 5% of the paga base nazionale conglobata to the staff normally at the till with full responsibility for it: levels[*].fixed_allowances[IND_CASSA], role cassiere, one value per period of the base_salary. |
| 2026-11-01 | claude-opus-5-5 (ai) | The hourly divisors of the 42 and 45 hour weeks, Art. 211 - Quota oraria (p. 156). | corrected | Art. 211 - Quota oraria (p. 156): 168 for a normal week of 40 hours, 182 for 42, 195 for 45: work_rules.time_supplements.hourly_divisor_weekly_hours 40 and week_divisors 42/182, 45/195. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Senior Manager (Quadro) | € 3,114.42 | 2027-02-01 |
| `I` | First Level | € 2,621.36 | 2027-02-01 |
| `II` | Second Level | € 2,335.04 | 2027-02-01 |
| `III` | Third Level | € 2,068.56 | 2027-02-01 |
| `IV` | Fourth Level | € 1,856.68 | 2027-02-01 |
| `V` | Fifth Level | € 1,725.77 | 2027-02-01 |
| `VI` | Sixth Level | € 1,600.53 | 2027-02-01 |
| `VII` | Seventh Level | € 1,447.98 | 2027-02-01 |

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

**standard** (type: `under_classification`)  
Destination levels: `II`, `III`, `IV`, `V`

**sesto-livello** (type: `under_classification`)  
Destination levels: `VI`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "terziario-confesercenti/lump_sum_2024_2025 · una_tantum · impact yes · open"
    One-off lump sum of the renewal of 22/03/2024 (CNEL 20260, pp. 49-50): EUR 350 at level IV, reparametrised for every level, paid in two instalments with the July 2024 and July 2025 pay (per instalment Q 303.81, I 273.67, II 236.73, III 202.34, IV 175.00, V 158.11, VI 141.95, VII 121.53), to the workers in force on 22/03/2024, pro rata over 1/1/2022-31/3/2023, outside the TFR and every other institute. Not modelled.

    **Applies when:** `una_tantum` applies; level in I, II, III, IV, Q, V, VI, VII; from 2024-07-01; before 2025-08-01.

    **Remediation:** Pay the una tantum as a one-off earning with the July 2024 and July 2025 pay: per instalment Q 303.81, I 273.67, II 236.73, III 202.34, IV 175.00, V 158.11, VI 141.95, VII 121.53, pro rata over 1/1/2022-31/3/2023.

!!! warning "terziario-confesercenti/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "terziario-confesercenti/sickness_net_basis · sickness · impact yes · open"
    SICKNESS (Art. 187): the CCNL integrates up to a share of the net daily pay ('retribuzione giornaliera netta') without saying how the net pay is computed. The engine grosses up the INPS indemnity by the worker's INPS rate and tops it up to the measure of the gross daily quota, as for the Commercio file. The events exempt from the carenza reduction are an input (SicknessEpisode.short_absence_exempt, read with carenza_by_event) (review of 2026-10-30).

    **Applies when:** `sickness` applies.

    **Remediation:** Model the net daily pay of Art. 187.

!!! warning "terziario-confesercenti/provincial_third_elements · territorial_supplement · impact yes · open"
    Art. 214: the provincial terzi elementi, amounts set by provincial agreements.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the provincial terzi elementi as inputs.

!!! note "terziario-confesercenti/cashier_allowance · base_salary · impact yes · resolved"
    Art. 218: the indennità di cassa e maneggio denaro of 5%.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Resolved: every level carries IND_CASSA, 5% of its paga base nazionale conglobata, for the role cassiere of Employment.roles.

!!! warning "terziario-confesercenti/sales_operators · base_salary · impact yes · open"
    The minimi of the operatori di vendita I and II categoria (CNEL 20279 tables).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the operatori di vendita levels.

!!! note "terziario-confesercenti/long_week_divisors · base_salary · impact yes · resolved"
    Art. 211: the hourly divisors 182 and 195 of the 42 and 45 hour weeks.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Resolved: work_rules.time_supplements.week_divisors holds 182 and 195, read for an employment whose full_time_weekly_hours is 42 or 45.

!!! warning "terziario-confesercenti/sunday_overtime · overtime · impact unknown · open"
    Art. 149: the 30% on Sunday overtime. Overtime declared as OvertimeKind.REST_DAY takes OT_FESTIVO, 30% (working_time/overtime/policies.py, tests/integration/ccnl_engine/working_time/overtime/test_rest_day.py::test_rest_day_band[terziario_sunday_30]); Sunday overtime of a worker whose weekly rest falls on another day is weekday overtime, 15%, and whether Art. 149 pays it 30% is not confirmed (review of 2026-10-30).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Read Art. 149 on Sunday overtime of a worker whose weekly rest is not Sunday; if it pays 30%, add a Sunday band, else resolve this limitation.

!!! warning "terziario-confesercenti/apprentice_sickness · sickness · impact yes · open"
    Art. 54: the apprentice sickness, 60% of the gross pay for the three days of carenza of six events a year and for hospital stays, while the file pays apprentices no integration.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the apprentice sickness of Art. 54.

!!! warning "terziario-confesercenti/long_apprenticeship_profiles · base_salary · impact yes · open"
    Art. 68 Tabella B: the 42 and 48 month apprenticeship profiles. The una tantum of the Protocollo 12/12/2022 (EUR 200 + 150 at level IV with the January and March 2023 pay) is historic.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the 42 and 48 month tracks.

!!! warning "terziario-confesercenti/rol_schedule_absorption · leave · impact yes · open"
    LEAVE, WEEKLY SCHEDULE (Artt. 133-134): an employer on a 39-hour week absorbs 36 hours of ROL, on a 38-hour week 72 hours (16 of ex festività and 56 of ROL), and the grandi magazzini, supermercati, cash&carry and ipermercati on a 38-hour average absorb 72 hours of ROL. The engine accrues the hours of a 40-hour week (Art. 133 a).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add an employer fact for the weekly schedule of Artt. 133-134 and absorb the hours it uses.

!!! warning "terziario-confesercenti/permit_deadline_payout · leave · impact yes · open"
    LEAVE, DEADLINE (Art. 158): the permits not taken within the year of accrual lapse and are paid with the retribuzione di fatto, or are carried and taken by 30 June of the following year; the text leaves the choice open. The engine carries the balances and pays the residual only at the end of the employment.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add an employer fact for the alternative of Art. 158 and pay the residual permits at its deadline.

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

!!! warning "mid_month_level_change · base_salary · impact unknown · open"
    A promotion on a day other than the first of a month splits the monthly pay of the run between the level before and the new level by the payable days of the CCNL daily quota on each side of the promotion, component by component; the hourly quotas of the month (overtime, permits, absences) read the same split chain whatever the day of the event. The CCNL texts read (Commercio and Terziario art. 118, DMO art. 102) give the new level from the promotion but not how its month is split.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source how a month is split by a promotion inside it (a CCNL clause or an INPS or Ministry ruling) and price the events of the month at the terms of their day, then resolve this limitation.

!!! warning "arrears_unused_deductions · contract_renewal_arrears · impact yes · open"
    The engine computes the rate of the separate taxation of arrears from PriorYearTaxFacts.net_income_biennio (art. 21 cc. 1, 3 TUIR) but does not reduce the tax by the deductions of artt. 12 and 13 cc. 1-2 the worker did not use in the years the arrears refer to (art. 21 c. 4): the request does not state them, so the tax may be overstated.

    **Applies when:** `contract_renewal_arrears` applies; the run takes the engine code path.

    **Remediation:** Add the deductions the worker declares as unused for each year of the arrears and reduce the tax by them, then resolve this limitation.

### Without monetary impact

!!! note ""
    Grade I and the quadri are not apprenticeship destinations: Art. 62 admits the professionalizzante for levels II-VI only.

!!! note ""
    Track sesto-livello: Art. 53 (last paragraph) sets level VII for the first half of a level VI apprenticeship; the second half is one level below VI, again VII. Level VI from month 25.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| Testo Unico 12 dicembre 2019 (sha256 18a2f10c...). Art. 53, 57, 64 (apprendistato), Art. 107 (Fon.Te), Artt. 186-187 (malattia), Art. 205 (scatti), Art. 210-211 (quote giornaliera e oraria), Art. 215 (terzo elemento), Artt. 220-221 (tredicesima e quattordicesima), Tabella I (p. 347) vigente dal 01.01.2020. | altro | 2019-12-12 | [↗](https://www.confesercenti.it/wp-content/uploads/2023/01/CCNL_contratto-collettivo-nazionale.pdf) |
| Ipotesi di accordo 22 marzo 2024 (CNEL 20260, scansione firmata), validità 2023-04-01/2027-03-31. Art. 213 aumenti in 6 tranche (01/04/2023, 01/04/2024, 01/03/2025, 01/11/2025, 01/11/2026, 01/02/2027). Una tantum EUR 350 at level IV, reparametrised for every level, paid 175+175 with the July 2024 and July 2025 pay: not modelled. | altro | 2024-03-22 | [↗](https://cdcpcnelblg01sa.blob.core.windows.net/archivio/2024//20260.pdf) |
| Accordo integrativo 28 marzo 2024 (CNEL 20279, scansione firmata): Art. 213 increases with the rounding fixed and the official tabelle retributive 2023-2027 (pp. 2-3), the source of every 2023-2027 base_salary period. | altro | 2024-03-28 | [↗](https://cdcpcnelblg01sa.blob.core.windows.net/archivio/2024//20279.pdf) |
| Protocollo straordinario 12 dicembre 2022 (CNEL 19967): acconto EUR 30 at level IV from 1 April 2023 (first 2023-2027 tranche) and una tantum EUR 350 at level IV (January and March 2023), not modelled. | altro | 2022-12-12 | [↗](https://cdcpcnelblg01sa.blob.core.windows.net/archivio/2022//19967.pdf) |

??? note "Coverage notes"
    Apprenticeship type b (professionalizzante). Durations (Art. 64): II-V 36 months, VI 24 months; half-period 18 and 12 months. The 42 and 48 month profiles of Art. 68 Tabella B are in the unmodelled note.
    
    TERZO ELEMENTO NAZIONALE (Art. 215, TU p. 157): EUR 2.07 a month due only in the provinces where no provincial third element is in force (Art. 214); paid when EmployerProfile.provincial_pay_element is false, left out with a missing_fact blocker when it is not stated.
    
    HOURLY RATE AND SUPPLEMENTS (Testo Unico 12 December 2019, unchanged by the 2024 renewal, artt. 149-157, 206-211): without a caller value the engine derives the hourly base (the normale retribuzione of art. 206 over 168), the 15% on ordinary night hours from 22 to 6 (art. 151), the 30% on festività hours paid as straordinario festivo (art. 155 with art. 149), the 30% on ordinary Sunday hours (art. 153; 10% at the motorway fuel stations of art. 157, role impianto_carburante_autostradale: Employment.roles must be stated) and the 30% on the hours of the weekly rest day (art. 156). Art. 155 also pays the festività hours themselves: the engine posts the 30% only and the run is provisional. Second-level agreements may replace the Sunday and night rules (art. 153). Not derived: the divisors 182 and 195 of the 42- and 45-hour weeks; shift work, left to second-level bargaining.
    
    Base salary table effective from 01.01.2020 (Table I, CCNL 12.12.2019, confesercenti.it PDF).
    
    Salary tables 2023-2027: the official tabelle retributive of the Accordo integrativo 28/03/2024 (CNEL 20279, pp. 2-3), which perfected the Art. 213 increases of the ipotesi 22/03/2024 (CNEL 20260) 'con la sistemazione degli arrotondamenti' (Q, I, II and VI differ by 1-5 cents from the ipotesi). Tranches 01/04/2023 (the acconto of the Protocollo 12/12/2022, CNEL 19967), 01/04/2024, 01/03/2025, 01/11/2025, 01/11/2026, 01/02/2027. base_salary is the 'Totale mensile' column: paga base + contingenza/EDR + altri elementi (Q 260.76 indennità di funzione, VII 5.16).
    
    Seniority increment amounts from Art. 205 CCNL 2019, effective from 01.01.1990 (triennial, max 10).
    
    Hourly divisor 168 from Art. 211 CCNL 2019 (40h/week).
    
    14 monthly payments from Art. 220 (thirteenth) and Art. 221 (fourteenth) CCNL 2019.
    
    Apprenticeship from Art. 53 (under-classification) and Art. 64 (durations: II-V 36 months, VI 24 months) of the Testo Unico 2019, unchanged by the 2024 renewal: at the end of the apprenticeship the worker is paid at the destination level (Art. 53).
    

## Raw data

The contract file this page is generated from: [`agreement/terziario-confesercenti.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/terziario-confesercenti.json).

## Usage example

```python
--8<-- "docs/examples/agreement/terziario-confesercenti/example.py"
```
