# CCNL Istituzioni e Servizi Socio-Assistenziali (ANASTE)

| | |
|---|---|
| **CNEL code** | `T131` |
| **Sector** | servizi socio-assistenziali |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~120k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🟢 Verified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANASTE
    - FISASCAT-CISL
    - UILTuCS-UIL
    - UGL Terziario

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
| **Last renewal** | — |
| **Last verified** | — |
| **Latest salary tranche** | 2025-08-01 |

### Semplificazioni note

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro (dirigente di struttura o coordinatore senior) | € 2,130.15 | 2025-08-01 |
| `10` | Livello 10 — Responsabile di area/servizio | € 1,972.13 | 2025-08-01 |
| `9` | Livello 9 — Coordinatore/Professionista senior | € 1,893.48 | 2025-08-01 |
| `8` | Livello 8 — Operatore specializzato senior | € 1,769.59 | 2025-08-01 |
| `7` | Livello 7 — Operatore specializzato | € 1,752.93 | 2025-08-01 |
| `6` | Livello 6 — Operatore qualificato senior | € 1,696.37 | 2025-08-01 |
| `5` | Livello 5 — Operatore qualificato | € 1,637.06 | 2025-08-01 |
| `4` | Livello 4 — Operatore | € 1,562.10 | 2025-08-01 |
| `3S` | Livello 3 Super — Operatore ausiliario specializzato | € 1,525.03 | 2025-08-01 |
| `3` | Livello 3 — Operatore ausiliario | € 1,487.96 | 2025-08-01 |
| `2` | Livello 2 — Addetto generico | € 1,390.12 | 2025-08-01 |
| `1` | Livello 1 — Addetto base (introdotto nel rinnovo 2025) | € 1,295.43 | 2023-01-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 35.12 |
| `10` | € 33.57 |
| `9` | € 30.99 |
| `8` | € 30.47 |
| `7` | € 29.95 |
| `6` | € 28.92 |
| `5` | € 28.41 |
| `4` | € 27.89 |
| `3S` | € 27.63 |
| `3` | € 27.37 |
| `2` | € 26.86 |
| `1` | € 25.31 |

## Apprenticeship

**professionalizzante_32** (type: `percentage`)  
Destination levels: `Q`, `10`, `9`, `8`, `7`, `6`, `5`, `4`, `3S`, `3`, `2`, `1`  
percentage: 0.95

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "istituzioni-servizi-socio-assistenziali-anaste/apprentice_seniority · seniority · impact unknown · open"
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
| — | — | 2025-07-23 | [↗](https://snalv.it/docs/anaste25/pdf6.pdf) |

??? note "Coverage notes"
    RENEWAL: CCNL signed 2025-07-23, triennio 2023-2025. Economic effects from 2025-08-01. Una tantum non modelled (non-recurring).
    
    CONGLOBATED (Art. 69): minimo contrattuale conglobato includes base wage, contingenza and EDR. No separate contingenza or EDR column.
    
    HOURLY DIVISOR (Art. 72): 164 h/month for 38h/week. Verified: 1696.37/10.34=164.06 (lvl 6), 1893.48/11.55=163.94 (lvl 9), 2130.15/12.99=163.98 (lvl Q).
    
    ADDITIONAL MONTHS (Art. 74): tredicesima only (paid December). Art. 75 states the quattordicesima equivalent is already embedded in the monthly conglobated minimum.
    
    SENIORITY (Art. 73): scatti triennali, max 10 scatti. Per-level amounts confirmed from Art. 73 table.
    
    LEVEL Q ALLOWANCE (Art. 70): indennita di funzione 77.47 EUR/month paid 13 months/year.
    
    LEVEL 1 PRE-2025: level 1 introduced ex-novo in 2025 renewal. Pre-2025 salary set equal to 2025-08-01 value (1295.43 EUR) — no historical data available.
    
    APPRENTICESHIP (Art. 22): modelled on levels 6-10 parameters (32 months, 90% mesi 1-28, 95% mesi 29+). Levels 1-5 have different duration (12 months, 95% from month 7) — not modelled separately.
    
    NURSES ALLOWANCE: indennita professionale infermieri 155 EUR/month (12 months) not included — qualifica-specific, not level-specific.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/istituzioni-servizi-socio-assistenziali-anaste.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/istituzioni-servizi-socio-assistenziali-anaste.py"
```
