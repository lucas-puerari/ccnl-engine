# CCNL Istituzioni Socio-Assistenziali — UNEBA

| | |
|---|---|
| **CNEL code** | `T141` |
| **Sector** | servizi socio-assistenziali |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~130k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - UNEBA
    - FP-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL

## Coverage

### Funzionalità

Derived from the capability registry, as in the [capability matrix](capability-matrix.md).

| | Functional coverage of a layer: its weakest capability |
|---|---|
| ✅ | Every capability native: computed from bundled rules and request facts |
| 📝 | At best caller-supplied: a capability takes a caller rate or amount |
| ⚠️ | A capability is partial: some variants only, or data the file lacks |
| 🔲 | A capability is unsupported: the engine does not compute it |

| Layer | Status |
|---|---|
| **L1 — Gross** | 🔲 |
| **L2 — Net** | 🔲 |
| **L3 — Work rules** | 🔲 |
| **Limits of this contract** | base_salary, seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | — |
| **Last verified** | — |
| **Latest salary tranche** | 2026-03-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

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

!!! warning "uneba-uneba/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

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
| — | — | 2025-01-24 | [↗](https://www.uneba.org/wp-content/uploads/2025/01/contratto-uneba-2025-testo-firmato.pdf) |
| — | — | 2020-01-20 | [↗](https://olympus.uniurb.it/index.php?Itemid=139&catid=242&id=21943%3A2020uneba&option=com_content&view=article) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (minimi retributivi mensili conglobati per Art. 43 CCNL Jan 2025). All base_salary values are the conglobated tabular minimums; contingenza and EDR are fully absorbed. Back-calculation: Oct 2024 level 4S = 1467.86 / 164 = 8.95 EUR/h; level 2 = 1735.81 / 164 = 10.58 EUR/h; level Q = 1957.15 / 164 = 11.93 EUR/h — consistent across all levels, confirming divisor 164 and conglobated model.
    
    TRANCHE DATES: three tranches — Oct 2024, Jul 2025, Mar 2026. Renewal signed 24 Jan 2025 (CCNL 2023-2025). Level 7 abolished from 01.02.2025 per Art. 80 of the renewal; not modelled.
    
    HOURLY DIVISOR: 164, derived from Art. 50 (38-hour week). Formula: 38 h/week × 52/12 = 164.67, rounded to 164 per contract usage.
    
    ADDITIONAL MONTHS: 14 (tredicesima + quattordicesima). Quattordicesima confirmed by Art. 46 CCNL 2025 (erogata in luglio). Applies to all levels.
    
    SENIORITY: triennial (every 36 months), maximum 10 scatti. Per-level amounts from Art. 48 table (CCNL 2025 signed PDF). Valid from first tranche date Oct 2024.
    
    LEVEL Q — IND_FUN: fixed allowance EUR 100.00/month (Art. 43, 'indennità di funzioni pari a EUR 100,00 mensili lorde'). Paid over 14 mensilità, non-absorbable. Applied to all Q-level workers.
    
    APPRENTICESHIP OSS/4S rule (Art. 22 CCNL 2020, unchanged by the 2025 renewal; primary source olympus.uniurb.it): destination 4S (OSS), 18 months, 85% months 1-9 and 90% months 10-18, track 'oss_4S'. Select it with Apprentice(track='oss_4S'): level 4S is also covered by the generic 24-month track.
    
    TEP ABOLISHED: Art. 80 of the 2025 renewal abolishes the Trattamento Economico Progressivo (progressive 36-month phased salary for new hires). Not modelled as it is no longer in force from 01.02.2025.
    
    ERMT: Elemento Retributivo Mensile Territoriale is a territorial supplement, not part of the national CCNL salary table. Not modelled at national level.
    
    INPS: reuses 2026-terziario.json (TERZIARIO sector). No separate INPS circular rate published for UNEBA; rate is consistent with general terziario sector (same as Commercio and Cooperative Sociali).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/uneba-uneba.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/uneba-uneba.py"
```
