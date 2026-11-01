# CCNL Dipendenti da Proprietari di Fabbricati (Confedilizia)

| | |
|---|---|
| **CNEL code** | `H401` |
| **Sector** | portieri e custodi di condominio |
| **Family** | `servizi-immobiliari` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-10-30 |
| **Workers (est.)** | ~40k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Confedilizia
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
| **Limits of this contract** | base_salary, seniority |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🟢 Verified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 38 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-10-30 |
| **Last review** | — |
| **Latest salary tranche** | 2028-01-01 |

## Review history

No review is recorded.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `C3` | C3 — custode qualificato (qualified custodian, senior grade) | € 1,868.50 | 2028-01-01 |
| `B1` | B1 — portiere con mansioni di custodia (senior doorman with custody duties) | € 1,580.47 | 2028-01-01 |
| `C4` | C4 — custode (custodian, 40 h/week without accommodation) | € 1,573.72 | 2028-01-01 |
| `B2` | B2 — portiere (doorman/caretaker, standard profile) | € 1,502.58 | 2028-01-01 |
| `B3` | B3 — portiere part-time (part-time doorman/caretaker) | € 1,500.00 | 2028-01-01 |
| `D1` | D1 — addetto servizi speciali (special services worker) | € 1,498.07 | 2028-01-01 |
| `D2` | D2 — addetto servizi generali (general services worker) | € 1,496.70 | 2028-01-01 |
| `D3` | D3 — addetto servizi generali (general services worker) | € 1,496.70 | 2028-01-01 |
| `D4` | D4 — addetto servizi generali (general services worker) | € 1,496.70 | 2028-01-01 |
| `B4` | B4 — addetto pulizie aree comuni (common areas cleaner) | € 1,396.57 | 2028-01-01 |
| `B5` | B5 — pulitore/lavascale (cleaner/stair cleaner) | € 1,315.60 | 2028-01-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 12 increments

| Level | Increment (monthly) |
|---|---:|
| `B1` | € 17.30 |
| `B2` | € 15.57 |
| `B3` | € 15.57 |
| `B4` | € 13.84 |
| `B5` | € 10.38 |
| `C3` | € 16.67 |
| `C4` | € 13.33 |
| `D1` | € 10.00 |
| `D2` | € 10.00 |
| `D3` | € 10.00 |
| `D4` | € 10.00 |

## Apprenticeship

**professionalizzante_36** (type: `percentage`)  
Destination levels: `B1`, `B2`, `B4`, `C3`, `C4`, `D1`, `D3`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "portieri-fabbricati-confedilizia/c4_first_employment_rate · base_salary · impact yes · open"
    EXCLUDED PROFILES: A1-A9 (portieri con alloggio, 45 h or 48 h/week — divisor would be 195 or 208, incompatible with single CCNLParameters.hourly_divisor; also alloggio in-kind not modelled). C1 and C2 (preposti alla direzione tecnica o amministrativa — Art. 62 comma 2 exempts them from the 40 h ceiling; no fixed hourly divisor applies). C4 primo impiego (entry-rate sub-classification at EUR 1290.52/2026, transitional not permanent level).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the C4 primo impiego entry rate (EUR 1290.52 in 2026) as a separate level or a role-gated variant, or record a limitation.

!!! warning "portieri-fabbricati-confedilizia/apprenticeship_24_month_profiles · base_salary · impact yes · open"
    APPRENTICESHIP: percentage type per Art. 35-36 of the 2025 renewal. Art. 36 comma 6: 80% months 1-12, 85% months 13-24, 90% months 25-36. Two tracks exist: 36 months (B1, C3) and 24 months (B2, B4, C4, D1, D3). SIMPLIFICATION: all seven destinations use the single 36-month schedule; the five 24-month profiles are over-modelled by 12 months — an apprentice in those profiles is paid 90% during months 25-36 instead of 100%. Impact: slight under-payment for 1 year for 5 destination levels. B3, B5, D2, D4 have no CCNL apprenticeship provision; excluded from destination_levels.

    **Applies when:** `base_salary` applies; level in B2, B4, C4, D1, D3.

    **Remediation:** Add a professionalizzante_24 track (80% months 1-12, 85% months 13-24, 100% after) for B2, B4, C4, D1, D3 and keep professionalizzante_36 for B1 and C3; until then add a limitation for apprentices of these levels.

