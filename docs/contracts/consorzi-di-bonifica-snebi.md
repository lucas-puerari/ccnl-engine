# CCNL Consorzi di Bonifica (SNEBI-FLAI-FAI-FILBI)

| | |
|---|---|
| **CNEL code** | `A131` |
| **Sector** | Agricoltura |
| **Family** | `bonifica-forestazione` |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2025-05-21 |
| **Workers (est.)** | ~4k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - SNEBI
    - FLAI-CGIL
    - FAI-CISL
    - FILBI-UIL

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

5 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 56 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-05-21 |
| **Last review** | — |
| **Latest salary tranche** | 2026-01-01 |

## Review history

No review is recorded.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `AQ187` | AQ187 — quadro | € 2,868.89 | 2026-01-01 |
| `AQ185` | AQ185 — quadro | € 2,838.21 | 2026-01-01 |
| `A184` | A184 | € 2,822.87 | 2026-01-01 |
| `A170` | A170 | € 2,608.08 | 2026-01-01 |
| `AQ164` | AQ164 — quadro | € 2,516.04 | 2026-01-01 |
| `AQ162` | AQ162 — quadro | € 2,485.35 | 2026-01-01 |
| `A160` | A160 | € 2,454.67 | 2026-01-01 |
| `A159` | A159 | € 2,439.32 | 2026-01-01 |
| `A157` | A157 | € 2,408.65 | 2026-01-01 |
| `A135` | A135 | € 2,071.13 | 2026-01-01 |
| `A134` | A134 | € 2,055.79 | 2026-01-01 |
| `B132_ex51` | B132 — ex cat. 5/1 (alternate scatto 47.73) | € 2,025.10 | 2026-01-01 |
| `B132` | B132 — ex cat. 4/1 (best-guess scatto 50.05) | € 2,025.10 | 2026-01-01 |
| `B128_ex52` | B128 — ex cat. 5/2 (alternate scatto 44.44) | € 1,963.73 | 2026-01-01 |
| `B128` | B128 — ex cat. 4/2 (best-guess scatto 47.92) | € 1,963.73 | 2026-01-01 |
| `C127` | C127 | € 1,948.38 | 2026-01-01 |
| `C122` | C122 | € 1,871.68 | 2026-01-01 |
| `C118` | C118 | € 1,810.32 | 2026-01-01 |
| `D117` | D117 | € 1,794.97 | 2026-01-01 |
| `D116` | D116 | € 1,779.62 | 2026-01-01 |
| `D115` | D115 | € 1,764.29 | 2026-01-01 |
| `D112` | D112 | € 1,718.28 | 2026-01-01 |
| `D107` | D107 | € 1,641.56 | 2026-01-01 |
| `D104` | D104 | € 1,595.53 | 2026-01-01 |
| `D100` | D100 | € 1,534.16 | 2026-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 10 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "consorzi-di-bonifica-snebi/pre_2000_cohort_table_missing · base_salary · impact yes · open"
    Dual-cohort: workers hired by 15-07-2000 have a lower salary table (~1.4% below post-2000) not modeled here. Those workers are a declining cohort (tenure 25+ years); new hires always enter the post-2000 table.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the lower salary table for workers hired by 15-07-2000 behind a hire-date fact.

!!! warning "consorzi-di-bonifica-snebi/ex_sublevel_scatto_mapping · seniority · impact unknown · open"
    B128 and B132 each contain two ex-classification sub-levels (B128: ex-4/2 and ex-5/2; B132: ex-4/1 and ex-5/1) sharing the same base salary but with different scatto amounts. Modeled as B128/B128_ex52 and B132/B132_ex51. Plain codes carry the ex-4 (higher) scatto as best-guess; _ex52/_ex51 codes carry the ex-5 (lower) scatto. Mapping is unverifiable from public sources (B128: 47.92 vs 44.44; B132: 50.05 vs 47.73).

    **Applies when:** `seniority` applies; level in B128, B128_ex52, B132, B132_ex51.

    **Remediation:** Verify which ex-classification sub-level carries each scatto amount against the CCNL text.

!!! warning "consorzi-di-bonifica-snebi/higher_tier_scatto_amounts · seniority · impact unknown · open"
    Seniority: 10 scatti total — tier 1: 6 biennali (cadence 24 months), tier 2: 1 dodicennale (cadence 144 months after tier 1 exhausted), tier 3: 3 quadriennali (cadence 48 months). All tiers modeled. Per-scatto amounts for tiers 2-3 assumed equal to tier 1 amounts (no independent source found for higher-tier amounts; best-guess from standard CCNL practice).

    **Applies when:** `seniority` applies.

    **Remediation:** Source the amounts of the dodicennale and quadriennali scatti and correct tiers 2-3.

