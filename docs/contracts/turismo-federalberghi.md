# CCNL Turismo — Federalberghi/Faita

| | |
|---|---|
| **CNEL code** | `H052` |
| **Sector** | Turismo |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-07-05 |
| **Workers (est.)** | ~220k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🏭 Production |

[← Contracts index](index.md)

??? note "Signatories"
    - Federalberghi
    - Faita (L'Ospitalità Italiana)
    - Filcams-CGIL
    - Fisascat-CISL
    - UILTuCS

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, seniority, sickness |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 71 verified / 1 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 🏭 Production | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-07-05 |
| **Last review** | 2026-10-13 |
| **Latest salary tranche** | 2027-11-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule read again in the signed texts: the ipotesi of 5 July 2024 (scan, Federalberghi copy), the renewal of 18 January 2014 and the CCNL of 20 February 2010. | corrected | 82 records verified. The salary periods cited the 2010 text: the 2016 values are in the 2014 renewal (p. 17), the 2024-2027 values in the 2024 ipotesi (p. 42). The 2024 text has no text layer: its quotes are OCR, checked on the page images.<br>Level B is quadro (art. 48 c.1), not impiegato; levels 1-7 have no category of their own (art. 50, by mansione): null.<br>Added the Quadri function allowance of art. 145: A 75.00, B 70.00 from January 2009.<br>Sickness: 75% for days 4-20 and 100% from day 21 of the net daily pay, 180 days a calendar year (art. 228), not a flat 100%.<br>Accrual: hotels and campsites counted twenty-sixths before 2024 too (artt. 225, 277): the cumulated-fractions clause dropped.<br>Seniority from 1 May 1990 (art. 158 c.4); Fon.Te. from 29 November 1996 (art. 162), no longer from 2026; ruleset and validity from the decorrenza of 1 July 2024 (art. 199); the ruleset source is the 2024 ipotesi.<br>Holiday overtime 30% stays derived from art. 219 c.1: the CCNL sets no festive overtime rate.<br>Overtime is paid on the retribuzione of art. 148 divided by 172 (art. 151): hourly_base_method gross_incl_allowances.<br>Production blocked: no signed copy of the accordo apprendistato of 17 April 2012 (base durations, art. 13) in the CNEL archive of H052 or at the signatories; only art. 14 bis is read in the 2014 renewal.<br>No renewal after the ipotesi of 5 July 2024 through October 2026. |
| 2026-10-13 | claude-opus-5-5 (ai) | Scope of the declared limitations. | corrected | sickness_net_basis is recorded on every run with a sickness event (trigger run), not only documented.<br>The apprenticeship durations without a signed source are now a limitation on every apprentice run (apprenticeship_durations_unsourced); with every remaining gap flagged on the runs it concerns, the file moves to production. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A` | Level A | € 2,495.22 | 2027-11-01 |
| `B` | Level B | € 2,310.11 | 2027-11-01 |
| `1` | Level 1 | € 2,152.32 | 2027-11-01 |
| `2` | Level 2 | € 1,967.20 | 2027-11-01 |
| `3` | Level 3 | € 1,855.32 | 2027-11-01 |
| `4` | Level 4 | € 1,750.69 | 2027-11-01 |
| `5` | Level 5 | € 1,641.85 | 2027-11-01 |
| `6s` | Level 6 super | € 1,578.72 | 2027-11-01 |
| `6` | Level 6 | € 1,556.35 | 2027-11-01 |
| `7` | Level 7 | € 1,458.42 | 2027-11-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 40.80 |
| `B` | € 39.25 |
| `1` | € 37.70 |
| `2` | € 36.15 |
| `3` | € 34.86 |
| `4` | € 33.05 |
| `5` | € 32.54 |
| `6s` | € 31.25 |
| `6` | € 30.99 |
| `7` | € 30.47 |

## Apprenticeship

**standard** (type: `percentage`)  
Destination levels: `2`, `3`, `4`, `5`, `6s`, `6`  
percentage: 0.95

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "turismo-federalberghi/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: art. 158 c.1 (2010 text, p. 140) grants the six scatti 'a tutto il personale' and art. 58 pays the apprentice a percentage of the normale retribuzione of the qualified worker, which art. 148 defines with the scatti: apprentices accrue the level amount. The engine pays no increment during the apprenticeship; the run is affected when the apprentice has matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "turismo-federalberghi/sickness_net_basis · sickness · impact yes · open"
    SICKNESS (art. 228, 2010 text p. 184): the CCNL integrates up to a share of the net daily pay without saying how the net pay is computed; the engine grosses up the INPS indemnity by the worker's INPS rate, as for the Commercio file. Day 1 of the carenza is the worker's when the illness lasts three days or less (c.5): the engine pays all three days. For fixed-term and seasonal workers no integration is due past the end of the contract (c.2).

    **Applies when:** `sickness` applies.

    **Remediation:** Model the net daily pay of art. 228, the unpaid first day of a short illness and the end of a fixed-term contract.

!!! warning "turismo-federalberghi/turismo_unmodelled_elements · base_salary · impact yes · open"
    NOT MODELLED AMOUNTS: the lower paga base of 1-2 star hotels and campsites up to 1200 presenze (art. 152 c.2 as replaced in 2024, p. 43; level 4 1,688.98 instead of 1,695.69 from May 2026); the elemento economico di garanzia paid with the November 2027 pay without an integrative agreement by 31 October 2026 (art. 13 c.10, pp. 11-12: A and B 186, 1-3 158, 4-5 140, 6s-7 112); the EDR of 0.60% of the paga base x 14 owed when the employer omits the EBNT/EBT quota (art. 23, p. 13) and the EUR 14 x 14 owed without Fondo FAST (art. 163, pp. 47-48); the hourly table of the extra workers (art. 155 c.3, p. 44); the absorption of the Quadri allowance into individual treatments (art. 145); the first scatto counted from age 18 and from the month after the triennium (art. 158 c.2-3); the net cap of the apprentice pay (art. 58 c.3); the ratei of the tredicesima and quattordicesima during maternity, paternity and parental leave (artt. 160 c.4 and 161 c.6); the lower ramp of the hires of 14 November 2016 (verbale 30 November 2016). The caller pays them as variable items.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the small-hotel table, the 2027 guarantee element, the fund omission EDRs and the extras table.

!!! warning "turismo-federalberghi/apprenticeship_durations_unsourced · base_salary · impact yes · open"
    APPRENTICESHIP DURATIONS: the durations of the professionalizzante come from the accord of 17 April 2012 as amended in 2014, of which no signed or CNEL copy was found (only aggregator copies); the percentages of art. 58 are verified. Every apprentice run carries this limitation.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Read a signed copy of the accord of 17 April 2012 and its 2014 amendment.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days. INPS computes it on its own daily base (retribuzione media globale giornaliera of the month before) and on calendar days. The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the INPS indemnity on the INPS daily base and calendar days of the INPS rules, with the pay of the month before, then resolve this limitation.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-07-05 | [↗](https://intranet.federalberghi.it/pubblicazioni/CCNL%20Turismo/CCNL%20Turismo%205%20luglio%202024/ccnl%20turismo%20-%20ipotesi%20di%20accordo%205%20luglio%202024.pdf) |
| — | — | 2014-01-18 | [↗](https://intranet.federalberghi.it/pubblicazioni/CCNL%20Turismo/CCNL%20Turismo%2018%20gennaio%202014/ccnl%20turismo%2018%2001%2014%20versione%20guida.pdf) |
| — | — | 2010-02-20 | [↗](http://www.uiltucs.it/pdf/turismo/CCNL_Turismo_Confcommercio_2010.pdf) |

??? note "Coverage notes"
    CNEL code H052 is shared with CCNL Agenzie di Viaggio Fiavet: the engine allows duplicates.
    
    SALARY TABLES: the 1 April 2016 values from art. 152 c.1 of the renewal of 18 January 2014 (p. 17); the five tranches lug 2024, giu 2025, mag 2026, apr 2027 and nov 2027 from art. 152 c.1 of the ipotesi of 5 July 2024 (p. 42).
    
    APPRENTICESHIP: 80%, 85%, 90% and 95% from the fourth year (art. 58 c.1, 2010 text p. 90), to which art. 152 c.4 of the 2024 text still refers. Destination levels 2, 3, 4, 5, 6s and 6. The durations of art. 54 of the 2010 text were replaced by the accordo apprendistato of 17 April 2012 and its art. 14 bis (renewal of 18 January 2014, p. 12: 2 and 3 34 months, 6 22 months with prior learning); no signed copy of the 2012 accord was found, so its base durations are not sourced. The 95% band is open-ended.
    
    HOURLY DIVISOR: 172 for the 40-hour week (art. 151 c.1, 2010 text p. 135); 190 and 192 for 44 and 45 hours not modelled.
    
    MONTHLY PAYMENTS: 14, art. 160 (tredicesima) and art. 161 (quattordicesima, paid with the July pay) as replaced by the renewal of 5 July 2024 (pp. 45-46).
    
    SENIORITY: six scatti triennali (art. 158, 2010 text pp. 140-141), fixed amounts per level from 1 May 1990.
    

## Raw data

The contract file this page is generated from: [`agreement/turismo-federalberghi.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/turismo-federalberghi.json).

## Usage example

```python
--8<-- "docs/examples/agreement/turismo-federalberghi/example.py"
```
