# CCNL Istituzioni Socio-Assistenziali — UNEBA

| | |
|---|---|
| **CNEL code** | `T141` |
| **Sector** | servizi socio-assistenziali |
| **Family** | `socio-sanitario` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-01-24 |
| **Workers (est.)** | ~130k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - UNEBA
    - FP-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, seniority, territorial_supplement |

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 41 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-01-24 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2026-03-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 44 - Tredicesima mensilità (p. 44): "Nel caso di inizio o di cessazione del rapporto di lavoro durante il corso dell’anno la lavoratrice ed il lavoratore avranno diritto a tanti dodicesimi dell’ammontare della 13° mensilità per quanti sono i mesi di servizio prestato. Le frazioni di mese pari o superiori ai 15 giorni saranno considerate come mese intero.". Match: at_least 15. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Senior Manager (Quadro) — executive / top-level manager (with function allowance) | € 2,057.15 | 2026-03-01 |
| `1` | Level 1 — director / facility manager | € 1,934.70 | 2026-03-01 |
| `2` | Level 2 — service manager / coordinator | € 1,824.49 | 2026-03-01 |
| `3S` | Level 3 Super — professional educator / qualified technician | € 1,689.78 | 2026-03-01 |
| `3` | Level 3 — specialist technical worker / educator | € 1,628.56 | 2026-03-01 |
| `4S` | Level 4 Super — social health care worker (OSS) | € 1,542.86 | 2026-03-01 |
| `4` | Level 4 — social care worker | € 1,493.89 | 2026-03-01 |
| `5S` | Level 5 Super — qualified care worker | € 1,469.42 | 2026-03-01 |
| `5` | Level 5 — basic care worker | € 1,432.66 | 2026-03-01 |
| `6S` | Level 6 Super — qualified auxiliary worker | € 1,395.94 | 2026-03-01 |
| `6` | Level 6 — generic auxiliary worker | € 1,359.20 | 2026-03-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 34.09 |
| `1` | € 32.54 |
| `2` | € 30.99 |
| `3S` | € 29.95 |
| `3` | € 28.92 |
| `4S` | € 28.41 |
| `4` | € 27.89 |
| `5S` | € 27.37 |
| `5` | € 26.86 |
| `6S` | € 26.34 |
| `6` | € 25.82 |

## Apprenticeship

**oss_4S** (type: `percentage`)  
Destination levels: `4S`  
percentage: 1.00

**standard_36** (type: `percentage`)  
Destination levels: `3`, `3S`, `2`  
percentage: 1.00

**standard_24** (type: `percentage`)  
Destination levels: `4`, `4S`  
percentage: 1.00

**standard_18** (type: `percentage`)  
Destination levels: `6`, `5`, `5S`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "uneba-uneba/equal_apprenticeship_bands · base_salary · impact unknown · open"
    APPRENTICESHIP generic rule (Art. 22): 90/95/100% in three bands over the destination-level duration: 36 months for 2, 3S, 3 (track 'standard_36'), 24 months for 4S and 4 (track 'standard_24'), 18 months for 5S, 5, 6 (track 'standard_18'). The three bands are assumed of equal length. 6S is not listed in Art. 22 and is not a destination; professionals excluded from apprenticeship (nurses, physiotherapists, psychologists, social workers) and levels 1/Q are not modelled.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Confirm the length of the three Art. 22 apprenticeship bands.

!!! warning "uneba-uneba/ermt_territorial · territorial_supplement · impact yes · open"
    ERMT: Elemento Retributivo Mensile Territoriale is a territorial supplement, not part of the national CCNL salary table. Not modelled at national level.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the ERMT outside the engine and record the limitation (as ert_veneto / provincial_third_elements).

!!! warning "uneba-uneba/apprentice_seniority · seniority · impact unknown · open"
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
| https://www.uneba.org/wp-content/uploads/2025/01/contratto-uneba-2025-testo-firmato.pdf | altro | 2025-01-24 | [↗](https://www.uneba.org/wp-content/uploads/2025/01/contratto-uneba-2025-testo-firmato.pdf) |
| https://olympus.uniurb.it/index.php?Itemid=139&catid=242&id=21943%3A2020uneba&option=com_content&view=article | altro | 2020-01-20 | [↗](https://olympus.uniurb.it/index.php?Itemid=139&catid=242&id=21943%3A2020uneba&option=com_content&view=article) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (minimi retributivi mensili conglobati per Art. 43 CCNL Jan 2025). All base_salary values are the conglobated tabular minimums; contingenza and EDR are fully absorbed. Back-calculation: Oct 2024 level 4S = 1467.86 / 164 = 8.95 EUR/h; level 2 = 1735.81 / 164 = 10.58 EUR/h; level Q = 1957.15 / 164 = 11.93 EUR/h — consistent across all levels, confirming divisor 164 and conglobated model.
    
    TRANCHE DATES: three tranches — Oct 2024, Jul 2025, Mar 2026. Renewal signed 24 Jan 2025 (CCNL 2023-2025). Level 7 abolished from 01.02.2025 per Art. 80 of the renewal; not modelled.
    
    HOURLY DIVISOR: 164, derived from Art. 50 (38-hour week). Formula: 38 h/week × 52/12 = 164.67, rounded to 164 per contract usage.
    
    ADDITIONAL MONTHS: 14 (tredicesima + quattordicesima). Quattordicesima confirmed by Art. 46 CCNL 2025 (erogata in luglio). Applies to all levels.
    
    SENIORITY: triennial (every 36 months), maximum 10 scatti. Per-level amounts from Art. 48 table (CCNL 2025 signed PDF). Valid from first tranche date Oct 2024.
    
    LEVEL Q — IND_FUN: fixed allowance EUR 100.00/month (Art. 43, 'indennità di funzioni pari a EUR 100,00 mensili lorde'). Paid over 14 mensilità, non-absorbable. Applied to all Q-level workers.
    
    APPRENTICESHIP OSS/4S rule (Art. 22 CCNL 2020, unchanged by the 2025 renewal; primary source olympus.uniurb.it): destination 4S (OSS), 18 months, 85% months 1-9 and 90% months 10-18, track 'oss_4S'. Select it with Apprentice(track='oss_4S'): level 4S is also covered by the generic 24-month track.
    
    TEP ABOLISHED: Art. 80 of the 2025 renewal abolishes the Trattamento Economico Progressivo (progressive 36-month phased salary for new hires). Not modelled as it is no longer in force from 01.02.2025.
    
    INPS: reuses 2026-terziario.json (TERZIARIO sector). No separate INPS circular rate published for UNEBA; rate is consistent with general terziario sector (same as Commercio and Cooperative Sociali).
    

## Raw data

The contract file this page is generated from: [`agreement/uneba-uneba.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/uneba-uneba.json).

## Usage example

```python
--8<-- "docs/examples/agreement/uneba-uneba/example.py"
```
