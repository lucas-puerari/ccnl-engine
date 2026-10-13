# CCNL per i lavoratori dell'industria alimentare (Federalimentare)

| | |
|---|---|
| **CNEL code** | `E012` |
| **Sector** | industria |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~145k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🏭 Production |

[← Contracts index](index.md)

??? note "Signatories"
    - Federalimentare
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
| **Limits of this contract** | base_salary, overtime, sickness |

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 75 verified / 0 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 🏭 Production | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | — |
| **Last review** | 2026-10-13 |
| **Latest salary tranche** | 2027-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule read again in the signed CCNL of 1 March 2024 (FLAI-CGIL text, 470 pages; FAI-CISL copy identical in the tables), for the production tier. | corrected | 87 records verified; every aggregator and union press source replaced by the signed text. Pages are physical PDF pages, one above the printed page number.<br>IAR from 1 September 2027: the printed Art. 51 lett. D column (73.73 to 169.57), not a scaling on level 4 (the 11 euro are on parameter 137).<br>EDR paid for 13 months (Art. 52): months_per_year 13.<br>Overtime 45% day, 50% night, 60% holiday (Art. 31, first table), not 30/37/45; the other sub-sector tables are a declared limitation.<br>Absence by the hour (monthly/173, 8 hours a day), not 1/26; ferie 22 working days on the 5-day week, not 20.<br>Sickness: 186 days at 100% of the net normal pay (Art. 47), not 180; the 50% band and the comporto windows are a declared limitation.<br>Apprenticeship: the period boundaries of Art. 21 per level (4 at 6/20, 1 at 10/20, 5 at 6); apprentice_seniority closed with a zero amount (derived).<br>Alifond 1.50%/1% from 1 January 2025 (Art. 74). Contingenza frozen at 1 November 1991, seniority amounts since 1 August 1998.<br>Art. 51 bis, Art. 74 bis, Art. 51 ter and the other contributions declared in one limitation. No renewal or verifica after the CCNL of 1 March 2024 through October 2026. |
| 2026-10-13 | claude-opus-5-5 (ai) | Scope of the declared limitations. | corrected | sickness_half_pay_and_comporto (the comporto of every worker and the half-pay days above five years) is recorded on every run with a sickness event. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1S` | 1S level — senior managers and executives (under L. 190/1985 for workers classified as Quadri) | € 2,836.32 | 2027-01-01 |
| `1` | 1st level — managers with significant managerial and directional responsibilities | € 2,466.34 | 2027-01-01 |
| `2` | 2nd level — intermediate managers and workers with coordination responsibilities | € 2,034.77 | 2027-01-01 |
| `3A` | 3A level — specialist workers with significant operational responsibilities | € 1,788.12 | 2027-01-01 |
| `3` | 3rd level — specialist workers with operational autonomy | € 1,603.17 | 2027-01-01 |
| `4` | 4th level — qualified workers with specific tasks and limited responsibilities | € 1,479.82 | 2027-01-01 |
| `5` | 5th level — qualified workers with simple executive tasks | € 1,356.52 | 2027-01-01 |
| `6` | 6th level — entry-level workers, simple operations | € 1,233.20 | 2027-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1S` | € 51.42 |
| `1` | € 44.71 |
| `2` | € 36.89 |
| `3A` | € 32.42 |
| `3` | € 29.06 |
| `4` | € 26.83 |
| `5` | € 24.59 |
| `6` | € 22.35 |

## Apprenticeship

**professionalizzante_36_10_22** (type: `under_classification`)  
Destination levels: `3`, `3A`, `2`

**professionalizzante_36_6_20** (type: `under_classification`)  
Destination levels: `4`

**professionalizzante_36_10_20** (type: `under_classification`)  
Destination levels: `1`

**professionalizzante_24** (type: `under_classification`)  
Destination levels: `5`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "alimentari-federalimentare/overtime_subsector_tables · overtime · impact yes · open"
    OVERTIME (Art. 31): the engine holds the first table (Carni, Dolciari, Alimenti zootecnici, Lattiero-caseari: 45% day, 50% night, 60% holiday). The other sub-sector tables (vini-liquori, bevande, acque minerali, distillatori, birra, conserve vegetali, alimentari varie, risiera, molitoria e pastificazione, conserve ittiche, avicoli, involucri) set other night and holiday rates, and most of them a higher column for intermedi and impiegati (up to 70% night, 90% holiday). The base of Art. 31 excludes the IAR and the EDR: the caller states OvertimeEvent.hourly_rate.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the Art. 31 table of each sub-sector with its operai and impiegati columns.

