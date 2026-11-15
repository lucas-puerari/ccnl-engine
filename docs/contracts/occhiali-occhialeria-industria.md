# CCNL Occhiali e Occhialeria — Industria (ANFAO)

| | |
|---|---|
| **CNEL code** | `D271` |
| **Sector** | industria occhialeria e ottica |
| **Family** | `tessile-moda` |
| **Tax sector** | `industria` |
| **Last renewal** | 2023-12-04 |
| **Workers (est.)** | ~20k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANFAO
    - Filctem-CGIL
    - Femca-CISL
    - UilTEC-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ✅ |
| **Limits of this contract** | — |

0 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🟢 Verified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 77 verified / 11 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2023-12-04 |
| **Last review** | 2026-11-15 |
| **Latest salary tranche** | 2028-11-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The Elemento Retributivo Nazionale (conglobated minimo, TEM) of the ten levels against the signed ipotesi of the 2023-2025 renewal (28 April 2023, ERN table for 1.05.2023, 1.03.2024, 1.02.2025) and of the 2026-2028 renewal (30 January 2026, ERN table for March 2026 to November 2028), both published by FILCTEM-CGIL, a signatory. | corrected | The two FILCTEM-CGIL scans (signed by ANFAO, Filctem, Femca, Uiltec) print the ERN per level for every tranche of the file: 2023 ipotesi PDF p. 22, 2026 ipotesi PDF p. 30 (All. 1). Both are image-only scans read on the page images (tesseract garbles the 2026 table). Level codes map one to one (Q, 6, 5S, 5, 4S, 4, 3S, 3, 2, 1); the 2023 table labels them by area and step professionale (e.g. '4° S Qualificata Consolidato').<br>The ERN is the conglobated tabular minimum and matches the file's base_salary meaning; the Q indennita di funzione is not in the ERN (Q ERN is only a few euro above level 6), consistent with the file's separate allowance.<br>Level 1 MAG.2027: the 2026 table prints 1.661,71, a transposition of 1.661,17 (1.622,04 + 39,13; 1.661,17 + 35,21 = 1.696,38 printed for MAG.28). The file's 1661.17 is kept as a derived value.<br>Level 4S 1.03.2024 and 1.02.2025: the 2023 table prints 2.014,69 and 2.074,05, but its own increments give 2.016,18 and 2.075,54, and the 2026 table (2.126,94 - 51,40) implies 2.075,54. The definitive text of 4 December 2023 reportedly corrected some minimi but is not published by a signatory; both periods are left unbacked.<br>One-cent residuals between the two signed tables remain for levels 6 and 5S (2025 ERN 2.448,66 and 2.323,28 vs 2.448,67 and 2.323,29 implied by the 2026 ERN minus the first 2026 tranche); each period is backed by the table that prints it.<br>Consistency check (base + printed increment) on both tables: 2023 table off by -0,01 for level 6 at 1.03.2024 (2.319,66 + 58,98 = 2.378,64 vs 2.378,63 printed) and by -1,49 for 4S; 2026 table consistent except the level 1 MAG.2027 transposition. Rule applied: a printed value stays a verified row unless a later signed table contradicts it by more than rounding (4S, unbacked); one-cent residuals are kept as printed and reported here.<br>The ruleset names a FILCTEM-CGIL document, a signatory: source_type contracting_party.<br>Corrected to the printed table: Q 2026-10-01: 2546.53 -> 2546.54; Q 2027-05-01: 2604.87 -> 2604.88; Q 2028-05-01: 2657.38 -> 2657.39; Q 2028-11-01: 2680.72 -> 2680.73; 6 2026-10-01: 2539.80 -> 2539.79; 6 2027-05-01: 2596.76 -> 2596.74; 6 2028-05-01: 2648.02 -> 2647.99; 6 2028-11-01: 2670.80 -> 2670.77; 5S 2027-05-01: 2467.76 -> 2467.75; 5S 2028-05-01: 2517.77 -> 2517.76; 5S 2028-11-01: 2540.00 -> 2539.99; 4S 2026-10-01: 2158.67 -> 2157.78; 4S 2027-05-01: 2211.56 -> 2209.18; 4S 2028-05-01: 2259.16 -> 2255.44; 4S 2028-11-01: 2280.32 -> 2276.00; 3S 2028-11-01: 2125.83 -> 2125.84; 2 2028-05-01: 1948.54 -> 1948.53; 2 2028-11-01: 1966.32 -> 1966.31; 1 2028-05-01: 1696.39 -> 1696.38; 1 2028-11-01: 1712.04 -> 1712.03. |
| 2026-11-06 | claude-opus-5-5 (ai) | Art. 24 apprenticeship of the CCNL of 10 June 2021 (pp. 39-40); the renewal of 30 January 2026 searched for an amendment. | corrected | The apprentices are under-classified (two levels, one, then the destination), not paid 100%: the 2026 percentages abrogated are those of the PPVA premium per step. |
| 2026-11-08 | gpt-6-sol (ai) | Open limitations claimed to be no longer gaps: one session read the clauses and the data, a second independent session checked the claim. | confirmed | level_1_entry_rate: The 2021 classification clause (also present in the 2023 definitive-text scan) assigns the single 1°/Operativa-Base classification for six months to first hires without sector experience, and also assigns it to non-production cleaning/manual workers; it does not create an 'L1 ing<br>apprenticeship_full_pay: Art. 24 specifies classification AND corresponding economic treatment: destination 3 through Q: 36 months in 10/10/16 periods at two levels below, one below, then destination; destination 2: 24 months in 6/6/12 periods, at level 1 for the first six months and level 2 from the sta |
| 2026-11-15 | claude-opus-5-5 (ai) | Comporto of several illnesses, against the research of a separate model session; quote checked on the source. | corrected | Added the comporto window of art. 52 (13 months, 18 for serious illnesses, within 30 months). |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro — Lavoratori con responsabilita di direzione e coordinamento (Art. 2095 c.c.) | € 2,680.73 | 2028-11-01 |
| `6` | Livello 6 — Lavoratori con autonomia decisionale e competenze trasversali elevate | € 2,670.77 | 2028-11-01 |
| `5S` | Livello 5 Super — Lavoratori con funzioni tecniche o di supervisione avanzata | € 2,539.99 | 2028-11-01 |
| `5` | Livello 5 — Lavoratori con funzioni di controllo o alta specializzazione | € 2,453.48 | 2028-11-01 |
| `4S` | Livello 4 Super — Lavoratori con elevata specializzazione o coordinamento | € 2,276.00 | 2028-11-01 |
| `4` | Livello 4 — Lavoratori polivalenti o con responsabilita tecnica | € 2,187.96 | 2028-11-01 |
| `3S` | Livello 3 Super — Lavoratori specializzati di livello superiore | € 2,125.84 | 2028-11-01 |
| `3` | Livello 3 — Lavoratori specializzati con autonomia operativa | € 2,082.62 | 2028-11-01 |
| `2` | Livello 2 — Lavoratori qualificati con conoscenze specifiche | € 1,966.31 | 2028-11-01 |
| `1` | Livello 1 — Lavoratori addetti a mansioni semplici e ripetitive | € 1,712.03 | 2028-11-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 6.84 |
| `2` | € 7.36 |
| `3` | € 7.80 |
| `3S` | € 7.80 |
| `4` | € 8.26 |
| `4S` | € 8.26 |
| `5` | € 9.76 |
| `5S` | € 9.76 |
| `6` | € 11.65 |
| `Q` | € 11.65 |

