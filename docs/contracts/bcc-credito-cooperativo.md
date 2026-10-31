# CCNL per i lavoratori delle Banche di Credito Cooperativo, Casse Rurali ed Artigiane

| | |
|---|---|
| **CNEL code** | `J271` |
| **Sector** | credito |
| **Family** | `credito` |
| **Tax sector** | `credito` |
| **Last renewal** | 2024-07-09 |
| **Workers (est.)** | ~33k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federcasse
    - FABI
    - FIRST-CISL
    - FISAC-CGIL
    - UGL Credito
    - UILCA

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, inps_employer, seniority |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 36 verified / 7 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-07-09 |
| **Last review** | 2026-10-31 |
| **Latest salary tranche** | 2026-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-14 | claude-opus-5-5 (ai) | Second review of the credito group: stipendio of the eleven levels in the three tranches, scatti, number of monthly payments, against the testo coordinato signed on 19 December 2024. | corrected | The 33 stipendi match Allegato A (p. 149) except two 2026 values, one cent off: 3ª Area 1° livello 2742.35 corrected to 2742.34, 2ª Area 2° livello 2572.10 corrected to 2572.11.<br>13 monthly payments: verified (Art. 46, tredicesima; no further monthly payment in the text).<br>Scatti: amounts match Allegato A; at most 8 for the 1st and 2nd level of the quadri, not 12: the 12 apply only to staff in service on 31 December 1997 (Art. 101). Corrected; the 1997 cohort is noted.<br>The FABI URL of the text no longer serves the PDF; the same signed text is cited from its Eutekne reproduction.<br>Not reviewed here: the hourly pay of Art. 114 (90.66% of one twelfth of the annual pay, divided by 160) and the overtime rates, which stay derived. |
| 2026-10-31 | claude-opus-5-5 (ai) | The comporto and the sick pay of the CCNL counted over several illnesses (work_rules.sickness_rules), read on the signed text. | corrected | Art. 55 (p. 75) of the testo coordinato signed on 19.12.2024: the job and the whole pay are kept 6, 8, 12, one month per year up to 18, or 22 months by seniority, summing the absences of the 18 months before. The file kept 180 days of one illness: corrected to a cumulation over 18 months with ten seniority bands. The FABI copy cited before returns 404; the Eutekne copy of the same signed text is cited. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QD4` | Executive Managers - 4th pay level | € 5,160.06 | 2026-01-01 |
| `QD3` | Executive Managers - 3rd pay level | € 4,396.88 | 2026-01-01 |
| `QD2` | Executive Managers - 2nd pay level | € 3,965.48 | 2026-01-01 |
| `QD1` | Executive Managers - 1st pay level | € 3,743.21 | 2026-01-01 |
| `3AP4` | 3rd Professional Area - 4th pay level | € 3,341.90 | 2026-01-01 |
| `3AP3` | 3rd Professional Area - 3rd pay level | € 3,059.49 | 2026-01-01 |
| `3AP2` | 3rd Professional Area - 2nd pay level | € 2,890.41 | 2026-01-01 |
| `3AP1` | 3rd Professional Area - 1st pay level | € 2,742.34 | 2026-01-01 |
| `2AP2` | 2nd Professional Area - 2nd pay level | € 2,572.11 | 2026-01-01 |
| `2AP1` | 2nd Professional Area - 1st pay level | € 2,406.80 | 2026-01-01 |
| `1AP` | 1st Professional Area - single level | € 2,241.53 | 2026-01-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `QD4` | € 95.31 |
| `QD3` | € 95.31 |
| `QD2` | € 41.55 |
| `QD1` | € 41.55 |
| `3AP4` | € 41.55 |
| `3AP3` | € 41.55 |
| `3AP2` | € 41.55 |
| `3AP1` | € 41.55 |
| `2AP2` | € 35.57 |
| `2AP1` | € 29.07 |
| `1AP` | € 20.12 |

## Apprenticeship

**terza_area** (type: `under_classification`)  
Destination levels: `3AP1`, `3AP2`, `3AP3`, `3AP4`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "bcc-credito-cooperativo/art3_derogation_apprenticeship · base_salary · impact unknown · open"
    Apprenticeship (Art. 30) modelled for destination levels 3AP1-3AP4: months 0-18 one level below the destination, then the destination level. The Art. 3 comma 3 derogation (higher destination level) is assumed to follow the same 18-month rule.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Confirm that the Art. 3 comma 3 derogation follows the 18-month rule.

!!! warning "bcc-credito-cooperativo/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "bcc-credito-cooperativo/inps_sector_rates_unsourced · inps_employer · impact unknown · open"
    INPS RATES: the employer and worker INPS rates of the sector (credito) are totals no 2026 INPS or association table confirms: the only component split found is the INPS guide of 2012 and the 2026 totals come from a software house page that does not prove its year. The contributions of every run rest on them.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Source the credito rates of 2026 on an INPS or association table, mark the inps block of contribution/2026/credito.json derived, then remove this note.

!!! warning "bcc-credito-cooperativo/pre_1998_cohort_scatti · seniority · impact yes · open"
    SCATTI: at most 8 for the 1st and 2nd level of the quadri direttivi and for the aree professionali, 7 for the 3rd and 4th level of the quadri (Art. 101, Art. 113). Staff in service on 31 December 1997 keep 12 scatti (9 for the 3rd and 4th level of the quadri) plus a further periodic increase: the engine applies the limits of later hires, so a run for that cohort past the 8th (7th) scatto needs the extra amounts as a fixed input.

    **Applies when:** `seniority` applies.

    **Remediation:** Model the 12 (9) scatti and the further periodic increase of staff in service on 31/12/1997 as a hire-date-gated maximum, or open a limitation naming the individual-element workaround.

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
| https://apilavoro.eutekne.it/v1/notizie/allegato/f571390d-5db7-457d-bde1-59ed2112e1e9/CCNL%2009.07.2024.pdf/download | altro | 2024-07-09 | [↗](https://apilavoro.eutekne.it/v1/notizie/allegato/f571390d-5db7-457d-bde1-59ed2112e1e9/CCNL%2009.07.2024.pdf/download) |
| https://www.fabi.it/wp-content/uploads/2025/01/CCNL-BCC-testo-coordinato-19-dicembre-2024.pdf | altro | 2024-07-09 | [↗](https://www.fabi.it/wp-content/uploads/2025/01/CCNL-BCC-testo-coordinato-19-dicembre-2024.pdf) |
| https://www.kitech.it/tabelle-retributive/banche-credito-cooperativo/ | tabella_retributiva | 2024-07-09 | [↗](https://www.kitech.it/tabelle-retributive/banche-credito-cooperativo/) |

??? note "Coverage notes"
    Salary model is conglobated (stipendio per Art. 112 replaces paga base + scala mobile + EDR + other components). Modelled as base_salary with fixed_allowances: [].
    
    First period valid_from set to 2024-09-01 (first tranche date per Allegato A). Pre-tranche salaries belong to the previous CCNL and are not modelled.
    
    Seniority (Art. 113): first scatto after 4 years (48 months), then every 36 months; maximum 8 scatti for the Aree Professionali and the 1st and 2nd level of the Quadri Direttivi, 7 for the 3rd and 4th level (Art. 101), via maximum_count_by_level; 12 (9) only for the staff in service on 31 December 1997 (review of 2026-10-30).
    
    Hourly divisor 160 in both periods per Art. 114 (rounding down to the nearest multiple of 5): 37.5h x 52 / 12 = 162.5 → 160 (pre-July 2025); 37h x 52 / 12 = 160.33 → 160 (from July 2025, Art. 118).
    
    Workers covered: approximately 36,000 (Federcasse / Banche di Credito Cooperativo, Casse Rurali ed Artigiane). Agreement signed 2024-07-09; valid until 2025-12-31 per Art. 9.
    
    INPS rates from 2026-credito.json (same sector as bancari-abi). IRPEF 2026 brackets applied (L. 199/2025).
    

## Raw data

The contract file this page is generated from: [`agreement/bcc-credito-cooperativo.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/bcc-credito-cooperativo.json).

## Usage example

```python
--8<-- "docs/examples/agreement/bcc-credito-cooperativo/example.py"
```
