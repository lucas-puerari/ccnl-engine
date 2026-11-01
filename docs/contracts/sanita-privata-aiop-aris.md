# CCNL Case di Cura Private - Personale Non Medico (AIOP/ARIS)

| | |
|---|---|
| **CNEL code** | `T011` |
| **Sector** | Sanità privata |
| **Family** | `socio-sanitario` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2020-10-08 |
| **Workers (est.)** | ~150k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - AIOP
    - ARIS
    - FP-CGIL
    - CISL-FPS
    - UIL-FPL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, overtime, seniority |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 36 verified / 1 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2020-10-08 |
| **Last review** | 2026-10-17 |
| **Latest salary tranche** | 2020-07-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-14 | claude-opus-5-5 (ai) | P1 audit: Tabella 1 of the CCNL of 8 October 2020 for the 28 positions, the number of monthly payments and the term. | corrected | The 28 monthly tabellari match column D of Tabella 1 (p. 104) to the cent: verified.<br>13 monthly payments: verified ('x 13 mensilità', column C).<br>No renewal after the CCNL of 8 October 2020 was found; the table stays in force (ultrattività). Seniority, overtime, absence and sickness rules are not re-read in this pass. |
| 2026-10-15 | claude-opus-5-5 (ai) | Registry check: CNEL code, name, signatories and term against the 21st CNEL report of CCNLs in force (30 June 2025) and the term clause of the text read in the P1 review. | corrected | CNEL T011 matches. Signatories corrected: the text of 8 October 2020 is signed by AIOP and ARIS with FP-CGIL, CISL-FPS and UIL-FPL only (the report adds UGL Sanità); FILCAMS, FISASCAT, UILTuCS, FIALS and CISAL Sanità were listed by mistake.<br>Term: 'Decorrenza: 1° gennaio 2016 - Scadenza: 31 dicembre 2018' (Art. 4), the same in the report; the CCNL applies in ultrattività. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'straordinario, notturno, festivo, turni e maggiorazioni cumulabili': the overtime bands and the night, holiday and shift premiums of the file against the text read in the P1 review. | corrected | Art. 59 (p. 89): daytime overtime is paid at 20%, not 15%: corrected. Night or holiday overtime 30% and night-holiday overtime 50% match. All four bands verified; the hourly quota is the monthly pay over 26 and 6 (Art. 58), the divisor 156 of the file.<br>Art. 60-61: the night and holiday shift indemnities, the on-call indemnity and the radiation risk indemnity were neither modelled nor declared: declared as an outside-input limitation. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'ferie, permessi, festività, assenze, malattia e comporto': the leave, accrual, absence and sickness rules of the file against the text read in the P1 review. | corrected | Sickness (Art. 43, pp. 58-60): the employer tops up to 100% of the retribuzione globale from the first day up to the 365th day of absence in four years, within a comporto of 540 days in a rolling four years, net of what the worker would have received working. The file paid 50% in the waiting days and 75% after, up to 180 days: corrected and verified.<br>Ferie (Art. 32, p. 42): 30 working days plus 4 days for the festività soppresse, 34 in all (was 30): corrected and verified.<br>Absence divisor 26 (Art. 58, p. 88) and the tredicesima accrual of more than 15 days (Art. 66, p. 96, was assumed): verified. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'part-time, tempo determinato, apprendistato e periodo di prova': the apprenticeship tracks and the part-time supplementary hours of the file against the text read in the P1 review. | corrected | Apprenticeship (p. 31): only the 36-month track (85% then 90%) was modelled; the 18-month and 24-month tracks are added. An apprentice now names the track.<br>Part-time supplementary hours are paid at 15% (Art. 22, p. 25): declared, the request cannot state them.<br>Probation and fixed-term rules carry no amount the engine computes. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'fondi sanitari, previdenza complementare, bilateralità e quote a carico di lavoratore e datore': the pension, health and bilateral contributions of the file against the text read in the P1 review. | confirmed | The CCNL of 8 October 2020 sets no contractual pension, health or bilateral contribution: Art. 74 only confirms the will to institute a supplementary pension. None is modelled. |
| 2026-10-17 | claude-opus-5-5 (ai) | Periodic review due 2026-12-31: the minimi of every level against the CCNL of 8 October 2020, the status of the renewal, and the readiness of the file. | confirmed | The 28 minimi of the file are printed in the CCNL of 8 October 2020. Match.<br>No renewal of the CCNL 2016-2018 was signed by 2026-10-17: the unions report a contract in ultrattività and a dispute open in January 2026 (FP CGIL, letter to the Ministry of Health and the Conferenza delle Regioni); the 2020 tables stay in force.<br>Not promoted to reviewed: verification.confidence is unverified, the level records are derived from a CCNL text of 2020 with an aggregator as second source, and shift_on_call_allowances and part_time_supplementary_rate are open. The derived rule stays derived. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `E2` | Categoria E — progressione orizzontale 2 | € 3,554.39 | 2020-07-01 |
| `E1` | Categoria E — progressione orizzontale 1 | € 2,936.33 | 2020-07-01 |
| `DS4` | Categoria DS — progressione orizzontale 4 | € 2,418.05 | 2020-07-01 |
| `E` | Categoria E — quadro / specialista | € 2,410.22 | 2020-07-01 |
| `DS3` | Categoria DS — progressione orizzontale 3 | € 2,345.38 | 2020-07-01 |
| `DS2` | Categoria DS — progressione orizzontale 2 | € 2,261.56 | 2020-07-01 |
| `D4` | Categoria D — progressione orizzontale 4 | € 2,209.98 | 2020-07-01 |
| `DS1` | Categoria DS — progressione orizzontale 1 | € 2,180.26 | 2020-07-01 |
| `D3` | Categoria D — progressione orizzontale 3 | € 2,147.12 | 2020-07-01 |
| `DS` | Categoria DS — coordinatore | € 2,101.08 | 2020-07-01 |
| `D2` | Categoria D — progressione orizzontale 2 | € 2,084.77 | 2020-07-01 |
| `C4` | Categoria C — progressione orizzontale 4 | € 2,076.38 | 2020-07-01 |
| `D1` | Categoria D — progressione orizzontale 1 | € 2,022.94 | 2020-07-01 |
| `C3` | Categoria C — progressione orizzontale 3 | € 1,984.10 | 2020-07-01 |
| `D` | Categoria D — professionista sanitario | € 1,953.87 | 2020-07-01 |
| `C2` | Categoria C — progressione orizzontale 2 | € 1,921.25 | 2020-07-01 |
| `C1` | Categoria C — progressione orizzontale 1 | € 1,857.14 | 2020-07-01 |
| `C` | Categoria C — operatore qualificato | € 1,803.61 | 2020-07-01 |
| `B4` | Categoria B — progressione orizzontale 4 | € 1,733.54 | 2020-07-01 |
| `B3` | Categoria B — progressione orizzontale 3 | € 1,697.76 | 2020-07-01 |
| `B2` | Categoria B — progressione orizzontale 2 | € 1,669.36 | 2020-07-01 |
| `B1` | Categoria B — progressione orizzontale 1 | € 1,624.54 | 2020-07-01 |
| `A4` | Categoria A — progressione orizzontale 4 | € 1,592.19 | 2020-07-01 |
| `B` | Categoria B — operatore tecnico-pratico | € 1,579.86 | 2020-07-01 |
| `A3` | Categoria A — progressione orizzontale 3 | € 1,566.67 | 2020-07-01 |
| `A2` | Categoria A — progressione orizzontale 2 | € 1,544.35 | 2020-07-01 |
| `A1` | Categoria A — progressione orizzontale 1 | € 1,506.44 | 2020-07-01 |
| `A` | Categoria A — ausiliario generico | € 1,467.45 | 2020-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**Apprendistato professionalizzante 18 mesi** (type: `percentage`)  
Destination levels: `A`, `B`, `C`, `D`  
percentage: 0.90

