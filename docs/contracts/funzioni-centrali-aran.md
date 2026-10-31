# CCNL Comparto Funzioni Centrali — Triennio 2022-2024

| | |
|---|---|
| **CNEL code** | `S005` |
| **Sector** | Pubblica Amministrazione — Comparto Funzioni Centrali |
| **Family** | `pubblico-impiego` |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2026-08-06 |
| **Workers (est.)** | ~250k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - CISL FP
    - CISL
    - CONFSAL UNSA
    - CONFSAL
    - FLP
    - CGS
    - CONFINTESA FP
    - CONFINTESA
    - UIL PA
    - UIL

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

2 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 26 verified / 5 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2026-08-06 |
| **Last review** | 2026-10-17 |
| **Latest salary tranche** | 2027-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-12 | claude-opus-5-5 (ai) | Salary tables, additional months, hourly and daily divisors, overtime, leave, sickness and seniority, against the CCNLs of 12 February 2018, 9 May 2022, 27 January 2025 and 6 August 2026. | corrected | Salary amounts confirmed (annual table over 12; elevate professionalità 2022: 35,000 / 13).<br>The first period started on 2022-05-09, the signing date; the new classification applies from 1 November 2022 (art. 18 c. 1).<br>The 2025-2027 values cited a union page; they are now cited to the ARAN text of 6 August 2026 (Tabella 3).<br>Daily quota: art. 29 c. 4 divides by 30, not 26.<br>Overtime is in art. 25 c. 5 of the CCNL 12.2.2018, kept in force by the CCNL 2025-2027.<br>Sickness: comporto of 18 months with 9 months at 100%, 3 at 90% and 6 at 50% (art. 24), not 270 days at 100%.<br>Leave: 26 days for the first three years of a first public employment until 31 December 2026 (art. 21 CCNL 2022-2024). |
| 2026-10-14 | claude-opus-5-5 (ai) | P1 audit: Tabella 3 of the CCNL of 6 August 2026 for the four areas and the three years; the remaining derived records; the next review date. | confirmed | The twelve monthly amounts (four areas from 1 January 2025, 2026 and 2027) are the annual tabellare of Tabella 3 over 12, to the cent.<br>Perseo Sirio stays derived: the 1% of the employer and of the worker are read in the fund's information sheet, which states the rates in force, not since when; the CCNL does not print them.<br>review_due set to 2027-12-31, the expiry of the 2025-2027 agreement. |
| 2026-10-15 | claude-opus-5-5 (ai) | Registry check: CNEL code, name, signatories and term against the 21st CNEL report of CCNLs in force (30 June 2025) and the term clause of the text read in the P1 review. | corrected | CNEL S005 matches (ARAN with CISL FP, CONFSAL UNSA, FLP, CGS, CONFINTESA FP, UIL PA).<br>Term: the CCNL of 6 August 2026 covers the triennio 2025-2027; meta.validity still held the CCNL of 9 May 2022 and is updated. |
| 2026-10-17 | claude-opus-5-5 (ai) | The CTPS rates the file reads, against the INPS table of the Gestione Dipendenti Pubblici. | confirmed | The INPS page prints 'CTPS 33 24,2 8,8' (total, employer, worker): the 24.20% and 8.80% of the bundle. The rates no longer rest on the kitech.it proxy the limitation named; ctps_rates_proxy is resolved. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `ELEVATE_PROFESSIONALITA` | Area Elevate Professionalità | € 3,107.21 | 2027-01-01 |
| `FUNZIONARI` | Area Funzionari ed Elevata Qualificazione — Funzionari | € 2,275.39 | 2027-01-01 |
| `ASSISTENTI` | Area Assistenti | € 1,873.56 | 2027-01-01 |
| `OPERATORI` | Area Operatori | € 1,780.57 | 2027-01-01 |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! note "funzioni-centrali-aran/ctps_rates_proxy · inps_employer · impact unknown · resolved"
    aliquote INPS CTPS (ex-INPDAP) — dipendente 8,80%, datore 24,20% — da proxy kitech.it 2026; verificare circolare INPS annuale per valori esatti.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Resolved: the CTPS rates of the bundle (employee 8.80%, employer 24.20%) are read from the INPS page 'I contributi dei dipendenti pubblici', table of the Gestione Dipendenti Pubblici, checked again on 2026-10-17 (contribution/2026/pubblica-amministrazione.json, inps.provenance, verified).

