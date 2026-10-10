# CCNL per i lavoratori addetti alle industrie delle pelli e dei succedanei della pelle (Assopellettieri)

| | |
|---|---|
| **CNEL code** | `D111` |
| **Sector** | industria |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~17k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Assopellettieri
    - Confindustria Moda
    - Filctem-Cgil
    - Femca-Cisl
    - Uiltec-Uil

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
| **Latest salary tranche** | 2025-12-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `6` | Level 6 — top-level quadri and sector executives | € 2,412.21 | 2025-12-01 |
| `5` | Level 5 — white-collar employees with managerial functions and specialist technicians | € 2,185.24 | 2025-12-01 |
| `4S` | Level 4 Super — technicians and white-collar employees with advanced duties | € 2,047.33 | 2025-12-01 |
| `4` | Level 4 — highly specialised workers | € 2,000.26 | 2025-12-01 |
| `3` | Level 3 — specialist workers | € 1,911.70 | 2025-12-01 |
| `2` | Level 2 — skilled workers | € 1,814.00 | 2025-12-01 |
| `1` | Level 1 — general workers (classification removed from 31/12/2023; table pay retained as apprenticeship reference Art. 55) | € 1,379.86 | 2025-12-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 4 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 6.71 |
| `2` | € 7.41 |
| `3` | € 7.95 |
| `4` | € 8.39 |
| `4S` | € 8.91 |
| `5` | € 9.68 |
| `6` | € 11.88 |

## Apprenticeship

**dest_6** (type: `under_classification`)  
Destination levels: `6`

**dest_5** (type: `under_classification`)  
Destination levels: `5`

**dest_4S** (type: `under_classification`)  
Destination levels: `4S`

**dest_4** (type: `under_classification`)  
Destination levels: `4`

**dest_3** (type: `under_classification`)  
Destination levels: `3`

**dest_2** (type: `under_classification`)  
Destination levels: `2`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "pelli-cuoio-industria-assopellettieri/level_1_apprentice_reference · base_salary · impact unknown · open"
    LEVEL 1: from the agreement of 22/12/2023, level 1 is no longer a classification level for permanent workers (automatic reclassification to level 2 by 31/12/2023). The pay value for level 1 remains defined in the contract for the entire duration up to 2025 (table Art. 32, CNEL PDF, confirmed primary source). It is assumed that Art. 55 (apprenticeship) was not modified by the 22/12/2023 agreement: that agreement was not accessible from the public sources consulted (CNEL archive, union websites), so the continuity of level 1 as a pay reference for apprentices destined for level 2 and level 3 is assumed but not verified against the supplementary agreement text.

    **Applies when:** `base_salary` applies; contract type in apprentice; level in 2, 3.

    **Remediation:** Verify the 22/12/2023 agreement for the apprenticeship pay reference of level 1.

!!! warning "pelli-cuoio-industria-assopellettieri/apprentice_seniority · seniority · impact unknown · open"
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
| — | — | 2023-05-26 | [↗](https://cdcpcnelblg01sa.blob.core.windows.net/archivio/2023//20098.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobato (table pay inclusive of base pay, former contingenza, E.d.r.). Art. 32 CCNL (CNEL PDF): 'Sono conglobati in un unica voce denominata Retribuzione tabellare i seguenti istituti: paga base, ex indennita di contingenza, E.d.r.' PELLETTERIA table with 7 levels and 4 tranches (Apr 2023, Dec 2023, Dec 2024, Dec 2025) from primary source CNEL PDF Art. 32.
    
    HOURLY DIVISOR 173: Art. 35 CCNL (CNEL PDF): 'La retribuzione e oraria e si ottiene dividendo la retribuzione mensile per 173'.
    
    ADDITIONAL MONTHS 13: tredicesima (thirteenth month). Source: ANCL summary CCNL D111.
    
    SENIORITY INCREMENTS: Art. 54 CCNL (CNEL PDF). 'quattro aumenti biennali periodici di anzianita' — 24-month cadence, maximum 4. Per-level amounts from Art. 54 CNEL PDF table.
    
    APPRENTICESHIP: Art. 55 CCNL (CNEL PDF). Under-classification model, maximum duration 36 months. Six distinct tracks (one per destination level) with specific pay progression for each level, as per Art. 55 table. Special note for level 2: 'Gli apprendisti con destinazione finale al secondo saranno inquadrati al livello di destinazione finale con decorrenza dall'inizio del secondo periodo di apprendistato' (from month 11 onwards at level 2).
    
    INPS: industry sector rates from 2026-industria.json (existing file reused). Employee 9.19%; employer: <=15 employees 30.13%, 16-50 employees 30.20%, >50 employees 30.50%.
    
    LEVEL 6Q: not present in the CCNL table of the CNEL PDF (August 2023). Excluded from the model.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/pelli-cuoio-industria-assopellettieri.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/pelli-cuoio-industria-assopellettieri.py"
```
