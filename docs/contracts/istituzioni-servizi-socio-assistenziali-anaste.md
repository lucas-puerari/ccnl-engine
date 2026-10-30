# CCNL Istituzioni e Servizi Socio-Assistenziali (ANASTE)

| | |
|---|---|
| **CNEL code** | `T131` |
| **Sector** | servizi socio-assistenziali |
| **Family** | `socio-sanitario` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-07-23 |
| **Workers (est.)** | ~120k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANASTE
    - FISASCAT-CISL
    - UILTuCS-UIL
    - UGL Terziario

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, seniority, una_tantum |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🟢 Verified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 31 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-07-23 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2025-08-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 74 - Tredicesima mensilità (p. 57): "4. Le frazioni di mese pari o superiori ai 15 giorni saranno considerate come mese intero.". Match: at_least 15. The quattordicesima differs: Art. 75: no separate 14th; an equivalent amount is already included in the minimo conglobato of art. 68, so no fraction rule applies to it. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro (dirigente di struttura o coordinatore senior) | € 2,130.15 | 2025-08-01 |
| `10` | Livello 10 — Responsabile di area/servizio | € 1,972.13 | 2025-08-01 |
| `9` | Livello 9 — Coordinatore/Professionista senior | € 1,893.48 | 2025-08-01 |
| `8` | Livello 8 — Operatore specializzato senior | € 1,769.59 | 2025-08-01 |
| `7` | Livello 7 — Operatore specializzato | € 1,752.93 | 2025-08-01 |
| `6` | Livello 6 — Operatore qualificato senior | € 1,696.37 | 2025-08-01 |
| `5` | Livello 5 — Operatore qualificato | € 1,637.06 | 2025-08-01 |
| `4` | Livello 4 — Operatore | € 1,562.10 | 2025-08-01 |
| `3S` | Livello 3 Super — Operatore ausiliario specializzato | € 1,525.03 | 2025-08-01 |
| `3` | Livello 3 — Operatore ausiliario | € 1,487.96 | 2025-08-01 |
| `2` | Livello 2 — Addetto generico | € 1,390.12 | 2025-08-01 |
| `1` | Livello 1 — Addetto base (introdotto nel rinnovo 2025) | € 1,295.43 | 2023-01-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 35.12 |
| `10` | € 33.57 |
| `9` | € 30.99 |
| `8` | € 30.47 |
| `7` | € 29.95 |
| `6` | € 28.92 |
| `5` | € 28.41 |
| `4` | € 27.89 |
| `3S` | € 27.63 |
| `3` | € 27.37 |
| `2` | € 26.86 |
| `1` | € 25.31 |

## Apprenticeship

**professionalizzante_32** (type: `percentage`)  
Destination levels: `Q`, `10`, `9`, `8`, `7`, `6`, `5`, `4`, `3S`, `3`, `2`, `1`  
percentage: 0.95

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "istituzioni-servizi-socio-assistenziali-anaste/una_tantum_2025 · una_tantum · impact yes · open"
    RENEWAL: CCNL signed 2025-07-23, triennio 2023-2025. Economic effects from 2025-08-01. Una tantum non modelled (non-recurring).

    **Applies when:** `una_tantum` applies; from 2025-08-01.

    **Remediation:** Source the amount and the payment months of the una tantum of the renewal of 23 July 2025, pay it outside the engine (ArrearsEvent) and record it as an open limitation.

!!! warning "istituzioni-servizi-socio-assistenziali-anaste/apprenticeship_low_levels_track · base_salary · impact yes · open"
    APPRENTICESHIP (Art. 22): modelled on levels 6-10 parameters (32 months, 90% mesi 1-28, 95% mesi 29+). Levels 1-5 have different duration (12 months, 95% from month 7) — not modelled separately.

    **Applies when:** `base_salary` applies; level in 1, 2, 3, 3S, 4, 5.

    **Remediation:** Add a 12-month percentage track for destinations 1-5 (90% months 1-6, 95% months 7-12, per Art. 22) and drop them from professionalizzante_32; record the limitation on the apprentice path until sourced.

