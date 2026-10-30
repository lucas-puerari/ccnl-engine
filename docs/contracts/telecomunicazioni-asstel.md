# CCNL Telecomunicazioni — Assotelecomunicazioni (Asstel)

| | |
|---|---|
| **CNEL code** | `K411` |
| **Sector** | telecomunicazioni |
| **Family** | `ict-telecomunicazioni` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-11-11 |
| **Workers (est.)** | ~110k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Assotelecomunicazioni-Asstel
    - SLC-CGIL
    - Fistel-CISL
    - Uilcom-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | inps_employer, seniority |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 45 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-11-11 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2028-12-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 42 - 13ª mensilità (p. 83): "Nel caso di inizio o di cessazione del rapporto di lavoro durante il corso dell'anno, il lavoratore non in prova ha diritto a tanti dodicesimi dell'ammontare della tredicesima mensilità quanti sono i mesi di anzianità di servizio presso l’azienda. La frazione di mese superiore a quindici giorni va considerata a questi effetti come mese intero.". Match: more_than 15. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `D1` | D1 — Quadri, maximum managerial and professional responsibility | € 2,814.86 | 2028-12-01 |
| `C4` | C4 — Grade 7, managerial functions of high organisational complexity | € 2,814.86 | 2028-12-01 |
| `C3` | C3 — Grade 6, high and consolidated professional and managerial expertise | € 2,559.28 | 2028-12-01 |
| `C2` | C2 — Grade 5S, specialist profiles with a high degree of specialisation | € 2,263.82 | 2028-12-01 |
| `C1` | C1 — Grade 5, advanced professional and managerial capabilities with high-level knowledge | € 2,186.73 | 2028-12-01 |
| `B2` | B2 — Grade 4, qualified specialist knowledge | € 2,020.45 | 2028-12-01 |
| `B1` | B1 — Grade 3, theoretical and practical knowledge of medium complexity | € 1,862.81 | 2028-12-01 |
| `A2` | A2 — Grade 2, basic professional knowledge | € 1,701.25 | 2028-12-01 |
| `A1` | A1 — Grade 1, predominantly manual tasks requiring no professional knowledge | € 1,518.96 | 2028-12-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 7 increments

| Level | Increment (monthly) |
|---|---:|
| `A1` | € 21.54 |
| `A2` | € 21.54 |
| `B1` | € 23.24 |
| `B2` | € 24.38 |
| `C1` | € 25.56 |
| `C2` | € 25.56 |
| `C3` | € 28.10 |
| `C4` | € 30.73 |
| `D1` | € 30.73 |

## Apprenticeship

**professionalizzante** (type: `under_classification`)  
Destination levels: `B1`, `B2`, `C1`, `C2`, `C3`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "telecomunicazioni-asstel/seniority_adjacent_level_amounts · seniority · impact unknown · open"
    SENIORITY biennale (24 months), max 7 scatti, amounts from Art. 41 CCNL 12/11/2020: 6 of 9 levels confirmed (A2, B1, B2, C1, C3, C4); A1=A2 (21.54), C2=C1 (25.56) and D1=C4 (30.73) by adjacent-level approximation (1° livello, 5°S and Quadri absent from the Art. 41 table).

    **Applies when:** `seniority` applies; level in A1, C2, D1.

    **Remediation:** Source the Art. 41 amounts of 1° livello, 5°S and Quadri and replace the adjacent-level values.

