# CCNL CED, ICT, Professioni Digitali e STP (Assoced-UGL)

| | |
|---|---|
| **CNEL code** | `H601` |
| **Sector** | Terziario |
| **Family** | `servizi-professionali` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-07-28 |
| **Workers (est.)** | ~22k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Assoced
    - LAIT
    - Confterziario
    - UGL Terziario

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, inps_employer, maternity_leave, shift_work, workplace_injury |

5 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 51 verified / 4 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-07-28 |
| **Last review** | 2026-11-14 |
| **Latest salary tranche** | 2028-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-11-08 | claude-opus-5-5 (ai) | Arts. 178-181 of the 2022 agreement and the 2025 renewal, cached primary PDFs pp. 112 and 32, plus effective dates. | corrected | Daily meal benefit €6 from 2022 and €8 from September 2025; transport and valuables are variable and remain a limitation; Art. 177 repealed. |
| 2026-11-08 | claude-opus-5-5 (ai) | The monthly values of the levels against the primary tables (text layer). | confirmed | 42 values found verbatim on the cited pages and marked verified; 0 left as they were (derived or not on a text page). |
| 2026-11-08 | claude-opus-5-5 (ai) | Art. 166 of the stesura of 9 March 2022 (PDF p. 106), text layer. | corrected | Modelled the scatti of the staff in service on 31 December 2018 (were none). |
| 2026-11-08 | claude-opus-5-5 (ai) | Art. 149 (PDF p. 97, text layer). | confirmed | Art. 149: the festività in a sickness or injury are topped up to 100% of the pay, net of the INPS and INAIL indemnity: sickness_rules.holiday rate 1; the injury part stays a limitation. |
| 2026-11-08 | claude-opus-5-5 (ai) | Art. 157, PDF p. 102: holiday top-up during compulsory maternity. | confirmed | Verified the quoted clause against the cached PDF; encoded only the compulsory maternity holiday target. |
| 2026-11-08 | gpt-6-sol (ai) | The maternity holiday clause against the encoding, by a separate model session. | corrected | Confirmed the 100% target net of the INPS share on the holidays of the compulsory leave.<br>Recorded as limitation maternity_holiday_scope: the Sunday holidays, the patron saint and 4 October, the optional leave. |
| 2026-11-08 | claude-opus-5-5 (ai) | Holiday pay during work injury, including the applicable holiday calendar and the offset against statutory and contractual daily pay. | confirmed | Covered weekday holiday target reaches full daily pay after INAIL and ordinary CCNL integration; employer-specific holidays remain outside the national calendar. |
| 2026-11-08 | claude-opus-5-5 (ai) | Art. 147 - Injury pay, ordinary injury integration and waiting days against the cached PDF. | corrected | The explicit numerical 75% is used rather than the contradictory parenthetical words (100%). The three days after the injury are paid at 60%; from offset 4 the INAIL benefit is topped up to 75% of net daily pay. The conflicting wording requires a clarification before a 100% target can be asserted. |
| 2026-11-08 | gpt-6-sol (ai) | Art. 147 against the injury integration bands, by a separate model session. | flagged | Confirmed the waiting days at 60%, the bands from the INAIL indemnity and the day mapping from the injury day.<br>Flagged, kept as limitations: the 75% of the numeral against the '(cento per cento)' in words. |
| 2026-11-08 | claude-opus-5-5 (ai) | Local patron saint day in sickness and work injury holiday clauses. | confirmed | Art. 149 - Festività nel periodo di malattia o infortunio (p. 97): Ai sensi della L. 31 marzo 1954, n. 90, per le festività cadenti nel periodo di malattia o infortunio, il lavoratore ha diritto ad un'indennità integrativa di quella a carico rispettivamente dell'INPS e dell'INAIL, da corrispondersi a carico del datore di lavoro, in modo da raggiungere complessivamente il 100% (cento per cento) della retribuzione di fatto di cui all'art. 168. The stated local patron saint day is covered when the target opts in; unstated days leave other holidays unchanged. |
| 2026-11-09 | claude-opus-5-5 (ai) | Arts. 149 and 157 and the patron saint holiday list, cached 2022 PDF pp. 97 and 102. | corrected | Sickness and injury already include the stated patron saint day; maternity now includes it too. Optional parental leave was outside the maternity target at the time of this review. |
| 2026-11-09 | claude-opus-5-5 (ai) | Art. 157, cached 2022 PDF p. 102: holidays during compulsory and optional leave. | corrected | The optional absence has the same daily holiday target as compulsory absence; the stated local patron is already a covered holiday. |
| 2026-11-14 | claude-opus-5-5 (ai) | Art. 119 of the stesura of 9 March 2022 (permits, ROL ramp, deadline). | corrected | The file had the ferie but no permit: added the 32 hours of ex festivita, the 56/72 hours of ROL with the ramp of the hires after 9 March 2022, and the 30 June deadline of Art. 119. |
| 2026-11-14 | claude-opus-5-5 (ai) | Artt. 134, 170 and 171 of the stesura of 9 March 2022. | corrected | The file had no basis for the leave left at termination, so the ferie and permits left were not paid: added the 1/26 day and the 1/173 hour. |
| 2026-11-14 | claude-opus-5-5 (ai) | Art. 116 (Festivita) (holiday on a Sunday). | corrected | The file had no clause for a holiday falling on a Sunday, so its further daily quota was not paid: added the clause with the holidays the text lists and 4 November. |
| 2026-11-14 | claude-opus-5-5 (ai) | Artt. 104, 106, 111, 117 and 118 of the stesura of 9 March 2022. | corrected | Corrected the weekday overtime band (15%, was 30%), added the tier beyond the 48th hour (20%), the night-holiday band, the holiday and rest-day premiums; recorded the Title XI shift premiums as a limitation. |
| 2026-11-14 | claude-opus-5-5 (ai) | Artt. 221, 266-269 of the stesura of 9 March 2022. | corrected | The file had no fund: added EBCE, EASI with their elements in place and the Il Mio Domani pension fund. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QDIR` | Quadri di Direzione | € 3,186.49 | 2028-01-01 |
| `Q` | Quadri | € 2,895.91 | 2028-01-01 |
| `1` | 1° livello | € 2,486.32 | 2028-01-01 |
| `2` | 2° livello | € 2,225.94 | 2028-01-01 |
| `3S` | 3° livello Super | € 2,134.17 | 2028-01-01 |
| `3` | 3° livello | € 1,997.93 | 2028-01-01 |
| `4` | 4° livello | € 1,859.01 | 2028-01-01 |
| `5` | 5° livello | € 1,769.98 | 2028-01-01 |
| `6` | 6° livello | € 1,494.74 | 2028-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `QDIR` | € 52.00 |
| `Q` | € 47.00 |
| `1` | € 44.00 |
| `2` | € 40.00 |
| `3S` | € 36.00 |
| `3` | € 33.00 |
| `4` | € 30.00 |
| `5` | € 27.00 |
| `6` | € 24.00 |

## Apprenticeship

**professionalizzante_36** (type: `under_classification`)  
Destination levels: `2`, `3S`, `3`, `4`  
under-level: `1`

**professionalizzante_24** (type: `under_classification`)  
Destination levels: `5`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "ced-assoced/conditional_allowances_title_xxiii · base_salary · impact yes · open"
    Title XXIII: the daily meal benefit (Art. 179) is valued only when the caller supplies verified eligible days; the caller must check the absence of a canteen and a lunch break or split shift. Only caller-confirmed electronic vouchers are posted as exempt welfare; paper vouchers (different tax limits) remain unmodelled. The municipal public-transport subscription cost (Art. 180) and the episodic custody or transport of valuables above EUR 250 (Art. 181) remain unmodelled. Art. 177 was a conditional April 2025 one-off payment, not a Title XXIII allowance; it was repealed from September 2025.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** For paper meal vouchers establish taxable value and treatment. For Art. 180 supply the actual municipal-only monthly public-transport subscription cost and verify the employer's limited-traffic-zone address. For Art. 181 supply each non-continuous custody/transport assignment and delivered value above EUR 250; establish its wage and TFR treatment before posting. Do not recur the repealed Art. 177 April 2025 one-off.

!!! warning "ced-assoced/terziario_inps_rates_unverified · inps_employer · impact unknown · open"
    INPS terziario rates reused from 2026-terziario.json (same sector as H016). Verify against annual INPS circular for exact H601 sub-sector rate.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Verify the H601 sub-sector INPS rate against the annual INPS circular.

!!! warning "ced-assoced/maternity_holiday_scope · maternity_leave · impact yes · open"
    Art. 157 (p. 102) covers holidays during compulsory and optional absence. A Sunday holiday is paid by its own quota rather than topped up; 4 October, introduced after this text, remains excluded. Optional leave without an INPS indemnity is not topped up.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Resolve the Sunday holiday's separate quota and whether 4 October and unindemnified optional leave qualify.

!!! warning "ced-assoced/injury_rate_text_conflict · workplace_injury · impact yes · open"
    Art. 147 prints 75% (cento per cento) for ordinary injury integration after the waiting period. The numerical 75% is encoded; the contradictory words could indicate a 100% intended rate. Confirm with the signatories before using this target as definitive.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Obtain an authoritative clarification of the conflicting percentage in Art. 147.

!!! warning "ced-assoced/shift_allowances · shift_work · impact yes · open"
    SHIFT WORK (Title XI, Art. 111): in the CED with long, very long or h24 hours, 15% of the de facto hourly quota for the hours in shifts outside the normal schedule, and an allowance of 25% of the de facto pay for a fixed night or holiday shift. Not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the Art. 111 shift premiums (15% of the hourly quota, 25% allowance for fixed night or holiday shifts).

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

!!! warning "parental_income_condition · parental_leave · impact unknown · open"
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

!!! warning "pension_extra_deduction_first_employed · pension_fund_contribution · impact unknown · unsourced"
    A worker first employed after D.Lgs. 252/2005 came into force may deduct, in the twenty years after the fifth year of membership, the contributions above the annual cap within the room the first five years left, up to half the annual cap (art. 8 c. 6, as amended by L. 199/2025 from 1 July 2026). The request has no field for the first employment or the room left, and the sources searched set no rule for the withholding agent: a run whose contributions exceed the cap left deducts within the ordinary cap, and the worker may claim the rest in the tax return.

    **Applies when:** `pension_fund_contribution` applies; the run takes the engine code path.

    **Remediation:** Source whether and how the withholding agent grants the extra deduction at the conguaglio, add the worker's statement as an optional input and apply it, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.fondoeasi.it/fondo-easi/ccnl-ced-ced-ict-professioni-digitali-e-stp/stesura-ccnl-ced-09-marzo-2022.pdf | altro | 2022-03-09 | [↗](https://www.fondoeasi.it/fondo-easi/ccnl-ced-ced-ict-professioni-digitali-e-stp/stesura-ccnl-ced-09-marzo-2022.pdf) |
| https://www.redigo.info/ccnl-ced-ict-professioni-digitali-stp | tabella_retributiva | 2025-07-28 | [↗](https://www.redigo.info/ccnl-ced-ict-professioni-digitali-stp) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=62 | tabella_retributiva | 2025-07-28 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=62) |

??? note "Coverage notes"
    Salary model: paga base nazionale conglobata (Art. 172, 2022 stesura). Single TimeSeries per level, no separate contingenza or EDR.
    
    Unified classification covers CED, ICT, Professioni Digitali and STP workers (Art. 172 + Tabella A, one scale). No separate STP salary table exists in the 2022 stesura or 2025 renewal.
    
    Divisore convenzionale 173 h/month (Art. 171) and 26 d/month (Art. 170). Source: 2022 stesura fondoeasi.it.
    
    Mensilita supplementari: tredicesima (Art. 175) and quattordicesima (Art. 176). additional_months = 14.
    
    Indennita di funzione (Tabella A note, 2025 renewal): QDIR 287/296/306 EUR, Q 250/258/266 EUR per 14 mensilita. Tranche dates: 01/09/2025, 01/09/2026, 01/09/2027, distinct from base salary tranches.
    
    Apprenticeship (Art. 23-24, 2022 stesura, ccnlced.it allegato): under_classification. First half 2 levels below, second half 1 level below. Level 5 exception: stays at Level 6 throughout 24-month track. Destination L2 duration 36 months (studiocerbone.com: 240 h/36 months for 2° livello). Source ccnlced.it showed '6 months' for L2 — treated as parsing artifact; 36 months adopted from studiocerbone.com.
    
    Salary tranches: 01/09/2025 (source-confirmed, redigo.info and kitech.it), 01/06/2026 (source-confirmed, both sources agree), 01/03/2027 (redigo.info only, single-source), 01/01/2028 (redigo.info only, single-source).
    
    APPRENTICESHIP SCOPE (Art. 22, stesura 9 March 2022, p. 40): 'L'apprendistato professionalizzante è ammesso [...] per tutte le qualifiche e mansioni comprese nei livelli 2°, 3°S, 3°, 4° e 5°': the tracks cover exactly these destinations; levels 1, Q and QDIR take no apprentice. Level 6 is a pay level of the level 5 apprentices, not a destination.
    
    SCATTI (Art. 166, stesura 9 March 2022, p. 106): abrogated from 1 January 2019, they keep maturing for the staff in service on 31 December 2018: five biennial increments from the hire date, QDIR 52, Q 47, 1° 44, 2° 40, 3°S 36, 3° 33, 4° 30, 5° 27, 6° 24 EUR (parameters.seniority_increments.hired_until).
    
    PERMITS (Art. 119, stesura 9 March 2022, p. 86): 32 hours for the abolished holidays and 56 of ROL, 72 in the firms with more than 15 employees (authentic interpretation: 88 and 104 hours in all); for the workers hired after 9 March 2022 the ROL are 50% after two years and 100% after four (the norma transitoria keeps 104 hours for the staff in service before); a twelfth per whole month of service; not taken within the year paid with the retribuzione di fatto at the deadline or taken by 30 June of the next year, as the employer states (EmployerProfile.permit_carryover).
    
    LEAVE AT TERMINATION (Artt. 134, 170, 171): ferie in twelfths per month of service (the text gives no rule for a month in part), each day paid at the monthly pay over 26; the permit hours left at the hourly quota (1/173).
    
    HOLIDAY ON A SUNDAY (Art. 116 (Festivita), p. 85): a listed holiday falling on a Sunday pays a further daily quota (1/26 of the monthly pay); 4 November, celebrated on the first Sunday of November, takes the same treatment.
    
    OVERTIME AND ORDINARY PREMIUMS (stesura 9 March 2022): overtime 15% from the 41st to the 48th weekly hour, 20% beyond, 30% on holidays, 50% at night (24-6), not cumulative (Art. 104); holiday work as holiday overtime (Art. 117); rest-day work the premium of 30% alone (Art. 118); ordinary night work is forbidden outside the shift CED of Title XI (Art. 106). The bands previously had 30% for weekday overtime and no tier beyond the 48th hour.
    
    FUNDS (stesura 9 March 2022): EBCE (art. 221) 8 EUR by the employer and 3 by the worker a month for 14 months, every employee, in full for part time, else an element of 26 EUR for 14 months in the TFR base, not reproportioned; EASI (artt. 266-268) 15 + 2 EUR a month for the permanent workers, the fixed terms of more than 12 months and the apprentices, else an element of 36 EUR for 14 months in the TFR base; pension fund Il Mio Domani (art. 269) 1,55% by the employer and 0,55% by the enrolled worker of the TFR base.
    

## Raw data

The contract file this page is generated from: [`agreement/ced-assoced.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/ced-assoced.json).

## Usage example

```python
--8<-- "docs/examples/agreement/ced-assoced/example.py"
```
