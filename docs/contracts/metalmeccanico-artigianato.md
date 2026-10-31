# CCNL Metalmeccanica e Installazione di Impianti — Artigianato

| | |
|---|---|
| **CNEL code** | `C030` |
| **Sector** | metalmeccanico |
| **Family** | `metalmeccanica` |
| **Tax sector** | `artigianato` |
| **Last renewal** | 2024-11-19 |
| **Workers (est.)** | ~350k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Confartigianato Imprese
    - CNA
    - Casartigiani
    - CLAAI
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
| **Limits of this contract** | base_salary, bilateral_funds, inps_employer, overtime, sickness |

6 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 38 verified / 43 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-11-19 |
| **Last review** | 2026-10-15 |
| **Latest salary tranche** | 2026-11-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-14 | claude-opus-5-5 (ai) | P1 audit: the tabellare of the Metalmeccanica ed Installazione di Impianti sector for the four tranches of the renewal of 19 November 2024 (verbale integrativo of 25 November 2024), and the term; comparison with the industrial CCNL. | corrected | The 32 tabellari of the four tranches (1 December 2024 to 1 November 2026, eight levels) match the signed table of p. 27: verified.<br>The tabellare 'fino al 30 novembre 2024' (with the AFAC of 21 December 2023) matches the period from 1 April 2024; its start date is not in this scan and stays derived.<br>Term: 1 January 2023 to 31 December 2026, then until the next renewal (Art. 2). review_due 2027-01-31.<br>The tredicesima is stated in the new unified article of the renewal (p. 16) and no quattordicesima appears: the number of monthly payments, 13, moves from assumed to derived (the period starts in 2022, before the renewal). |
| 2026-10-15 | claude-opus-5-5 (ai) | Registry check: CNEL code, name, signatories and term against the 21st CNEL report of CCNLs in force (30 June 2025) and the term clause of the text read in the P1 review. | confirmed | CNEL C030 matches (the Confartigianato and CNA categories, Casartigiani, CLAAI with FIM, FIOM, UILM).<br>Term: 'Il presente CCNL decorre dal 1° gennaio 2023 e avrà validità fino al 31 dicembre 2026' (Art. 2), the same in the report. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'scatti di anzianità, indennità e altri elementi fissi': the scatti and fixed allowances of the file against the text read in the P1 review. | corrected | The renewal of 19 November 2024 (Art. 27, p. 6) gives apprentices scatti of 10 euro from 1 January 2025, accrued from that date also by apprentices already in service, so none before: the apprentice_seniority limitation is resolved with seniority_increments.apprentice_amount 0.00 until 2024 and 10.00 from 2025.<br>The per-level scatti amounts (1Q 32,94 to 6 18,40), the 24-month cadence and the 5-scatti maximum are not restated in the renewal: they stay derived from the 2021 text. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'straordinario, notturno, festivo, turni e maggiorazioni cumulabili': the overtime bands and the night, holiday and shift premiums of the file against the text read in the P1 review. | flagged | The overtime rates could not be read from a party text: the EBNA copy of the 2021 CCNL returns an HTML page and the 2024 renewal does not restate them. A summary (direzionelavoro, p. 3) adds Saturday overtime at 25% for the first 3 hours and 50% after, not modelled, and other summaries give night overtime at 55% against the 45% of the file. Runs with overtime are blocked until the article is read. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'part-time, tempo determinato, apprendistato e periodo di prova': the apprenticeship tracks and the part-time supplementary hours of the file against the text read in the P1 review. | corrected | The operai track matches the ten semesters of Art. 27 (p. 6). The impiegati track paid yearly averages (77% for months 13-24, 87% for months 25-36): the text pays 75, 80, 85 and 90% by semester. Corrected.<br>The 24-month track of the centralinisti (70, 70, 75, 80%) is not modelled apart: noted. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'fondi sanitari, previdenza complementare, bilateralità e quote a carico di lavoratore e datore': the pension, health and bilateral contributions of the file against the text read in the P1 review. | flagged | No pension, health or bilateral contribution is modelled; EBNA, FSBA, San.Arti and the pension fund are declared. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'scatti di anzianità, indennità e altri elementi fissi', re-read on the full text published by a party, found on 15 October 2026. | confirmed | Scatti: the eight amounts, the 24-month cadence and the maximum of 5 match Art. 60 and 71 for the workers hired after 27 November 1997: verified. The pre-1998 mechanism is noted. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'straordinario, notturno, festivo, turni e maggiorazioni cumulabili', re-read on the full text published by a party, found on 15 October 2026. | corrected | Art. 22 (p. 84): straordinario 25% and straordinario festivo 45% match; straordinario notturno is 55%, not 45%: corrected; the rates apply to the retribuzione di fatto (hourly base gross_incl_allowances) and do not cumulate (night holiday 55%). The unconfirmed-rates limitation is resolved; the Saturday rule and the ordinary night and holiday work are declared. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'ferie, permessi, festività, assenze, malattia e comporto', re-read on the full text published by a party, found on 15 October 2026. | corrected | Sickness of the operai (Art. 61, pp. 137-138): top-up to 100% of the net pay from the fourth day (from the first past 7 days), for at most 150 days; the file paid 100% from the first day for 180 days: corrected. The impiegati rule of Art. 73 (p. 147) is declared by category.<br>Ferie 160 hours, 20 days (Art. 58, p. 133): verified. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'fondi sanitari, previdenza complementare, bilateralità e quote a carico di lavoratore e datore': the amounts of the declared contributions, read on the full text published by a party. | confirmed | Bilateralità 11,65 euro a month, FSBA 0,45% + 0,15%, San.Arti 10,42 euro a month and the E.a.r. of 30 and 25 euro read on pp. 30-32: the declared limitation now states every amount. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1Q` | Level 1Q — quadri: high-responsibility managerial functions | € 2,106.03 | 2026-11-01 |
| `1` | Level 1 — white-collar employees with managerial functions | € 2,106.03 | 2026-11-01 |
| `2` | Level 2 — conceptual tasks or high technical specialisation | € 1,959.57 | 2026-11-01 |
| `2bis` | Level 2 bis — specialised tasks, high operative autonomy | € 1,850.31 | 2026-11-01 |
| `3` | Level 3 — qualified tasks with operative autonomy | € 1,779.22 | 2026-11-01 |
| `4` | Level 4 — qualified operative tasks, partial operative autonomy | € 1,676.98 | 2026-11-01 |
| `5` | Level 5 — simple tasks with minimal operative autonomy | € 1,615.17 | 2026-11-01 |
| `6` | Level 6 — elementary operations without autonomy | € 1,540.21 | 2026-11-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1Q` | € 32.94 |
| `1` | € 32.94 |
| `2` | € 29.08 |
| `2bis` | € 26.13 |
| `3` | € 24.29 |
| `4` | € 21.72 |
| `5` | € 20.24 |
| `6` | € 18.40 |