!!! warning "alimentari-federalimentare/sickness_half_pay_and_comporto · sickness · impact yes · open"
    SICKNESS (Art. 47): modelled as 100% of the net normal pay for 186 calendar days per episode. Not modelled: over 5 years of seniority the next 179 days at 50%; the comporto of 186 days within 17 months (up to 5 years) and 365 days within 24 months (over 5), summed over different illnesses; the 90 more days for disabled workers; the fixed-term limit (4 months, integration no longer than the INPS indemnity); the apprentice's normal pay for at most six months a year (Art. 21). The net pay is computed by grossing up the INPS indemnity by the worker's INPS rate, as for the Commercio file.

    **Applies when:** `sickness` applies.

    **Remediation:** Model the 50% band over 5 years and the 17 and 24 month comporto windows of Art. 47.

!!! warning "alimentari-federalimentare/alimentari_unmodelled_elements · base_salary · impact yes · open"
    NOT MODELLED AMOUNTS: the trattamento economico per mancata contrattazione di secondo livello of Art. 51 bis (EUR 21.90 at level 6 to 50.37 at 1S a month for 12 months from 1 January 2023, 32.85 to 75.55 from 1 January 2027, outside the TFR), owed by firms without a premio per obiettivi; the EDR of EUR 20 x 12 of Art. 74 bis owed by firms outside the bilateral funds; the premio di campagna of the conserve vegetali (Art. 51 ter); the employer contributions to FASA (EUR 16 a month), the Cassa maternità, the bilateralità and the Cassa rischio vita (Art. 74 ter-quinquies); the premiums of Art. 31 on ordinary night, shift night, holiday and Sunday work; the EDR enters the TFR base only from 1 March 2024 (Art. 73); the pay of first-level and alta formazione apprentices (Art. 21 B-C).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model Art. 51 bis, Art. 74 bis, Art. 51 ter and the Art. 31 premiums on ordinary hours.

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
| — | — | 2024-03-01 | [↗](https://www.flai.it/wp-content/uploads/2018/11/CCNL-Industria-Alimentare-2023-2027.pdf) |

??? note "Coverage notes"
    SALARY MODEL: split, as the CCNL of 1 March 2024 (FLAI-CGIL text). Minimo tabellare (T.E.M.) by level and tranche, Art. 51 lett. A (1/12/2023, 1/9/2024, 1/1/2025, 1/1/2026, 1/1/2027); ex contingenza frozen at 1 November 1991 and EDR EUR 10.33 for 13 months (Art. 52); I.A.R. of Art. 51 lett. D, which bears only on the tredicesima, the quattordicesima and the TFR, as separate allowances.
    
    IAR tranche September 2027: EUR 11 on parameter 137, reparametrised; the per-level amounts are the column 'Nuovo I.A.R. dal 1/09/2027' printed in Art. 51 lett. D (from 73.73 at level 6 to 169.57 at level 1S).
    
    CONTINGENCY ALLOWANCE: the amounts frozen at 1 November 1991 of Art. 52: 1S=545.72, 1=538.70, 2=530.51, 3A=525.83, 3=522.32, 4=519.99, 5=517.65, 6=515.31. The oleario-margariniero categories 1-10 and the viaggiatori o piazzisti tables are outside the 8 modelled levels.
    
    FUNCTION ALLOWANCE 1S: EUR 100 a month for the Quadri (Art. 23, L. 190/1985), modelled as an allowance with role 'quadro' (compute(..., roles={'quadro'})).
    
    APPRENTICESHIP under_classification (Art. 21 A, CCNL 1 March 2024): two levels below in the first period, one below in the second, the destination in the third, with the periods of the Durata table: levels 3, 3A, 2 at 10/12/14 months, level 4 at 6/14/16, level 1 at 10/10/16; level 5 at 24 months, at the destination from the second period (month 6), the first period at level 6 being the reading of 'two levels below' kept. Level 6 and 1S are not destinations. First-level and alta formazione apprenticeships are not modelled.
    
    ADDITIONAL MONTHS: 14, the tredicesima paid at Christmas and the quattordicesima (Art. 54).
    
    SENIORITY: five biennial increments (Art. 53); the per-level amounts of the table 'Importi singolo scatto dal 1/8/1998' are consolidated and not recalculated, in force for the whole ruleset. Apprentices accrue none; on confirmation half the apprenticeship counts (Art. 21).
    

## Raw data

The contract file this page is generated from: [`agreement/alimentari-federalimentare.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/alimentari-federalimentare.json).

## Usage example

```python
--8<-- "docs/examples/agreement/alimentari-federalimentare/example.py"
```