## Apprenticeship

**professionalizzante** (type: `under_classification`)  
Destination levels: `3`, `3S`, `4`, `4S`, `5`, `5S`, `6`, `Q`

**professionalizzante_2** (type: `under_classification`)  
Destination levels: `2`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

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

!!! warning "parental_month_split · parental_leave · impact unknown · unsourced"
    When a counter of the parental leave (a rate band or the indemnified months) ends inside a calendar month of the leave that is not of thirty days, the engine pays the days of that month in order, one day of counter each and the last day what is left of the thirty: INPS counts the calendar month as one month (FAQ congedo parentale 2024, n. 10) but no source says which of its days fall in which band.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source how INPS splits a calendar month between two rates of the parental leave and apply it, then resolve this limitation.

!!! warning "parental_extra_month_share · parental_leave · impact unknown · unsourced"
    The days of parental leave accrue the 13th and the other extra months in full at the employer's charge (art. 34 c. 5 D.Lgs. 151/2001: the leave does not reduce them), while the INPS indemnity is computed on a base that already holds their daily rateo (art. 23 c. 2, INPS circ. 122/2022): no source read settles whether the employer's extra month is reduced by the share INPS pays, so the rateo of a month on leave may be overstated.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source how the extra months of a parental leave are split between INPS and the employer and net the INPS share from the employer's rateo, then resolve this limitation.

