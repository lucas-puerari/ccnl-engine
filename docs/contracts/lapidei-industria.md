# CCNL Lapidei — Industria (Confindustria Marmomacchine/ANEPLA)

| | |
|---|---|
| **CNEL code** | `F041` |
| **Sector** | industria lapidea e delle cave |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~18k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🟢 Verified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Confindustria Marmomacchine
    - ANEPLA
    - FENEAL-UIL
    - FILCA-CISL
    - FILLEA-CGIL

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
| **Latest salary tranche** | 2027-07-01 |

### Semplificazioni note

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `AS` | Livello AS — A Super: lavoratori con responsabilita direttive di alto livello | € 2,562.44 | 2027-07-01 |
| `A` | Livello A — Lavoratori con elevata autonomia e responsabilita gestionale | € 2,357.34 | 2027-07-01 |
| `B` | Livello B — Lavoratori altamente specializzati con coordinamento operativo | € 1,921.76 | 2027-07-01 |
| `CS` | Livello CS — C Super: lavoratori specializzati con responsabilita di processo | € 1,845.14 | 2027-07-01 |
| `C` | Livello C — Livello di riferimento parametrico (lavoratori con qualifiche tecniche) | € 1,742.64 | 2027-07-01 |
| `D` | Livello D — Lavoratori specializzati con autonomia operativa | € 1,642.89 | 2027-07-01 |
| `E` | Livello E — Lavoratori qualificati con mansioni esecutive | € 1,514.52 | 2027-07-01 |
| `F` | Livello F — Lavoratori addetti a mansioni semplici (+ superminimum collettivo 7.75 EUR) | € 1,290.23 | 2027-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `F` | € 6.65 |
| `E` | € 7.69 |
| `D` | € 8.31 |
| `C` | € 8.82 |
| `CS` | € 9.45 |
| `B` | € 9.80 |
| `A` | € 11.97 |
| `AS` | € 13.01 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `F`, `E`, `D`, `C`, `CS`, `B`, `A`, `AS`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "lapidei-industria/apprenticeship_passthrough · base_salary · impact unknown · open"
    APPRENTICESHIP: 2022 CCNL Art. 3d changed system from sotto-inquadramento to percentage ('calcolate in percentuale...come da allegata tabella'). Pre-2022 system confirmed from full CCNL 2008 text (integrating Accordo 15/03/2006): 2 levels below destination for first half of apprenticeship, 1 level below for second half, no seniority increments accrued. Post-2022 percentage values from scanned allegata tabella not extractable (OCR-confirmed: image-only PDF). 2025-2028 rinnovo (12-page OCR) does not modify apprenticeship. Modelled as 1.00 passthrough pending actual 2022+ percentage values.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Extract the post-2022 percentage table and model the percentage track.

!!! warning "lapidei-industria/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "apprenticeship_pct_undeclared_components · base_salary · impact unknown · open"
    A percentage apprenticeship reduces every fixed allowance whose apprenticeship_pct_relevant flag the data leaves at its default, together with the base salary. Whether the CCNL applies the percentage to that allowance (an EDR, a contingenza, a function allowance) was not sourced. The run is affected when such an allowance is in the apprentice's pay.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source, for each CCNL, the elements the apprenticeship percentage applies to and set apprenticeship_pct_relevant on every allowance; the limitation then no longer applies to its runs.

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
    PRE-31/12/2022 HISTORY: the 2022-2025 CCNL is retroactively valid from 01/04/2022. Values for April 2022 through November 2022 are not modelled (data not retrieved from public sources). Engine history starts at 31/12/2022.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2022-11-24 | [↗](https://www.consulenza.it/Contenuti/Scadenziario/Scadenza/19851/lapidei-industria) |
| — | — | 2025-07-15 | [↗](https://www.cdltorino.it/ccnl-lapidei-industria-con-ladeguamento-ipca-in-arrivo-nuovi-minimi/) |

??? note "Coverage notes"
    CCNL 2022-2025 signed 24/11/2022 (valid 01/04/2022-31/03/2025). CCNL 2025-2028 signed 15/07/2025 (valid 01/04/2025-31/03/2028). Signatories: Confindustria Marmomacchine+ANEPLA+FENEAL-UIL+FILCA-CISL+FILLEA-CGIL.
    
    SPLIT model: paga base + contingenza frozen Nov 1991 + EDR 10.33 EUR. Paga base changes at each tranche; contingenza and EDR modelled as fixed_allowances.
    
    2022-2025 paga base tranches: 31/12/2022 (base), 01/01/2023 (+40 EUR at C), 01/01/2024 (+39 EUR at C), 01/01/2025 (+44 EUR at C). Confirmed from consulenza.it per-level tables.
    
    2025-2028 totals confirmed from cdltorino.it: 01/07/2025, 01/07/2026, 01/07/2027 (+80 EUR per tranche at C reference). Paga base derived by subtracting frozen contingenza and EDR from confirmed totals.
    
    LEVEL F superminimum: +7.75 EUR/month collective superminimum treated as paga base for contractual purposes. Added to paga base values in this file.
    
    HOURLY DIVISOR: 174. Daily divisor: 25.
    
    ADDITIONAL MONTHS: 13 (tredicesima only).
    
    SENIORITY: 5 biennali (24-month) scatti. Per-level EUR amounts: F=6.65, E=7.69, D=8.31, C=8.82, CS=9.45, B=9.80, A=11.97, AS=13.01. Confirmed from ilccnl.it.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/lapidei-industria.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/lapidei-industria.py"
```
