# CCNL Scuole Materne — FISM

| | |
|---|---|
| **CNEL code** | `T271` |
| **Sector** | istruzione privata cattolica per l'infanzia |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~30k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🟢 Verified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - FISM
    - CISL Scuola
    - FLC-CGIL
    - UIL Scuola RUA
    - SNALS-CONFSAL

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
| **Latest salary tranche** | 2027-09-01 |

### Semplificazioni note

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `VIII` | Livello VIII — Dirigente scolastico / direttore | € 1,955.38 | 2027-09-01 |
| `VII` | Livello VII — Coordinatore pedagogico / insegnante senior | € 1,912.11 | 2027-09-01 |
| `VI` | Livello VI — Insegnante di scuola dell'infanzia | € 1,739.55 | 2027-09-01 |
| `V` | Livello V — Educatore di nido / personale specializzato | € 1,719.76 | 2027-09-01 |
| `IV` | Livello IV — Educatore / personale qualificato | € 1,630.03 | 2027-09-01 |
| `III` | Livello III — Personale amministrativo / ausiliario specializzato | € 1,579.50 | 2027-09-01 |
| `II` | Livello II — Personale ausiliario qualificato / assistente | € 1,577.20 | 2027-09-01 |
| `I` | Livello I — Personale ausiliario non qualificato | € 1,517.75 | 2027-09-01 |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

| Level | Increment (monthly) |
|---|---:|
| `I` | € 0.00 |
| `II` | € 0.00 |
| `III` | € 0.00 |
| `IV` | € 0.00 |
| `V` | € 0.00 |
| `VI` | € 0.00 |
| `VII` | € 0.00 |
| `VIII` | € 0.00 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `I`, `II`, `III`, `IV`, `V`, `VI`, `VII`, `VIII`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "scuole-materne-fism/salario_di_anzianita · seniority · impact yes · open"
    SENIORITY (Arts. 44-46): periodic scatti (Arts. 35 CCNL 2006-2009) were frozen at 31/12/2015 and consolidated by CCNL 2016-2018. Salario di anzianita (Art. 46): 15 EUR/month (livelli I-II-III-IV) or 20 EUR/month (livelli V-VI-VII-VIII) as at 01/09/2025. Engine seniority model cannot express the milestone/hire-date nature; maximum_count=0 models new-hire case correctly but understates cost for long-tenure workers.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the Art. 46 salario di anzianita with a hire-date or milestone input.

!!! warning "scuole-materne-fism/apprenticeship_identity_track · base_salary · impact unknown · open"
    APPRENTICESHIP: no apprenticeship clause found in main CCNL text. Sector primarily employs teachers on permanent contracts. Modelled as single percentage period at 100% (identity transform) for all levels; correct for permanent staff.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Source the apprenticeship clause and replace the 100% identity track.

!!! warning "scuole-materne-fism/apprentice_seniority · seniority · impact unknown · open"
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
| — | — | 2025-05-28 | [↗](https://fism.net/wp-content/uploads/2026/06/28-05-25-ccnl-24-27-definitivo-con-firme.pdf) |
| — | — | 2026-07-07 | [↗](https://fism.net/wp-content/uploads/2026/07/CCNL-FISM-ACCORDO-ECONOMICO-2026-2027.pdf) |

??? note "Coverage notes"
    CCNL FISM signed 28/05/2025 (sede ASI). Validity 01/09/2023-31/08/2027. Economic accord for 2026-2027 signed 07/07/2026.
    
    CONGLOBATED (Art. 43): indennita di contingenza maturata al 30/11/1991 inglobata nella retribuzione tabellare (Art. 42 lett. B). No separate contingenza column.
    
    SALARY TABLE (Art. 42 lett. B): 5 tranches — 01/09/2023, 01/06/2025, 01/09/2025 from main CCNL PDF; 01/09/2026, 01/09/2027 from 2026-2027 economic accord.
    
    HOURLY DIVISOR (Art. 51): 160 h/month for 37h/week. Divisors for 35h=152, 32h=139 also stated.
    
    ADDITIONAL MONTHS (Art. 49): tredicesima only, paid by 20 December.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/scuole-materne-fism.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/scuole-materne-fism.py"
```