!!! warning "istituzioni-servizi-socio-assistenziali-anaste/nurses_professional_allowance · base_salary · impact yes · open"
    NURSES ALLOWANCE: indennita professionale infermieri 155 EUR/month (12 months) not included — qualifica-specific, not level-specific.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the indennita professionale infermieri (155 EUR x 12) as a fixed allowance with role 'infermiere' (Allowance.role, months_per_year 12).

!!! warning "istituzioni-servizi-socio-assistenziali-anaste/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "apprenticeship_pct_undeclared_components · base_salary · impact unknown · open"
    A percentage apprenticeship reduces every fixed allowance whose apprenticeship_pct_relevant flag the data leaves at its default, together with the base salary. Whether the CCNL applies the percentage to that allowance (an EDR, a contingenza, a function allowance) was not sourced. The run is affected when such an allowance is in the apprentice's pay.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source, for each CCNL, the elements the apprenticeship percentage applies to and set apprenticeship_pct_relevant on every allowance; the limitation then no longer applies to its runs.

!!! note "sickness_inps_daily_base · sickness · impact unknown · resolved"
    The INPS share of a sick day is computed on the INPS daily base of the episode, on the days INPS pays (the weekdays of an operaio, every day but the national holidays on a Sunday of an impiegato, point 7.3 of INPS circ. 134368/1981): the retribuzione media globale giornaliera of the month before the illness (INPS circ. 134368/1981 point 11; circ. 55/2024 Allegato 1), whole or partial month, impiegato or operaio, or for the lavoratori dello spettacolo the average pay of the last 40 daily contributions, capped for a fixed-term worker (INPS circ. 132/2021 par. 2.4). The base is a fact of the payroll history the episode states (SicknessEpisode.inps_base).

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Resolved: the INPS share is computed on the base of every regime of the bundle; an episode that states no base the engine can read has the missing_fact issue sickness_inps_base_unknown (fact inps_base), which blocks the run. Tests: tests/integration/ccnl_engine/sickness/base/test_rules.py, tests/unit/ccnl_engine/sickness/base/test_rules.py.

!!! warning "sickness_cumulation_window · sickness · impact unknown · open"
    The CCNL tier and the comporto are counted on the days of one episode and the relapses it continues. A CCNL that sums the sickness of separate episodes over a window (a calendar year, the last three years) can reach a lower tier or the end of the comporto earlier than the engine shows. The run is affected when an earlier episode outside the relapse chain is recorded.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://snalv.it/docs/anaste25/pdf6.pdf | altro | 2025-07-23 | [↗](https://snalv.it/docs/anaste25/pdf6.pdf) |

??? note "Coverage notes"
    CONGLOBATED (Art. 69): minimo contrattuale conglobato includes base wage, contingenza and EDR. No separate contingenza or EDR column.
    
    HOURLY DIVISOR (Art. 72): 164 h/month for 38h/week. Verified: 1696.37/10.34=164.06 (lvl 6), 1893.48/11.55=163.94 (lvl 9), 2130.15/12.99=163.98 (lvl Q).
    
    ADDITIONAL MONTHS (Art. 74): tredicesima only (paid December). Art. 75 states the quattordicesima equivalent is already embedded in the monthly conglobated minimum.
    
    SENIORITY (Art. 73): scatti triennali, max 10 scatti. Per-level amounts confirmed from Art. 73 table.
    
    LEVEL Q ALLOWANCE (Art. 70): indennita di funzione 77.47 EUR/month paid 13 months/year.
    
    LEVEL 1 PRE-2025: level 1 introduced ex-novo in 2025 renewal. Pre-2025 salary set equal to 2025-08-01 value (1295.43 EUR) — no historical data available.
    

## Raw data

The contract file this page is generated from: [`agreement/istituzioni-servizi-socio-assistenziali-anaste.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/istituzioni-servizi-socio-assistenziali-anaste.json).

## Usage example

```python
--8<-- "docs/examples/agreement/istituzioni-servizi-socio-assistenziali-anaste/example.py"
```
