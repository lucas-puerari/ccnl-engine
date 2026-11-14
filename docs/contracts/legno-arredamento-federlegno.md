# CCNL per i lavoratori dell'industria del legno, del sughero, del mobile, dell'arredamento e delle industrie affini (Federlegno-Arredo)

| | |
|---|---|
| **CNEL code** | `F051` |
| **Sector** | industria |
| **Family** | `legno-arredamento` |
| **Tax sector** | `industria` |
| **Last renewal** | 2023-06-20 |
| **Workers (est.)** | ~90k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federlegno-Arredo
    - Feneal-Uil
    - Filca-Cisl
    - Fillea-Cgil

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 17 verified / 88 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2023-06-20 |
| **Last review** | 2026-11-10 |
| **Latest salary tranche** | 2026-09-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 36 (ex 18) - Tredicesima mensilità (p. 86): "il lavoratore non in prova ha diritto a tanti dodicesimi dell'ammontare della tredicesima mensilità quanti sono i mesi di servizio prestato presso l'azienda. La frazione di mese superiore ai 15 giorni va considerata a questi effetti come mese intero.". Match: more_than 15. |
| 2026-10-18 | claude-opus-5-5 (ai) | The paga base (split model: base_salary excludes contingenza and EDR) of the 16 level codes for 1 July 2023, 1 January 2024 and 1 January 2025, derived from the minimi (paga base + contingenza + EDR) and per-level contingenza printed in the signed agreements of 20 June 2023 and 27 January 2025 between FederlegnoArredo and Feneal, Filca, Fillea (FILLEA-CGIL copies). | confirmed | No signatory document prints the paga base alone for these dates: the 20 June 2023 ipotesi (PDF p. 3) prints paga base al 31.12.2022, contingenza, EDR 10,33, minimi al 31.12.2022, aumento dal 1.07.2023 and nuovi minimi; the 27 January 2025 verbale (PDF p. 2) prints minimi anno 2024 and minimi dal 01-01-2025, stated to include paga base, contingenza and EDR non conglobati. The file's base_salary is the paga base (contingenza and EDR modelled separately), so every period is derived: 45 derived values, all equal to the file.<br>Level mapping: the tables group levels sharing a salary band (AE4/AS1, AC1/AS2, AC3/AC2/AS4); each code of a group takes the group's value, as in the file.<br>AS3, AE4 and AS1 at 2023-07-01: the 2023 table is off by one cent (paga base + aumento = 1.639,62 and 1.489,49, nuovi minimi - contingenza - EDR = 1.639,61 and 1.489,48); the 2024 IPCA increments (129,91 and 120,65 on the 2025 allegato) follow the printed minimi. Left unbacked; the maintainer should choose (the minimi-based 1639.61 / 1489.48 match the parties' later arithmetic).<br>Rule applied: a derived value with two conflicting derivation paths in the signed text is left unbacked (AS3, AE4, AS1 at 2023-07-01), even for one cent.<br>Level naming: the signed 2023 table labels the top row '12° AD3 (Quadri)', while the file's level descriptions and apprenticeship note call AC5 'quadri' (and model a function allowance for AD3). Values are unaffected; the descriptions should be checked.<br>The file is out of date: the ipotesi of the 2026-2028 renewal signed 3 September 2026 (FILLEA-CGIL copy, PDF pp. 52-53) grants from September 2026 an increase of 95,00 at AS1 (parametro 134) riparametrated on all levels and prints a new paga base dal 01-09-2026 per level (contingenza and EDR unchanged); from January 2027 a further 39,00 at AS1. The file's 2025-01-01 period is open-ended and lacks a 2026-09-01 period.<br>The ruleset names a document signed by FederlegnoArredo and the three unions (FILLEA-CGIL copy): source_type contracting_party. |
| 2026-11-07 | claude-opus-5-5 (ai) | Ipotesi of 3 September 2026: the minimi from 1 September 2026 (p. 53, page image). | corrected | The paga base rises from 1 September 2026 (AE1 +70.90 to 1,301.59, AD3 +148.88 to 2,685.16); contingenza and EDR unchanged. |
| 2026-11-08 | gpt-6-sol (ai) | CCNL top-ups of maternity and work injury, read from the signed text by a separate model session; every quote found on the PDF text layer. | confirmed | Added work_rules.insured_absence.maternity.<br>Added work_rules.insured_absence.injury. |
| 2026-11-08 | gpt-6-sol (ai) | Monthly values on scanned pages, each read twice from the page image by two independent sessions of another model, the second without being told the expected value. | confirmed | 32 values read identically by both readings and equal to the file. |
| 2026-11-08 | gpt-6-sol (ai) | Employer top-up of the INAIL indemnity, read from the signed text by a separate model session (audit of the injury rules); quote checked on the text layer or the page image. | corrected | The injury rule had no top-up of the INAIL indemnity; added: {"integration_rate": "1", "carenza_rate": "1"} |
| 2026-11-10 | claude-opus-5-5 (ai) | Third-period intermediate remuneration clause in the signed 2016 agreement and components of the tabular minimum in the signed 2026 renewal. | confirmed | The third period pays an intermediate retribuzione at the level below destination; the 2026 table prints base, contingenza and EDR in each minimum. Averaging the full tabular minimum gives AE3 to AE4 EUR 2209.26 in September 2026. The clause does not enumerate payslip components or personal superminima. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `AD3` | Management Area — Level 3 (top management) | € 2,685.16 | 2026-09-01 |
| `AD2` | Management Area — Level 2 | € 2,623.56 | 2026-09-01 |
| `AD1` | Management Area — Level 1 | € 2,496.99 | 2026-09-01 |
| `AC5` | Competency Area — Level 5 (quadri) | € 2,371.09 | 2026-09-01 |
| `AC4` | Competency Area — Level 4 | € 2,182.35 | 2026-09-01 |
| `AS4` | Specialist Area — Level 4 | € 1,993.55 | 2026-09-01 |
| `AC3` | Competency Area — Level 3 | € 1,993.55 | 2026-09-01 |
| `AC2` | Competency Area — Level 2 | € 1,993.55 | 2026-09-01 |
| `AS3` | Specialist Area — Level 3 | € 1,899.74 | 2026-09-01 |
| `AS2` | Specialist Area — Level 2 | € 1,804.61 | 2026-09-01 |
| `AC1` | Competency Area — Level 1 | € 1,804.61 | 2026-09-01 |
| `AS1` | Specialist Area — Level 1 | € 1,728.95 | 2026-09-01 |
| `AE4` | Executive Area — Level 4 (highly skilled workers) | € 1,728.95 | 2026-09-01 |
| `AE3` | Executive Area — Level 3 (skilled workers) | € 1,634.62 | 2026-09-01 |
| `AE2` | Executive Area — Level 2 (qualified workers) | € 1,540.24 | 2026-09-01 |
| `AE1` | Executive Area — Level 1 (general workers) | € 1,301.59 | 2026-09-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `AE1` | € 7.95 |
| `AE2` | € 8.53 |
| `AE3` | € 8.80 |
| `AE4` | € 9.09 |
| `AS1` | € 9.09 |
| `AC1` | € 10.76 |
| `AS2` | € 9.66 |
| `AS3` | € 10.22 |
| `AC2` | € 10.79 |
| `AC3` | € 10.79 |
| `AS4` | € 10.79 |
| `AC4` | € 11.92 |
| `AC5` | € 13.07 |
| `AD1` | € 13.92 |
| `AD2` | € 14.77 |
| `AD3` | € 14.77 |

## Apprenticeship

**professionalizzante_1** (type: `under_classification`)  
Destination levels: `AE3`, `AE4`

**professionalizzante_2** (type: `under_classification`)  
Destination levels: `AS1`, `AC1`

**professionalizzante_3** (type: `under_classification`)  
Destination levels: `AS2`, `AC4`

**professionalizzante_4** (type: `under_classification`)  
Destination levels: `AS3`, `AC3`

**professionalizzante_5** (type: `under_classification`)  
Destination levels: `AC2`

**professionalizzante_6** (type: `under_classification`)  
Destination levels: `AS4`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "legno-arredamento-federlegno/renewal_2026_ipotesi · base_salary · impact yes · open"
    RENEWAL 2026-2028 (ipotesi di accordo of 3 September 2026, pp. 52-53): the paga base from 1 September 2026 is modelled; the ipotesi is not yet a definitive text. Not modelled: the una tantum of December 2026 and the IPCA increases of 1 January 2027 and 2028, which the parties will set in later meetings.

    **Applies when:** `base_salary` applies; from 2026-09-01.

    **Remediation:** Check the definitive text, add the una tantum of December 2026 and the 2027 and 2028 tranches once set, then remove this note.

!!! note "apprenticeship_midpoint_allowances · base_salary · impact yes · resolved"
    A midpoint_to_destination period pays the mean of the whole monthly pay of the pay level and the destination level: base salary and every active fixed allowance (an allowance of one level counts as zero on the other); the base takes the rest of the rounded mean of the totals. A CCNL whose text leaves the averaged components open carries its own limitation <ccnl_id>/apprenticeship_midpoint_components, recorded on the midpoint path.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: CCNLs whose midpoint components are unsourced are tracked by their own apprenticeship_midpoint_components limitation.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! note "sickness_inps_daily_base · sickness · impact unknown · resolved"
    The INPS share of a sick day is computed on the INPS daily base of the episode, on the days INPS pays (the weekdays of an operaio, every day but the national holidays on a Sunday of an impiegato, point 7.3 of INPS circ. 134368/1981): the retribuzione media globale giornaliera of the month before the illness (INPS circ. 134368/1981 point 11; circ. 55/2024 Allegato 1), whole or partial month, impiegato or operaio, or for the lavoratori dello spettacolo the average pay of the last 40 daily contributions, capped for a fixed-term worker (INPS circ. 132/2021 par. 2.4). The base is a fact of the payroll history the episode states (SicknessEpisode.inps_base).

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Resolved: the INPS share is computed on the base of every regime of the bundle; an episode that states no base the engine can read has the missing_fact issue sickness_inps_base_unknown (fact inps_base), which blocks the run. Tests: tests/mutation/ccnl_engine/sickness/base/test_rules_wiring.py, tests/mutation/ccnl_engine/sickness/base/test_rules.py.

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

!!! note "tfr_compensation_apprentice_guarantee_fund · inps_employer · impact yes · resolved"
    An apprentice whose TFR goes to a pension fund or to the Fondo Tesoreria takes the 0.28-point relief of D.L. 203/2005 art. 8 and no Fondo di garanzia exemption: the 10% apprentice rate of L. 296/2006 art. 1 c. 773 is split by the D.M. 28 marzo 2007 among FPLD 9.01, CUAF 0.11, malattia 0.53, maternità 0.05 and INAIL 0.30, with no Fondo di garanzia share to exempt.

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the apprentice rate holds no Fondo di garanzia share, so none is exempted.

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

### Without monetary impact

!!! note ""
    APPRENTICESHIP under_classification (CCNL Legno, renewal 20/06/2023, CNEL F051 PDF): 1st period (0-12 months) two salary bands below destination; 2nd period (12-24) one band below; 3rd period (24-36) one band below with intermediate pay between current and destination level (midpoint_to_destination); then destination. The bands are AE1 | AE2 | AE3 | AE4-AS1 | AC1-AS2 | AS3 | AC2-AC3-AS4 | AC4 | AC5 | AD1 | AD2 | AD3; tracks group destinations sharing the same order offset. Modelled destinations: from AE3 to AC4; AE1/AE2 (no band two steps below), AC5 (quadri) and management area excluded.

!!! note ""
    LEVEL DESCRIPTIONS: the level description texts (e.g. 'Area Esecutiva — 1° livello') are placeholders generated by the engine based on area codes (AE/AS/AC/AD) and do not correspond to the official classification article texts of the CCNL. The text extracted from the CNEL F051 PDF did not include the official category names for each level code.

!!! note ""
    INTRA-BAND ORDERING: for levels sharing the same base pay (AE4/AS1, AC1/AS2, AC2/AC3/AS4), the relative order is assigned arbitrarily (ascending within the group) to satisfy the engine's order-uniqueness constraint. The CCNL does not define an internal hierarchy among levels within the same salary band. Functionally irrelevant — the validator only requires salary to be non-decreasing for ascending order.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.direzionelavoro.it/wp-content/uploads/2023/07/Legno-industria-CNEL-F051.pdf | altro | 2023-06-20 | [↗](https://www.direzionelavoro.it/wp-content/uploads/2023/07/Legno-industria-CNEL-F051.pdf) |
| https://www.lexplain.it/ccnl-legno-arredamento-industria/ | tabella_retributiva | — | [↗](https://www.lexplain.it/ccnl-legno-arredamento-industria/) |
| https://www.previdenza-professionisti.it/ccnl-legno-industria-scatti-anzianita/ | tabella_retributiva | — | [↗](https://www.previdenza-professionisti.it/ccnl-legno-industria-scatti-anzianita/) |
| CCNL Legno arredamento industria, ipotesi di accordo di rinnovo 3 settembre 2026 | associazione | 2026-09-03 | [↗](https://www.filcacisl.it/sindacato/wp-content/uploads/2026/09/contratto-legno-industria.pdf) |

??? note "Coverage notes"
    SALARY MODEL: split (paga base + contingenza + EDR). Base pay varies by tranche (Jul 2023, Jan 2024, Jan 2025). Contingenza frozen from 31/07/1992 (values from CNEL F051 PDF). EDR fixed at EUR 10.33 for all levels (Agreement 31/07/1992). Table sources: CNEL F051 PDF (renewal 20/06/2023); Jan 2024 tranche confirmed by lexplain.it; Jan 2025 tranche derived from the difference between the total from dottrinalavoro.it and contingenza+EDR.
    
    ADDITIONAL MONTHS: 13 mensilità (tredicesima). Source: CNEL F051 PDF, field 'Numero mensilità: 13'.
    
    CONTINGENZA: 12 salary bands for 16 level codes. Levels AE4 and AS1 share the same base pay and contingenza (band 4). Levels AC1 and AS2 share the same base pay and contingenza (band 5); AS2 has a different seniority increment from AC1. Levels AC2, AC3 and AS4 share the same base pay and contingenza (band 7). All contingenza values from CNEL F051 PDF.
    
    MANAGEMENT FUNCTION ALLOWANCE AD3: EUR 25.82/month, not included in the minimum pay table, modelled as a fixed_allowance for level AD3.
    
    INPS: industry sector rates from contribution/2026/industria.json (existing file reused). Employee 9.19% up to 15 employees, 9.49% above; employer (operai): up to 15 employees 30.68%, 16-50 employees 31.28%, >50 employees 31.58% (impiegati and quadri 28.46%, 29.06%, 29.36%). No substitute bilateral fund for CCNL Legno Industria (Fondimpresa for training only, does not affect INPS contribution rates) (review of 2026-10-30)
    
    APPRENTICESHIP MIDPOINT: the signed agreement of 13 December 2016, p. 35, sets third-period pay at the intermediate value between the current and destination categories. The signed 2026 renewal, p. 53, prints paga base, contingenza and EDR separately in each level's minimum. The engine averages both levels' entire tabular pay (base plus both fixed allowances); this is an interpretation of 'retribuzione', not an explicit enumeration of components in the apprenticeship clause. Personal superminima are not specified by this clause.
    
    APPRENTICE SENIORITY (Parte VII, Regolamentazione dell'apprendistato professionalizzante, p. 149 of the CCNL Legno industria, https://www.filcacisl.it/sindacato/wp-content/uploads/2022/04/Ccnl-Legno-Industria-definitivo1.pdf, sha256 591296abac43a018b9ffe08f60a521584129d9717e87a46583b8125a58d067bf): 'L’intero periodo di apprendistato professionalizzante è utile ai fini della maturazione dell’anzianità aziendale, anche ai fini degli aumenti periodici di anzianità; tali aumenti saranno corrisposti nelle misure previste dal livello di appartenenza': seniority_increments.apprentice_level_amount.
    
    HOURLY DIVISOR 174 (40h x 52 / 12 = 173.33, rounded up as used by the sector): no published hourly table in accessible primary sources; independent secondary sources converge on 174 (previdenza-professionisti.it). Daily coefficient 26 confirmed by the CNEL F051 PDF.
    
    SENIORITY: biennial cadence (24 months), maximum 5 increments; amounts from previdenza-professionisti.it (2025, unchanged since 2009). AS2 (9.66) and AC1 (10.76) have different increment amounts despite sharing the same base pay. valid_from 2023-07-01 assumed equal to the first tranche; the 2023 renewal did not modify seniority increments.
    

## Raw data

The contract file this page is generated from: [`agreement/legno-arredamento-federlegno.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/legno-arredamento-federlegno.json).

## Usage example

```python
--8<-- "docs/examples/agreement/legno-arredamento-federlegno/example.py"
```
