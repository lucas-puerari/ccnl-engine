# CCNL Turismo (Assoturismo-Confesercenti)

| | |
|---|---|
| **CNEL code** | `H058` |
| **Sector** | turismo — alberghi, campeggi, pubblici esercizi, agenzie di viaggi |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-07-22 |
| **Workers (est.)** | — |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Assoturismo-Confesercenti
    - Assohotel
    - Assocamping
    - Assoviaggi
    - FIEPET
    - FIBA
    - FILCAMS-CGIL
    - FISASCAT-CISL
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
| **Last renewal** | 2024-07-22 |
| **Last verified** | — |
| **Latest salary tranche** | 2027-11-01 |

### Semplificazioni note

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QA` | Quadro A | € 2,495.22 | 2027-11-01 |
| `QB` | Quadro B | € 2,310.11 | 2027-11-01 |
| `1` | Livello 1 | € 2,152.32 | 2027-11-01 |
| `2` | Livello 2 | € 1,967.20 | 2027-11-01 |
| `3` | Livello 3 | € 1,855.32 | 2027-11-01 |
| `4` | Livello 4 | € 1,750.69 | 2027-11-01 |
| `5` | Livello 5 | € 1,641.85 | 2027-11-01 |
| `6S` | Livello 6S | € 1,578.72 | 2027-11-01 |
| `6` | Livello 6 | € 1,556.35 | 2027-11-01 |
| `7` | Livello 7 | € 1,458.42 | 2027-11-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `7` | € 30.47 |
| `6` | € 30.99 |
| `6S` | € 31.25 |
| `5` | € 32.54 |
| `4` | € 33.05 |
| `3` | € 34.86 |
| `2` | € 36.15 |
| `1` | € 37.70 |
| `QB` | € 39.25 |
| `QA` | € 40.80 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `7`, `6`, `6S`, `5`, `4`, `3`, `2`, `1`, `QB`, `QA`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "turismo-confesercenti/apprentice_seniority · seniority · impact unknown · open"
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
| — | — | 2024-07-22 | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=257) |
| — | — | 2024-07-22 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=82) |
| — | — | 2024-07-22 | [↗](https://www.redigo.info/2024/07/24/ccnl-turismo-confesercenti-il-rinnovo-consolida-il-contratto-unico/) |

??? note "Coverage notes"
    CCNL H058 — Assoturismo-Confesercenti. Conglobated. 10 levels: 7-6-6S-5-4-3-2-1-QB-QA. Divisor 172, 14 months. Seniority 36-month cadence, max 6. 5 tranches: Jul-2024 to Nov-2027.
    
    Models the alberghi/campeggi sub-sector only (CCNL H058, conglobated model). Pubblici esercizi and stabilimenti balneari use a split (paga base + contingenza) model with different values — out_of_scope deliberate: these sub-sectors have meaningfully different pay structures requiring separate files.
    
    Indennita di funzione for QA (EUR 75/month) and QB (EUR 70/month) conglobated into base_salary. Consistent with turismo-federalberghi.json modeling for the same allowances. The CCNL H058 does not publish them as separate line items in the tabella retributiva; absorption into base_salary matches the conglobated model.
    
    Apprenticeship model confirmed: CCNL Turismo Confesercenti provides sotto-inquadramento 2 levels below destination (consistent with Testo Unico apprendistato Art. 11, secondary sources). Engine uses 100% passthrough because schema requires static pay_level_code; the 2-level under-classification cannot be modelled dynamically. Modeled as 100% passthrough pending contract text.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/turismo-confesercenti.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/turismo-confesercenti.py"
```
