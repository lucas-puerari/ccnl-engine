# CCNL Consorzi Agrari (ASSOCAP-FLAI-FAI-UILA)

| | |
|---|---|
| **CNEL code** | `A141` |
| **Sector** | Agricoltura |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2023-12-12 |
| **Workers (est.)** | ~2k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ASSOCAP
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
| **Limits of this contract** | base_salary, health_fund_employer |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2023-12-12 |
| **Last verified** | — |
| **Latest salary tranche** | 2026-01-01 |

### Semplificazioni note

4 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro | € 2,212.99 | 2026-01-01 |
| `1` | Livello 1 | € 2,212.99 | 2026-01-01 |
| `2` | Livello 2 | € 2,002.97 | 2026-01-01 |
| `3S` | Livello 3 Super | € 1,710.74 | 2026-01-01 |
| `3` | Livello 3 | € 1,574.42 | 2026-01-01 |
| `4S` | Livello 4 Super | € 1,468.82 | 2026-01-01 |
| `4` | Livello 4 | € 1,375.68 | 2026-01-01 |
| `5` | Livello 5 | € 1,233.03 | 2026-01-01 |
| `6` | Livello 6 | € 1,070.87 | 2026-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 53.20 |
| `1` | € 53.20 |
| `2` | € 50.61 |
| `3S` | € 47.00 |
| `3` | € 45.19 |
| `4S` | € 44.16 |
| `4` | € 43.12 |
| `5` | € 41.32 |
| `6` | € 39.51 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "consorzi-agrari-assocap/tranche_2027_01_missing · base_salary · impact yes · open"
    SIMPLIFICATION: Jan 2027 tranche not yet published per-level; not modeled.

    **Applies when:** `base_salary` applies; from 2027-01-01.

    **Remediation:** Add the January 2027 tranche per level once the official table is published.

!!! warning "consorzi-agrari-assocap/cashier_allowance_missing · base_salary · impact yes · open"
    SIMPLIFICATION: Indennita di cassa (EUR 55.00/month, cashiers only) not modeled — applies only to a subset of workers.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the 55 EUR/month indennita di cassa as a role-gated allowance for cashiers.

!!! warning "consorzi-agrari-assocap/filcoop_health_fund_missing · health_fund_employer · impact yes · open"
    SIMPLIFICATION: FILCOOP SANITARIO bilateral health fund not modeled.

    **Applies when:** `health_fund_employer` applies.

    **Remediation:** Model the FILCOOP SANITARIO contributions once health funds enter the engine input.

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
    SIMPLIFICATION: Jan 2024 tranche (first of four per 12/12/2023 accord) not modeled; no per-level table found in public sources. Engine returns no result for as_of before 2025-01-01.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-12-12 | [↗](https://www.wolterskluwer.it/) |
| — | — | 2023-12-12 | [↗](https://www.kitech.it/) |
| — | — | 2023-12-12 | [↗](https://www.flai.it/) |
| — | — | 2023-12-12 | [↗](https://ilccnl.it/contratto/ccnl/consorzi-agrari) |

??? note "Coverage notes"
    Salary model: split (paga base + contingenza) confirmed from ilccnl.it tables showing separate paga base, contingenza, and terzo elemento (0.00) columns.
    
    Indennita di funzione modeled as INDENNITA_DI_FUNZIONE fixed_allowance for levels Q (335.50), 1 (192.50), 2 (115.50 EUR/month). Source: kitech.
    
    Seniority: 5 biennial scatti per Art. 34 CCNL (FLAI-CGIL PDF primary source). Scatto amounts from kitech Jan 2026 table; applied from 2025-01-01 — no Jan 2025 per-level table found in public sources.
    
    Apprenticeship: Art. 16 delegates rules to Annex E, not publicly available. layer_2 = out_of_scope.
    
    Headcount: ~2,133 workers (ASSOCAP, CNEL archive 2023).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/consorzi-agrari-assocap.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/consorzi-agrari-assocap.py"
```
