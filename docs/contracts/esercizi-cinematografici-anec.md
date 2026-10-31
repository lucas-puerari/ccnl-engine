# CCNL Esercizi Cinematografici e Cinema-Teatrali (ANEC)

| | |
|---|---|
| **CNEL code** | `G211` |
| **Sector** | cinema |
| **Family** | `spettacolo-media` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-10-16 |
| **Workers (est.)** | ~6k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANEC
    - FISTel CISL
    - UILCOM UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | inps_employer, seniority, sickness |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 54 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-10-16 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2025-07-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 20 - Tredicesima mensilita' o gratifica natalizia (p. 27): "La frazione di mese superiore a 15 giorni sarà considerata, a tali effetti, come mese intero.". Match: more_than 15. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QA` | Quadro A — Multiplex/Megaplex (parametro 240) | € 2,103.45 | 2025-07-01 |
| `QB` | Quadro B — Multiplex/Megaplex (parametro 220) | € 1,970.12 | 2025-07-01 |
| `Q` | Quadro — Monosala/Multisala (parametro 220) | € 1,970.12 | 2025-07-01 |
| `F` | Livello F — Multiplex/Megaplex (parametro 185) | € 1,736.47 | 2025-07-01 |
| `5S` | V livello superiore — Monosala/Multisala (parametro 185) | € 1,736.47 | 2025-07-01 |
| `5` | V livello — Monosala/Multisala (parametro 176) | € 1,677.32 | 2025-07-01 |
| `E` | Livello E — Multiplex/Megaplex (parametro 165) | € 1,603.17 | 2025-07-01 |
| `4` | IV livello — Monosala/Multisala (parametro 159) | € 1,563.49 | 2025-07-01 |
| `D` | Livello D — Multiplex/Megaplex (parametro 150) | € 1,503.61 | 2025-07-01 |
| `C` | Livello C — Multiplex/Megaplex (parametro 140) | € 1,436.95 | 2025-07-01 |
| `3` | III livello — Monosala/Multisala (parametro 132) | € 1,383.48 | 2025-07-01 |
| `B` | Livello B — Multiplex/Megaplex (parametro 122) | € 1,316.62 | 2025-07-01 |
| `2` | II livello — Monosala/Multisala (parametro 112) | € 1,249.95 | 2025-07-01 |
| `A` | Livello A — Multiplex/Megaplex (parametro 100) | € 1,170.00 | 2025-07-01 |
| `1` | I livello — Monosala/Multisala (parametro 100) | € 1,170.00 | 2025-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 13.26 |
| `A` | € 13.26 |
| `2` | € 14.37 |
| `B` | € 15.38 |
| `3` | € 16.34 |
| `C` | € 17.11 |
| `D` | € 18.07 |
| `4` | € 18.96 |
| `E` | € 19.52 |
| `5` | € 20.62 |
| `5S` | € 21.45 |
| `F` | € 21.45 |
| `Q` | € 24.82 |
| `QB` | € 24.82 |
| `QA` | € 26.75 |

## Apprenticeship