!!! warning "portieri-fabbricati-confedilizia/b5_short_schedule_premium · base_salary · impact yes · open"
    B5 PART-TIME NOTE: Art. 122 provides a 15% hourly premium for B5 (pulitori/lavascale) with weekly schedule below 8 hours. Not modelled (SIMPLIFICATION).

    **Applies when:** `base_salary` applies; level in B5.

    **Remediation:** Model the Art. 122 15% hourly premium for B5 with a weekly schedule below 8 hours (e.g. a conditional allowance on part_time_pct below 0.2), or record it as a limitation.

!!! warning "portieri-fabbricati-confedilizia/apprentice_seniority · seniority · impact unknown · open"
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

!!! warning "sickness_cumulation_window · sickness · impact unknown · open"
    The CCNL tier and the comporto are counted on the days of one episode and the relapses it continues. A CCNL that sums the sickness of separate episodes over a window (a calendar year, the last three years) can reach a lower tier or the end of the comporto earlier than the engine shows. The run is affected when an earlier episode outside the relapse chain is recorded. A CCNL whose comporto the engine counts over the calendar year (Commercio Art. 186 and the others with comporto_calendar_year) is not affected.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Add the cumulation window of each CCNL to its sickness rule, with the source, and count the tier and the comporto over it.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.confedilizia.it/retribuzioni-dipendenti-da-proprietari-di-fabbricati/ | tabella_retributiva | 2025-10-30 | [↗](https://www.confedilizia.it/retribuzioni-dipendenti-da-proprietari-di-fabbricati/) |
| https://lexplain.it/ccnl-dipendenti-portieri-fabbricati-aumenti-stipendio/ | tabella_retributiva | — | [↗](https://lexplain.it/ccnl-dipendenti-portieri-fabbricati-aumenti-stipendio/) |

??? note "Coverage notes"
    RENEWAL 2025: CCNL signed 2025-10-30. Normative provisions from 2025-11-01; economic provisions (salary tranches) from 2026-01-01. Contract expiry 2028-10-31. Signatories: Confedilizia + FILCAMS-CGIL, FISASCAT-CISL, UILTuCS.
    
    CONGLOBATED MINIMUMS: base_salary values are the monthly conglobated tabular minimums (paga base + contingenza rolled in), as published by Confedilizia at confedilizia.it/retribuzioni-dipendenti-da-proprietari-di-fabbricati. fixed_allowances is empty for all levels. Back-calculation: B1 2026 = 1519.10 / 173 = 8.78 EUR/h; C3 2026 = 1795.94 / 173 = 10.38 EUR/h; D1 2026 = 1439.90 / 173 = 8.32 EUR/h — consistent divisor confirmed.
    
    HOURLY DIVISOR: 173 h/month (40 h/week x 52/12). Applicable to profiles B (B1-B5), C3, C4, D (D1-D4) per Art. 60 (B profiles), Art. 62 comma 1 (C3/C4), Art. 69 commi 1-2 (D profiles) — all 40 h/week standard schedule.
    
    SALARY TRANCHES: three annual steps — 2026-01-01, 2027-01-01, 2028-01-01 — as published on Confedilizia official table (3-column layout: 2026, 2027, 2028). D1 is a separate row (1439.90/1468.70/1498.07); D2-D3-D4 share a combined row (1438.58/1467.35/1496.70), confirmed by parsing raw HTML from confedilizia.it.
    
    SENIORITY INCREMENTS: 36-month cadence (triennale), maximum 12 scatti per Art. 111-114. Art. 114 sets 12 scatti triennali for D profiles. D-profile scatto = 10.00 EUR (all D levels identical, per Art. 114; source: lexplain.it/scatti-di-anzianita-contratto-portieri-custodi-e-proprietari-di-fabbricati). B/C amounts from same source.
    
    ADDITIONAL MONTHS: 13 (tredicesima only — Art. 130 'Gratifica natalizia'). Art. 130 provides tredicesima in December equal to one monthly salary; no quattordicesima provision exists in this CCNL. Confirmed via ilccnl.it full CCNL text and targeted search.
    
    INPS: uses 2026-terziario.json (same tax_sector as commercio-confcommercio and turismo-federalberghi).
    

## Raw data

The contract file this page is generated from: [`agreement/portieri-fabbricati-confedilizia.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/portieri-fabbricati-confedilizia.json).

## Usage example

```python
--8<-- "docs/examples/agreement/portieri-fabbricati-confedilizia/example.py"
```
