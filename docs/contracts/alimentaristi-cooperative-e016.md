# CCNL Alimentaristi Cooperative (Fedagripesca/Legacoop Agroalimentare/AGCI-Agrital)

| | |
|---|---|
| **CNEL code** | `E016` |
| **Sector** | industria alimentare — cooperative di produzione e lavoro |
| **Tax sector** | `industria` |
| **Last renewal** | 2024-05-14 |
| **Workers (est.)** | ~15k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Fedagripesca-Confcooperative
    - Legacoop Agroalimentare
    - AGCI-Agrital
    - FLAI-CGIL
    - FAI-CISL
    - UILA-UIL

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
| **Last renewal** | 2024-05-14 |
| **Last verified** | — |
| **Latest salary tranche** | 2027-01-01 |

### Semplificazioni note

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1A` | Livello 1A | € 2,836.32 | 2027-01-01 |
| `1` | Livello 1 | € 2,466.34 | 2027-01-01 |
| `2` | Livello 2 | € 2,034.77 | 2027-01-01 |
| `3A` | Livello 3A | € 1,788.12 | 2027-01-01 |
| `3` | Livello 3 | € 1,603.17 | 2027-01-01 |
| `4` | Livello 4 | € 1,479.82 | 2027-01-01 |
| `5` | Livello 5 | € 1,356.52 | 2027-01-01 |
| `6` | Livello 6 | € 1,233.20 | 2027-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `6` | € 22.35 |
| `5` | € 24.59 |
| `4` | € 26.83 |
| `3` | € 29.06 |
| `3A` | € 32.42 |
| `2` | € 36.89 |
| `1` | € 44.71 |
| `1A` | € 51.42 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `6`, `5`, `4`, `3`, `3A`, `2`, `1`, `1A`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "alimentaristi-cooperative-e016/apprenticeship_full_pay_passthrough · base_salary · impact yes · open"
    Apprenticeship rules involve per-level classification reduction not fully resolvable from available sources. Modeled as 100% passthrough for all levels.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Source the per-level apprenticeship under-classification and model it as a track.

!!! warning "alimentaristi-cooperative-e016/apprentice_seniority · seniority · impact unknown · open"
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

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days. INPS computes it on its own daily base (retribuzione media globale giornaliera of the month before) and on calendar days. The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the INPS indemnity on the INPS daily base and calendar days of the INPS rules, with the pay of the month before, then resolve this limitation.

!!! warning "sickness_cumulation_window · sickness · impact unknown · open"
    The CCNL tier and the comporto are counted on the days of one episode and the relapses it continues. A CCNL that sums the sickness of separate episodes over a window (a calendar year, the last three years) can reach a lower tier or the end of the comporto earlier than the engine shows. The run is affected when an earlier episode outside the relapse chain is recorded.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Add the cumulation window of each CCNL to its sickness rule, with the source, and count the tier and the comporto over it.

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax or INPS ruleset marked provisional: the sources of its year are not published yet (INPS circular on the massimale, minimale and rates of the year; regional and municipal surtax resolutions; budget law of the year), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; the indexed amounts (INPS massimale and minimale) do not, and any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

### Without monetary impact

!!! note ""
    Quadri (livello 1A Q) and V.P. variants not modeled. Only the 8 standard levels are implemented.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-05-14 | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=E016) |

??? note "Coverage notes"
    CCNL E016 renewed 14/05/2024, valid 01/12/2023-30/11/2027. Signatories: Fedagripesca-Confcooperative, Legacoop Agroalimentare, AGCI-Agrital + FLAI-CGIL/FAI-CISL/UILA-UIL.
    
    SPLIT model: paga base (time-series, 5 tranches) + CONTINGENZA (frozen, 14 months) + EDR (EUR 10.33, all levels, 13 months) + IAR (Indennita Aggiuntiva dei Redditi, per-level, 14 months, 2 periods).
    
    8 core levels: 6 (lowest, order 1) to 1A (highest, order 8). Divisor 173, 14 months. Seniority: 24-month cadence, max 5 scatti biennali.
    
    IAR first period from 01/12/2023: 1A=151.11, 1=131.39, 2=108.40, 3A=95.26, 3=85.41, 4=78.84, 5=72.27, 6=65.70. Second period from 01/09/2027.
    
    INPS: uses 2026-industria.json (TaxSector.INDUSTRIA). Alimentaristi cooperative are classified as industria for INPS purposes.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/alimentaristi-cooperative-e016.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/alimentaristi-cooperative-e016.py"
```
