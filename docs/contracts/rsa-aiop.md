# CCNL RSA e Strutture Residenziali Socio-Assistenziali (AIOP)

| | |
|---|---|
| **CNEL code** | `T091` |
| **Sector** | residenze sanitarie assistenziali — personale non medico |
| **Family** | `socio-sanitario` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2012-03-22 |
| **Workers (est.)** | ~17k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - AIOP
    - FP-CGIL
    - CISL-FP
    - UIL-FPL
    - UGL Sanità
    - FISMIC-CONFSAL
    - FIALS

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

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 32 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2012-03-22 |
| **Last review** | — |
| **Latest salary tranche** | 2023-10-01 |

## Review history

No review is recorded.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `H` | Livello H | € 3,294.68 | 2023-10-01 |
| `G` | Livello G | € 2,749.49 | 2023-10-01 |
| `F` | Livello F | € 2,095.50 | 2023-10-01 |
| `E3` | Livello E3 | € 1,806.00 | 2023-10-01 |
| `E2` | Livello E2 | € 1,746.00 | 2023-10-01 |
| `E1` | Livello E1 | € 1,550.56 | 2023-10-01 |
| `D3` | Livello D3 | € 1,496.06 | 2023-10-01 |
| `D2` | Livello D2 | € 1,463.33 | 2023-10-01 |
| `D1` | Livello D1 | € 1,419.80 | 2023-10-01 |
| `C` | Livello C | € 1,419.80 | 2023-10-01 |
| `B` | Livello B | € 1,311.68 | 2023-10-01 |
| `A` | Livello A | € 1,223.57 | 2023-10-01 |

## Seniority increments

**Cadence:** every 60 months  
**Maximum:** 1 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 40.00 |
| `B` | € 40.00 |
| `C` | € 40.00 |
| `D1` | € 40.00 |
| `D2` | € 40.00 |
| `D3` | € 40.00 |
| `E1` | € 40.00 |
| `E2` | € 40.00 |
| `E3` | € 40.00 |
| `F` | € 0.00 |
| `G` | € 0.00 |
| `H` | € 0.00 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `A`, `B`, `C`, `D1`, `D2`, `D3`, `E1`, `E2`, `E3`, `F`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "rsa-aiop/seniority_premium_2023 · una_tantum · impact yes · open"
    Seniority: CCNL RSA-AIOP provides a flat EUR 40/month after 5 years of service (levels A-E3 only; F/G/H excluded). Modelled as cadence_months=60, maximum_count=1 — correct for new hires (single increment at month 60). Oct 2023 'premio di anzianita' (EUR 40 one-time for 10+ year workers) is a one-time payment, out_of_scope.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model or track the Oct 2023 one-time premio di anzianità (EUR 40 to workers with 10+ years) as an una tantum.

!!! warning "rsa-aiop/apprenticeship_under_classification · base_salary · impact yes · open"
    Apprenticeship: CCNL RSA-AIOP specifies sotto-inquadramento up to 2 levels below destination (levels A-F eligible, 36 months). Modelled as 100% passthrough (overstates pay for apprentices); the engine supports under_classification tracks with levels_below, not yet used here. (review of 2026-10-30)

    **Applies when:** `base_salary` applies.

    **Remediation:** Replace the 100% professionalizzante track with under_classification tracks (levels_below up to 2, 36 months) as servizi-postali-appalto-fise or tessile-smi do.

!!! warning "rsa-aiop/apprentice_seniority · seniority · impact unknown · open"
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

!!! warning "maternity_daily_base · maternity_leave · impact unknown · open"
    The INPS maternity indemnity of an operaia, or of a leave whose month before was not worked in full, is 80% of the pay of the run over 30 with the rateo of the extra months, not of the pay of the month before the leave: art. 23 c. 5 D.Lgs. 151/2001 divides the pay of an operaia by the days worked or paid (or by the hours, when fewer than the contract), and the divisor of her daily rateo of the 13th is not settled by a primary source. The base of another worker over a whole month is computed from MaternityLeaveEvent.base_pay.

    **Applies when:** `maternity_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of an operaia (an INPS circular on art. 23 c. 5) and compute her base and that of a month not worked in full, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| Original CCNL signed 22/03/2012, effective 01/04/2012. Art. 49 salary table, Art. 51 hourly divisor, Art. 54 tredicesima. | altro | 2012-03-22 | [↗](https://acopnazionale.it/wp-content/uploads/2022/03/ccnl-rsa-aiop-2012.pdf) |
| Accordo ponte 03/10/2023, effective 01/10/2023, valid to 30/06/2024. Full salary table confirmed. | altro | 2023-10-03 | [↗](https://www.frgeditore.it/images/cop/pdf/titolo-6/ccnl/rsa/63_accordo_3-10-2023_aiop.pdf) |

??? note "Coverage notes"
    CCNL T091 — AIOP RSA. Conglobated. 12 levels: A-B-C-D1-D2-D3-E1-E2-E3-F-G-H. Divisor 165, 13 months. Original 2012 contract, updated by accordo ponte Oct 2023.
    
    Accordo ponte (Oct 2023) expired June 2024. Contract applied in ultrattività pending renewal. Oct 2023 table modeled as current (valid_until null).
    

## Raw data

The contract file this page is generated from: [`agreement/rsa-aiop.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/rsa-aiop.json).

## Usage example

```python
--8<-- "docs/examples/agreement/rsa-aiop/example.py"
```
