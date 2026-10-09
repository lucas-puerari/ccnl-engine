# CCNL Agenzie di Viaggio e Turismo — Fiavet/Confcommercio

| | |
|---|---|
| **CNEL code** | `H052` |
| **Sector** | Turismo (agenzie di viaggio) |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-07-26 |
| **Workers (est.)** | ~25k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Fiavet (Federazione Italiana Associazioni Imprese Viaggi e Turismo)
    - Federviaggio
    - Filcams-CGIL
    - Fisascat-CISL
    - Uiltucs-UIL

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
| **Last renewal** | 2024-07-26 |
| **Last verified** | — |
| **Latest salary tranche** | 2027-12-01 |

### Semplificazioni note

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QA` | Quadro A — Top management function | € 2,495.21 | 2027-12-01 |
| `QB` | Quadro B — Management function | € 2,310.11 | 2027-12-01 |
| `1` | Level 1 — Conceptual employee with managerial functions | € 2,152.33 | 2027-12-01 |
| `2` | Level 2 — Conceptual employee | € 1,967.21 | 2027-12-01 |
| `3` | Level 3 — Qualified employee | € 1,855.32 | 2027-12-01 |
| `4` | Level 4 — Employee | € 1,750.69 | 2027-12-01 |
| `5` | Level 5 — Qualified clerical employee | € 1,641.83 | 2027-12-01 |
| `6S` | Level 6S — Super clerical employee | € 1,578.72 | 2027-12-01 |
| `6` | Level 6 — Clerical employee | € 1,556.35 | 2027-12-01 |
| `7` | Level 7 — Auxiliary staff | € 1,458.41 | 2027-12-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `QA` | € 40.80 |
| `QB` | € 39.25 |
| `1` | € 37.70 |
| `2` | € 36.15 |
| `3` | € 34.86 |
| `4` | € 33.05 |
| `5` | € 32.54 |
| `6S` | € 31.25 |
| `6` | € 30.99 |
| `7` | € 30.47 |

## Apprenticeship

**standard** (type: `percentage`)  
Destination levels: `1`, `2`, `3`, `4`, `5`, `6S`, `6`, `7`  
percentage: 0.90

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "agenzie-viaggio-fiavet/apprentice_seniority · seniority · impact unknown · open"
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
    The run reads a tax or INPS ruleset marked provisional: the sources of its year are not published yet (INPS circular on the massimale, minimale and rates of the year; regional and municipal surtax resolutions; budget law of the year), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; the indexed amounts (INPS massimale and minimale) do not, and any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

### Without monetary impact

!!! note ""
    Levels QA and QB (Quadri) excluded from the apprenticeship track (apprenticeship not applicable to Quadri by law).

!!! note ""
    Layer 3 (overtime, night shifts, public holidays) out of scope.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2019-07-11 | [↗](https://cdcpcnelblg01sa.blob.core.windows.net/archivio/2019//20108.pdf) |
| — | — | 2024-07-26 | [↗](https://cdcpcnelblg01sa.blob.core.windows.net/archivio/2024//20108.pdf) |

??? note "Coverage notes"
    Salary tables 2024-2027 from CCNL renewal of 26 July 2024 (CNEL PDF). Six tranches: Jun-24, Jul-24, Sep-25, Sep-26, Jun-27, Dec-27.
    
    Hourly divisor 172 from Art. 146 CCNL base 2019 (CNEL PDF doc 20108). Same basis as the Confcommercio tourism sector.
    
    14 additional monthly payments from Art. 157 (thirteenth month) and Art. 158 (fourteenth month) of the 2024 renewal.
    
    Triennial seniority increments (Art. 156 CCNL 2019): 36-month cadence, maximum 6 increments. Per-level amounts from the table attached to the 2024 renewal.
    
    Percentage-based apprenticeship from Art. 64 CCNL 2019 (OCR pages 32-33): first year 80%, second year 85%, third year 90%.
    
    CNEL code H052 confirmed from kitech.it CodiceCateg=81 (Confcommercio tourism sector, travel agencies included).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/agenzie-viaggio-fiavet.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/agenzie-viaggio-fiavet.py"
```