!!! warning "funzioni-centrali-aran/agency_salary_tables · base_salary · impact unknown · open"
    sub-settori ENAC, ANSFISA, ANSV e AGID hanno tabelle retributive proprie (Tabelle 3-6 CCNL) non modellate — out_of_scope per implementazione standard.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the ENAC, ANSFISA, ANSV and AGID tables with a fact selecting them, or refuse those employers.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| CCNL Comparto Funzioni Centrali 2025-2027, signed definitively on 6 August 2026. Tabella 3 (p. 66): tabellare from 1.1.2025, 1.1.2026, 1.1.2027. | altro | 2026-08-06 | [↗](https://www.aranagenzia.it/wp-content/uploads/2026/08/2026_08_06_CCNL_CFC_2025-2027-1.pdf) |
| CCNL 2022-2024 signed on 27 January 2025 (UIL PA and UIL adhered on 4 November 2025). Tabella 2 (p. 55), art. 29 (divisors), art. 21 (ferie), art. 24 (malattia). | altro | 2025-01-27 | [↗](https://www.aranagenzia.it/wp-content/uploads/2025/01/CCNL_L_C_FC_2022_2024.pdf) |
| CCNL 2019-2021. Tabella H (p. 104), art. 18 (classification in force from 1.11.2022), art. 53 (elevate professionalità). | altro | 2022-05-09 | [↗](https://www.aranagenzia.it/wp-content/uploads/2023/05/Frontespizio-e-CCNL-Comparto-Funzioni-Centrali-2019-2021-1.pdf) |
| CCNL 2016-2018. Art. 25 (straordinario), art. 72 (tredicesima). | altro | 2018-02-12 | [↗](https://www.aranagenzia.it/wp-content/uploads/2025/01/CCNL-definitivo-Funzioni-centrali-triennio-2016-2018_firmato_12-2-2018.pdf) |

??? note "Coverage notes"
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    apprendistato assente dal CCNL vigente (fonte primaria: indice ARAN CCNL 2022-2024, Art. 1-38 senza capitolo apprendistato) e dal CCNL Ministeri 12/6/2003 richiamato dall'Art. 38 Conferme, che esclude espressamente gli apprendisti dall'ambito di applicazione (fonte secondaria: olympus.uniurb.it); quadro normativo PA D.Lgs. 165/2001 non prevede apprendistato ex D.Lgs. 81/2015.
    
    CCNL Funzioni Centrali 2025-2027 (S005) firmato definitivamente il 2026-08-06; in vigore dal 2026-08-07. Incrementi retroattivi al 1/1/2025 e 1/1/2026 liquidati con gli stipendi di agosto/settembre 2026. Tre periodi aggiornati: 2025-01-01, 2026-01-01, 2027-01-01. Fonte: CISL FP (cislfp.it), testo ARAN definitivo non ancora pubblicato su aranagenzia.it al 2026-09-09.
    
    codice CNEL S005 confermato da tre fonti secondarie convergenti: lavoro-economia.it (intestazione pagina "CCNL Comparto Funzioni Centrali [Cnel: S005]"), blia.it (ID S005-209278), contratticcnl.it (/ccnl/s005/). Verificato 2026-09-09.
    
    progressione economica non automatica — differenziali stipendiali assegnati per graduatoria (Art. 16 CCNL 2022-2024); seniority_increments.maximum_count=0.
    
    PENSION FUND. Perseo Sirio (1% + 1% of the retribuzione utile ai fini del TFR). Enrolment is a fact: the silenzio-assenso of the hires from 2 January 2019 (accordo ARAN 16/09/2021) is not inferred, nor the three months a fixed term needs to enrol. The TFR conferred stays a notional INPS accrual.
    
    SALARY TABLES: 1.11.2022-31.12.2023 CCNL 9.5.2022 Tabella H (new classification from 1.11.2022; elevate professionalità art. 53: 35,000 a year with the tredicesima); 2024 CCNL 27.1.2025 Tabella 2; 2025, 2026, 2027 CCNL 6.8.2026 Tabella 3. Monthly = annual / 12, the tredicesima paid apart. Hourly divisor 156 (art. 29 c. 3), daily 30 (art. 29 c. 4).
    

## Raw data

The contract file this page is generated from: [`agreement/funzioni-centrali-aran.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/funzioni-centrali-aran.json).

## Usage example

```python
--8<-- "docs/examples/agreement/funzioni-centrali-aran/example.py"
```
