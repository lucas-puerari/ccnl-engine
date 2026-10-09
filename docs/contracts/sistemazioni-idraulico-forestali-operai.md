# CCNL Sistemazioni Idraulico-Forestali e Idraulico-Agraria (Operai OTI)

| | |
|---|---|
| **CNEL code** | `A181` |
| **Sector** | sistemazioni idraulico-forestali e idraulico-agrarie — operai a tempo indeterminato |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2025-12-04 |
| **Workers (est.)** | ~430 (operai OTI subset) |
| **Ruleset version** | `2026.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - AGCI-Agrital
    - Confcooperative-Fedagripesca
    - Confcooperative-Lavoro-e-Servizi
    - Federforeste
    - Legacoop-Agroalimentare
    - FAI-CISL
    - FLAI-CGIL
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
| **Last renewal** | 2025-12-04 |
| **Last verified** | — |
| **Latest salary tranche** | 2028-01-01 |

### Semplificazioni note

4 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `O5` | Operaio OTI 5° livello | € 1,695.97 | 2028-01-01 |
| `O4` | Operaio OTI 4° livello | € 1,596.98 | 2028-01-01 |
| `O3` | Operaio OTI 3° livello | € 1,528.08 | 2028-01-01 |
| `O2` | Operaio OTI 2° livello | € 1,491.16 | 2028-01-01 |
| `O1` | Operaio OTI 1° livello | € 1,376.66 | 2028-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

| Level | Increment (monthly) |
|---|---:|
| `O1` | € 0.00 |
| `O2` | € 0.00 |
| `O3` | € 0.00 |
| `O4` | € 0.00 |
| `O5` | € 0.00 |

## Apprenticeship

**apprendistato_O3_22mesi** (type: `under_classification`)  
Destination levels: `O3`

**apprendistato_O4_32mesi** (type: `under_classification`)  
Destination levels: `O4`

**apprendistato_O5_36mesi** (type: `under_classification`)  
Destination levels: `O5`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "sistemazioni-idraulico-forestali-operai/structural_rules_from_2021_text · base_salary · impact unknown · open"
    Structural rules (Art. 7, 49, 52) taken from 2021 previgente CCNL text. The 2025 rinnovo PDF is image-only and full text is unavailable for independent verification.

    **Applies when:** `base_salary` applies.

    **Remediation:** Verify the structural rules against the 2025 renewal text.

!!! warning "sistemazioni-idraulico-forestali-operai/apprentice_seniority · seniority · impact unknown · open"
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
    Serie retributiva starts 01/01/2026 (first tranche with primary-source data). Retroactive 2025 tabella not available in machine-readable form; pre-2026 amounts omitted.

!!! note ""
    Apprendistato: livelli O1 e O2 esclusi da destination_levels (engine requires at least 2 levels below minimum; O2 at order=2 cannot go 2 below). Only O3, O4, O5 supported.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-12-04 | [↗](https://redigo.info/) |
| — | — | 2021-01-01 | [↗](file:ccnl-idraulico-forestali-2021.txt) |

??? note "Coverage notes"
    CCNL A181 — Sistemazioni Idraulico-Forestali (Operai OTI). Split from impiegati contract: salary bands overlap, requiring separate files for correct engine ordering and under-classification apprenticeship. 5 livelli operai (O1-O5). Conglobato. Divisore 169, 14 mensilita.
    
    Seniority operai: nessuno scatto di anzianita previsto a livello CCNL nazionale. Gli scatti sono disciplinati dai CIRL (contratti integrativi regionali). Modellati con importo zero e maximum_count=0.
    
    Apprendistato durate: la tabella Art. 7 elenca livelli 2-6 (scala impiegati). Le durate sono mappate su O3/O4/O5 per corrispondenza di livello; la ripartizione per categoria non e confermata dal testo.
    
    OVERTIME/LEAVE/ABSENCE (L3): Art. 50 CCNL 2023 — straordinario diurno 24%, notturno straordinario 38%, festivo straordinario 50%. Ferie 22 giorni (orario su 5 giorni, Art. 12). Malattia: trattamento INPS; nessuna integrazione datoriale a livello CCNL nazionale (Art. 60). Assenza: divisore 26. Rates from 2023 CCNL PDF; 2025 rinnovo structural rules assumed unchanged (text image-only).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/sistemazioni-idraulico-forestali-operai.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/sistemazioni-idraulico-forestali-operai.py"
```
