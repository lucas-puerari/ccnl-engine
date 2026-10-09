# CCNL Recapito Corrispondenza (FISE-ARE)

| | |
|---|---|
| **CNEL code** | `K711` |
| **Sector** | Recapito corrispondenza e spedizioni |
| **Tax sector** | `terziario` |
| **Last renewal** | 2023-11-14 |
| **Workers (est.)** | ~1k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - FISE-ARE
    - SLC-CGIL
    - SLP-CISL
    - UILPOSTE-UIL

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
| **Limits of this contract** | — |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2023-11-14 |
| **Last verified** | — |
| **Latest salary tranche** | 2026-06-01 |

### Semplificazioni note

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1` | Livello 1 | € 2,224.51 | 2026-06-01 |
| `2` | Livello 2 | € 2,006.77 | 2026-06-01 |
| `3S` | Livello 3 Super | € 1,791.30 | 2026-06-01 |
| `3` | Livello 3 | € 1,687.29 | 2026-06-01 |
| `4` | Livello 4 | € 1,600.99 | 2026-06-01 |
| `5S` | Livello 5 Super | € 1,489.70 | 2026-06-01 |
| `5` | Livello 5 | € 1,446.71 | 2026-06-01 |
| `6` | Livello 6 | € 1,359.91 | 2026-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 36.15 |
| `2` | € 33.05 |
| `3S` | € 32.54 |
| `3` | € 31.50 |
| `4` | € 30.47 |
| `5S` | € 29.70 |
| `5` | € 29.44 |
| `6` | € 28.41 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

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

### Without monetary impact

!!! note ""
    SIMPLIFICATION: apprenticeship type and percentages not publicly available from any free source (paywalled). Modelled as apprenticeship: [] with no rules defined.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-11-14 | [↗](https://www.redigo.info/2023/11/20/ccnl-recapito-corrispondenza-fise-nuove-tabelle-dal-rinnovo-di-novembre-2023/) |
| — | — | 2023-11-14 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=26) |

??? note "Coverage notes"
    CCNL Recapito Corrispondenza (FISE-ARE) signed 14/11/2023 by FISE-ARE, SLC-CGIL, SLP-CISL, UILPOSTE-UIL.
    
    Salary model: split — base_salary = paga tabellare + contingenza combined (rolled); EDR=10.33 as fixed_allowance. GOAL.md CCNL research confirms this structure from ilccnl.it cross-check.
    
    8 levels (1 highest, 6 lowest): 1, 2, 3S, 3, 4, 5S, 5, 6. 4 tranches: 01/02/2024, 01/09/2024, 01/07/2025, 01/06/2026. Values from redigo.info (14/11/2023 renewal article).
    
    Hourly divisor 173 confirmed from ilccnl.it cross-check (4 levels). Back-calc: 2224.51+10.33=2234.84 / 173 = 12.92 EUR/h for level 1 at Jun 2026.
    
    Additional months: 14 (tredicesima + quattordicesima) confirmed from GOAL.md research.
    
    Seniority: biennale (cadence=24), maximum 8 scatti. Per-level amounts from lavoro-economia.it (c=26), confirmed against kitech at Jun 2026 (L1=36.15, L2=33.05, L3S=32.54, L3=31.50, L4=30.47, L5S=29.70, L5=29.44, L6=28.41).
    
    Levels 1Q (Quadri), Operatore A (1650), Operatore B (1540) exist from Jun 2026 only — no prior tranche history. Not modelled to avoid open-ended periods with single-tranche data.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/recapito-corrispondenza-fise.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/recapito-corrispondenza-fise.py"
```
