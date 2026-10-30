# CCNL Ceramica Industria (Confindustria-Assopiastrelle)

| | |
|---|---|
| **CNEL code** | `B122` |
| **Sector** | ceramica |
| **Family** | `chimica` |
| **Tax sector** | `industria` |
| **Last renewal** | 2024-07-22 |
| **Workers (est.)** | ~23k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Confindustria Ceramica
    - FILCTEM-CGIL
    - FEMCA-CISL
    - UILTEC-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, seniority |

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 60 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-07-22 |
| **Last review** | — |
| **Latest salary tranche** | 2027-06-01 |

## Review history

No review is recorded.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A` | Level A — quadri and workers with maximum autonomy and managerial responsibility | € 2,793.96 | 2027-06-01 |
| `B1` | Level B1 — workers with high professional skill or specialisation and full IPO | € 2,515.17 | 2027-06-01 |
| `B2` | Level B2 — workers with high professional skill or specialisation, without IPO | € 2,515.17 | 2027-06-01 |
| `C1` | Level C1 — workers with basic technical or managerial responsibility and full IPO | € 2,194.75 | 2027-06-01 |
| `C2` | Level C2 — workers with basic technical or managerial responsibility and reduced IPO | € 2,194.75 | 2027-06-01 |
| `C3` | Level C3 — workers with basic technical or managerial responsibility, without IPO | € 2,194.75 | 2027-06-01 |
| `D1` | Level D1 — workers with medium-complexity operative functions and full IPO | € 1,972.36 | 2027-06-01 |
| `D2` | Level D2 — workers with medium-complexity operative functions and reduced IPO | € 1,972.36 | 2027-06-01 |
| `D3` | Level D3 — workers with medium-complexity operative functions, without IPO | € 1,972.36 | 2027-06-01 |
| `E1` | Level E1 — workers with executive duties and position IPO allowance (CCNL IPO art.) | € 1,783.43 | 2027-06-01 |
| `E2` | Level E2 — workers with executive duties, standardised operative tasks | € 1,783.43 | 2027-06-01 |
| `F` | Level F — entry-level workers performing basic operations | € 1,666.45 | 2027-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 19.63 |
| `B1` | € 17.56 |
| `B2` | € 17.56 |
| `C1` | € 12.91 |
| `C2` | € 12.91 |
| `C3` | € 12.91 |
| `D1` | € 12.14 |
| `D2` | € 12.14 |
| `D3` | € 12.14 |
| `E1` | € 8.78 |
| `E2` | € 8.78 |
| `F` | € 7.75 |

## Apprenticeship

**qualificazione_professionale** (type: `percentage`)  
Destination levels: `A`, `B1`, `B2`, `C1`, `C2`, `C3`, `D1`, `D2`, `D3`, `E1`, `E2`, `F`  
percentage: 0.95

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! note "ceramica-industria-confindustria/apprentice_seniority_amount · seniority · impact unknown · resolved"
    APPRENTICE INCREMENT: apprentice_amount=null. No confirmation from any accessible primary source for B122 industria. The EUR 6 value is confirmed only for CCNL Ceramica Artigianato (V751), not B122. Italian CCNLs frequently exclude apprentices from seniority accrual during the training period (D.Lgs 81/2015 Art. 47), so null may be the correct answer rather than a gap. Verification requires full CCNL text (Arts. 80-82 of the July 2024 rinnovo), which is not publicly machine-readable.

    **Applies when:** `seniority` applies; contract type in apprentice.

    **Remediation:** Resolved as a duplicate of ceramica-industria-confindustria/apprentice_seniority, which stays open (review of 2026-10-30): both track the missing parameters.seniority_increments.apprentice_amount, which makes seniority_first_cadence pay apprentices no increment.

!!! warning "ceramica-industria-confindustria/sanitary_ceramics_tables · base_salary · impact yes · open"
    SUB-SECTORS: CCNL B122 covers Tiles (porcelain and stoneware), Refractory Materials, Sanitary Ceramics and Tableware, and Artistic and Traditional Ceramics. This file models the PIASTRELLE sub-sector (and REFRATTARI, which has identical tables). Sanitary Ceramics has a different pay structure (significantly higher IPO) and is not modelled here.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the Sanitari e stoviglie tables (higher IPO) as a separate ruleset or a sub-sector fact, or open a limitation like chimica-farmaceutica other_sector_tables.

!!! warning "ceramica-industria-confindustria/apprentice_seniority · seniority · impact unknown · open"
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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.filctemcgil.it/images/download/CONTRATTI/ceramica_piastrelle/240722_CERAMICHE_RINNOVO_1LUGLIO2023_30GIUGNO2027_TABELLE.pdf | tabella_retributiva | 2024-07-22 | [↗](https://www.filctemcgil.it/images/download/CONTRATTI/ceramica_piastrelle/240722_CERAMICHE_RINNOVO_1LUGLIO2023_30GIUGNO2027_TABELLE.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobated tabular minimum (single base pay absorbing contingency and EDR) + IPO (Organisational Position Allowance) as a separate fixed_allowance for the levels that receive it. Source: official FILCTEM-CGIL tables (PDF signed 22/07/2024, PIASTRELLE sub-sector). REFRACTORY MATERIALS has tables identical to PIASTRELLE.
    
    HOURLY_DIVISOR: 173 hours/month (40h weeks × 52/12 = 173.33 rounded). Verified on lavoro-economia.it for CCNL B122.
    
    SENIORITY: 5 biennial increments (cadence 24 months, maximum 5). Amounts from kitech.it (B122, primary levels). Amounts for B2, C2, C3, D2, D3, E2 confirmed equal to B1, C1, D1, E1 respectively: kitech.it (B122, 2026-07-01) shows B1=B2=17.56, C1=C2=C3=12.91, D1=D2=D3=12.14, E1=E2=8.78 EUR. All sub-levels within a grade share the same scatto amount per CCNL B122 category rule (same tabular minimum, standard practice for CCNL ceramica); not confirmed from a primary source.
    
    APPRENTICESHIP: 95% of destination level (base + IPO) for full contract duration. Confirmed by ISFOL official monitoring report (old.isfol.it, citing the ceramica apprendistato agreement of 17/07/2012): 'La retribuzione dell’apprendista per tutta la durata del contratto formativo di qualificazione è fissata nella misura del 95% del livello salariale (minimo di categoria più indennità di posizione)'. The 22/07/2024 renewal modifies Arts. 75 and 80-82 but independent sources confirm no change to apprenticeship structure. Maximum legal duration per D.Lgs 81/2015 Art. 44.
    

## Raw data

The contract file this page is generated from: [`agreement/ceramica-industria-confindustria.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/ceramica-industria-confindustria.json).

## Usage example

```python
--8<-- "docs/examples/agreement/ceramica-industria-confindustria/example.py"
```