## Apprenticeship

**operai** (type: `percentage`)  
Destination levels: `5`, `4`, `3`, `2bis`  
percentage: 1.00

**impiegati** (type: `percentage`)  
Destination levels: `2`, `1`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "metalmeccanico-artigianato/inps_sector_rates_unsourced · inps_employer · impact unknown · open"
    INPS RATES: the employer and worker INPS rates of the sector (artigianato) are totals no 2026 INPS or association table confirms: the only component split found is the INPS guide of 2012 and the 2026 totals come from a software house page that does not prove its year. The contributions of every run rest on them.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Source the artigianato rates of 2026 on an INPS or association table, mark the inps block of contribution/2026/artigianato.json derived, then remove this note.

!!! warning "metalmeccanico-artigianato/apprentice_inps_rates_unsourced · inps_employer · impact unknown · open"
    APPRENTICE INPS RATES: the apprentice rates of the sector (artigianato) apply the 10% of L. 296/2006 art. 1 c. 773 plus the 1.61% NASpI, but no source found settles whether the 0.91 NASpI reduction of the artisan employers also applies to apprentices, nor the wage-integration contribution they owe (the FSBA is paid outside INPS). The contributions of an apprentice may differ.

    **Applies when:** `inps_employer` applies; contract type in apprentice.

    **Remediation:** Source the apprentice rates of artigianato (an INPS circular or an association table of 2026), mark the apprentice block of contribution/2026/artigianato.json derived, then remove this note.