!!! warning "parental_hourly_ccnl_rule · parental_leave · impact unknown · open"
    A parental leave by the hour takes half the average daily hours a day and counts two such days as one day of leave, the general criterion of art. 32 c. 1-ter D.Lgs. 151/2001 (INPS circ. 152/2015 par. 2.2), which also excludes its cumulation with the nursing rests on the same day. A national CCNL rule that sets other hours to a day of leave prevails (art. 32 c. 1-bis): the run records this limitation while the bundle does not record the rule of the CCNL (work_rules.parental_hourly) or the rule sets its own hours, which the engine does not apply yet; a company or territorial agreement is the fact local_hourly_agreement of the event.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the collective rules on the leave by the hour of the CCNL (hours of a day of leave, cumulation) and apply them, then resolve this limitation.

!!! warning "disability_permit_tfr · disability_permits · impact unknown · unsourced"
    The days of permit under L. 104/1992 art. 33 c. 3 keep the TFR base, as payroll practice holds; art. 2120 c. 3 c.c. keeps in the TFR base only the absences of art. 2110 c.c. and the wage integration, and no primary source read says the permits are among them, so the TFR quota of a month with permits may be overstated.

    **Applies when:** `disability_permits` applies; the run takes the engine code path.

    **Remediation:** Source the TFR treatment of the permit days (an INPS or Ministry ruling, or case law of the Cassazione) and apply it, then resolve this limitation.

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

!!! warning "notice_indemnity_day_measure · termination_notice · impact unknown · unsourced"
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

