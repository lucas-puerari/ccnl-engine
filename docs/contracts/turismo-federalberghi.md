# CCNL Turismo — Federalberghi/Faita

| | |
|---|---|
| **CNEL code** | `H052` |
| **Sector** | Turismo |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-07-05 |
| **Workers (est.)** | ~220k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federalberghi
    - Faita (L'Ospitalità Italiana)
    - Filcams-CGIL
    - Fisascat-CISL
    - UILTuCS

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
| **Limits of this contract** | seniority, worker_category |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2024-07-05 |
| **Last verified** | — |
| **Latest salary tranche** | 2027-11-01 |

### Semplificazioni note

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

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

!!! warning "turismo-federalberghi/indicative_level_category · worker_category · impact unknown · open"
    The level category (quadro/impiegato/operaio) is indicative. The CCNL 2010 uses numeric levels 1-6 plus A, B, 6s, 7 with no formal contractual category distinction.

    **Applies when:** `worker_category` applies.

    **Remediation:** Confirm the category of each level, or require the category in the request.

!!! warning "turismo-federalberghi/apprentice_seniority · seniority · impact unknown · open"
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

### Without monetary impact

!!! note ""
    Layer 3 (overtime, night work, public holidays) out of scope.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2010-01-01 | [↗](http://www.uiltucs.it/pdf/turismo/CCNL_Turismo_Confcommercio_2010.pdf) |
| — | — | 2014-01-18 | [↗](https://uiltucs.it/wp-content/uploads/2019/01/CCNL-Federalberghi-18.01.2014.pdf) |
| — | — | 2024-07-05 | [↗](https://uiltucs.it/wp-content/uploads/2024/07/ccnl_turismo_ipotesi_accordo_5-luglio-2024_agg_11_7_24.pdf) |

??? note "Coverage notes"
    CNEL code H052 is shared with CCNL Agenzie di Viaggio Fiavet — the engine allows duplicates.
    
    Apprenticeship durations Art. 54 CCNL 2010 (visual confirm page 89): grades 2/3/4=48m, 5/6s=36m, 6=24m. Levels A/B/1/7 are not apprenticeship destinations.
    
    Apprenticeship percentages Art. 58 CCNL 2010 (pdftotext pages 90-97): 1st year=80%, 2nd year=85%, 3rd year=90%, from 4th year=95%. Uniform for all destination levels.
    
    Hourly divisor 172 from Art. 151 CCNL 2010 (standard working hours 40h/week). Verification: 1550.69/9.01=172.1 (Jul-2024: 1620.69/9.42=172.0).
    
    14 monthly payments from Art. 160 (thirteenth) and Art. 161 (fourteenth) of the 2024 renewal.
    
    Seniority increments Art. 158 CCNL 2010: six triennial increments (cadence_months=36, maximum_count=6). Per-level amounts visually verified from PDF image pages 140-141: A=40.80, B=39.25, 1=37.70, 2=36.15, 3=34.86, 4=33.05, 5=32.54, 6s=31.25, 6=30.99, 7=30.47.
    
    Base salary table effective 01.04.2016 from the 2014 renewal (UILTuCS PDF): A=2210.16, B=2046.20, 1=1906.44, 2=1742.47, 3=1643.37, 4=1550.69, 5=1454.28, 6s=1398.37, 6=1378.55, 7=1291.81.
    
    5 salary tranches 2024-2027 from the 5 July 2024 renewal (UILTuCS PDF): Jul-2024, Jun-2025, May-2026, Apr-2027, Nov-2027.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/turismo-federalberghi.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/turismo-federalberghi.py"
```
