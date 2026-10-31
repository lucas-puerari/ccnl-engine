# CCNL Materiali da Costruzione PMI — Lapidei (CONFAPI ANIEM)

| | |
|---|---|
| **CNEL code** | `F020` |
| **Sector** | Industria materiali da costruzione — Lapidei piccola industria |
| **Family** | `materiali-estrattive` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-09-09 |
| **Workers (est.)** | ~5000 |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CONFAPI ANIEM
    - FILLEA-CGIL
    - FENEAL-UIL
    - FILCA-CISL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | inps_employer, pension_fund_contribution |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 41 verified / 8 derived / 21 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-09-09 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2025-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-17 | claude-opus-5-5 (ai) | The minimi of the eight Lapidei levels against the testo definitivo of 9 September 2025. | confirmed | 40 minimi (eight levels, April 2019, September 2020, February 2021, January 2022 and January 2025) are printed in Art. 25 (PDF p. 96) and in the tables of Allegato V (PDF pp. 219-220): verified.<br>8 minimi of 1 January 2024 are not printed: the verbale of 25 January 2024 (Allegato V, PDF p. 219) prints the totals at 31 December 2023 and the increments; the minimo is the total plus the increment less the EDR (and the superminimo collettivo of level 8). Derived; every one matches the file.<br>The table of the verbale prints level 6 'a regime' at 1.935,75, the Art. 25 table at 1.935,76 (1.925,43 + 10,33): a one-cent misprint of the verbale; the file follows Art. 25.<br>The ruleset now names its source, the testo definitivo published by FENEAL-UIL, a signatory: source_type contracting_party instead of estimated. |
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 28 - Tredicesima mensilità (o gratifica natalizia) (p. 103): "Nel caso di inizio o cessazione del rapporto durante il corso dell'anno, l'impiegato avrà diritto a tanti dodicesimi dell'ammontare della tredicesima mensilità per quanti sono i mesi interi di servizio prestato presso l'azienda. La frazione di mese superiore ai 15 giorni va considerata a questi effetti come mese intero.". Match: more_than 15. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1` | Livello 1 — Lavoratori con funzioni direttive apicali e autonomia decisionale (quadri, dirigenti) | € 2,795.46 | 2025-01-01 |
| `2` | Livello 2 — Lavoratori con responsabilità di unità organizzativa (responsabili amministrazione/produzione) | € 2,587.54 | 2025-01-01 |
| `3` | Livello 3 — Lavoratori di concetto e coordinamento (responsabili uffici, capi reparto/impianto) | € 2,202.40 | 2025-01-01 |
| `4` | Livello 4 — Lavoratori con rilevante preparazione tecnico-pratica (capi linea, tecnici specializzati) | € 2,096.25 | 2025-01-01 |
| `5` | Livello 5 — Lavoratori specializzati (caposquadra, escavatoristi, scalpellini artistici) | € 2,014.85 | 2025-01-01 |
| `6` | Livello 6 — Lavoratori qualificati con capacità tecnico-pratiche (minatori, scalpellini, gruisti) | € 1,925.43 | 2025-01-01 |
| `7` | Livello 7 — Lavoratori con normali capacità (cavatori, operai di cantiere, addetti linee produzione) | € 1,813.41 | 2025-01-01 |
| `8` | Livello 8 — Lavoratori addetti a mansioni semplici (pulizie, manovalanza, prima assunzione) | € 1,613.14 | 2025-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `8` | € 6.76 |
| `7` | € 7.57 |
| `6` | € 8.31 |
| `5` | € 8.99 |
| `4` | € 9.60 |
| `3` | € 10.14 |
| `2` | € 11.83 |
| `1` | € 12.76 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "materiali-costruzione-lapidei-confapi/contractual_fund_partial · pension_fund_contribution · impact unknown · open"
    The Fondapi contractual contribution (5 EUR riparametrati a month) is owed on every run that pays the month, in full. The Scheda and the circolare operativa of Fondapi state no rule for a partly employed month, a part-time worker or the extra months: a partial month or part time pays the full amount, an extra-month run none.

    **Applies when:** `pension_fund_contribution` applies; the run takes the engine code path.

    **Remediation:** Source the rule of the accordo of 10 November 2020 for a partial month and part time and model it, then remove this note.

!!! warning "materiali-costruzione-lapidei-confapi/cigo_rate_by_activity · inps_employer · impact yes · open"
    CIGO: the operai of the stone-working firms owe 3.30% ('operai delle imprese dell'industria e artigianato lapidei', D.Lgs. 148/2015 art. 13 c. 1 (Normattiva, text in force on 2026-10-14, https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2015-09-14;148~art13!vig=2026-10-14, snapshot sha256 3f7019a244e01d36ac8e7c9e25bcf058c777c8ed758418ba261d83867672c46a), lett. d); the industria table charges the 1.70% / 2.00% of lett. a-b, so the employer contributions of an operaio are understated by 1.60 or 1.30 points. Impiegati and quadri owe the 1.70% / 2.00% of lett. e-f the table already charges.

    **Applies when:** `inps_employer` applies; category in operaio.

    **Remediation:** Model the CIGO of D.Lgs. 148/2015 art. 13 c. 1 by activity (edile, lapidei) apart from the tax sector, then remove this note.

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

### Without monetary impact

!!! note ""
    SIMPLIFICATION: Apprenticeship not modelled. Art. 3 defines three periods (0-12 months 2 levels below, 12-24 months 1 level below, 24-36 months destination pay) with a special 18-month track for L6 and destination pay in period 3. The engine supports ApprenticeshipUnderClassification with levels_below periods, but L6's shorter duration and period-3 destination-pay override require per-destination customisation not yet extracted from source. Deferred pending dedicated source review.

!!! note ""
    SIMPLIFICATION: Work rules (overtime, leave, sickness) not modelled. Discipline lapidei spans multiple articles; scope deferred.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.fenealuil.it/wp-content/uploads/2026/02/CCNL_MaterialiCostruzione_testo-completo.pdf | associazione | 2025-09-09 | [↗](https://www.fenealuil.it/wp-content/uploads/2026/02/CCNL_MaterialiCostruzione_testo-completo.pdf) |

??? note "Coverage notes"
    SCOPE: Lapidei subsector only. Laterizi and Cemento subsectors have different level codes and salary structures; not modelled in this file.
    
    SALARY MODEL: split. Art. 25 Lapidei: contingenza congelata e conglobata nei minimi (Minimo = paga base + contingenza frozen). fixed_allowances: EDR 10.33 EUR (tutti i livelli) and supermin.coll 7.75 EUR (livello 8 only).
    
    SALARY HISTORY: 6 tranches from Allegato V (accordo 25.1.2024) and Art. 25 Lapidei dal 1.1.2025. Periods: 1.4.2019, 1.9.2020, 1.2.2021, 1.1.2022, 1.1.2024, 1.1.2025 (open). Source: CCNL testo completo FENEAL-UIL.
    
    HOURLY DIVISOR: 174. Art. 24 Disciplina Lapidei: 'Le quote orarie degli elementi mensilizzati della retribuzione si ottengono dividendo gli elementi stessi per 174'.
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Art. 73 Disciplina Lapidei: gratifica natalizia annuale pari a una mensilita'.
    
    SENIORITY: 5 scatti biennali (cadence 24 months). Art. 26 Lapidei: importi fissi calcolati al 5% dei minimi 1980 e trasformati in cifra fissa. Amounts: L1=12.76, L2=11.83, L3=10.14, L4=9.60, L5=8.99, L6=8.31, L7=7.57, L8=6.76.
    
    SIGNATORIES: CONFAPI ANIEM + FILLEA-CGIL + FENEAL-UIL + FILCA-CISL. Testo definitivo signed 9 settembre 2025. Contract period 1.7.2022-30.6.2025.
    

## Raw data

The contract file this page is generated from: [`agreement/materiali-costruzione-lapidei-confapi.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/materiali-costruzione-lapidei-confapi.json).

## Usage example

```python
--8<-- "docs/examples/agreement/materiali-costruzione-lapidei-confapi/example.py"
```
