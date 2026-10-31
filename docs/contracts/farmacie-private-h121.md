# CCNL Dipendenti delle Farmacie Private

| | |
|---|---|
| **CNEL code** | `H121` |
| **Sector** | Farmacie private |
| **Family** | `farmacie` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2021-09-07 |
| **Workers (est.)** | ~60k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - FEDERFARMA
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS

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
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 37 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2021-09-07 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2021-11-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Titolo XVIII - Anzianità di servizio, Art. 51 (p. 23): "Le frazioni di anno sono computate a tutti gli effetti contrattuali per dodicesimi, computando come mese intero le frazioni di mese superiori a 15 giorni.". Added: more_than 15 (the file applied the engine default, at least 15 days). |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q1` | Area Q1 - Direttore responsabile di farmacia | € 1,668.97 | 2021-11-01 |
| `Q2` | Area Q2 - Farmacista collaboratore specializzato | € 1,499.19 | 2021-11-01 |
| `Q3` | Area Q3 - Farmacista collaboratore con 24+ mesi in qualifica | € 1,429.19 | 2021-11-01 |
| `1` | 1o livello - Farmacista collaboratore | € 1,429.19 | 2021-11-01 |
| `2` | 2o livello - Lavoratori di concetto con funzioni di coordinamento | € 1,215.92 | 2021-11-01 |
| `3` | 3o livello - Lavoratori di concetto con conoscenze tecniche | € 1,130.17 | 2021-11-01 |
| `4` | 4o livello - Lavoratori con compiti operativi e conoscenze tecnico-pratiche | € 1,017.02 | 2021-11-01 |
| `5` | 5o livello - Lavoratori qualificati con normali conoscenze | € 898.97 | 2021-11-01 |
| `6` | 6o livello - Lavoratori di pulizia e operazioni semplici | € 807.81 | 2021-11-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 15 increments

| Level | Increment (monthly) |
|---|---:|
| `Q1` | € 25.82 |
| `Q2` | € 25.30 |
| `Q3` | € 25.30 |
| `1` | € 25.30 |
| `2` | € 23.24 |
| `3` | € 22.72 |
| `4` | € 20.65 |
| `5` | € 20.14 |
| `6` | € 19.62 |

## Apprenticeship

**farmacista_collaboratore** (type: `under_classification`)  
Destination levels: `1`

**professionalizzante** (type: `under_classification`)  
Destination levels: `4`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "farmacie-private-h121/rural_pharmacy_table · base_salary · impact yes · open"
    SIMPLIFICATION: Farmacie Rurali Sussidiate (Tabella B) excluded. Rural pharmacies have lower base salaries; Tabella A (urban) is modelled only.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the Tabella B pay of the Farmacie Rurali Sussidiate with a fact selecting it, or refuse such employers.

!!! warning "farmacie-private-h121/isq_twelve_year_tier · base_salary · impact yes · open"
    SIMPLIFICATION: ISQ for Q2 and Q3 modelled at flat 100 EUR (the 2+ anni tier per Tabella C). Workers with 12+ anni receive 130 EUR (delta 30 EUR/month, max ~360 EUR/yr). The 12-year tier is not modelled, although an allowance can be gated on service months (service_months_threshold) (review of 2026-10-30)

    **Applies when:** `base_salary` applies; level in Q2, Q3.

    **Remediation:** Check whether the 12 anni of Tabella C count service or time in the quadro qualification; if service, split the ISQ of Q2/Q3 into a 100 EUR allowance with service_months_until=144 and a 130 EUR one with service_months_threshold=144 (Employment.seniority), otherwise add a worker fact for the qualification time.

!!! warning "farmacie-private-h121/edr_thirteen_months · base_salary · impact yes · open"
    SIMPLIFICATION: EDR (10.33 EUR, Art. 54e) is contractually due for 13 mensilita but the file leaves its months_per_year unset, so the engine also pays it in the quattordicesima. Annual overcount ~10 EUR per worker (review of 2026-10-30)

    **Applies when:** `base_salary` applies.

    **Remediation:** Set months_per_year=13 on the edr allowance of every level, then remove this limitation.

!!! warning "farmacie-private-h121/apprentice_seniority · seniority · impact unknown · open"
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
| https://www.mnlf.it/documenti/ContrattoCollettivoNazionalediLavorodeidipendentidafarmaciaprivata2021.pdf | altro | 2021-09-07 | [↗](https://www.mnlf.it/documenti/ContrattoCollettivoNazionalediLavorodeidipendentidafarmaciaprivata2021.pdf) |

??? note "Coverage notes"
    Salary model: split. base_salary = retribuzione base nazionale conglobata (Tabella A, Art. 58). fixed_allowances = contingenza (per-level, frozen since 1977 per settore commercio) + EDR 10.33 (all levels, accordo 31/07/1992) + ISQ (Q levels, Tabella C).
    
    Divisore convenzionale 173 confirmed from Art. 57 of primary CCNL text.
    
    Additional months: 14. Art. 62 (13a mensilita) and Art. 63 (14a mensilita) confirmed from primary source.
    
    Seniority: 15 scatti biennali (Art. 53). Amounts from Tabella D (1.2.1996 column) of primary CCNL PDF.
    
    Contract expired 31/08/2024 (Art. 102). No successor signed as of 2026-09-09 (INPS-CNEL spreadsheet updated 25/07/2026 shows Periodo finale=null for H121). Tables valid open-ended under ultrattività.
    
    SIMPLIFICATION resolved: The CCNL rinnovo 07/09/2021 (Tabella A confirmed from UILTUCS primary PDF) established ONE salary tranche from 01/11/2021 — not three separate tranches. Increases vs. Dec 2012 base: Q1=+89.97, Q2=+150.00 (incl. 70 Area Q2), Q3=+80.00, L1=+80.00, L2=+70.98, L3=+67.39, L4=+62.65, L5=+57.72, L6=+53.90. These are fully modelled in this file. The '3 tranches / +113 EUR' figure cited in some secondary sources refers to the separate CCNL farmacie speciali/municipalizzate (Assofarm H122), not this contract.
    
    Apprenticeship from Accordo 14 giugno 2012 (Allegato II). Farmacista collaboratore (dest 1o) stays at level 1o for all 36 months. Commesso/Magazziniere/Contabile (dest 4o): months 0-12 at level 6o, months 13-36 at level 5o.
    
    Headcount: 77,146 workers in 16,324 companies (INPS-CNEL archive, H121).
    
    SIMPLIFICATION: Tabella D groups Q2, Q3, and 1o into a single scatto amount of 25.30 EUR. Q1 uses 25.82 EUR.
    

## Raw data

The contract file this page is generated from: [`agreement/farmacie-private-h121.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/farmacie-private-h121.json).

## Usage example

```python
--8<-- "docs/examples/agreement/farmacie-private-h121/example.py"
```
