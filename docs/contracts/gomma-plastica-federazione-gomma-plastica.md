# CCNL Gomma e Plastica Industria (Federazione Gomma Plastica)

| | |
|---|---|
| **CNEL code** | `B371` |
| **Sector** | gomma-plastica |
| **Family** | `chimica` |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~90k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federazione Gomma Plastica
    - FILCTEM-CGIL
    - FEMCA-CISL
    - UILTEC-UIL

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

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 70 verified / 7 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | — |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2028-12-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The TEM minimi of the ten levels against the minimi tables of the renewals of 26 January 2023 (2023-2025) and 10 December 2025 (2026-2028), both published by FILCTEM-CGIL. | corrected | Rinnovo 26 gennaio 2023 (signed scan with the integration of 2 February 2023, PDF p. 15, read on the page image): Art. 17 c. 3 prints the minimi of levels I-Q from 1/1/2023, 1/1/2024 and 1/4/2025. The 30 values of the file match.<br>Rinnovo 10 dicembre 2025: the signed ipotesi (45-page scan, PDF p. 31) states only the level F increment (60 from 1/01/2026, 60 from 1/04/2027, 60 from 1/04/2028, 15 from 1/12/2028); FILCTEM-CGIL publishes the per-level table of Art. 17 as a separate one-page file, which prints the minimi of the ten levels on the four dates and the per-level increments. The 40 values of the file were derived parametrically from level F; 11 differ by one or two cents from the printed table and are corrected.<br>The file's base_salary is the conglobated TEM (Art. 17 Paragrafo A), the same item the tables print. The ruleset names a source published by FILCTEM-CGIL, a signatory: source_type contracting_party.<br>Corrected to the printed table: I 2027-04-01: 1662.67 -> 1662.66; I 2028-04-01: 1710.60 -> 1710.59; I 2028-12-01: 1722.59 -> 1722.57; G 2028-04-01: 1995.28 -> 1995.27; E 2027-04-01: 2136.42 -> 2136.43; E 2028-04-01: 2198.02 -> 2198.03; E 2028-12-01: 2213.42 -> 2213.43; D 2028-04-01: 2290.45 -> 2290.44; D 2028-12-01: 2306.50 -> 2306.49; B 2028-04-01: 2350.47 -> 2350.48; B 2028-12-01: 2366.94 -> 2366.95. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Q — senior manager grade (quadro under L. 190/1985), highest responsibility | € 2,664.67 | 2028-12-01 |
| `A` | A — quadro, highly specialised technical or functional expert | € 2,508.94 | 2028-12-01 |
| `B` | B — technical or administrative manager, high professional grade | € 2,366.95 | 2028-12-01 |
| `C` | C — department head, white-collar employee with operational autonomy | € 2,335.85 | 2028-12-01 |
| `D` | D — team leader, qualified technical/administrative employee | € 2,306.49 | 2028-12-01 |
| `E` | E — highly skilled worker, expert technical employee | € 2,213.43 | 2028-12-01 |
| `F` | F — skilled worker, technical employee (CCNL reference level) | € 2,156.12 | 2028-12-01 |
| `G` | G — qualified worker 2nd category, white-collar employee | € 2,009.25 | 2028-12-01 |
| `H` | H — qualified worker 1st category, clerical staff | € 1,916.08 | 2028-12-01 |
| `I` | I — elementary tasks, simple operations with brief training | € 1,722.57 | 2028-12-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 20.14 |
| `A` | € 18.59 |
| `B` | € 16.53 |
| `C` | € 16.53 |
| `D` | € 16.53 |
| `E` | € 13.94 |
| `F` | € 13.94 |
| `G` | € 13.43 |
| `H` | € 11.88 |
| `I` | € 10.33 |

## Apprenticeship

**professionalizzante** (type: `under_classification`)  
Destination levels: `G`, `F`, `E`, `D`, `C`, `B`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "gomma-plastica-federazione-gomma-plastica/q_allowance_2023_unverified · base_salary · impact unknown · open"
    Q LEVEL INDENNITA' DI FUNZIONE 50.00 EUR/month (quadri ex L. 190/1985), cross-verified at April 2025 (lexplain.it total 2473.68 vs contratticcnl.it TEM 2423.68). valid_from set to 2023-01-01 for consistency with the first modelled tranche; not verified whether the amount was already 50 EUR in 2023.

    **Applies when:** `base_salary` applies; level in Q; before 2025-04-01.

    **Remediation:** Source the Q indennità di funzione in force from 2023-01-01 to 2025-03-31.