**Apprendistato professionalizzante 24 mesi** (type: `percentage`)  
Destination levels: `A`, `B`, `C`, `D`  
percentage: 0.90

**Apprendistato professionalizzante 36 mesi** (type: `percentage`)  
Destination levels: `A`, `B`, `C`, `D`  
percentage: 0.90

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "sanita-privata-aiop-aris/frozen_individual_seniority · seniority · impact yes · open"
    Retribuzione individuale di anzianità frozen at 1993-12-31 per Art. 56 (no new seniority accruals). Modelled as seniority_increments.maximum_count=0.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Let the caller state the RIA frozen at 1993-12-31 (EarnedIncrements or an individual allowance) and record the limitation.

!!! warning "sanita-privata-aiop-aris/statutory_ipca_adjustment · base_salary · impact unknown · open"
    CCNL applied in ultrattività; Decreto Lavoro 2026 introduced a statutory 30% IPCA auto-adjustment if no renewal within 12 months of expiry. If triggered, legally applicable 2026 minimums may exceed the 2020 Tabella 1 values modelled here. Engine models contractual tables only.

    **Applies when:** `base_salary` applies.

    **Remediation:** Verify whether the statutory IPCA adjustment applies to T011 under ultrattività and model it, or record the limitation.

!!! warning "sanita-privata-aiop-aris/shift_on_call_allowances · overtime · impact yes · open"
    SHIFT, ON-CALL AND RISK ALLOWANCES (Art. 60-61, pp. 89-90): the indennità notturna of 2,74 euro an hour of shift between 22 and 6, the holiday shift indemnity of 17,82 euro (8,91 for half a shift or less), the pronta disponibilità of 21,69 euro per 12 hours and the radiation risk indemnity of 1.239,50 euro a year are not modelled: no field of the request states the shifts or the on-call duty of the worker.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the Art. 60-61 indemnities with facts naming the night and holiday shift hours and the on-call turns of the worker.

