# CCNL per i dipendenti da aziende dei settori Pubblici Esercizi, Ristorazione Collettiva e Commerciale e Turismo - Ristorazione collettiva (aziende dell'art. 1 c. 1 par. II)

| | |
|---|---|
| **CNEL code** | `H05Y` |
| **Sector** | turismo |
| **Family** | `turismo` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-06-26 |
| **Workers (est.)** | ~350k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🏭 Production |

[← Contracts index](index.md)

??? note "Signatories"
    - FIPE-Confcommercio
    - Legacoop Produzione e Servizi
    - Confcooperative Lavoro e Servizi
    - AGCI-Servizi
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
| **Limits of this contract** | base_salary, bilateral_funds, overtime, seniority, trattamento_integrativo |

8 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 62 verified / 6 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 🏭 Production | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-06-26 |
| **Last review** | 2026-11-01 |
| **Latest salary tranche** | 2027-12-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-11 | claude-opus-5-5 (ai) | Inherited from pubblici-esercizi-fipe-angem, of which this file is a copy: the review covered that file's levels; here it stands for the shared rules (work rules, parameters) only. Every payable rule of the file (72 records) and the hourly divisor read again in the signed texts: the CCNL of 8 February 2018, the renewal of 5 June 2024 and its accordo integrativo of 26 June 2024 with the final salary tables. | corrected | All 50 salary periods and the 10 level rows match the accordo integrativo of 26 June 2024 (pp. 1-2) and are verified, with the Quadri allowances (Art. 154), the 14 monthly payments (Artt. 183-184), seniority (Art. 182), overtime 30% and 60% (Art. 126), the daily quota 1/26 (Art. 159), leave (Art. 134) and the hourly divisor 172 (Art. 160). Pages are PDF page indexes.<br>Corrected: sickness (Art. 190, Art. 194). INPS pays 80% for the whole sickness in this sector (regime pubblici_esercizi, funded by the 0.77% supplement) and the CCNL adds no top-up, so the target is 80%; the three days of carenza are paid in full only when the sickness lasts more than five days; the comporto is 180 days a calendar year.<br>Assumed: the overtime bands for holidays (30%) and holiday nights (60%). The CCNL sets only 30% by day and 60% by night (Art. 126) and 20% for ordinary work on a holiday (Art. 132); the two bands are inferences, not cited values.<br>Left derived: the Fon.Te. rates, read in the fund's information sheet, not in the CCNL.<br>Not modelled: the quattordicesima excludes the seniority increments (Art. 184), the collective catering companies move the June 2025 and June 2026 tranches to September (accordo integrativo p. 3), and the conditions of Art. 190 beyond the carenza.<br>FIPE and the Turismo CCNLs are two agreements: FIPE was renewed on 5 June 2024 (level 4 at 1,692.69 from June 2026), the Turismo CCNL of Federalberghi and Faita on 5 July 2024 (1,695.69 from May 2026). |
| 2026-10-12 | claude-opus-5-5 (ai) | Quattordicesima and seniority, holiday overtime, September tranches of the ristorazione collettiva: follow-ups of the review of 2026-10-11. | corrected | Quattordicesima: art. 184 c. 1 excludes the matured seniority increments; the engine paid them. Now excluded.<br>Holiday overtime: the 30% and 60% are art. 126 itself (by time of day), not an analogy: derived from p. 99; whether art. 132's 20% is added is left open (outside_input note).<br>Ristorazione collettiva: the 2025 and 2026 tranches start in September for the companies of art. 1 c. 1 par. II (accordo integrativo 26.6.2024, p. 3); still the limitation contract_catering_tranche_dates.<br>This file was created from pubblici-esercizi-fipe-angem for the collective catering companies: same rules and review history, with the 2025 and 2026 tranches from 1 September (accordo integrativo of 26 June 2024, p. 3). |
| 2026-10-12 | claude-opus-5-5 (ai) | Accrual of the tredicesima and quattordicesima (artt. 183 c. 2 and 184 c. 4). | corrected | The accrual rule was missing (engine default of 15 days per month): the CCNL cumulates the fractions of month, a rateo for each 30 days and one for a remainder of 15 days or more, now modelled (cumulated_fractions). |
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule not yet verified, the apprenticeship (arts. 68 and 72), the limitations and the L2 values, for the production tier. | corrected | 22 records verified on the signed texts (salary periods on the accordo integrativo of 26 June 2024, accrual rule and Fon.Te. on the CCNL of 8 February 2018).<br>Fon.Te.: 0.55% employer and worker on the TFR base, art. 185 c. 3; valid from 29 November 1996 (the fund table), not from 2026.<br>Apprenticeship: level 1 is not a destination; level 6 lasts 24 months (art. 72 c. 1), now its own track; the 42 and 48 month profiles stay a limitation.<br>Holiday overtime: whether the 20% of art. 132 adds to the 30%/60% of art. 126 is not stated; the two bands stay derived with the limitation.<br>L2: INPS terziario verified (circ. 117/2022 allegato accepted on 2026-10-13), with the 0.77% sickness supplement of the pubblici esercizi (CCNL art. 190 c. 3); TFR art. 217, the scatti included since 1 November 2021.<br>No renewal after the accordo integrativo of 26 June 2024 changes gross pay. |
| 2026-10-16 | claude-opus-5-5 (ai) | Checklist item 'confrontare lordo, netto e costo azienda con esempi indipendenti': a run of the engine against the cost table of the Ministry of Labour for the comparto ristorazione collettiva (DD 63 of 10 July 2025, national table of January 2026, D.Lgs. 36/2023 art. 41 c. 13). | flagged | Level 4, January 2026: paga base conglobata 19.832,28 a year over 12 equals the 1652.69 of the file (tranche of 1 September 2025); the quattordicesima of the table, 1.652,69, is that month. Match: reference case pubblici-esercizi-fipe-angem-ristorazione-collettiva_4_2026_ministry.json.<br>Employer contributions: the table prints Inps 29,75%, FIS 0,53% and CIGS 0,60%, 30.88% in all; the engine applies 30.8833% to an impiegato of a company of 51 employees (the FIS employer share 0.80% x 2/3 = 0.5333%, printed rounded). The CIGS line places the table above 50 employees (D.Lgs. 148/2015 art. 20, commercial companies with more than fifty employees). Match within the rounding of the printed rate; a rate, not a total, so no output is credited.<br>Deviations, with cause and decision: INAIL 1,09% is not computed by the engine (documented); the health fund (158,40 a year) is the owed limitation health_and_bilateral_funds, which leaves the employer cost incomplete on every run (checked: is_employer_cost_complete false); the EBT contribution, the complementary pension at a 30% enrolment and the three seniority increments of row A are averages of the table, not facts of one worker: not compared. No independent net pay example: not compared. |
| 2026-10-17 | claude-opus-5-5 (ai) | The paga base and contingenza of every level from June 2024 against the accordo integrativo of 26 June 2024, the quattordicesima against the CCNL of 8 February 2018, and a year and a termination of a 4th level worker against a hand oracle. | confirmed | Accordo integrativo of 26 June 2024 (pp. 1-3): the 50 totals of contingenza and paga base of the ten levels from June 2024 to December 2027 match the file, with the tranches of 2025 and 2026 in September.<br>Art. 184 of the CCNL of 8 February 2018 (p. 128, scan read by OCR): quattordicesima of the pay in force on 30 June, paid with the July pay, in ratei of the twelve months before 1 July. Match.<br>Hand oracle (tests/knowledge/ccnl_engine/period/sector, scenarios ristorazione-year and ristorazione-june): a 4th level impiegato hired on 1 January 2026 by an employer with 10 employees, with the terziario rates up to 15 employees and the 0.77% sickness supplement of the pubblici esercizi taken apart; every payment and the year (gross, contributions, tax, net, TFR, employer cost) match the engine to the cent. The CCNL now covers every total of the definition of done. |
| 2026-10-31 | claude-opus-5-5 (ai) | The basis of the indemnity for the leave not taken at the end of the employment, searched in the OCR of the signed text of 2018 (Artt. 114, 134, 135, 159, 160). | corrected | Art. 159 - Determinazione della retribuzione giornaliera (p. 116): the daily pay is the monthly pay divided by 26 for every contractual purpose: work_rules.leave_rules.termination; the accrual of the leave is not modelled, so the basis is not used yet. |
| 2026-11-01 | claude-opus-5-5 (ai) | The notice of Artt. 208-209 (PDF pp. 143-144), checked by a separate session on the rendered pages. | confirmed | Art. 208 (PDF pp. 143-144, sha256 32a2831b... matched, page images read): 15 bands, A e B / 1 / 2 e 3 / 4 e 5 / 6S, 6 e 7 over the three service bands, the same for dismissal and resignation, no start day: work_rules.notice.<br>Art. 209 (p. 144): the indemnity is the normale retribuzione of the period, extra_months_included false; the exception of Art. 179 for the pubblici esercizi does not concern this file. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Qa` | Quadri A — managerial functions with a high level of management responsibility | € 2,578.07 | 2027-12-01 |
| `Qb` | Quadri B — managerial functions with continuous responsibility over a complex unit | € 2,375.56 | 2027-12-01 |
| `1` | Level 1 — staff with high professional content and operational autonomy | € 2,201.85 | 2027-12-01 |
| `2` | Level 2 — staff with initiative and operational autonomy (coordination) | € 1,999.36 | 2027-12-01 |
| `3` | Level 3 — staff with specialist technical knowledge (conceptual work) | € 1,877.00 | 2027-12-01 |
| `4` | Level 4 — staff with executive autonomy (specialised technical-administrative duties) | € 1,762.69 | 2027-12-01 |
| `5` | Level 5 — staff with qualified technical-practical knowledge and skills | € 1,643.50 | 2027-12-01 |
| `6s` | Level 6 super — staff with adequate technical-practical skills (formerly qualified commis or experienced staff) | € 1,574.42 | 2027-12-01 |
| `6` | Level 6 — staff with standard practical training and basic professional knowledge | € 1,549.78 | 2027-12-01 |
| `7` | Level 7 — general assistants, cleaning staff (simple manual tasks) | € 1,442.45 | 2027-12-01 |

## Seniority increments

**Cadence:** every 48 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `Qa` | € 40.80 |
| `Qb` | € 39.25 |
| `1` | € 37.70 |
| `2` | € 36.15 |
| `3` | € 34.86 |
| `4` | € 33.05 |
| `5` | € 32.54 |
| `6s` | € 31.25 |
| `6` | € 30.99 |
| `7` | € 30.47 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `2`, `3`, `4`, `5`, `6s`  
percentage: 1.00

**professionalizzante_24_mesi** (type: `percentage`)  
Destination levels: `6`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "pubblici-esercizi-fipe-angem-ristorazione-collettiva/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: no clause says it in so many words. Art. 182 c. 1 (PDF p. 126) grants the six scatti 'A tutto il personale', art. 71 applies to the apprentice the normative treatment of the qualified worker, and art. 68 c. 1 pays a percentage of the qualified pay of the level, scatti included: the apprenticeship counts for the scatti and a matured scatto is paid at the apprentice percentage. The first scatto matures after 48 months, so only an apprentice with prior seniority reaches one; the engine pays no increment during the apprenticeship.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "pubblici-esercizi-fipe-angem-ristorazione-collettiva/holiday_overtime_cumulation · overtime · impact unknown · open"
    HOLIDAY OVERTIME: Art. 126 (PDF p. 99) gives 30% by day and 60% by night for every overtime hour; Art. 132 (p. 103) gives 20% for the hours worked on a festività. No clause links them: art. 126 c. 3 excludes cumulation only with ordinary night work, art. 130 c. 2 only Sunday work with the festività, and the special parts (arts. 246-247, 263-264) and the 2024 renewal repeat or leave them. The engine pays holiday overtime at 30%/60% without the 20%.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Confirm whether the 20% of art. 132 is added to the overtime rate on a festività; if so set the bands to 0.5 and 0.8, else close this note.

!!! warning "pubblici-esercizi-fipe-angem-ristorazione-collettiva/apprenticeship_long_profiles · base_salary · impact yes · open"
    APPRENTICESHIP PROFILES: art. 72 c. 2 gives 48 months to named profiles of levels 2 and 3 and 42 months to named profiles of level 4, and art. 68 c. 1 pays 95% in their fourth year. The profile is not an input: the engine pays them the 36-month track, 100% from month 37 instead of 95%.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Let the caller state the art. 72 c. 2 profile and add the 42 and 48 month tracks with the 95% fourth year.

!!! warning "pubblici-esercizi-fipe-angem-ristorazione-collettiva/guarantee_premium_2027 · base_salary · impact yes · open"
    Art. 13 c. 10 of the renewal of 5 June 2024: the guarantee premium paid with the November 2027 pay to workers without second-level bargaining. The caller pays it as a variable item.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the 2027 guarantee premium as a conditional allowance.

!!! warning "pubblici-esercizi-fipe-angem-ristorazione-collettiva/health_and_bilateral_funds · bilateral_funds · impact yes · open"
    HEALTH FUND: the Fondo Est is owed for every worker (CCNL 2018 art. 186); an employer that does not pay it owes the worker instead the elemento distinto of EUR 16.00 for 14 months (c. 12). Neither is modelled: the employer cost, and with the elemento the net pay, are short of it.

    **Applies when:** `bilateral_funds` applies.

    **Remediation:** Model the contributions per worker, with a fact for an employer that pays the worker the alternative element instead, then remove this note.

!!! warning "pubblici-esercizi-fipe-angem-ristorazione-collettiva/tourism_special_supplement · trattamento_integrativo · impact yes · open"
    TRATTAMENTO INTEGRATIVO SPECIALE (L. 199/2025 art. 1 cc. 18-20, Gazzetta Ufficiale text, https://www.gazzettaufficiale.it/atto/serie_generale/caricaArticolo?art.codiceRedazionale=26A00149&art.dataPubblicazioneGazzetta=2026-01-21&art.flagTipoArticolo=0&art.idArticolo=1&art.idGruppo=1&art.idSottoArticolo=1&art.idSottoArticolo1=10&art.progressivo=1&art.versione=1, page sha256 e05f6f864509f87e7488cdae075fe3a1f2632f6f4577b87ee05479a1ed193c1d): from 1 January to 30 September 2026 the workers of the esercizi di somministrazione di alimenti e bevande (L. 287/1991 art. 5) and of the 'comparto del turismo, ivi inclusi gli stabilimenti termali', with employment income of 2025 not above 40,000 EUR, receive 'un trattamento integrativo speciale, che non concorre alla formazione del reddito, pari al 15 per cento delle retribuzioni lorde corrisposte in relazione al lavoro notturno e alle prestazioni di lavoro straordinario [...] effettuate nei giorni festivi'. The employer pays it 'su richiesta del lavoratore' (c. 20), a fact the request has no field for: the engine does not pay it, so the net pay of a worker who asked for it is understated.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the worker's request of c. 20 to the request, pay 15% of the night and holiday overtime pay of the run as a credit, then remove this note.

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

!!! warning "una_tantum_readings · base_salary · impact unknown · open"
    The una tantum of a renewal is paid from the CCNL data with readings no text read settles in full: a month of service in the covered period counts with the days of the una tantum (15 when the text is silent), over the months of the period; the absences of a month do not reduce it, though a text may pay the months 'di effettiva prestazione'; a part time is paid in proportion to its hours; a run without the employment period is paid none; the share of the covered months of earlier years is taxed apart as arrears.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source the counting of the months, the part time and the taxation of each una tantum from its agreement, then resolve this limitation.

### Without monetary impact

!!! note ""
    SALARY MODEL: the contractual pay structure provides for a separate national base pay and contingenza. For engine purposes they are consolidated into base_salary (monthly total per tranche). The totals are read in the accordo integrativo of 26 June 2024 (pp. 1-2), the same as the FIPE pay tables. fixed_allowances models the function allowance for quadri: Qa=75 EUR and Qb=70 EUR, from Art. 154 of the CCNL of 8 February 2018 (CCNL 2024-2027).

!!! note ""
    APPRENTICESHIP (CCNL 8 February 2018, arts. 68 and 72, PDF pp. 74-75, read on the signed scan): the professionalizzante apprentice is paid 80%, 85% and 90% of the qualified pay of the level in the first three years (art. 68 c. 1). Durations (art. 72 c. 1): 36 months for levels 2, 3, 4, 5 and 6s, 24 months for level 6. Level 1, level 7 and the quadri are not apprenticeship destinations. Art. 75 (apprenticeship for qualification or diploma) is out of scope.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.confcommerciomilano.it/export/sites/unione/doc/contratti_lavoro/contrattazione_collettiva/ACCORDO-INTEGRATIVO_Tabelle-Retributive_CCNL_P_E_Risto_Collettiva_Commerciale_Turismo.pdf | tabella_retributiva | 2024-06-26 | [↗](https://www.confcommerciomilano.it/export/sites/unione/doc/contratti_lavoro/contrattazione_collettiva/ACCORDO-INTEGRATIVO_Tabelle-Retributive_CCNL_P_E_Risto_Collettiva_Commerciale_Turismo.pdf) |
| https://www.fipe.it/wp-content/uploads/2024/06/Contratto-CCNL-05_06_24.pdf | altro | 2024-06-05 | [↗](https://www.fipe.it/wp-content/uploads/2024/06/Contratto-CCNL-05_06_24.pdf) |
| https://www.confcommerciomilano.it/export/sites/unione/doc/contratti_lavoro/contrattazione_collettiva/ccnl_ristorazione_2018.pdf | altro | 2018-02-08 | [↗](https://www.confcommerciomilano.it/export/sites/unione/doc/contratti_lavoro/contrattazione_collettiva/ccnl_ristorazione_2018.pdf) |

??? note "Coverage notes"
    SUB-SECTOR: collective catering companies of art. 1 c. 1 par. II (ristorazione collettiva). Same rules as pubblici-esercizi-fipe-angem; the 2025 and 2026 tranches apply from 1 September (accordo integrativo 26 June 2024, p. 3: 'Per le aziende di cui all'art. 1 comma 1 paragrafo II, le Parti stabiliscono incrementi dei valori di paga base nazionale mensile nelle modalità di seguito indicate').
    
    2024 RENEWAL: CCNL signed 5 June 2024, validity 1 June 2024 – 31 December 2027 (CNEL H05Y, ~592,364 workers Uniemens 2022 / over 1 million according to FIPE). Pay table source: fipe.it/wp-content/uploads/2025/02/Tabelle-retributive-2024.pdf.
    
    SENIORITY INCREMENTS: 6 quadrennial increments (48 months). Per-level amounts from FIPE pay tables (fipe.it/wp-content/uploads/2025/02/Tabelle-retributive-2024.pdf). Paid over 14 monthly instalments.
    
    MONTHLY PAYMENTS: 14, the tredicesima of Art. 183 and the quattordicesima of Art. 184 of the CCNL of 8 February 2018 (PDF pp. 127-128). The quattordicesima excludes the matured seniority increments (seniority_increments.excluded_from_extra_months).
    
    HOURLY DIVISOR: 172 for a 40-hour week (Art. 160 of the CCNL of 8 February 2018, PDF p. 116; 190 for a 44-hour week, not modelled).
    
    INPS: uses 2026-terziario.json (tax_sector terziario, same as commercio-confcommercio and turismo-federalberghi).
    

## Raw data

The contract file this page is generated from: [`agreement/pubblici-esercizi-fipe-angem-ristorazione-collettiva.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/pubblici-esercizi-fipe-angem-ristorazione-collettiva.json).

## Usage example

```python
--8<-- "docs/examples/agreement/pubblici-esercizi-fipe-angem-ristorazione-collettiva/example.py"
```