!!! warning "metalmeccanico-artigianato/centralinisti_apprenticeship · base_salary · impact yes · open"
    APPRENTICESHIP (Art. 27 as renewed on 19 November 2024, signed scan p. 6, by semester on the retribuzione tabellare of the destination level): operai of the 1st and 2nd group 70, 70, 75, 78, 80, 85, 88, 92, 100, 100%; impiegati amministrativi 70, 70, 75, 80, 85, 90%; impiegati centralinisti 70, 70, 75, 80%, not modelled apart (their destination level is not distinguished).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add an 'impiegati_centralinisti' track (70, 70, 75, 80% by semester, then 100%) selectable by Apprentice.track.

!!! warning "metalmeccanico-artigianato/health_and_bilateral_funds · bilateral_funds · impact yes · open"
    HEALTH AND BILATERAL FUNDS (EBNA text, Art. 11-12, pp. 30-32): bilateralità artigiana 11,65 euro a month for 12 months from the employer, also for part-time and apprentices, plus FSBA 0,45% from the employer and 0,15% from the worker of the INPS base (from 1 January 2022), or 30 euro a month for 13 months paid to the worker by a firm outside the bilateral system; San.Arti 10,42 euro a month for 12 months from the employer, or an E.a.r. of 25 euro a month for 13 months when the firm does not enrol. Not modelled: the worker's 0,15% lowers the net pay.

    **Applies when:** `bilateral_funds` applies.

    **Remediation:** Pass the contributions as bilateral fund events, or model them per worker.

!!! warning "metalmeccanico-artigianato/artisan_saturday_overtime · overtime · impact yes · open"
    SATURDAY OVERTIME AND ORDINARY NIGHT AND HOLIDAY WORK: in a five-day week Saturday overtime is paid 25% for the first 3 hours and 50% after; ordinary night work is paid 15% and holiday work 45% (Art. 22, p. 84). The request has no Saturday kind and the bands hold only the overtime rates.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a Saturday kind with the 3-hour threshold, and bands for ordinary night and holiday work.

!!! warning "metalmeccanico-artigianato/artisan_impiegati_sickness · sickness · impact yes · open"
    SICKNESS OF THE IMPIEGATI: Art. 73 (p. 147) pays the impiegati the whole pay for 2 months and half for the next 4 up to 5 years of service, the whole for 3 months and half for the next 5 above; the file applies the operai rule of Art. 61.

    **Applies when:** `sickness` applies; category in impiegato, quadro.

    **Remediation:** Model the Art. 73 bands for the impiegati by category.

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

