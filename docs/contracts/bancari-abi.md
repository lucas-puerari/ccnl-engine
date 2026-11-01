# CCNL per i lavoratori dipendenti dalle aziende di credito (ABI)

| | |
|---|---|
| **CNEL code** | `J241` |
| **Sector** | credito |
| **Family** | `credito` |
| **Tax sector** | `credito` |
| **Last renewal** | 2023-11-23 |
| **Workers (est.)** | ~270k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ABI
    - FABI
    - FIRST-CISL
    - FISAC-CGIL
    - UILCA
    - UNISIN

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, inps_employer, overtime, seniority, sickness |

8 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 43 verified / 2 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2023-11-23 |
| **Last review** | 2026-10-31 |
| **Latest salary tranche** | 2026-03-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-14 | claude-opus-5-5 (ai) | P1 audit: stipendio of the nine levels in the four tranches, scatti, number of monthly payments and term, against the renewal of 23 November 2023. | corrected | The 36 stipendi match the tables to the cent; they were cited to a union news page and are now verified against the tables of the renewal (pp. 35-38).<br>The first tranche runs from 1 July 2023 (the tables), not from the signing date 23 November 2023: corrected.<br>13 monthly payments: verified ('Importi mensili per 13 mensilità').<br>Scatti amounts match; cadence and maximum counts not in the tables: derived.<br>Importo ex ristrutturazione not modelled: declared. The agreement expired on 31 March 2026 (Art. 1). |
| 2026-10-15 | claude-opus-5-5 (ai) | Registry check: CNEL code, name, signatories and term against the 21st CNEL report of CCNLs in force (30 June 2025) and the term clause of the text read in the P1 review. | confirmed | CNEL J241 matches (ABI with FABI, FIRST CISL, FISAC CGIL, UILCA, UNISIN; the report adds Intesa Sanpaolo as a depositor).<br>Term: Art. 1 of the renewal 'scadrà [...] il 31 marzo 2026'. The report shows 31/12/2028, which no text or party source supports; the parties suspended the deadlines to 31 July 2026 and the renewal is still open. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'straordinario, notturno, festivo, turni e maggiorazioni cumulabili': the overtime bands and the night, holiday and shift premiums of the file against the text read in the P1 review. | flagged | The overtime bands (25%, 55% night, 65% holiday) stay derived: the CCNL of 19 December 2019 that sets them is not published by a party in full, and the renewal of 23 November 2023 does not amend them. The hourly base of the ABI CCNL was not read: the BCC CCNL computes it on 90.66% of one twelfth of the annual pay, which the engine does not apply. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'scatti di anzianità, indennità e altri elementi fissi', re-read on the full text published by a party, found on 15 October 2026. | corrected | Scatti: the 48-month first scatto, the 36-month cadence and the maxima (8; 7 for QD3 and QD4) match Art. 94 and 103: verified. The freeze of 1 January 2013 - 31 July 2014 (Art. 103 c. 3) is declared. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'straordinario, notturno, festivo, turni e maggiorazioni cumulabili', re-read on the full text published by a party, found on 15 October 2026. | corrected | Art. 114 c. 15 (p. 152): 25% weekday and 55% night match; 65% is the night overtime of the rest days and festività, not the daytime holiday overtime: moved to night_holiday. Art. 115 (p. 153): holiday work 30% and rest-day work 25%: added; the daytime holiday band was 65%, corrected. Saturday 30% and the 1/360 / 7,4 hourly base are declared. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'ferie, permessi, festività, assenze, malattia e comporto', re-read on the full text published by a party, found on 15 October 2026. | corrected | Sickness (Art. 66, p. 101): full pay for 6 to 24 months by seniority, not a flat 180 days: modelled on the 48-month count of c. 2 with six seniority bands; the c. 1 count and the extended periods are declared.<br>Ferie (Art. 60, p. 89): 20/22/25 days of the aree match; the quadri have 26 (noted). Tredicesima accrual: a fraction of month counts (Art. 51, p. 77): verified. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'part-time, tempo determinato, apprendistato e periodo di prova', re-read on the full text published by a party. | corrected | Art. 36 (p. 53): one level below for 18 months, then the destination; all 3a area profiles are destinations: 3A1 added (from 1e2A); the apprenticeship_destination_levels limitation is resolved. |
| 2026-10-17 | claude-opus-5-5 (ai) | Periodic review due 2026-12-31: the stipendi from 2023 and the scatti against the CCNL ABI of 23 November 2023, the hourly divisor, and the readiness of the file. | flagged | The 36 stipendi of the nine levels from 2023 and the scatti (QD4 and QD3 95,31, QD2 to 3A1 41,55, 1a and 2a area 29,07) are printed in the texts read. Match.<br>Flagged: the hourly divisor of the file (162, then 160) has no provenance. Art. 114 c. 15 of the testo coordinato computes the paga oraria 'secondo il comune criterio (1/360 della retribuzione annua per ogni giornata diviso 7,4)': on thirteen monthly payments the monthly pay over 204,92, not over 160. Every amount the engine derives from the hourly divisor (absence deductions, the hourly rate of the overtime bands) is affected; the elements of the 'retribuzione annua' were not read.<br>Not promoted to reviewed: verification.confidence is unverified and the hourly divisor is unsourced. The two derived rules (the solidarity fund rates and the absence rule) stay derived. |
| 2026-10-31 | claude-opus-5-5 (ai) | The sick pay and the comporto of the CCNL (work_rules.sickness_rules), read on the signed text. | corrected | Art. 66 (p. 99): c. 1 keeps the job and the whole pay for 6, 8, 12, 15, 18, 22 months by seniority; c. 2 lets the bank count instead over the 48 months before the last day, with 8 to 24 months. The file stored the option of c. 2 as the rule: corrected to the bands of c. 1 for one illness, the option of c. 2 in the note. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QD4` | Executive Managers - 4th level | € 5,160.06 | 2026-03-01 |
| `QD3` | Executive Managers - 3rd level | € 4,396.88 | 2026-03-01 |
| `QD2` | Executive Managers - 2nd level | € 3,965.48 | 2026-03-01 |
| `QD1` | Executive Managers - 1st level | € 3,743.21 | 2026-03-01 |
| `3A4` | 3rd Professional Area - 4th level | € 3,341.90 | 2026-03-01 |
| `3A3` | 3rd Professional Area - 3rd level | € 3,059.49 | 2026-03-01 |
| `3A2` | 3rd Professional Area - 2nd level | € 2,890.41 | 2026-03-01 |
| `3A1` | 3rd Professional Area - 1st level | € 2,742.34 | 2026-03-01 |
| `1e2A` | 1st and 2nd Professional Area (Unified Area) | € 2,479.45 | 2026-03-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `QD4` | € 95.31 |
| `QD3` | € 95.31 |
| `QD2` | € 41.55 |
| `QD1` | € 41.55 |
| `3A4` | € 41.55 |
| `3A3` | € 41.55 |
| `3A2` | € 41.55 |
| `3A1` | € 41.55 |
| `1e2A` | € 29.07 |

## Apprenticeship

**terza_area** (type: `under_classification`)  
Destination levels: `3A1`, `3A2`, `3A3`, `3A4`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! note "bancari-abi/inps_credit_rate_unverified · inps_employer · impact unknown · resolved"
    INPS employer_rate 26.76% flat from kitech.it (Credito e Assicurazioni 2026); the Fondo di solidarietà del credito (bilateral) is presumed included in the aggregate rate. Verify against the annual INPS circular.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Resolved as a duplicate of bancari-abi/inps_sector_rates_unsourced, which stays open (review of 2026-10-30): both say the credito employer rate is not confirmed by a 2026 INPS source. contribution/2026/credito.json now takes 26.76 from the INPS 2012 table and keeps the Fondo di solidarietà out of the totals, in parameters.solidarity_fund.

!!! warning "bancari-abi/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "bancari-abi/inps_sector_rates_unsourced · inps_employer · impact unknown · open"
    INPS RATES: the employer and worker INPS rates of the sector (credito) are totals no 2026 INPS or association table confirms: the only component split found is the INPS guide of 2012 and the 2026 totals come from a software house page that does not prove its year. The contributions of every run rest on them.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Source the credito rates of 2026 on an INPS or association table, mark the inps block of contribution/2026/credito.json derived, then remove this note.

!!! warning "bancari-abi/ex_ristrutturazione_amount · seniority · impact yes · open"
    IMPORTO EX RISTRUTTURAZIONE: the tables of the renewal print, next to the scatto, an 'importo ex ristrutturazione' (14,30 for QD3 and QD4, 7,99 for QD1, QD2 and the 3a Area, 5,59 for the Area Unificata); the bundle does not pay it. TERM: the renewal of 23 November 2023 expires on 31 March 2026 (Art. 1); the tables stay those of March 2026 until a renewal is read.

    **Applies when:** `seniority` applies.

    **Remediation:** Source who receives the importo ex ristrutturazione and model it with the scatti, then remove this note.

!!! warning "bancari-abi/scatti_freeze_2013_2014 · seniority · impact yes · open"
    SCATTI FREEZE 2013-2014: no seniority for the scatti and the importo ex ristrutturazione accrues from 1 January 2013 to 31 July 2014 (Art. 103 c. 3, testo coordinato p. 142); staff in service on 19 December 1994 keep 12 scatti (Art. 94 c. 2, Art. 103 c. 2). The engine counts the seniority of the request without the freeze.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** State the seniority of a worker in service in 2013-2014 net of the 19 months of the freeze.

!!! warning "bancari-abi/abi_saturday_overtime_and_hourly_base · overtime · impact yes · open"
    OVERTIME, SATURDAY AND HOURLY BASE: Saturday overtime is paid 30% (Art. 114 c. 15), and the request has no Saturday kind. The hourly pay of overtime and of holiday work is 1/360 of the annual pay for each day divided by 7,4 (Art. 114 c. 15): the hourly divisor carries the 360 x 7,4 / 13, but the engine applies it to the minimo tabellare, and the elements of the 'retribuzione annua' (scatti and other fixed items) were not read.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a Saturday kind and read the elements of the annual pay that art. 114 c. 15 divides.

!!! warning "bancari-abi/abi_sickness_counting · sickness · impact yes · open"
    SICKNESS COUNTING: Art. 66 c. 1 keeps the job and the whole pay for 6, 8, 12, 15, 18 or 22 months by seniority; c. 2 lets the employer count instead the 48 months before the last day of absence, with 8, 10, 14, 18, 22 or 24 months. The file applies c. 2; an employer counting by c. 1 pays fewer months. The periods rise by 50% for tbc, AIDS and disabilità grave and double for oncological illness (cc. 4-5), not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a fact for the counting the employer adopts and the extended periods of Art. 66 cc. 4-5.

!!! warning "bancari-abi/apprentice_net_equivalent_allowance · base_salary · impact yes · open"
    APPRENTICESHIP (Art. 36, testo coordinato p. 53): the apprentice of a 3a area profile is placed one level below the destination for the first 18 months, then paid the destination level 'con assegno temporaneo, corrispondente, al netto'; at most 3 years. Every 3a area level is a destination: an apprentice to 3A1 starts at the Area unificata (1e2A). The assegno equals the destination in net terms; the engine pays the destination gross.

    **Applies when:** `base_salary` applies; level in 3A1, 3A2, 3A3, 3A4.

    **Remediation:** Model the assegno temporaneo as the gross that gives the destination-level net under the apprentice contribution rates, or open a limitation stating the overpayment.

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

!!! warning "una_tantum_readings · base_salary · impact unknown · open"
    The una tantum of a renewal is paid from the CCNL data with readings no text read settles in full: a month of service in the covered period counts with the days of the una tantum (15 when the text is silent), over the months of the period; the absences of a month do not reduce it, though a text may pay the months 'di effettiva prestazione'; a part time is paid in proportion to its hours; a run without the employment period is paid none; the share of the covered months of earlier years is taxed apart as arrears.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source the counting of the months, the part time and the taxation of each una tantum from its agreement, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.first-cisl.it/rinnovo-ccnl-bancari-2023/ | altro | 2023-11-23 | [↗](https://www.first-cisl.it/rinnovo-ccnl-bancari-2023/) |
| https://www.ccnlbancari.it/ | tabella_retributiva | — | [↗](https://www.ccnlbancari.it/) |

??? note "Coverage notes"
    Hourly divisor 207,69 for the 37.5h/week period (2023-11-23 to 2024-06-30) and 204,92 from 2024-07-01 (37h/week): 360 x daily hours / 13 (Art. 114 c. 15, Art. 108).
    
    Seniority: first scatto after 48 months, then every 36 months; maximum 8 scatti for the Aree Professionali and 7 for QD3/QD4 (maximum_count_by_level).
    
    Apprenticeship: https://www.ccnlbancari.it/ Art. 35, post-rinnovo 2023-11-23.
    

## Raw data

The contract file this page is generated from: [`agreement/bancari-abi.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/bancari-abi.json).

## Usage example

```python
--8<-- "docs/examples/agreement/bancari-abi/example.py"
```
