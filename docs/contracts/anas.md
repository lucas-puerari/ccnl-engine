# CCNL Gruppo ANAS

| | |
|---|---|
| **CNEL code** | `T511` |
| **Sector** | anas spa - personale non dirigente |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-12-18 |
| **Workers (est.)** | ~7k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANAS SpA
    - FILT-CGIL
    - FIT-CISL
    - UILTRASPORTI
    - UGL Viabilità e Logistica

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
| **Limits of this contract** | seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2025-12-18 |
| **Last verified** | — |
| **Latest salary tranche** | 2027-07-01 |

### Semplificazioni note

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A` | Livello A | € 3,475.91 | 2027-07-01 |
| `A1` | Livello A1 | € 2,896.61 | 2027-07-01 |
| `B` | Livello B | € 2,462.15 | 2027-07-01 |
| `B1` | Livello B1 | € 2,244.84 | 2027-07-01 |
| `B2` | Livello B2 | € 2,027.55 | 2027-07-01 |
| `C` | Livello C | € 1,665.53 | 2027-07-01 |
| `C1` | Livello C1 | € 1,448.36 | 2027-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `C1` | € 16.66 |
| `C` | € 19.16 |
| `B2` | € 23.32 |
| `B1` | € 25.82 |
| `B` | € 28.30 |
| `A1` | € 33.31 |
| `A` | € 39.97 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `C1`, `C`, `B2`, `B1`, `B`, `A1`, `A`  
percentage: 0.92

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "anas/apprentice_seniority · seniority · impact unknown · open"
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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-12-18 | [↗](https://www.stradeanas.it/sites/default/files/Azienda/Lavora_con_noi/CCNL-2025-2027.pdf) |

??? note "Coverage notes"
    Split model: minimo tabellare + IIS (Indennita Integrativa Speciale, frozen). 7 levels C1-C-B2-B1-B-A1-A. Divisor 156, 13 months. 4 tranches: 01/03/2026, 01/09/2026, 01/03/2027, 01/07/2027.
    
    IIS months_per_year=13: confirmed equal to additional_months (ANAS CCNL: 13 mensilità standard; INPS/secondary sources confirm 13-month pay cycle).
    
    Seniority maximum_count=10 — confirmed: ANAS CCNL provides 10 biennial seniority increments (secondary source cross-reference, consistent with comparable PA-adjacent contracts).
    
    Apprenticeship 70/85/92% confirmed from CCNL ANAS 2025-2027 Art. 28 text. Last period (months_until=null at 92%) reflects the contractual open-ended formulation; upon qualification the worker moves to full pay at the destination level.
    
    Overtime base (Art. 101 CCNL ANAS): the official retribuzione oraria includes minimo tabellare + IIS (contingenza) + RIA + AEP + EDR. Engine uses hourly_base_method=minimo_tabellare, which understates the overtime base by excluding IIS, RIA, AEP, EDR. Structural engine limitation (no per-allowance hourly_relevant flag); monthly/annual figures unaffected.
    
    Malattia: 100% mesi 1-12, 50% mesi 13+ — CCNL ANAS 2025-2027 Art. malattia. Modellato con SicknessTier (comporto standard). Periodi a cavallo di soglia mensile ricevono un unico tasso (engine limitation accettabile).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/anas.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/anas.py"
```