!!! warning "sanita-privata-aiop-aris/part_time_supplementary_rate · overtime · impact yes · open"
    PART-TIME SUPPLEMENTARY HOURS: the ore supplementari of a part-time worker are paid with 15% of the retribuzione oraria globale (Art. 22, CCNL 8 October 2020, p. 25). OvertimeKind.SUPPLEMENTARY exists, but the file has no supplementary-hours band: the event takes the overtime bands unless the caller passes the multiplier (review of 2026-10-30).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the supplementary-hours band (15%) of Art. 22.

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
| Official CCNL text signed 2020-10-08; salary tables in Tabella 1 effective 2020-07-01 per Art. 51; values conglobated (EADR included per Art. 55) | altro | 2020-10-08 | [↗](https://www.fondazionerimed.eu/wp-content/uploads/2023/12/CCNL-CASE-DI-CURA-PRIVATE-08.10.2020.pdf) |
| CNEL registry entry confirming code T011, 146585 employees, ARIS/AIOP signatories | cnel | — | [↗](https://www.contratticcnl.it/ccnl/t011/) |

??? note "Coverage notes"
    CCNL signed 2020-10-08; nominally covers 2016-2018 (Art. 4). Applied in ultrattività from 2019 onwards. Salary tables (Tabella 1) effective 2020-07-01 per Art. 51. No renewal signed as of 2026-09-09. Confirmed 2026-09-09: preintesa June 2020 is the last event; all 2023-2025 bridge agreements found refer to the separate AIOP RSA contract (different CNEL code). The AIOP-ARIS ospedaliero (T011) T011 remains in pure ultrattività.
    
    Salary values are conglobated: EADR incorporated into tabellare from 2020-07-01 per Art. 55. Back-calculation: A 1467.45×13=19076.85 ✓; C4 2076.38×13=26992.94 ✓; DS4 2418.05×13=31434.65 ✓.
    
    28 levels (A, A1–A4, B, B1–B4, C, C1–C4, D, D1–D4, DS, DS1–DS4, E, E1, E2). Order assigned by 2020-07-01 salary because professional families A/B/C/D/DS/E have overlapping salary ranges — categories are not a single hierarchy. A4 (order 6) is paid above B (order 5) per Tabella 1. Horizontal progressions within each category are modelled as static levels per Art. 48; the engine does not auto-advance a worker's level after the contractual service threshold.
    
    CCNL covers ospedalieri, IRCCS, riabilitazione (AIOP/ARIS members). Does not apply to RSA governed by separate AIOP RSA or Uneba agreements.
    
    hourly_divisor=156 (Art. 58: paga giornaliera=monthly/26, oraria=giornaliera/6 for 36h/week). Levels D4, DS4, E, E1, E2 work 38h/week per Art. 18 (oraria=giornaliera/6.33, exact divisor≈164.6), modelled as 156 uniformly.
    
    Apprenticeship (Art. 23 §14, Art. 23 §2): destination levels are the four category entry positions A, B, C, D only. Horizontal-progression steps (A1-A4, B1-B4, C1-C4, D1-D4) are not apprenticeship destinations. DS and E categories excluded per Art. 23 §2. OSS and Albo-registered health professions excluded per Art. 23 §2 but per-qualification restriction not modellable at level granularity.
    
    INPS: terziario sector, 2026-terziario.json: employee 9.36% (up to 5 employees), 9.46% (6-15), 9.76% (above 15); employer 29.31%, 29.51% and 30.11% on the same tiers. Private healthcare (AIOP/ARIS) is classified under terziario standard rates; no healthcare-specific INPS regime applies. INPS Circolare n. 6/2026 confirms the 9.19% IVS employee rate for private sector workers. (review of 2026-10-30)
    
    TERM: the CCNL of 8 October 2020 renews the economic part 2016-2018 and its table applies from 1 July 2020; no later renewal signed by AIOP and ARIS was found on 14 October 2026 (the unions were still asking to open the table), so the 2020 tabellari stay in force under ultrattività.
    
    APPRENTICESHIP (CCNL 8 October 2020, apprendistato professionalizzante, point 14, p. 31): 85% of the pay of the qualifica da conseguire, then 90%, by the length of the contract: months 1-9 and 10-12 for up to 18 months (the text does not state months 13-18, which keep 90%), 1-12 and 13-24 for up to 24 months, 1-18 and 19-36 for up to 36 months. Three tracks: set Apprentice.track. Apprentices accrue no seniority 'a nessun fine'.
    
    CNEL code T011 verified at https://www.contratticcnl.it/ccnl/t011/ (146585 employees, ARIS/AIOP, ATECO 86).
    

## Raw data

The contract file this page is generated from: [`agreement/sanita-privata-aiop-aris.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/sanita-privata-aiop-aris.json).

## Usage example

```python
--8<-- "docs/examples/agreement/sanita-privata-aiop-aris/example.py"
```
