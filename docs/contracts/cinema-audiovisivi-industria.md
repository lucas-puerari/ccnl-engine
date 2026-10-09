# CCNL Industrie Cineaudiovisive (ANICA)

| | |
|---|---|
| **CNEL code** | `G111` |
| **Sector** | Cinema e audiovisivo |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-07-23 |
| **Workers (est.)** | ~2.3k |
| **Ruleset version** | `2025.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANICA
    - SLC-CGIL
    - FISTEL-CISL
    - UILCOM-UIL

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
| **Limits of this contract** | bilateral_funds |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2025-07-23 |
| **Last verified** | — |
| **Latest salary tranche** | 2028-01-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `7S` | Livello 7 Super (QA — Quadro) | € 2,880.55 | 2028-01-01 |
| `7` | Livello 7 (QB — Quadro) | € 2,758.66 | 2028-01-01 |
| `6S` | Livello 6 Super | € 2,510.69 | 2028-01-01 |
| `6` | Livello 6 | € 2,430.46 | 2028-01-01 |
| `5S` | Livello 5 Super | € 2,217.61 | 2028-01-01 |
| `5` | Livello 5 | € 2,164.88 | 2028-01-01 |
| `4S` | Livello 4 Super | € 2,103.30 | 2028-01-01 |
| `4` | Livello 4 | € 1,980.32 | 2028-01-01 |
| `3` | Livello 3 | € 1,796.03 | 2028-01-01 |
| `2` | Livello 2 | € 1,608.31 | 2028-01-01 |
| `1` | Livello 1 | € 1,440.48 | 2028-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 12.65 |
| `2` | € 13.17 |
| `3` | € 13.94 |
| `4` | € 14.46 |
| `4S` | € 14.46 |
| `5` | € 16.01 |
| `5S` | € 16.79 |
| `6` | € 17.56 |
| `6S` | € 17.56 |
| `7` | € 19.37 |
| `7S` | € 20.17 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "cinema-audiovisivi-industria/bilateral_funds_not_modelled · bilateral_funds · impact unknown · open"
    SIMPLIFICATION: No employer bilateral funds modeled. No public data found for a cinema-specific bilateral fund for impiegati/tecnici in production companies.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Confirm whether a sector bilateral fund applies and pass it as a bilateral fund event.

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
    SIMPLIFICATION: Apprenticeship provisions not modeled (primary CCNL text not publicly available). Field left empty.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-07-23 | [↗](https://www.lavoro-economia.it/contratti-collettivi/ccnl.aspx?c=153) |

??? note "Coverage notes"
    Salary model: conglobated (paga base unica, nessuna contingenza/EDR separata). Source: lavoro-economia.it c=153 (CNEL G111), tabella Jul 2026.
    
    Hourly divisor 173 (industria standard, confirmed from lavoro-economia.it). Daily divisor: 26.
    
    Additional months: 14 (tredicesima + quattordicesima). UILCOM informativa 24/07/2025.
    
    Seniority: 5 scatti biennali (cadence_months=24, maximum_count=5). Amounts from published table Jul 2026.
    
    Salary periods: 5 tranches — Jan 2025 (+45 at L4), Jan 2026 (+45 at L4), Jul 2026 (+90, published anchor), Jul 2027 (+90), Jan 2028 (+90). Source: quotidianopiu.it + lavoro-economia.it.
    
    Non-Jul-2026 salary values computed parametrically: each level scaled by the L4 ratio at each tranche. Published Jul 2026 values are the direct source; others are derived.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/cinema-audiovisivi-industria.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/cinema-audiovisivi-industria.py"
```
