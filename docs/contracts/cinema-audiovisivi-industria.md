# CCNL Industrie Cineaudiovisive (ANICA)

| | |
|---|---|
| **CNEL code** | `G111` |
| **Sector** | Cinema e audiovisivo |
| **Family** | `spettacolo-media` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-07-23 |
| **Workers (est.)** | ~2.3k |
| **Ruleset version** | `2025.1` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANICA
    - SLC-CGIL
    - FISTEL-CISL
    - UILCOM-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | bilateral_funds, inps_employer |

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 62 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-07-23 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2028-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Art. 26 Gratifica natalizia o 13° mensilità (p. 19): "Nel caso di inizio o cessazione del rapporto di lavoro durante il corso dell'anno, il lavoratore ha diritto a tanti dodicesimi della gratifica natalizia per quanti sono i mesi di servizio prestato presso l'azienda. Le frazioni di mese superiori a 15 giorni sono considerate come mese intero di servizio.". Added: more_than 15 (the file applied the engine default, at least 15 days). |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `7S` | Livello 7 Super (QA — Quadro) | € 2,880.55 | 2028-01-01 |
| `7` | Livello 7 (QB — Quadro) | € 2,758.66 | 2028-01-01 |
| `6S` | Livello 6 Super | € 2,510.69 | 2028-01-01 |
| `6` | Livello 6 | € 2,430.46 | 2028-01-01 |
| `5S` | Livello 5 Super | € 2,217.61 | 2028-01-01 |
| `5` | Livello 5 | € 2,164.88 | 2028-01-01 |
| `4S` | Livello 4 Super | € 2,103.30 | 2028-01-01 |
| `4` | Livello 4 | € 1,980.32 | 2028-01-01 |
| `3` | Livello 3 | € 1,796.03 | 2028-01-01 |
| `2` | Livello 2 | € 1,608.31 | 2028-01-01 |
| `1` | Livello 1 | € 1,440.48 | 2028-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 12.65 |
| `2` | € 13.17 |
| `3` | € 13.94 |
| `4` | € 14.46 |
| `4S` | € 14.46 |
| `5` | € 16.01 |
| `5S` | € 16.79 |
| `6` | € 17.56 |
| `6S` | € 17.56 |
| `7` | € 19.37 |
| `7S` | € 20.17 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "cinema-audiovisivi-industria/bilateral_funds_not_modelled · bilateral_funds · impact unknown · open"
    SIMPLIFICATION: No employer bilateral funds modeled. No public data found for a cinema-specific bilateral fund for impiegati/tecnici in production companies.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Confirm whether a sector bilateral fund applies and pass it as a bilateral fund event.

!!! warning "cinema-audiovisivi-industria/fpls_rates_approximated · inps_employer · impact unknown · open"
    SIMPLIFICATION: the employees of film and audiovisual production are insured with the Fondo pensioni lavoratori dello spettacolo (FPLS, ex ENPALS) of INPS, whose contribution regime differs from the ordinary one; the industria rates are used as an approximation pending a dedicated FPLS contribution ruleset. For the workers enrolled after 31 December 1995 the IVS of the FPLS is the ordinary 33% (23.81 + 9.19) up to the annual massimale (INPS, Calcolo dei contributi IVS dei lavoratori dello spettacolo, updated 5 October 2026), as charged here; approximated are the daily bands of the workers enrolled before 1996 (massimale 892 a day in 2026, solidarity 5% above it) and the non-IVS contributions.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Add a dedicated FPLS contribution ruleset for film and audiovisual production employees.

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
    SIMPLIFICATION: Apprenticeship provisions not modeled (primary CCNL text not publicly available). Field left empty.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.lavoro-economia.it/contratti-collettivi/ccnl.aspx?c=153 | altro | 2025-07-23 | [↗](https://www.lavoro-economia.it/contratti-collettivi/ccnl.aspx?c=153) |

??? note "Coverage notes"
    Salary model: conglobated (paga base unica, nessuna contingenza/EDR separata). Source: lavoro-economia.it c=153 (CNEL G111), tabella Jul 2026.
    
    Hourly divisor 173 (industria standard, confirmed from lavoro-economia.it). Daily divisor: 26.
    
    Additional months: 14 (tredicesima + quattordicesima). UILCOM informativa 24/07/2025.
    
    Seniority: 5 scatti biennali (cadence_months=24, maximum_count=5). Amounts from published table Jul 2026.
    
    Salary periods: 5 tranches — Jan 2025 (+45 at L4), Jan 2026 (+45 at L4), Jul 2026 (+90, published anchor), Jul 2027 (+90), Jan 2028 (+90). Source: quotidianopiu.it + lavoro-economia.it.
    
    Non-Jul-2026 salary values computed parametrically: each level scaled by the L4 ratio at each tranche. Published Jul 2026 values are the direct source; others are derived.
    
    SICKNESS INPS REGIME: the employees insured with the Fondo pensioni lavoratori dello spettacolo, operai and impiegati alike, have their own INPS sickness indemnity (INPS circ. 132/2021): from the fourth day, 60% up to the 20th day and 80% from the 21st to the 180th (regime 'spettacolo'), with 40 daily contributions from 1 January of the year before (SicknessEpisode.daily_contributions).
    

## Raw data

The contract file this page is generated from: [`agreement/cinema-audiovisivi-industria.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/cinema-audiovisivi-industria.json).

## Usage example

```python
--8<-- "docs/examples/agreement/cinema-audiovisivi-industria/example.py"
```
