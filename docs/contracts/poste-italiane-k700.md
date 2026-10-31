# CCNL Poste Italiane S.p.A. (personale non dirigente)

| | |
|---|---|
| **CNEL code** | `K700` |
| **Sector** | Servizi postali |
| **Family** | `servizi-postali` |
| **Tax sector** | `industria` |
| **Last renewal** | 2024-07-23 |
| **Workers (est.)** | ~117k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - POSTE ITALIANE S.p.A.
    - SLP-CISL
    - SLC-CGIL
    - UIL Poste

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, inps_employer, seniority, sickness, una_tantum |

5 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 53 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-07-23 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2027-12-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 67 - Tredicesima mensilità (p. 141): "quanti sono i mesi di servizio prestati presso la Società, computando come mese intero la frazione di mese pari o superiore a 15 giorni.". Match: at_least 15. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A1` | Livello A — posizione retributiva A1 | € 2,169.37 | 2027-12-01 |
| `A2` | Livello A — posizione retributiva A2 | € 1,926.89 | 2027-12-01 |
| `B` | Livello B | € 1,652.98 | 2027-12-01 |
| `C` | Livello C | € 1,522.56 | 2027-12-01 |
| `D` | Livello D | € 1,452.20 | 2027-12-01 |
| `E` | Livello E | € 1,287.61 | 2027-12-01 |
| `F` | Livello F | € 1,154.49 | 2027-12-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**professionalizzante** (type: `under_classification`)  
Destination levels: `B`, `C`, `D`, `E`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "poste-italiane-k700/edr_pre_privatization · base_salary · impact yes · open"
    SIMPLIFICATION: EDR (elemento distintivo della retribuzione) omitted. Art. 65 I qualifies it as 'ove spettante'; amount not stated in Allegato 9 or CCNL body. Legacy entitlement for pre-privatization workers only.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the EDR for pre-privatization workers once its amount is sourced.

!!! warning "poste-italiane-k700/fondo_quiescenza_poste_rates · inps_employer · impact unknown · open"
    SIMPLIFICATION: INPS industria rates applied. Poste Italiane employees are enrolled in the Fondo Quiescenza Poste (INPS special fund, Art. 7 L. 335/1995; merged from IPOST 2012). Correct rates differ from standard industria rates. Verify against INPS Fondo Quiescenza Poste documentation. Verified 2026-09-09: INPS website confirms Fondo Quiescenza Poste exists for Poste Italiane SpA but specific aliquote not publicly listed on INPS portal in machine-readable form.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Source the Fondo Quiescenza Poste rates and apply them in place of the industria rates.

!!! warning "poste-italiane-k700/legacy_individual_seniority · seniority · impact yes · open"
    SIMPLIFICATION: Legacy retribuzione individuale di anzianità (D.P.R. 335/1990) and posizioni economiche differenziate (CCNL 1997) not modeled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Let the caller state the retribuzione individuale di anzianità and the posizioni economiche differenziate (e.g. EarnedIncrements or an individual allowance) and record the limitation.

!!! warning "poste-italiane-k700/anticipo_lump_sum_2024 · una_tantum · impact yes · open"
    SIMPLIFICATION: Salary tranche 01/07/2024–31/08/2025 covered by one-time 'anticipo sui futuri miglioramenti economici' (lump sum, September 2024). Engine carries paga base at 2024-07-23 level (same as pre-renewal) for that window.

    **Applies when:** `una_tantum` applies; from 2024-09-01.

    **Remediation:** Model the September 2024 anticipo sui futuri miglioramenti economici as an una tantum (or a caller event) and its absorption, or record a limitation for runs of September 2024.

!!! warning "poste-italiane-k700/sickness_comporto_speciale · sickness · impact yes · open"
    SICKNESS (Art. 41 II): the comporto speciale of the workers with a serious illness listed in letter A), a disability under L. 68/99 or on life-saving therapy keeps the job for 730 days in the 48 months, with the whole fixed pay for all of them; the engine applies the comporto ordinario (609 days, 502 paid) to every worker.

    **Applies when:** `sickness` applies.

    **Remediation:** Take the serious illness, disability or life-saving therapy of Art. 41 II as a fact of the episode and apply the 730 days at full pay.

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

!!! warning "personal_withholding_same_kind · personal_withholdings · impact unknown · open"
    Two garnishments of the same kind, or two salary assignments, share the measure of their kind (a fifth, or the tenth or seventh of the agente della riscossione) in the order of notification: art. 545 c. 4 c.p.c. sets 'un quinto per i tributi ... ed in eguale misura per ogni altro credito' and art. 5 DPR 180/1950 a cessione 'fino al quinto', but no text read says how two orders of the same kind split the measure, so the later order may be under- or overstated.

    **Applies when:** `personal_withholdings` applies; the run takes the engine code path.

    **Remediation:** Source how the employer splits the measure between two orders of the same kind (art. 499 c.p.c. on the intervention of creditors, case law of the Cassazione) and apply it, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.uilposte.it/wp-content/uploads/2025/01/CCNL-Posteitaliane-Uilposte2024.pdf | altro | 2024-07-23 | [↗](https://www.uilposte.it/wp-content/uploads/2025/01/CCNL-Posteitaliane-Uilposte2024.pdf) |

??? note "Coverage notes"
    Salary model: split. base_salary = minimo tabellare (Allegato 9, changes each tranche); fixed_allowances = contingenza (per-level, frozen) + indennità di funzione for A1/A2 (months_per_year=12).
    
    Hourly divisor 156 from Art. 65 III: retribuzione base oraria = mensile / 156. Cross-check: 36h/week × 52/12 = 156 h/month (Art. 26 normal workweek = 36h).
    
    Additional months: 14. Art. 67 tredicesima: base = posizione retributiva + contingenza + EDR — funzione excluded. Art. 68 quattordicesima: same explicit enumeration. Both articles confirm funzione not in mensilità aggiuntive.
    
    Seniority: no traditional scatti di anzianità for new hires. Retribuzione individuale di anzianità (D.P.R. 335/1990) is a legacy element for pre-privatization workers only (Art. 25 CCNL). Model: cadence_months=24, maximum_count=0.
    
    A1/A2 levels: paga base and contingenza are identical for staff and produzione; funzione differs (Art. 21 CCNL). Modeled as two-tier allowances: base rate (staff, unconditional) + produzione delta via role="produzione". Pass Employee(roles=frozenset(["produzione"])) to add the differential.
    
    Apprenticeship: Art. 24 CCNL — under_classification, inquadrato al livello immediatamente inferiore per l'intera durata (max 36 mesi). Destinations B, C, D, E. Level A excluded (Quadri e coordinamento/controllo). Level F excluded (lowest, no level below).
    
    Headcount: ~116,801 workers (CNEL/INPS archive, K700).
    
    INDENNITA DI FUNZIONE — PRODUZIONE DIFFERENTIAL: Staff rate (A1: 333.33/mo, A2: 187.50/mo) is unconditional. Produzione workers receive an additional delta (A1: +58.34, A2: +45.83) via IND_FUNZIONE_A*_PROD_DELTA with role="produzione". Total produzione: A1=391.67, A2=233.33 (Art. 21 CCNL K700). Callers: pass Employee(roles=frozenset(['produzione'])) for the higher rate.
    
    SIMPLIFICATION: industria CIGO (1.70-2.00%) included in employer INPS rate. Poste Italiane is not a manufacturing firm and is not CIGO-subject; actual employer cost is lower. Verify against INPS circ. for the correct Poste INPS classification.
    

## Raw data

The contract file this page is generated from: [`agreement/poste-italiane-k700.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/poste-italiane-k700.json).

## Usage example

```python
--8<-- "docs/examples/agreement/poste-italiane-k700/example.py"
```