!!! warning "gomma-plastica-federazione-gomma-plastica/apprenticeship_period_boundaries · base_salary · impact unknown · open"
    APPRENTICESHIP under_classification (art. apprendistato professionalizzante CCNL Gomma e Plastica; rule from contratticcnl.it: the apprentice cannot be classified more than two levels below the destination). Track 'professionalizzante' for destinations G, F, E, D, C, B: 0-12 months two levels below, 12-24 one level below, then destination. The 12/12 boundaries are an approximation (no public monthly table). H (only one level below exists), I, A and Q are not modelled as destinations.

    **Applies when:** `base_salary` applies; contract type in apprentice; level in B, C, D, E, F, G.

    **Remediation:** Source the monthly apprenticeship table and correct the 12/12 period boundaries.

!!! warning "gomma-plastica-federazione-gomma-plastica/apprentice_seniority · seniority · impact unknown · open"
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

!!! warning "personal_withholding_same_kind · personal_withholdings · impact unknown · open"
    Two garnishments of the same kind, or two salary assignments, share the measure of their kind (a fifth, or the tenth or seventh of the agente della riscossione) in the order of notification: art. 545 c. 4 c.p.c. sets 'un quinto per i tributi ... ed in eguale misura per ogni altro credito' and art. 5 DPR 180/1950 a cessione 'fino al quinto', but no text read says how two orders of the same kind split the measure, so the later order may be under- or overstated.

    **Applies when:** `personal_withholdings` applies; the run takes the engine code path.

    **Remediation:** Source how the employer splits the measure between two orders of the same kind (art. 499 c.p.c. on the intervention of creditors, case law of the Cassazione) and apply it, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.lexplain.it/tabelle-retributive-gomma-plastica/ | tabella_retributiva | — | [↗](https://www.lexplain.it/tabelle-retributive-gomma-plastica/) |
| https://www.contratticcnl.it/gomma-plastica/tabelle-retributive/ | tabella_retributiva | 2025-12-10 | [↗](https://www.contratticcnl.it/gomma-plastica/tabelle-retributive/) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=156 | tabella_retributiva | 2026-01-01 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=156) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (TEM — Trattamento Economico Minimo). All base_salary values incorporate paga base, contingenza, and EDR in a single figure. Evidence: the F/level coefficient ratio is stable to 4 decimal places across all 4 tranches (2023-2026), which is only possible in a fully parametric (conglobated) system. fixed_allowances is empty for all levels except Q.
    
    CONGLOBATED CHECK: coefficient ratios computed as level_value / F_value for all tranches. Q/F=1.2359, A/F=1.1636, B/F=1.0978, C/F=1.0834, D/F=1.0697, E/F=1.0266, G/F=0.9319, H/F=0.8887, I/F=0.7989 — identical across 01.01.2023, 01.01.2024, 01.04.2025, 01.01.2026. This confirms conglobated model.
    
    TRANCHE DATES 01.01.2023, 01.01.2024, 01.04.2025, 01.01.2026 from lexplain.it and kitech.it. Future tranches 01.04.2027, 01.04.2028, 01.12.2028 from the rinnovo 10.12.2025 (ipotesi accordo PDF uniolex.com, confirmed by fiscoetasse.com, paserio.it, edotto.com): F +60, +60, +15. Other levels derived parametrically via the stable coefficients documented in CONGLOBATED CHECK — math verified ±0.01 EUR across all 3 tranches and all 10 levels.
    
    SENIORITY amounts unchanged across 01.01.2023, 01.01.2024, 01.04.2025, 01.01.2026: the January 2023 rinnovo and December 2025 rinnovo both addressed only TEM (minimi tabellari) and left Art.23 (scatti di anzianità) untouched. Amounts at kitech.it/lavoro-economia.it apply from at least 01.01.2023 onward. Source: rinnovo 10.12.2025 full text (filctemcgil.it); rinnovo Jan 2023 summary (terzomillennio.uil.it); no source reports scatti change in either rinnovo.
    
    INPS: reuses 2026-industria.json (Confindustria/CIGO). Federazione Gomma Plastica is a member of Confindustria; CIGO applicable pursuant to D.Lgs. 148/2015.
    
    ADDITIONAL MONTHS: 13 (tredicesima). A quattordicesima is not provided for by the CCNL Gomma e Plastica Industria.
    
    HOURLY DIVISOR 173 derived from the standard formula (40h/week x 52 / 12 = 173.33 rounded to 173); secondary sources (contratticcnl.it, fiscoetasse.com) confirm the 40h week but the contractual clause was not retrieved directly.
    

## Raw data

The contract file this page is generated from: [`agreement/gomma-plastica-federazione-gomma-plastica.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/gomma-plastica-federazione-gomma-plastica.json).

## Usage example

```python
--8<-- "docs/examples/agreement/gomma-plastica-federazione-gomma-plastica/example.py"
```