!!! note "personal_withholding_same_kind · personal_withholdings · impact unknown · resolved"
    Two garnishments of the same kind, or two salary assignments, share the measure of their kind (a fifth, or the tenth or seventh of the agente della riscossione) in the order of notification: art. 545 c. 4 c.p.c. sets 'un quinto per i tributi ... ed in eguale misura per ogni altro credito' and art. 5 DPR 180/1950 a cessione 'fino al quinto', but no text read says how two orders of the same kind split the measure, so the later order may be under- or overstated.

    **Applies when:** `personal_withholdings` applies; the run takes the engine code path.

    **Remediation:** Resolved: art. 553 c. 1 c.p.c. (Normattiva, https://www.normattiva.it/atto/caricaArticolo?art.versione=4&art.idGruppo=93&art.flagTipoArticolo=1&art.codiceRedazionale=040U1443&art.idArticolo=553&art.idSottoArticolo=1&art.idSottoArticolo1=10&art.dataPubblicazioneGazzetta=1940-10-28&art.progressivo=0&, sha256 b41bf831e63fcaacfe95231f9595da5d0e5619c162cc455a80632bba90c147cd): the judge 'le assegna in pagamento [...] ai creditori concorrenti' and 'L'obbligo di pagamento decorre, per il terzo, dalla notifica dell'ordinanza di assegnazione'. The amount each garnishment takes is the fact of its ordinanza: PersonalWithholding.installment, and two garnishments of one kind without it give the missing-fact issue personal_withholding_unassigned. Read on 2026-11-15.

!!! warning "mid_month_level_change · base_salary · impact unknown · unsourced"
    A promotion on a day other than the first of a month splits the monthly pay of the run between the level before and the new level by the payable days of the CCNL daily quota on each side of the promotion, component by component; the hourly quotas of the month (overtime, permits, absences) read the same split chain whatever the day of the event. The CCNL texts read (Commercio and Terziario art. 118, DMO art. 102) give the new level from the promotion but not how its month is split.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source how a month is split by a promotion inside it (a CCNL clause or an INPS or Ministry ruling) and price the events of the month at the terms of their day, then resolve this limitation.

!!! note "arrears_unused_deductions · contract_renewal_arrears · impact yes · resolved"
    The engine computes the rate of the separate taxation of arrears from PriorYearTaxFacts.net_income_biennio (art. 21 cc. 1, 3 TUIR) and reduces the tax by ArrearsEvent.unused_deductions, the deductions of artt. 12 and 13 cc. 1-2 the worker did not use in the years the arrears refer to (art. 21 c. 4). An arrears event that does not state them, among which the una tantum the engine pays itself, is taxed without the reduction, so the tax may be overstated.

    **Applies when:** `contract_renewal_arrears` applies; the run takes the engine code path.

    **Remediation:** Resolved: art. 21 c. 4 TUIR (Normattiva, https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art21!vig=, sha256 aafc3e5d5cd7254c7eb52e74051e86f1243b3a7b3cbadcd951daf7bc5e113fc6): 'Gli aventi diritto agli arretrati devono dichiarare al soggetto che li corrisponde l'ammontare delle detrazioni fruite per ciascuno degli anni cui si riferiscono'. The deductions are a fact the worker declares: ArrearsEvent.unused_deductions, and PriorYearTaxFacts.arrears_unused_deductions for the una tantum the engine pays as arrears; unstated, the run carries the missing-fact issue arrears_unused_deductions_unknown. Read on 2026-11-14.

!!! warning "sunday_holiday_ccnl_clause · sunday_holiday · impact yes · open"
    L. 260/1949 art. 5 pays the workers with a fixed salary a further daily quota only for the civil holidays (25 April, 1 May, 2 June) falling on a Sunday; the other holidays of art. 2 (1 January, 6 January, Easter Monday, 15 August, 4 October, 1 November, 8 December, 25 and 26 December) give it only by CCNL clause, and the payment of 4 November is a CCNL institute. A run of a month with such a holiday on a Sunday, in a CCNL whose clause is not sourced (work_rules.sunday_holidays), pays the statutory holidays only; a public employment is paid none, its treatment not being sourced.

    **Applies when:** `sunday_holiday` applies; the run takes the engine code path.

    **Remediation:** Source the CCNL clause on the holidays falling on a Sunday and record it as work_rules.sunday_holidays.

!!! warning "pension_extra_deduction_first_employed · pension_fund_contribution · impact unknown · unsourced"
    A worker first employed after D.Lgs. 252/2005 came into force may deduct, in the twenty years after the fifth year of membership, the contributions above the annual cap within the room the first five years left, up to half the annual cap (art. 8 c. 6, as amended by L. 199/2025 from 1 July 2026). The request has no field for the first employment or the room left, and the sources searched set no rule for the withholding agent: a run whose contributions exceed the cap left deducts within the ordinary cap, and the worker may claim the rest in the tax return.

    **Applies when:** `pension_fund_contribution` applies; the run takes the engine code path.

    **Remediation:** Source whether and how the withholding agent grants the extra deduction at the conguaglio, add the worker's statement as an optional input and apply it, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://italpaghe.ilccnl.it/ccnl/occhiali---industria/occhiali---industria/tabelleretributive | altro | 2023-12-04 | [↗](https://italpaghe.ilccnl.it/ccnl/occhiali---industria/occhiali---industria/tabelleretributive) |
| https://www.cisl.it/ccnl-occhiali-sindacati-sottoscritta-ipotesi-accordo-per-rinnovo-contratto-204e-laumento-del-complessivo-triennio-2026-2028/ | altro | 2026-01-30 | [↗](https://www.cisl.it/ccnl-occhiali-sindacati-sottoscritta-ipotesi-accordo-per-rinnovo-contratto-204e-laumento-del-complessivo-triennio-2026-2028/) |

??? note "Coverage notes"
    CCNL signed 04/12/2023 valid 01/01/2023-31/12/2025; renewed 30/01/2026 valid 01/01/2026-31/12/2028 (ANFAO+Filctem-CGIL+Femca-CISL+UilTEC-UIL).
    
    CONGLOBATED (since 01/01/2009): contingenza and EDR are inglobated into the tabular minimum. Single base_salary column per level; no separate contingenza allowance.
    
    Level Q (Quadro): indennita di funzione +82.63 EUR/month on top of the tabular minimum (all tranches). Modelled as INDENNITA_FUNZIONE fixed allowance, months_per_year=13.
    
    SENIORITY: 5 biennali (24-month) scatti. Per-level amounts (EUR): 1=6.84, 2=7.36, 3=3S=7.80, 4=4S=8.26, 5=5S=9.76, 6=Q=11.65.
    
    TRANCHES 01/10/2026 through 01/11/2028: L4 reference increments confirmed from primary source (CISL communique CCNL occhialeria 30/01/2026: +30, +50, +45, +20 EUR at L4). All-level amounts derived via the parametric ratio matrix from confirmed 01/03/2026 per-level deltas. The CCNL occhialeria uses a declared parametric system; parametric derivation is contractually consistent.
    
    APPRENTICE SENIORITY (Art. 24, p. 40 of the CCNL testo definitivo 2023, CNEL deposit 176781, https://azstcnesa0002prodwe001.blob.core.windows.net/archivio-contratti/archivio%2F2023%2Fe5a59528-7634-4026-b087-0c21d247f1c7%2F20175.pdf, sha256 f32ae476b175e22d8b918c7f3e07f5472d91852505dc29e3ab022547f3b139c1, read on the OCR of the scan and on the 2021 text, same page): 'L’intero periodo di apprendistato professionalizzante è utile ai fini della maturazione dell’anzianità aziendale, anche ai fini degli aumenti periodici di anzianità; tali aumenti saranno corrisposti nelle misure previste dal livello/area-step di appartenenza': seniority_increments.apprentice_level_amount.
    
    COMPORTO OF SEVERAL ILLNESSES (Art. 52, rinnovo 28 aprile 2023, PDF p. 16 (scanned), https://www.filctemcgil.it/images/download/CONTRATTI/occhiali/230428_OCCHIALI_RINNOVO%20CCNL%202023%202025.pdf, sha256 dc5d33a21e61b0801df70a2d22363a842fcf5dc7264634daf1ae5cce1e67749c): 'L'obbligo di conservazione del posto per l'azienda cesserà comunque ove nell'arco di 30 mesi si superino i predetti limiti di 13 e 18 mesi, anche con più malattie, con esclusione, per entrambi i limiti, dei periodi di ricovero ospedaliero e di ricovero in day hospital'. Modelled as sickness_rules.comporto_windows: 395 days (13 months x 365/12), 548 for a serious illness, within 30 months, hospital stays left out; the 2-month extension for oncological therapies is not modelled.
    

## Raw data

The contract file this page is generated from: [`agreement/occhiali-occhialeria-industria.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/occhiali-occhialeria-industria.json).

## Usage example

```python
--8<-- "docs/examples/agreement/occhiali-occhialeria-industria/example.py"
```