!!! warning "telecomunicazioni-asstel/industria_tax_sector_unverified · inps_employer · impact unknown · open"
    INPS: reuses the industria contribution table. SIMPLIFICATION: tax_sector='industria' is a modelling choice. Supporting facts: (a) Asstel is a Confindustria federation; (b) large TLC operators (Telecom Italia, etc.) have historically accessed CIGO/CIGS; (c) the CCNL itself (Art. 58 rinnovo 11/11/2025) describes the Fondo di Solidarietà Bilaterale TLC as 'in aggiunta' (supplementary), not as a CIG substitute. Counterargument: D.Lgs. 148/2015 Art. 26 bilateral funds are formally for sectors without CIG coverage; this was not verified against an INPS circular. The employer rate of the terziario table is about 1.2 points lower than the industria one in each headcount band of the bundle. The Fondo di Solidarietà Bilaterale (0.20% datore + 0.10% lavoratore) is NOT modelled in either case (review of 2026-10-30).

    **Applies when:** `inps_employer` applies.

    **Remediation:** Verify the INPS classification of TLC employers and model the Fondo di Solidarieta Bilaterale TLC.

!!! warning "telecomunicazioni-asstel/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

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

### Without monetary impact

!!! note ""
    APPRENTICESHIP professionalizzante, under_classification (Art. 20 CCNL 12/11/2020): 36 months, first 18 months two levels below the destination, next 18 months one level below, then the destination. Track covers destinations B1, B2, C1, C2, C3; A1/A2 (no level two steps below), C4 and D1 (funzioni direttive/Quadri) are not destinations.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.asstel.it/lavoro-e-relazioni-industriali/ccnl-tlc/ | altro | 2025-11-11 | [↗](https://www.asstel.it/lavoro-e-relazioni-industriali/ccnl-tlc/) |
| https://www.asstel.it/wp-content/uploads/2023/05/CCNL-TLC-Slc-Cgil-Fistel-Cisl-Uilcom-Uil-12-novembre-2020-nuovo.pdf | altro | 2020-11-12 | [↗](https://www.asstel.it/wp-content/uploads/2023/05/CCNL-TLC-Slc-Cgil-Fistel-Cisl-Uilcom-Uil-12-novembre-2020-nuovo.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (TEM = minimo tabellare + ex-contingenza + EDR + Elemento Retributivo di Settore), confirmed by footnote in rinnovo PDF (11/11/2025), tabelle retributive p.99-100. Back-calculation: C1(01/01/2026)=1988.73/173=11.50 EUR/h; A1=1399.68/173=8.09 EUR/h; C3=2317.44/173=13.39 EUR/h — all consistent with divisor 173. base_salary = TEM; fixed_allowances=[] for levels A1-C3.
    
    FIXED ALLOWANCES: C4 (7° livello) carries Elemento Retributivo di Settore EUR 59.39/month separate from TEM (rinnovo PDF p.97). D1 (Quadri) carries Indennità di Funzione EUR 98.13/month inclusive of the 59.39 ERS (rinnovo PDF + CCNL 12/11/2020 sezione Quadri). Both use TEM parametro=228, identical base_salary. The validator checks base_salary only so the equal values are valid.
    
    SALARY TRANCHES: four tranches from rinnovo 11/11/2025 — 01/01/2026, 01/12/2026, 01/07/2027, 01/12/2028. Pre-rinnovo salary tables (CCNL 12/11/2020) not modelled; engine scope starts from first 2026 tranche.
    
    NEW CLASSIFICATION SYSTEM: rinnovo 11/11/2025 Art. 23 introduces Professional Areas A-D (effective 01/07/2026). Old→new mapping: 1°→A1, 2°→A2, 3°→B1, 4°→B2, 5°→C1, 5°S→C2, 6°→C3, 7°→C4, Q→D1. TEM values are identical regardless of which code system is in use; engine uses new codes throughout.
    
    HOURLY DIVISOR: 173 (Art. 40, CCNL 12/11/2020: 'dividendo per 173'; 40h/week standard).
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: Art. 42, CCNL 12/11/2020. Quattordicesima not provided by this CCNL.
    

## Raw data

The contract file this page is generated from: [`agreement/telecomunicazioni-asstel.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/telecomunicazioni-asstel.json).

## Usage example

```python
--8<-- "docs/examples/agreement/telecomunicazioni-asstel/example.py"
```
