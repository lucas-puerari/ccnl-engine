# CCNL CED, ICT, Professioni Digitali e STP (Assoced-UGL)

| | |
|---|---|
| **CNEL code** | `H601` |
| **Sector** | Terziario |
| **Family** | `servizi-professionali` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-07-28 |
| **Workers (est.)** | ~22k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Assoced
    - LAIT
    - Confterziario
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
| **Limits of this contract** | base_salary, inps_employer, seniority |

3 documented simplification(s) and 1 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 44 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-07-28 |
| **Last review** | — |
| **Latest salary tranche** | 2028-01-01 |

## Review history

No review is recorded.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QDIR` | Quadri di Direzione | € 3,186.49 | 2028-01-01 |
| `Q` | Quadri | € 2,895.91 | 2028-01-01 |
| `1` | 1° livello | € 2,486.32 | 2028-01-01 |
| `2` | 2° livello | € 2,225.94 | 2028-01-01 |
| `3S` | 3° livello Super | € 2,134.17 | 2028-01-01 |
| `3` | 3° livello | € 1,997.93 | 2028-01-01 |
| `4` | 4° livello | € 1,859.01 | 2028-01-01 |
| `5` | 5° livello | € 1,769.98 | 2028-01-01 |
| `6` | 6° livello | € 1,494.74 | 2028-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**professionalizzante_36** (type: `under_classification`)  
Destination levels: `2`, `3S`, `3`, `4`  
under-level: `1`

**professionalizzante_24** (type: `under_classification`)  
Destination levels: `5`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "ced-assoced/grandfathered_scatti · seniority · impact yes · open"
    Scatti di anzianita (Art. 166, 2022 stesura): abrogated from 01/01/2019. Grandfathered for personale in forza al 31-12-2018 only. New hires (post-2018): maximum_count=0. Per-level 2009 amounts: QDIR=52, Q=47, L1=44, L2=40, L3S=36, L3=33, L4=30, L5=27, L6=24 (frozen, not updated since 2009 across 2022 and 2025 renewals).

    **Applies when:** `seniority` applies.

    **Remediation:** Model the scatti frozen at 31/12/2018 for the staff then in service (amounts listed in the note) gated on the hire date, or tell the caller to pass them as Employment.individual_elements (absorbable false) as chimica-farmaceutica-federchimica does.

!!! warning "ced-assoced/conditional_allowances_title_xxiii · base_salary · impact yes · open"
    Titolo XXIII conditional allowances not modelled: indennita di mensa (Art. 179), rimborso mezzi pubblici (Art. 180), indennita valori (Art. 181), and elemento economico di garanzia (Art. 177). These are condition-gated or azienda-specific and cannot be determined without employer-level data.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model Art. 177 elemento economico di garanzia and Arts. 179-181 (mensa, mezzi pubblici, valori) as conditional fixed allowances or caller-declared items once a fact can express their conditions.

!!! warning "ced-assoced/terziario_inps_rates_unverified · inps_employer · impact unknown · open"
    INPS terziario rates reused from 2026-terziario.json (same sector as H016). Verify against annual INPS circular for exact H601 sub-sector rate.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Verify the H601 sub-sector INPS rate against the annual INPS circular.

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

!!! warning "disability_permit_tfr · disability_permits · impact unknown · open"
    The days of permit under L. 104/1992 art. 33 c. 3 keep the TFR base, as payroll practice holds; art. 2120 c. 3 c.c. keeps in the TFR base only the absences of art. 2110 c.c. and the wage integration, and no primary source read says the permits are among them, so the TFR quota of a month with permits may be overstated.

    **Applies when:** `disability_permits` applies; the run takes the engine code path.

    **Remediation:** Source the TFR treatment of the permit days (an INPS or Ministry ruling, or case law of the Cassazione) and apply it, then resolve this limitation.

!!! warning "extraordinary_leave_daily_base · extraordinary_leave · impact unknown · open"
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year over 365: art. 42 c. 5-ter D.Lgs. 151/2001 and INPS messaggio 30/2024 set the pay and its rateo of the extra months, and the INPS table of the yearly maximum divides it by 365 (2026: 43,486.00 / 365 = 119.14), but no source read states the divisor of the worker's own pay.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily divisor INPS applies to the last pay (circ. INPS 64/2001 or 32/2012) and apply it, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.fondoeasi.it/fondo-easi/ccnl-ced-ced-ict-professioni-digitali-e-stp/stesura-ccnl-ced-09-marzo-2022.pdf | altro | 2022-03-09 | [↗](https://www.fondoeasi.it/fondo-easi/ccnl-ced-ced-ict-professioni-digitali-e-stp/stesura-ccnl-ced-09-marzo-2022.pdf) |
| https://www.redigo.info/ccnl-ced-ict-professioni-digitali-stp | tabella_retributiva | 2025-07-28 | [↗](https://www.redigo.info/ccnl-ced-ict-professioni-digitali-stp) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=62 | tabella_retributiva | 2025-07-28 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=62) |

??? note "Coverage notes"
    Salary model: paga base nazionale conglobata (Art. 172, 2022 stesura). Single TimeSeries per level, no separate contingenza or EDR.
    
    Unified classification covers CED, ICT, Professioni Digitali and STP workers (Art. 172 + Tabella A, one scale). No separate STP salary table exists in the 2022 stesura or 2025 renewal.
    
    Divisore convenzionale 173 h/month (Art. 171) and 26 d/month (Art. 170). Source: 2022 stesura fondoeasi.it.
    
    Mensilita supplementari: tredicesima (Art. 175) and quattordicesima (Art. 176). additional_months = 14.
    
    Indennita di funzione (Tabella A note, 2025 renewal): QDIR 287/296/306 EUR, Q 250/258/266 EUR per 14 mensilita. Tranche dates: 01/09/2025, 01/09/2026, 01/09/2027, distinct from base salary tranches.
    
    Apprenticeship (Art. 23-24, 2022 stesura, ccnlced.it allegato): under_classification. First half 2 levels below, second half 1 level below. Level 5 exception: stays at Level 6 throughout 24-month track. Destination L2 duration 36 months (studiocerbone.com: 240 h/36 months for 2° livello). Source ccnlced.it showed '6 months' for L2 — treated as parsing artifact; 36 months adopted from studiocerbone.com.
    
    Salary tranches: 01/09/2025 (source-confirmed, redigo.info and kitech.it), 01/06/2026 (source-confirmed, both sources agree), 01/03/2027 (redigo.info only, single-source), 01/01/2028 (redigo.info only, single-source).
    

## Raw data

The contract file this page is generated from: [`agreement/ced-assoced.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/ced-assoced.json).

## Usage example

```python
--8<-- "docs/examples/agreement/ced-assoced/example.py"
```
