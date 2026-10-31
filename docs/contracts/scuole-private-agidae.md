# CCNL Istituzioni Formative Private (Scuole Private Religiose) — AGIDAE

| | |
|---|---|
| **CNEL code** | `T241` |
| **Sector** | istruzione privata |
| **Family** | `istruzione-formazione` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-07-03 |
| **Workers (est.)** | ~50k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - AGIDAE
    - FLC-CGIL
    - CISL-Scuola
    - UIL-Scuola

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | seniority |

2 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 43 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-07-03 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2027-12-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Art. 33 - Tredicesima mensilità (p. 21): "Nel caso di inizio o cessazione del rapporto di lavoro nel corso dell'anno, vanno corrisposti tanti dodicesimi dell'ultima mensilità percepita pari ai mesi di servizio prestati. 3. Le frazioni di mese vengono prese in considerazione solo se superiori a 15 giorni ed in tal caso equiparate ad un mese intero.". Added: more_than 15 (the file applied the engine default, at least 15 days). |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `L6` | Livello 6 — Personale direttivo (presidi, coordinatori didattici, direttori amministrativi) | € 2,205.27 | 2027-12-01 |
| `L5` | Livello 5 — Personale docente scuola secondaria, psicologi, psicoterapeuti, responsabili CED e amministrativi senior | € 1,987.80 | 2027-12-01 |
| `L4` | Livello 4 — Personale docente scuola infanzia/primaria, educatrici, assistenti sociali e sanitari, fisioterapisti, logopedisti | € 1,896.82 | 2027-12-01 |
| `L3` | Livello 3 — Personale amministrativo e tecnico specializzato (segretari, addetti amministrativi, capo-cuochi, capi-sala con diploma) | € 1,838.95 | 2027-12-01 |
| `L2` | Livello 2 — Personale tecnico-ausiliario (tecnici caldaie, autisti, centralinisti, cuochi, guardarobieri, camerieri specializzati) | € 1,784.67 | 2027-12-01 |
| `L1` | Livello 1 — Personale ausiliario non specializzato (addetti pulizie, bidelli, portieri, personale di fatica, accompagnatori) | € 1,731.18 | 2027-12-01 |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

| Level | Increment (monthly) |
|---|---:|
| `L1` | € 0.00 |
| `L2` | € 0.00 |
| `L3` | € 0.00 |
| `L4` | € 0.00 |
| `L5` | € 0.00 |
| `L6` | € 0.00 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "scuole-private-agidae/salario_di_anzianita · seniority · impact yes · open"
    SENIORITY: frozen at 31/12/2005. Art. 29 clause 1 of the CCNL 2024 lists 'salario di anzianità maturato al 31/12/2005' as a retributive element. Art. 32 governs this frozen amount. No new scatti di anzianità accrue after 2005. The current progression mechanism is POC (Progressione Orizzontale di Carriera), calculated as 100% of the 3-year average of PAP productivity awards (Art. 38, in force from 31/08/2024), which is merit-conditioned and excluded from Layer 1. Maximum_count set to 0; amount_by_level set to 0.00 EUR for all levels. Cadence_months set to 1 (minimum legal value; maximum_count=0 so no scatti ever apply; historical quinquennial cadence noted here only).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Let the caller state the salario di anzianità maturato al 31/12/2005 (EarnedIncrements or an individual allowance) and record the limitation.

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

### Without monetary impact

!!! note ""
    APPRENTICESHIP (Layer 2): apprendistato professionalizzante not modelled. Governed by Allegato 4 of the CCNL (Art. 25). Allegato 4 is not publicly accessible. Part-time and fixed-term (NASpI addizionale) function via generic engine rules without per-contract data. Layer 2 is therefore partial: apprenticeship gap is the only missing component.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.terrazzini.it/wp-content/uploads/14bis-2024.pdf | associazione | 2024-07-03 | [↗](https://www.terrazzini.it/wp-content/uploads/14bis-2024.pdf) |
| https://www.terrazzini.it/wp-content/uploads/19bis-2026.pdf | associazione | 2024-07-03 | [↗](https://www.terrazzini.it/wp-content/uploads/19bis-2026.pdf) |
| https://ilccnl.it/ccnl/scuole-private-religiose/scuole-private-religiose---agidae-dal-010794 | associazione | 2024-07-03 | [↗](https://ilccnl.it/ccnl/scuole-private-religiose/scuole-private-religiose---agidae-dal-010794) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (retribuzione tabellare comprensiva dell'indennità di contingenza maturata al 30/11/1991, per Art. 29 CCNL 2024). All base_salary values are the conglobated tabular minimums. Contingenza and EDR are fully absorbed. Source: Terrazzini & Partners circular 14bis/2024 (tranches 01/09/2024 and 01/09/2025) and circular 19bis/2026 (tranches 01/09/2026 through 01/12/2027).
    
    TRANCHE DATES: six tranches — 01/09/2024, 01/09/2025, 01/09/2026, 01/01/2027, 01/09/2027, 01/12/2027. CCNL signed 03/07/2024; economic validity 01/01/2024–31/12/2025 (first biennium), second biennium 01/01/2026–31/12/2027 signed 19/05/2026. No arrears for the 01/01/2024–31/08/2024 gap. First modelled period starts at the first salary tranche 01/09/2024.
    
    HOURLY DIVISOR: 164, derived from Art. 49 CCNL (38h/week for non-teaching staff at all levels). Formula: 38h/week × 52/12 = 164.67, truncated to 164 per Italian payroll convention. Source: ilccnl.it (aggregator); confirmed by Art. 49 working-hours article in the CCNL normative text (PDF page 29–30).
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Confirmed by Art. 23.6 CCNL ('Al lavoratore assunto con contratto a tempo determinato spettano le ferie e la 13.ma mensilità, il T.F.R. e ogni altro trattamento in atto').
    
    INPS: reuses 2026-terziario.json (TERZIARIO sector). Private religious schools are private-sector employers; employer INPS classification follows the general terziario sector consistent with other private educational and social institutions (cf. UNEBA T141 which uses the same sector).
    
    HOURLY RATE — TEACHING STAFF: hourly_divisor=164 (38h/week) applies to ATA/non-teaching staff. L4 docenti (scuola infanzia/primaria) have 24h/week; L5 docenti (scuola secondaria) have 18–22h/week; L6 (presidi) differ. The engine derives no hourly base for this CCNL (no verified hourly base provenance): overtime and absences take the caller's hourly rate, so the single divisor reaches no amount; it must be split by profile before the hourly base is verified. Base monthly salary and all annual financial figures (gross, net, INPS, TFR, IRPEF) are unaffected. (review of 2026-10-30)
    

## Raw data

The contract file this page is generated from: [`agreement/scuole-private-agidae.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/scuole-private-agidae.json).

## Usage example

```python
--8<-- "docs/examples/agreement/scuole-private-agidae/example.py"
```
