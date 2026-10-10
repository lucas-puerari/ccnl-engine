# CCNL Organizzazioni Allevatori, Consorzi ed Enti Zootecnici (AIA-FLAI-FAI-UILA)

| | |
|---|---|
| **CNEL code** | `A221` |
| **Sector** | Agricoltura |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2024-12-12 |
| **Workers (est.)** | ~2k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - AIA
    - FLAI-CGIL
    - FAI-CISL
    - UILA-UIL
    - Confederdia

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
| **Limits of this contract** | base_salary |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2024-12-12 |
| **Last verified** | — |
| **Latest salary tranche** | 2025-09-01 |

### Semplificazioni note

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1/2` | Area 1 Livello 2 (Quadri) | € 2,392.51 | 2025-09-01 |
| `1/3` | Area 1 Livello 3 | € 2,288.35 | 2025-09-01 |
| `1/4` | Area 1 Livello 4 | € 2,183.71 | 2025-09-01 |
| `1/5` | Area 1 Livello 5 | € 2,105.96 | 2025-09-01 |
| `2/1` | Area 2 Livello 1 | € 2,028.26 | 2025-09-01 |
| `2/2` | Area 2 Livello 2 | € 1,974.23 | 2025-09-01 |
| `2/3` | Area 2 Livello 3 | € 1,895.67 | 2025-09-01 |
| `2/4A` | Area 2 Livello 4A | € 1,791.72 | 2025-09-01 |
| `2/4B` | Area 2 Livello 4B | € 1,757.61 | 2025-09-01 |
| `2/5` | Area 2 Livello 5 | € 1,737.68 | 2025-09-01 |
| `2/6` | Area 2 Livello 6 | € 1,659.20 | 2025-09-01 |
| `3/1` | Area 3 Livello 1 | € 1,500.21 | 2025-09-01 |
| `3/2` | Area 3 Livello 2 | € 1,372.00 | 2025-09-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `1/2` | € 53.10 |
| `1/3` | € 50.36 |
| `1/4` | € 48.17 |
| `1/5` | € 45.97 |
| `2/1` | € 44.34 |
| `2/2` | € 43.24 |
| `2/3` | € 41.05 |
| `2/4A` | € 38.87 |
| `2/4B` | € 37.77 |
| `2/5` | € 37.22 |
| `2/6` | € 35.58 |
| `3/1` | € 31.74 |
| `3/2` | € 29.00 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "organizzazioni-allevatori-aia/third_tranche_sep_2026 · base_salary · impact yes · open"
    SIMPLIFICATION: Third tranche (Sep 2026) not modeled; per-level amounts not yet published in primary sources.

    **Applies when:** `base_salary` applies; from 2026-09-01.

    **Remediation:** Add the September 2026 tranche once the per-level amounts are published.

!!! warning "organizzazioni-allevatori-aia/quadri_function_allowance · base_salary · impact yes · open"
    SIMPLIFICATION: Indennita di funzione for area 1 Quadri (min 13% monthly) not modeled — variable floor amount, not expressible as fixed allowance.

    **Applies when:** `base_salary` applies; level in 1/2, 1/3, 1/4, 1/5.

    **Remediation:** Model the area 1 Quadri function allowance (minimum 13%).

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

!!! warning "inps_minimum_base_exempt_category · inps_employer · impact unknown · open"
    D.L. 463/1983 art. 7 c. 5 keeps the operai agricoli out of the 9.50% minimum daily base, and the run applies no minimum to them. Tabella A of INPS circ. 6/2026 still lists 51.70 for the operai agricoli, 'non soggetto all'adeguamento' of art. 7 c. 1; no source found says whether it is a floor of their contribution base. A base below it may understate the contributions.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Source the role of the 51.70 of the operai agricoli (INPS circ. 43/2026 on the agricultural contributions, or the minimum daily wages of art. 1 L. 389/1989), then apply it as their minimum or record that none applies.

### Without monetary impact

!!! note ""
    SIMPLIFICATION: First tranche (Jan 2025) from Dec 2024 renewal not modeled; no per-level table confirmed for that date. Engine returns no result for as_of before 2025-09-01.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-12-12 | [↗](https://www.wolterskluwer.it/) |
| — | — | 2024-12-12 | [↗](https://www.kitech.it/) |
| — | — | 2023-11-14 | [↗](https://www.confederdia.it/2023/11/30/ipotesi-di-accordo-rinnovo-ccnl-dipendenti-dalle-organizzazioni-degli-allevatori-consorzi-ed-enti-zootecnici/) |
| — | — | 2024-12-12 | [↗](https://www.lavoro-economia.it/) |

??? note "Coverage notes"
    Salary model: conglobated. Wolters Kluwer tables show Minimo = Totale with no separate contingenza column. fixed_allowances = [] for all levels.
    
    Hourly divisor 164.67 = 38h/week x 52 / 12, confirmed from Art. 11 CCNL (FLAI PDF). Tredicesima + quattordicesima = 14 additional months (Art. 17 CCNL).
    
    Seniority: 10 biennial scatti per Art. 18 CCNL (FLAI PDF + Confederdia confirmed). Cadence biennale (24 months). Amounts effective 2025-01-01 per Dec 2024 economic renewal.
    
    Indennita di funzione for Quadri (area 1): at least 13% of monthly salary per Art. 19 CCNL. Not modeled: percentage-based floor, not a fixed amount.
    
    Apprenticeship: Annex 4 (profili formativi) referenced but not publicly parsed. layer_2 = out_of_scope.
    
    Headcount: ~1,822 workers (AIA, CNEL archive 2023).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/organizzazioni-allevatori-aia.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/organizzazioni-allevatori-aia.py"
```