!!! warning "notice_indemnity_tfr · termination_notice · impact unknown · open"
    The notice indemnity enters the TFR base as payroll practice holds; art. 2120 c. 2 c.c. counts the sums paid 'a titolo non occasionale' and no primary source read settles whether this indemnity is among them, so the TFR quota of the termination run may be overstated.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source the TFR treatment of the notice indemnity (case law of the Cassazione or a Ministry ruling) and apply it, then resolve this limitation.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.ebna.it/wp-content/uploads/2022/01/CCNL-artigianato-metalmeccanico-2021.pdf | altro | 2021-12-17 | [↗](https://www.ebna.it/wp-content/uploads/2022/01/CCNL-artigianato-metalmeccanico-2021.pdf) |
| https://www.kitech.it/tabelle-retributive-metalmeccanici-artigianato/ | tabella_retributiva | 2024-11-19 | [↗](https://www.kitech.it/tabelle-retributive-metalmeccanici-artigianato/) |
| https://www.eblart.it/scheda-ccnl-artigianato-metalmeccanici/ | tabella_retributiva | — | [↗](https://www.eblart.it/scheda-ccnl-artigianato-metalmeccanici/) |
| https://www.direzionelavoro.it/ccnl-metalmeccanici-artigianato-tabelle-retributive/ | tabella_retributiva | — | [↗](https://www.direzionelavoro.it/ccnl-metalmeccanici-artigianato-tabelle-retributive/) |

??? note "Coverage notes"
    CONGLOBATED MINIMUMS: base_salary values are conglobated minimum pay figures, incorporating base pay, contingenza and EDR in a single amount. Conglobation confirmed in force from 16.06.2011 (source: EBNA CCNL 17.12.2021, Art. 28 and attached tables). fixed_allowances is empty for all levels.
    
    2022 TRANCHES: three tranches CCNL 17.12.2021 (01.01.2022, 01.05.2022, 01.12.2022). Per-level increments verified against EBNA/Direzionelavoro.it. Values at 01.12.2022 confirmed from EBNA primary source.
    
    AFAC TRANCHES: Accordo Fondo Anticipazione Contrattuale 21.12.2023, two tranches (01.12.2023, 01.04.2024). Values at 01.04.2024 cross-verified against kitech.it for all 8 levels.
    
    2024 RENEWAL TRANCHES: agreement 19.11.2024 (operative 20.12.2024), four tranches (01.12.2024, 01.07.2025, 01.03.2026, 01.11.2026). All per-level amounts for all 8 levels confirmed from UILM national synthesis PDF (20250128 CCNL Artigianato area meccanica 2023-2026, url: https://www.uilmnazionale.it/). Values match kitech.it for levels verified there. All 4 tranches fully modelled with primary-source amounts.
    
    HOURLY DIVISOR: 173 hours/month (40h/week, Art. 28 CCNL 17.12.2021). Arithmetic monthly/hourly verification did not yield clean integer results on the available values; confirmation is based on the primary CCNL text.
    
    SENIORITY INCREMENTS: biennial, at most 5, fixed amounts of Art. 60 and 71 for the workers without a scatto on 27 November 1997 (EBNA text pp. 135-136, 143-145). Workers with earlier scatti keep the 5% mechanism and the maxima at 30 June 2000 (181,79 for the Primo livello to 101,22 for the Sesto), not modelled.
    
    APPRENTICESHIP percentage, 10 semesters (60 months max), operai progression (source EBLART, apprenticeship professionalizzante article): 70% (sem. I-II), 75% (III), 78% (IV), 80% (V), 85% (VI), 88% (VII), 92% (VIII), 100% (IX-X); track 'operai' for destinations 5, 4, 3, 2bis. Since the 2015 reform level 6° cannot be used as a destination.
    
    INPS OPERAI/IMPIEGATI: 2026-artigianato.json models both categories via employer_rate_by_category (operai default 26.93%; impiegati/quadri 24.71%). Pass Employee(category='impiegato') or Employee(category='quadro') to receive the lower rate; omitting category routes to operaio rate. Components: IVS 23.81% + NASpI 1.61% + CUAF 0.68% + malattia operai ~0.83% = 26.93%; malattia for impiegati is lower (hence ~24.71%). No CIGO/CIGS (D.Lgs. 148/2015 Art. 3, artigianato excluded). FSBA (0.45% employer + 0.15% employee) is bilateral, excluded from the tax file.
    
    ADDITIONAL MONTHS: 13 (tredicesima). A quattordicesima is not provided for by the CCNL Artigianato Metalmeccanico.
    
    APPRENTICESHIP administrative impiegati (destination levels 2, 1): 3 years, by semester 70, 70, 75, 80, 85 and 90% (Art. 27 as renewed on 19 November 2024), 100% thereafter. Track 'impiegati'. Level 1Q (quadro) excluded. Source: CCNL metalmeccanico artigianato renewal 17.12.2021 (EBLART summary); formazione-apprendistato.com; conflavoro.it 2021 summary; renewal of 19 November 2024 (review of 2026-10-30)
    
    APPRENTICE SENIORITY: apprentices accrue no scatti before 1 January 2025; from that date they accrue scatti of 10 euro each, not scaled by the apprentice percentage, on the cadence of the other workers, and those in service on that date accrue from it ('la maturazione dell'anzianità di servizio ai fini del riconoscimento degli scatti decorre da pari data', Art. 27 as renewed on 19 November 2024, signed scan p. 6). At the end of the apprenticeship the matured scatti are revalued to the amount of the final level.
    
    TERM: the renewal of 19 November 2024 runs from 1 January 2023 to 31 December 2026 (Art. 2, signed scan) and keeps applying until the next renewal takes effect; the tabellare of 1 November 2026 stays in force after 2026 until a renewal is read.
    

## Raw data

The contract file this page is generated from: [`agreement/metalmeccanico-artigianato.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/metalmeccanico-artigianato.json).

## Usage example

```python
--8<-- "docs/examples/agreement/metalmeccanico-artigianato/example.py"
```
