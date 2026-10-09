# CCNL Cooperative e Consorzi Agricoli

| | |
|---|---|
| **CNEL code** | `A016` |
| **Sector** | cooperative e consorzi agricoli — impiegati e operai agricoli |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2024-07-19 |
| **Workers (est.)** | ~60k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - AGCI-Agrital
    - Confcooperative-Fedagripesca
    - Legacoop-Agroalimentare
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
| **Last renewal** | 2024-07-19 |
| **Last verified** | — |
| **Latest salary tranche** | 2027-02-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1` | Livello 1° | € 2,303.40 | 2027-02-01 |
| `2` | Livello 2° | € 2,070.77 | 2027-02-01 |
| `3` | Livello 3° | € 1,906.06 | 2027-02-01 |
| `4` | Livello 4° | € 1,772.31 | 2027-02-01 |
| `5` | Livello 5° | € 1,685.38 | 2027-02-01 |
| `6` | Livello 6° | € 1,636.55 | 2027-02-01 |
| `7` | Livello 7° | € 1,518.40 | 2027-02-01 |
| `np` | Area non professionalizzati | € 1,280.82 | 2027-02-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 12 increments

| Level | Increment (monthly) |
|---|---:|
| `np` | € 0.00 |
| `7` | € 9.44 |
| `6` | € 10.85 |
| `5` | € 11.39 |
| `4` | € 11.93 |
| `3` | € 12.20 |
| `2` | € 29.44 |
| `1` | € 33.05 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `np`, `7`, `6`, `5`, `4`, `3`, `2`, `1`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "cooperative-consorzi-agricoli/apprenticeship_passthrough · base_salary · impact unknown · open"
    Apprendistato: regola non reperita nel PDF 2024. Modellato come 100% passthrough.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Source the apprenticeship rule of the 2024 CCNL and model its track.

!!! warning "cooperative-consorzi-agricoli/apprentice_seniority · seniority · impact unknown · open"
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
| — | — | 2024-07-19 | [↗](https://www.flai.it/wp-content/uploads/2018/11/CCNL-Cooperative-e-consorzi-agricoli-2024-2027.pdf) |

??? note "Coverage notes"
    CCNL A016 — Cooperative e Consorzi Agricoli. Conglobated model. 8 livelli: np-7-6-5-4-3-2-1. Divisore 169, 14 mesi. 4 tranches: apr-2024, mag-2025, mag-2026, feb-2027.
    
    Quadri: i livelli 1Q e 2Q del precedente impianto corrispondono a livello 1° e 2° con aggiunta dell'indennità di funzione quadri (Art. 45): 1Q +EUR 180→230/mese, 2Q +EUR 125→160/mese dal 01/08/2024. Modellata come fixed_allowance a 14 mensilità su ciascun livello.
    
    SENIORITY: operai Art. 61 (max 5 biennali) e impiegati Art. 49 (max 12 biennali) hanno importi differenti per livelli 3-7. Operai amounts confirmed from rinnovo 2024 (lavoro-economia.it, businessonline.it): L7=9.44, L6=10.85, L5=11.39, L4=11.93, L3=12.20, L2=29.44, L1=33.05 EUR/biennio. Modelled with operai amounts (dominant workforce in cooperatives) and maximum_count=12 (impiegati cap). Queries for operai with seniority_count>5 will overstate by at most 1-5 scatti; this is a structural engine limitation (single seniority table per level).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/cooperative-consorzi-agricoli.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/cooperative-consorzi-agricoli.py"
```
