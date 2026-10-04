# CCNL per i lavoratori delle Banche di Credito Cooperativo, Casse Rurali ed Artigiane

| | |
|---|---|
| **CNEL code** | `J271` |
| **Sector** | credito |
| **Tax sector** | `credito` |
| **Last renewal** | — |
| **Workers (est.)** | ~33k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federcasse
    - FABI
    - FIRST-CISL
    - FISAC-CGIL
    - UGL Credito
    - UILCA

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
| **Latest salary tranche** | 2026-01-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QD4` | Executive Managers - 4th pay level | € 5,160.06 | 2026-01-01 |
| `QD3` | Executive Managers - 3rd pay level | € 4,396.88 | 2026-01-01 |
| `QD2` | Executive Managers - 2nd pay level | € 3,965.48 | 2026-01-01 |
| `QD1` | Executive Managers - 1st pay level | € 3,743.21 | 2026-01-01 |
| `3AP4` | 3rd Professional Area - 4th pay level | € 3,341.90 | 2026-01-01 |
| `3AP3` | 3rd Professional Area - 3rd pay level | € 3,059.49 | 2026-01-01 |
| `3AP2` | 3rd Professional Area - 2nd pay level | € 2,890.41 | 2026-01-01 |
| `3AP1` | 3rd Professional Area - 1st pay level | € 2,742.35 | 2026-01-01 |
| `2AP2` | 2nd Professional Area - 2nd pay level | € 2,572.10 | 2026-01-01 |
| `2AP1` | 2nd Professional Area - 1st pay level | € 2,406.80 | 2026-01-01 |
| `1AP` | 1st Professional Area - single level | € 2,241.53 | 2026-01-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `QD4` | € 95.31 |
| `QD3` | € 95.31 |
| `QD2` | € 41.55 |
| `QD1` | € 41.55 |
| `3AP4` | € 41.55 |
| `3AP3` | € 41.55 |
| `3AP2` | € 41.55 |
| `3AP1` | € 41.55 |
| `2AP2` | € 35.57 |
| `2AP1` | € 29.07 |
| `1AP` | € 20.12 |

## Apprenticeship

**terza_area** (type: `under_classification`)  
Destination levels: `3AP1`, `3AP2`, `3AP3`, `3AP4`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "bcc-credito-cooperativo/art3_derogation_apprenticeship · base_salary · impact unknown · open"
    Apprenticeship (Art. 30) modelled for destination levels 3AP1-3AP4: months 0-18 one level below the destination, then the destination level. The Art. 3 comma 3 derogation (higher destination level) is assumed to follow the same 18-month rule.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Confirm that the Art. 3 comma 3 derogation follows the 18-month rule.

!!! warning "bcc-credito-cooperativo/apprentice_seniority · seniority · impact unknown · open"
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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-07-09 | [↗](https://www.fabi.it/wp-content/uploads/2025/01/CCNL-BCC-testo-coordinato-19-dicembre-2024.pdf) |
| — | — | 2024-07-09 | [↗](https://www.kitech.it/tabelle-retributive/banche-credito-cooperativo/) |

??? note "Coverage notes"
    Salary model is conglobated (stipendio per Art. 112 replaces paga base + scala mobile + EDR + other components). Modelled as base_salary with fixed_allowances: [].
    
    First period valid_from set to 2024-09-01 (first tranche date per Allegato A). Pre-tranche salaries belong to the previous CCNL and are not modelled.
    
    Seniority (Art. 113): first scatto after 4 years (48 months), then every 36 months; maximum 8 scatti for the Aree Professionali and 12 for the Quadri Direttivi (Art. 101), via maximum_count_by_level.
    
    Hourly divisor 160 in both periods per Art. 114 (rounding down to the nearest multiple of 5): 37.5h x 52 / 12 = 162.5 → 160 (pre-July 2025); 37h x 52 / 12 = 160.33 → 160 (from July 2025, Art. 118).
    
    Workers covered: approximately 36,000 (Federcasse / Banche di Credito Cooperativo, Casse Rurali ed Artigiane). Agreement signed 2024-07-09; valid until 2025-12-31 per Art. 9.
    
    INPS rates from 2026-credito.json (same sector as bancari-abi). IRPEF 2026 brackets applied (L. 199/2025).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/bcc-credito-cooperativo.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/bcc-credito-cooperativo.py"
```
