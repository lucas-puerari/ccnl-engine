# CCNL per i dipendenti dalle aziende di lavorazione della foglia di tabacco secco allo stato sciolto

| | |
|---|---|
| **CNEL code** | `E042` |
| **Sector** | lavorazione foglia di tabacco |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-07-02 |
| **Workers (est.)** | ~2k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🧑 Manual |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - APTI
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
| **Limits of this contract** | pension_fund_contribution, seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🟡 Needs review |
| **Last human review** | 2026-09-18 |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2025-07-02 |
| **Last verified** | 2026-09-18 |
| **Latest salary tranche** | 2028-01-01 |

### Semplificazioni note

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1S` | Categoria Super — funzioni direttive di particolare rilievo | € 2,271.18 | 2028-01-01 |
| `1` | 1a Categoria — funzioni direttive amministrative o tecniche | € 2,106.68 | 2028-01-01 |
| `2` | 2a Categoria — funzioni di concetto con coordinamento | € 1,847.04 | 2028-01-01 |
| `3A` | 3a Categoria A — compiti esecutivi tecnici o amministrativi con iniziativa | € 1,625.55 | 2028-01-01 |
| `3B` | 3a Categoria B — compiti esecutivi tecnici o amministrativi | € 1,462.16 | 2028-01-01 |
| `4A` | 4a Categoria A — qualificazione per il processo di lavorazione del tabacco | € 1,334.90 | 2028-01-01 |
| `4B` | 4a Categoria B — conoscenze tecnico-pratiche di controllo o produzione | € 1,279.29 | 2028-01-01 |
| `5` | 5a Categoria — mansioni operative standard | € 1,242.28 | 2028-01-01 |
| `6` | 6a Categoria — mansioni semplici di prima assunzione | € 1,115.90 | 2028-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1S` | € 17.00 |
| `1` | € 17.00 |
| `2` | € 15.00 |
| `3A` | € 14.00 |
| `3B` | € 13.00 |
| `4A` | € 12.00 |
| `4B` | € 12.00 |
| `5` | € 11.00 |
| `6` | € 10.00 |

## Apprenticeship

**apprendistato professionalizzante (livelli 2-4)** (type: `under_classification`)  
Destination levels: `2`, `3A`, `3B`, `4A`, `4B`

**apprendistato professionalizzante (livello 1)** (type: `under_classification`)  
Destination levels: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "tabacco-apti/alifond_before_july_2025 · pension_fund_contribution · impact yes · open"
    ALIFOND employer contribution (1.50%) modeled from 01/07/2025 (renewal Art. 47). Pre-July-2025 ALIFOND contribution not modeled.

    **Applies when:** `pension_fund_contribution` applies; before 2025-07-01.

    **Remediation:** Model the ALIFOND employer rate in force before 1 July 2025.

!!! warning "tabacco-apti/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax or INPS ruleset marked provisional: the sources of its year are not published yet (INPS circular on the massimale, minimale and rates of the year; regional and municipal surtax resolutions; budget law of the year), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; the indexed amounts (INPS massimale and minimale) do not, and any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

### Without monetary impact

!!! note ""
    APPRENTICESHIP: under_classification for destinations 2, 3A, 3B, 4A, 4B (36-month, 10/12/14 periods) and level 1 (36-month, 10/10/16 periods). Destination 5 (24-month exception, Article 6) not modeled. Level 1S is not an apprenticeship destination.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| CCNL Tabacco Lavorazione foglia 2025-2028 — Accordo 02/07/2025 | altro | — | [↗](https://www.uila.eu/web/wp-content/uploads/2022/04/Accordo-rinnovo-ccnl-nazionale-tabacco-sciolto-2025-2028-02-07-25.pdf) |
| CCNL Tabacco (Lavorazione) — lavoro-economia.it | tabella_retributiva | — | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=25) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = minimo tabellare (4 tranches: +60 at 4A on 01/01/2025, +50 on 01/01/2026, +50 on 01/01/2027, +40 on 01/01/2028). 50/50 parametric formula verified against published Allegato A table.
    
    CONTINGENZA: per-level amounts frozen at 01/11/1991 (Allegato B, CCNL 2021). EDR 10.33 EUR uniform for all levels (Accordo Interconfederale 31/07/1992).
    
    SENIORITY: cadence 24 months, maximum 5 scatti. Amounts from Article 32 of the 2025 renewal. Operai amounts roughly doubled vs 2021 CCNL (4A/B: 5.68->12.00, 5: 5.42->11.00, 6: 5.16->10.00).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/tabacco-apti.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/tabacco-apti.py"
```