!!! warning "consorzi-di-bonifica-snebi/quadri_function_allowance · base_salary · impact unknown · open"
    AQ-category levels (AQ162, AQ164, AQ185, AQ187) are quadri. An indennita di funzione may apply per standard quadri CCNL practice, but the amount could not be confirmed from available public sources; not modeled.

    **Applies when:** `base_salary` applies; level in AQ162, AQ164, AQ185, AQ187.

    **Remediation:** Source whether the CCNL pays an indennità di funzione to the AQ levels and model it.

!!! warning "consorzi-di-bonifica-snebi/apprentice_inps_rates_unsourced · inps_employer · impact unknown · open"
    APPRENTICE INPS RATES: the apprentice rates of the sector (agricoltura) apply the 10% of L. 296/2006 art. 1 c. 773 plus the 1.61% NASpI, but no source found settles the disoccupazione and CISOA contributions of agricultural apprentices (INPS circ. 43/2026 gives no apprentice rates). The contributions of an apprentice may differ.

    **Applies when:** `inps_employer` applies; contract type in apprentice.

    **Remediation:** Source the apprentice rates of agricoltura (an INPS circular or an association table of 2026), mark the apprentice block of contribution/2026/agricoltura.json derived, then remove this note.

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

!!! warning "inps_minimum_base_exempt_category · inps_employer · impact unknown · open"
    D.L. 463/1983 art. 7 c. 5 keeps the operai agricoli out of the 9.50% minimum daily base, and the run applies no minimum to them. Tabella A of INPS circ. 6/2026 still lists 51.70 for the operai agricoli, 'non soggetto all'adeguamento' of art. 7 c. 1; no source found says whether it is a floor of their contribution base. A base below it may understate the contributions.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Source the role of the 51.70 of the operai agricoli (INPS circ. 43/2026 on the agricultural contributions, or the minimum daily wages of art. 1 L. 389/1989), then apply it as their minimum or record that none applies.

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
| https://www.redigo.info/2026/03/06/ccnl-consorzi-di-bonifica-le-tabelle-retributive-aggiornate/ | tabella_retributiva | 2025-05-21 | [↗](https://www.redigo.info/2026/03/06/ccnl-consorzi-di-bonifica-le-tabelle-retributive-aggiornate/) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=286 | tabella_retributiva | 2025-05-21 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=286) |
| https://ilccnl.it/contratto/ccnl/consorzi-di-bonifica | altro | 2025-05-21 | [↗](https://ilccnl.it/contratto/ccnl/consorzi-di-bonifica) |

??? note "Coverage notes"
    Salary model: split (paga base + contingenza) per ilccnl.it, contingenza frozen at EUR 0.00, terzo elemento 0.00 (confirmed via ilccnl.it for D100, D104, D107). base_salary is the full minimo tabellare. Note: ilccnl.it tabelle show the pre-2000 cohort (e.g. D100 Jan2026=1513.09); post-2000 values (D100 Jan2026=1534.16) are sourced from redigo.info and kitech=286.
    
    Cohort: two salary tables — 'in servizio al 15-07-2000' (pre-2000) and 'in servizio dal 15-07-2000' (post-2000). This file models the post-2000 table. kitech.it CodiceCateg=286 title confirms post-2000 identity; redigo.info column 2 matches (D100 Jan2026=1534.16). Pre-2000 table is ~1.4% lower.
    
    Hourly divisor 164.67 h/month from ilccnl.it (single source). Consistent with 38h/week: 52x38/12=164.67. Daily divisor: 26.
    
    Additional months: 14 — tredicesima (dicembre) + quattordicesima (giugno). Source: ilccnl.it ('quattordici mensilitA').
    
    Tranches: 2025-07-01 (+3%) and 2026-01-01 (+2.2%). Both sourced from redigo.info primary table. No pre-July-2025 salary is modeled; engine returns no result for as_of before 2025-07-01.
    
    layer_2 out_of_scope: no apprenticeship data found in available public sources. Full CCNL PDF required.
    

## Raw data

The contract file this page is generated from: [`agreement/consorzi-di-bonifica-snebi.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/consorzi-di-bonifica-snebi.json).

## Usage example

```python
--8<-- "docs/examples/agreement/consorzi-di-bonifica-snebi/example.py"
```
