# CCNL per i lavoratori dipendenti dalle aziende di credito (ABI)

| | |
|---|---|
| **CNEL code** | `J241` |
| **Sector** | credito |
| **Tax sector** | `credito` |
| **Last renewal** | 2023-11-23 |
| **Workers (est.)** | ~270k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ABI
    - FABI
    - FIRST-CISL
    - FISAC-CGIL
    - UILCA
    - UNISIN

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | inps_employer, overtime, seniority, sickness |

7 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 43 verified / 2 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2023-11-23 |
| **Last review** | 2026-10-17 |
| **Latest salary tranche** | 2026-03-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-14 | claude-opus-5-5 (ai) | P1 audit: stipendio of the nine levels in the four tranches, scatti, number of monthly payments and term, against the renewal of 23 November 2023. | corrected | The 36 stipendi match the tables to the cent; they were cited to a union news page and are now verified against the tables of the renewal (pp. 35-38).<br>The first tranche runs from 1 July 2023 (the tables), not from the signing date 23 November 2023: corrected.<br>13 monthly payments: verified ('Importi mensili per 13 mensilità').<br>Scatti amounts match; cadence and maximum counts not in the tables: derived.<br>Importo ex ristrutturazione not modelled: declared. The agreement expired on 31 March 2026 (Art. 1). |
| 2026-10-15 | claude-opus-5-5 (ai) | Registry check: CNEL code, name, signatories and term against the 21st CNEL report of CCNLs in force (30 June 2025) and the term clause of the text read in the P1 review. | confirmed | CNEL J241 matches (ABI with FABI, FIRST CISL, FISAC CGIL, UILCA, UNISIN; the report adds Intesa Sanpaolo as a depositor).<br>Term: Art. 1 of the renewal 'scadrà [...] il 31 marzo 2026'. The report shows 31/12/2028, which no text or party source supports; the parties suspended the deadlines to 31 July 2026 and the renewal is still open. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'straordinario, notturno, festivo, turni e maggiorazioni cumulabili': the overtime bands and the night, holiday and shift premiums of the file against the text read in the P1 review. | flagged | The overtime bands (25%, 55% night, 65% holiday) stay derived: the CCNL of 19 December 2019 that sets them is not published by a party in full, and the renewal of 23 November 2023 does not amend them. The hourly base of the ABI CCNL was not read: the BCC CCNL computes it on 90.66% of one twelfth of the annual pay, which the engine does not apply. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'scatti di anzianità, indennità e altri elementi fissi', re-read on the full text published by a party, found on 15 October 2026. | corrected | Scatti: the 48-month first scatto, the 36-month cadence and the maxima (8; 7 for QD3 and QD4) match Art. 94 and 103: verified. The freeze of 1 January 2013 - 31 July 2014 (Art. 103 c. 3) is declared. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'straordinario, notturno, festivo, turni e maggiorazioni cumulabili', re-read on the full text published by a party, found on 15 October 2026. | corrected | Art. 114 c. 15 (p. 152): 25% weekday and 55% night match; 65% is the night overtime of the rest days and festività, not the daytime holiday overtime: moved to night_holiday. Art. 115 (p. 153): holiday work 30% and rest-day work 25%: added; the daytime holiday band was 65%, corrected. Saturday 30% and the 1/360 / 7,4 hourly base are declared. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'ferie, permessi, festività, assenze, malattia e comporto', re-read on the full text published by a party, found on 15 October 2026. | corrected | Sickness (Art. 66, p. 101): full pay for 6 to 24 months by seniority, not a flat 180 days: modelled on the 48-month count of c. 2 with six seniority bands; the c. 1 count and the extended periods are declared.<br>Ferie (Art. 60, p. 89): 20/22/25 days of the aree match; the quadri have 26 (noted). Tredicesima accrual: a fraction of month counts (Art. 51, p. 77): verified. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'part-time, tempo determinato, apprendistato e periodo di prova', re-read on the full text published by a party. | corrected | Art. 36 (p. 53): one level below for 18 months, then the destination; all 3a area profiles are destinations: 3A1 added (from 1e2A); the apprenticeship_destination_levels limitation is resolved. |
| 2026-10-17 | claude-opus-5-5 (ai) | Periodic review due 2026-12-31: the stipendi from 2023 and the scatti against the CCNL ABI of 23 November 2023, the hourly divisor, and the readiness of the file. | flagged | The 36 stipendi of the nine levels from 2023 and the scatti (QD4 and QD3 95,31, QD2 to 3A1 41,55, 1a and 2a area 29,07) are printed in the texts read. Match.<br>Flagged: the hourly divisor of the file (162, then 160) has no provenance. Art. 114 c. 15 of the testo coordinato computes the paga oraria 'secondo il comune criterio (1/360 della retribuzione annua per ogni giornata diviso 7,4)': on thirteen monthly payments the monthly pay over 204,92, not over 160. Every amount the engine derives from the hourly divisor (absence deductions, the hourly rate of the overtime bands) is affected; the elements of the 'retribuzione annua' were not read.<br>Not promoted to reviewed: verification.confidence is unverified and the hourly divisor is unsourced. The two derived rules (the solidarity fund rates and the absence rule) stay derived. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QD4` | Executive Managers - 4th level | € 5,160.06 | 2026-03-01 |
| `QD3` | Executive Managers - 3rd level | € 4,396.88 | 2026-03-01 |
| `QD2` | Executive Managers - 2nd level | € 3,965.48 | 2026-03-01 |
| `QD1` | Executive Managers - 1st level | € 3,743.21 | 2026-03-01 |
| `3A4` | 3rd Professional Area - 4th level | € 3,341.90 | 2026-03-01 |
| `3A3` | 3rd Professional Area - 3rd level | € 3,059.49 | 2026-03-01 |
| `3A2` | 3rd Professional Area - 2nd level | € 2,890.41 | 2026-03-01 |
| `3A1` | 3rd Professional Area - 1st level | € 2,742.34 | 2026-03-01 |
| `1e2A` | 1st and 2nd Professional Area (Unified Area) | € 2,479.45 | 2026-03-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `QD4` | € 95.31 |
| `QD3` | € 95.31 |
| `QD2` | € 41.55 |
| `QD1` | € 41.55 |
| `3A4` | € 41.55 |
| `3A3` | € 41.55 |
| `3A2` | € 41.55 |
| `3A1` | € 41.55 |
| `1e2A` | € 29.07 |

## Apprenticeship

**terza_area** (type: `under_classification`)  
Destination levels: `3A1`, `3A2`, `3A3`, `3A4`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "bancari-abi/inps_credit_rate_unverified · inps_employer · impact unknown · open"
    INPS employer_rate 26.76% flat from kitech.it (Credito e Assicurazioni 2026); the Fondo di solidarietà del credito (bilateral) is presumed included in the aggregate rate. Verify against the annual INPS circular.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Verify the 26.76% employer rate and the solidarity fund share against the annual INPS circular.

!!! warning "bancari-abi/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "bancari-abi/inps_sector_rates_unsourced · inps_employer · impact unknown · open"
    INPS RATES: the employer and worker INPS rates of the sector (credito) are totals no 2026 INPS or association table confirms: the only component split found is the INPS guide of 2012 and the 2026 totals come from a software house page that does not prove its year. The contributions of every run rest on them.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Source the credito rates of 2026 on an INPS or association table, mark the inps block of contribution/2026/credito.json derived, then remove this note.

!!! warning "bancari-abi/ex_ristrutturazione_amount · seniority · impact yes · open"
    IMPORTO EX RISTRUTTURAZIONE: the tables of the renewal print, next to the scatto, an 'importo ex ristrutturazione' (14,30 for QD3 and QD4, 7,99 for QD1, QD2 and the 3a Area, 5,59 for the Area Unificata); the bundle does not pay it. TERM: the renewal of 23 November 2023 expires on 31 March 2026 (Art. 1); the tables stay those of March 2026 until a renewal is read.

    **Applies when:** `seniority` applies.

    **Remediation:** Source who receives the importo ex ristrutturazione and model it with the scatti, then remove this note.

!!! warning "bancari-abi/scatti_freeze_2013_2014 · seniority · impact yes · open"
    SCATTI FREEZE 2013-2014: no seniority for the scatti and the importo ex ristrutturazione accrues from 1 January 2013 to 31 July 2014 (Art. 103 c. 3, testo coordinato p. 142); staff in service on 19 December 1994 keep 12 scatti (Art. 94 c. 2, Art. 103 c. 2). The engine counts the seniority of the request without the freeze.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** State the seniority of a worker in service in 2013-2014 net of the 19 months of the freeze.

!!! warning "bancari-abi/abi_saturday_overtime_and_hourly_base · overtime · impact yes · open"
    OVERTIME, SATURDAY AND HOURLY BASE: Saturday overtime is paid 30% (Art. 114 c. 15), and the request has no Saturday kind. The hourly pay of overtime and of holiday work is 1/360 of the annual pay for each day divided by 7,4 (Art. 114 c. 15): the hourly divisor carries the 360 x 7,4 / 13, but the engine applies it to the minimo tabellare, and the elements of the 'retribuzione annua' (scatti and other fixed items) were not read.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a Saturday kind and read the elements of the annual pay that art. 114 c. 15 divides.

!!! warning "bancari-abi/abi_sickness_counting · sickness · impact yes · open"
    SICKNESS COUNTING: Art. 66 c. 1 keeps the job and the whole pay for 6, 8, 12, 15, 18 or 22 months by seniority; c. 2 lets the employer count instead the 48 months before the last day of absence, with 8, 10, 14, 18, 22 or 24 months. The file applies c. 2; an employer counting by c. 1 pays fewer months. The periods rise by 50% for tbc, AIDS and disabilità grave and double for oncological illness (cc. 4-5), not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a fact for the counting the employer adopts and the extended periods of Art. 66 cc. 4-5.

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
| — | — | 2023-11-23 | [↗](https://www.first-cisl.it/rinnovo-ccnl-bancari-2023/) |
| — | — | — | [↗](https://www.ccnlbancari.it/) |

??? note "Coverage notes"
    Hourly divisor 207,69 for the 37.5h/week period (2023-11-23 to 2024-06-30) and 204,92 from 2024-07-01 (37h/week): 360 x daily hours / 13 (Art. 114 c. 15, Art. 108).
    
    Seniority: first scatto after 48 months, then every 36 months; maximum 8 scatti for the Aree Professionali and 7 for QD3/QD4 (maximum_count_by_level).
    
    APPRENTICESHIP (Art. 36, testo coordinato p. 53): the apprentice of a 3a area profile is placed one level below the destination for the first 18 months, then paid the destination level 'con assegno temporaneo, corrispondente, al netto'; at most 3 years. Every 3a area level is a destination: an apprentice to 3A1 starts at the Area unificata (1e2A). The assegno equals the destination in net terms; the engine pays the destination gross.
    
    Apprenticeship: https://www.ccnlbancari.it/ Art. 35, post-rinnovo 2023-11-23.
    

## Raw data

The contract file this page is generated from: [`agreement/bancari-abi.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/bancari-abi.json).

## Usage example

```python
--8<-- "docs/examples/agreement/bancari-abi/example.py"
```
