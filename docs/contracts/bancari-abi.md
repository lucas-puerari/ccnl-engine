# CCNL per i lavoratori dipendenti dalle aziende di credito (ABI)

| | |
|---|---|
| **CNEL code** | `J241` |
| **Sector** | credito |
| **Tax sector** | `credito` |
| **Last renewal** | — |
| **Workers (est.)** | ~270k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ABI
    - FABI
    - FIRST-CISL
    - FISAC-CGIL
    - UILCA
    - UNISIN

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
| **Limits of this contract** | base_salary, inps_employer, seniority |

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

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QD4` | Executive Managers - 4th level | € 5,160.06 | 2026-03-01 |
| `QD3` | Executive Managers - 3rd level | € 4,396.88 | 2026-03-01 |
| `QD2` | Executive Managers - 2nd level | € 3,965.48 | 2026-03-01 |
| `QD1` | Executive Managers - 1st level | € 3,743.21 | 2026-03-01 |
| `3A4` | 3rd Professional Area - 4th level | € 3,341.90 | 2026-03-01 |
| `3A3` | 3rd Professional Area - 3rd level | € 3,059.49 | 2026-03-01 |
| `3A2` | 3rd Professional Area - 2nd level | € 2,890.41 | 2026-03-01 |
| `3A1` | 3rd Professional Area - 1st level | € 2,742.34 | 2026-03-01 |
| `1e2A` | 1st and 2nd Professional Area (Unified Area) | € 2,479.45 | 2026-03-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `QD4` | € 95.31 |
| `QD3` | € 95.31 |
| `QD2` | € 41.55 |
| `QD1` | € 41.55 |
| `3A4` | € 41.55 |
| `3A3` | € 41.55 |
| `3A2` | € 41.55 |
| `3A1` | € 41.55 |
| `1e2A` | € 29.07 |

## Apprenticeship

**terza_area** (type: `under_classification`)  
Destination levels: `3A2`, `3A3`, `3A4`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "bancari-abi/apprenticeship_destination_levels · base_salary · impact unknown · open"
    Apprenticeship (Art. 35, rinnovo 23-11-2023) targets the 3ª area professionale without naming the level; modelled for destination levels 3A2, 3A3 and 3A4 with 18 months one level below, then the destination level. 3A1 is excluded because the level below (Area Unificata 1ª e 2ª area) is not an apprenticeship classification.

    **Applies when:** `base_salary` applies; contract type in apprentice; level in 3A2, 3A3, 3A4.

    **Remediation:** Confirm the destination levels of the Art. 35 apprenticeship against the contract text.

!!! warning "bancari-abi/inps_credit_rate_unverified · inps_employer · impact unknown · open"
    INPS employer_rate 26.76% flat from kitech.it (Credito e Assicurazioni 2026); the Fondo di solidarietà del credito (bilateral) is presumed included in the aggregate rate. Verify against the annual INPS circular.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Verify the 26.76% employer rate and the solidarity fund share against the annual INPS circular.

!!! warning "bancari-abi/apprentice_seniority · seniority · impact unknown · open"
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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-11-23 | [↗](https://www.first-cisl.it/rinnovo-ccnl-bancari-2023/) |
| — | — | — | [↗](https://www.ccnlbancari.it/) |

??? note "Coverage notes"
    Hourly divisor 162 for the 37.5h/week period (2023-11-23 to 2024-06-30) and 160 from 2024-07-01 (37h/week).
    
    Seniority: first scatto after 48 months, then every 36 months; maximum 8 scatti for the Aree Professionali and 7 for QD3/QD4 (maximum_count_by_level).
    
    Apprenticeship: https://www.ccnlbancari.it/ Art. 35, post-rinnovo 2023-11-23.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/bancari-abi.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/bancari-abi.py"
```
