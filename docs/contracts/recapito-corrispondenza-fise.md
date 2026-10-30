# CCNL Recapito Corrispondenza (FISE-ARE)

| | |
|---|---|
| **CNEL code** | `K711` |
| **Sector** | Recapito corrispondenza e spedizioni |
| **Family** | `servizi-postali` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2023-11-14 |
| **Workers (est.)** | ~1k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - FISE-ARE
    - SLC-CGIL
    - SLP-CISL
    - UILPOSTE-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ✅ |
| **Limits of this contract** | — |

1 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 47 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2023-11-14 |
| **Last review** | — |
| **Latest salary tranche** | 2026-06-01 |

## Review history

No review is recorded.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1` | Livello 1 | € 2,224.51 | 2026-06-01 |
| `2` | Livello 2 | € 2,006.77 | 2026-06-01 |
| `3S` | Livello 3 Super | € 1,791.30 | 2026-06-01 |
| `3` | Livello 3 | € 1,687.29 | 2026-06-01 |
| `4` | Livello 4 | € 1,600.99 | 2026-06-01 |
| `5S` | Livello 5 Super | € 1,489.70 | 2026-06-01 |
| `5` | Livello 5 | € 1,446.71 | 2026-06-01 |
| `6` | Livello 6 | € 1,359.91 | 2026-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 36.15 |
| `2` | € 33.05 |
| `3S` | € 32.54 |
| `3` | € 31.50 |
| `4` | € 30.47 |
| `5S` | € 29.70 |
| `5` | € 29.44 |
| `6` | € 28.41 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days, when the episode does not let the engine compute the INPS daily base: no SicknessEpisode.inps_base in its relapse chain, an operaio without the days worked or paid of the month before, an impiegato who did not work that whole month, an unknown worker category, or a sector INPS regime (spettacolo). With the base, INPS pays its share on the retribuzione media globale giornaliera of the month before the illness and on calendar days (INPS circ. 134368/1981 point 11). The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the base of an impiegato's partial month (point 11.2 letters d-f), of the sector regimes, and from the closing state of the engine's own runs so the caller need not state it, then resolve this limitation.

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
    SIMPLIFICATION: apprenticeship type and percentages not publicly available from any free source (paywalled). Modelled as apprenticeship: [] with no rules defined.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.redigo.info/2023/11/20/ccnl-recapito-corrispondenza-fise-nuove-tabelle-dal-rinnovo-di-novembre-2023/ | tabella_retributiva | 2023-11-14 | [↗](https://www.redigo.info/2023/11/20/ccnl-recapito-corrispondenza-fise-nuove-tabelle-dal-rinnovo-di-novembre-2023/) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=26 | tabella_retributiva | 2023-11-14 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=26) |

??? note "Coverage notes"
    CCNL Recapito Corrispondenza (FISE-ARE) signed 14/11/2023 by FISE-ARE, SLC-CGIL, SLP-CISL, UILPOSTE-UIL.
    
    Salary model: split — base_salary = paga tabellare + contingenza combined (rolled); EDR=10.33 as fixed_allowance. GOAL.md CCNL research confirms this structure from ilccnl.it cross-check.
    
    8 levels (1 highest, 6 lowest): 1, 2, 3S, 3, 4, 5S, 5, 6. 4 tranches: 01/02/2024, 01/09/2024, 01/07/2025, 01/06/2026. Values from redigo.info (14/11/2023 renewal article).
    
    Hourly divisor 173 confirmed from ilccnl.it cross-check (4 levels). Back-calc: 2224.51+10.33=2234.84 / 173 = 12.92 EUR/h for level 1 at Jun 2026.
    
    Additional months: 14 (tredicesima + quattordicesima) confirmed from GOAL.md research.
    
    Seniority: biennale (cadence=24), maximum 8 scatti. Per-level amounts from lavoro-economia.it (c=26), confirmed against kitech at Jun 2026 (L1=36.15, L2=33.05, L3S=32.54, L3=31.50, L4=30.47, L5S=29.70, L5=29.44, L6=28.41).
    
    Levels 1Q (Quadri), Operatore A (1650), Operatore B (1540) exist from Jun 2026 only — no prior tranche history. Not modelled to avoid open-ended periods with single-tranche data.
    

## Raw data

The contract file this page is generated from: [`agreement/recapito-corrispondenza-fise.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/recapito-corrispondenza-fise.json).

## Usage example

```python
--8<-- "docs/examples/agreement/recapito-corrispondenza-fise/example.py"
```
