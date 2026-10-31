# CCNL per i dipendenti dalle aziende di lavorazione della foglia di tabacco secco allo stato sciolto

| | |
|---|---|
| **CNEL code** | `E042` |
| **Sector** | lavorazione foglia di tabacco |
| **Family** | `alimentare` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-07-02 |
| **Workers (est.)** | ~2k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - APTI
    - FLAI-CGIL
    - FAI-CISL
    - UILA-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | pension_fund_contribution, seniority |

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🧑 Manual | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 37 verified / 0 derived / 22 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟡 Needs review | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-07-02 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2028-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | flagged | The review recorded no list of the documents it read.<br>Confidence set to needs_review: values to re-check. |
| 2026-10-17 | claude-opus-5-5 (ai) | The minimi of the nine categories against Allegato A of the accordo di rinnovo of 2 July 2025. | confirmed | Allegato A (p. 13 of the signed scan, read by OCR and on the page image): the 36 minimi of the nine categories from January 2025 to January 2028 match the file (3°B from 1/1/2027 is printed '1420,1').<br>The ruleset names this source, published by UILA-UIL, a signatory: source_type contracting_party instead of estimated.<br>The contingenza and EDR of each category (18 rules) are not in the accordo and stay assumed. |
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Articolo 33 - 13a e 14a MENSILITÀ (p. 43): "il lavoratore non in prova ha diritto a tanti dodicesimi dell’ammontare della 13a e della 14a mensilità per quanti sono i mesi interi di servizio prestati. Le frazioni di mese superiori a 15 giorni saranno calcolate come mese intero.". Added: more_than 15 (the file applied the engine default, at least 15 days). |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1S` | Categoria Super — funzioni direttive di particolare rilievo | € 2,271.18 | 2028-01-01 |
| `1` | 1a Categoria — funzioni direttive amministrative o tecniche | € 2,106.68 | 2028-01-01 |
| `2` | 2a Categoria — funzioni di concetto con coordinamento | € 1,847.04 | 2028-01-01 |
| `3A` | 3a Categoria A — compiti esecutivi tecnici o amministrativi con iniziativa | € 1,625.55 | 2028-01-01 |
| `3B` | 3a Categoria B — compiti esecutivi tecnici o amministrativi | € 1,462.16 | 2028-01-01 |
| `4A` | 4a Categoria A — qualificazione per il processo di lavorazione del tabacco | € 1,334.90 | 2028-01-01 |
| `4B` | 4a Categoria B — conoscenze tecnico-pratiche di controllo o produzione | € 1,279.29 | 2028-01-01 |
| `5` | 5a Categoria — mansioni operative standard | € 1,242.28 | 2028-01-01 |
| `6` | 6a Categoria — mansioni semplici di prima assunzione | € 1,115.90 | 2028-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1S` | € 17.00 |
| `1` | € 17.00 |
| `2` | € 15.00 |
| `3A` | € 14.00 |
| `3B` | € 13.00 |
| `4A` | € 12.00 |
| `4B` | € 12.00 |
| `5` | € 11.00 |
| `6` | € 10.00 |

## Apprenticeship

**apprendistato professionalizzante (livelli 2-4)** (type: `under_classification`)  
Destination levels: `2`, `3A`, `3B`, `4A`, `4B`

**apprendistato professionalizzante (livello 1)** (type: `under_classification`)  
Destination levels: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "tabacco-apti/alifond_before_july_2025 · pension_fund_contribution · impact yes · open"
    ALIFOND employer contribution (1.50%) modeled from 01/07/2025 (renewal Art. 47). Pre-July-2025 ALIFOND contribution not modeled.

    **Applies when:** `pension_fund_contribution` applies; before 2025-07-01.

    **Remediation:** Model the ALIFOND employer rate in force before 1 July 2025.

!!! warning "tabacco-apti/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

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

### Without monetary impact

!!! note ""
    APPRENTICESHIP: under_classification for destinations 2, 3A, 3B, 4A, 4B (36-month, 10/12/14 periods) and level 1 (36-month, 10/10/16 periods). Destination 5 (24-month exception, Article 6) not modeled. Level 1S is not an apprenticeship destination.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| CCNL Tabacco Lavorazione foglia 2025-2028 — Accordo 02/07/2025 | altro | — | [↗](https://www.uila.eu/web/wp-content/uploads/2022/04/Accordo-rinnovo-ccnl-nazionale-tabacco-sciolto-2025-2028-02-07-25.pdf) |
| CCNL Tabacco (Lavorazione) — lavoro-economia.it | tabella_retributiva | — | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=25) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = minimo tabellare (4 tranches: +60 at 4A on 01/01/2025, +50 on 01/01/2026, +50 on 01/01/2027, +40 on 01/01/2028). 50/50 parametric formula verified against published Allegato A table.
    
    CONTINGENZA: per-level amounts frozen at 01/11/1991 (Allegato B, CCNL 2021). EDR 10.33 EUR uniform for all levels (Accordo Interconfederale 31/07/1992).
    
    SENIORITY: cadence 24 months, maximum 5 scatti. Amounts from Article 32 of the 2025 renewal. Operai amounts roughly doubled vs 2021 CCNL (4A/B: 5.68->12.00, 5: 5.42->11.00, 6: 5.16->10.00).
    

## Raw data

The contract file this page is generated from: [`agreement/tabacco-apti.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/tabacco-apti.json).

## Usage example

```python
--8<-- "docs/examples/agreement/tabacco-apti/example.py"
```