**standard** (type: `percentage`)  
Destination levels: `1`, `A`, `2`, `B`, `3`, `C`, `D`, `4`, `E`, `5`, `5S`, `F`, `Q`, `QB`, `QA`  
percentage: 0.90

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "esercizi-cinematografici-anec/fpls_rates_approximated · inps_employer · impact unknown · open"
    SIMPLIFICATION: tax_sector=TERZIARIO. Cinema exhibition employees (esercizio cinematografico) were historically under ENPALS (now FPLS — Fondo Pensione Lavoratori dello Spettacolo dell'INPS, Art. 12 comma 6 of this CCNL). The FPLS contribution regime differs from ordinary terziario. terziario rates are used as an approximation pending a dedicated cinema-FPLS tax file. For the workers enrolled after 31 December 1995 the IVS of the FPLS is the ordinary 33% (23.81 + 9.19) up to the annual massimale (INPS, Calcolo dei contributi IVS dei lavoratori dello spettacolo, updated 5 October 2026), as charged here; approximated are the daily bands of the workers enrolled before 1996 (massimale 892 a day in 2026, solidarity 5% above it) and the non-IVS contributions.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Add a dedicated FPLS contribution ruleset for cinema exhibition employees.

!!! warning "esercizi-cinematografici-anec/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "esercizi-cinematografici-anec/sickness_net_basis · sickness · impact unknown · open"
    SICKNESS (Art. 64): the CCNL integrates up to 100% of the normal net pay ('normale retribuzione netta') without saying how the net pay is computed. The engine grosses up the INPS indemnity by the worker's INPS rate (the 'lordizzazione' of payroll practice, Ordine dei Consulenti del Lavoro di Salerno) and tops it up to the measure of the gross daily quota; IRPEF is left out, as it falls on both. Day bands, carenza by event, the yearly comporto and the exclusion of apprentices are modelled.

    **Applies when:** `sickness` applies.

    **Remediation:** Find a source (an interpretation of the parties, an INPS or Ministry text) that defines the net daily pay of Art. 64, align the computation, then resolve this limitation.

!!! warning "esercizi-cinematografici-anec/sickness_hospital_exclusions · sickness · impact yes · open"
    SICKNESS (Art. 64): the hospital stays (day hospital included), the life-saving therapies and the continuous absences over a month for serious illnesses (at most 90 days) are left out of the comporto and of the pay count; and from day 181 the CCNL pays 50% of its own integration, which the engine reads as 50% of the pay: a day INPS still indemnifies in a new year is paid only the INPS share.

    **Applies when:** `sickness` applies.

    **Remediation:** Leave the hospital stays, life-saving therapies and serious illnesses of Art. 64 out of the counts and pay half of the integration past day 180, then resolve this limitation.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.fistelcisl.it/wp-content/uploads/2025/10/CCNL-Esercizi-cinematografici-2023-2026.pdf | altro | 2025-10-16 | [↗](https://www.fistelcisl.it/wp-content/uploads/2025/10/CCNL-Esercizi-cinematografici-2023-2026.pdf) |

??? note "Coverage notes"
    Two parallel level systems in the same contract (one CNEL code G211): Monosala/Multisala (7 levels: 1,2,3,4,5,5S,Q with parametri 100/112/132/159/176/185/220) and Multiplex/Megaplex (8 levels: A,B,C,D,E,F,QB,QA with parametri 100/122/140/150/165/185/220/240). The 15 levels are interleaved by salary for ordering (non-decreasing constraint). Levels 1 and A share identical salaries (parametro 100), as do 5S and F (parametro 185) and Q and QB (parametro 220). Level QA (parametro 240) is Multiplex/Megaplex only. The 'order' field is a global salary rank across both classification scales and is not a promotion ladder.
    
    Level code aliases in the PDF: monosala Q is also written 'VI Qua' in the paga table header and '6' in Tabella B. Code 'Q' (Tabella A label) is used consistently here.
    
    Workers: 6,427 (ADAPT 18th Report, CNEL aggiornamento 31/12/2023).
    
    SICKNESS INPS REGIME: the employees insured with the Fondo pensioni lavoratori dello spettacolo, operai and impiegati alike, have their own INPS sickness indemnity (INPS circ. 132/2021): from the fourth day, 60% up to the 20th day and 80% from the 21st to the 180th (regime 'spettacolo'), with 40 daily contributions from 1 January of the year before (SicknessEpisode.daily_contributions).
    
    Primary source: CCNL Esercizi Cinematografici 2023-2026 (FISTel CISL, signed 16/10/2025). Art. 54: period 01/01/2023-31/12/2026. Three salary tranches: 01/01/2023, 01/11/2024, 01/07/2025 from salary tables (pages 59-65 of the PDF). Baseline (31/12/2022 column) used only for increment verification, not modelled as a separate period.
    
    Hourly divisor 173: Art. 63 Dichiarazione a verbale (explicit formula: 'la retribuzione oraria si ottiene dividendo quella mensile per il coefficiente 173'). Daily divisor 26 also from Art. 63.
    
    Additional months 14: Art. 20 (tredicesima, December) and Art. 21 (quattordicesima, paid 1 luglio each year).
    
    Seniority (Art. 22): biennale (cadence 24 months), maximum 5 scatti. Amounts from Tabella A (appended to CCNL). Cross-verified against Art. 62 (Indennita di Cassa 'Sola P.B.' table): Tabella A formula is 5% of frozen paga base (Art. 62 column) plus a fixed addend (3.62 for monosala L3, confirming 12.72+3.62=16.34). The salary table bottom row shows 16.26 for monosala L3 (IV scatto basis) — this is a typographic error; Tabella A value 16.34 is authoritative.
    
    Apprenticeship (Art. 16): percentage type, 70%/80%/90% for years 1/2/3 of the apprenticeship, calculated on the minimo salariale of the classification level. In vigore dal 01/01/2018. Applicable to all 15 levels (Art. 16 states no level exclusion).
    

## Raw data

The contract file this page is generated from: [`agreement/esercizi-cinematografici-anec.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/esercizi-cinematografici-anec.json).

## Usage example

```python
--8<-- "docs/examples/agreement/esercizi-cinematografici-anec/example.py"
```
