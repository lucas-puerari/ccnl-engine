# CCNL Occhiali e Occhialeria — Industria (ANFAO)

| | |
|---|---|
| **CNEL code** | `D271` |
| **Sector** | industria occhialeria e ottica |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~20k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🟢 Verified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANFAO
    - Filctem-CGIL
    - Femca-CISL
    - UilTEC-UIL

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
| **Latest salary tranche** | 2028-11-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro — Lavoratori con responsabilita di direzione e coordinamento (Art. 2095 c.c.) | € 2,680.72 | 2028-11-01 |
| `6` | Livello 6 — Lavoratori con autonomia decisionale e competenze trasversali elevate | € 2,670.80 | 2028-11-01 |
| `5S` | Livello 5 Super — Lavoratori con funzioni tecniche o di supervisione avanzata | € 2,540.00 | 2028-11-01 |
| `5` | Livello 5 — Lavoratori con funzioni di controllo o alta specializzazione | € 2,453.48 | 2028-11-01 |
| `4S` | Livello 4 Super — Lavoratori con elevata specializzazione o coordinamento | € 2,280.32 | 2028-11-01 |
| `4` | Livello 4 — Lavoratori polivalenti o con responsabilita tecnica | € 2,187.96 | 2028-11-01 |
| `3S` | Livello 3 Super — Lavoratori specializzati di livello superiore | € 2,125.83 | 2028-11-01 |
| `3` | Livello 3 — Lavoratori specializzati con autonomia operativa | € 2,082.62 | 2028-11-01 |
| `2` | Livello 2 — Lavoratori qualificati con conoscenze specifiche | € 1,966.32 | 2028-11-01 |
| `1` | Livello 1 — Lavoratori addetti a mansioni semplici e ripetitive | € 1,712.04 | 2028-11-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 6.84 |
| `2` | € 7.36 |
| `3` | € 7.80 |
| `3S` | € 7.80 |
| `4` | € 8.26 |
| `4S` | € 8.26 |
| `5` | € 9.76 |
| `5S` | € 9.76 |
| `6` | € 11.65 |
| `Q` | € 11.65 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `1`, `2`, `3`, `3S`, `4`, `4S`, `5`, `5S`, `6`, `Q`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "occhiali-occhialeria-industria/apprenticeship_full_pay · base_salary · impact yes · open"
    APPRENTICESHIP: 2026 rinnovo (signed 30/01/2026) explicitly 'abroga la ripartizione in percentuale in relazione agli step professionali' (edotto.com). Pre-2026 CCNL used a percentage system. Post-2026 replacement type is not confirmed from a D271 primary source — the cognate piccola industria (ccnlportatili.it) uses sotto-inquadramento (2 levels below for first 12m, 1 level below for next 12m, then destination). Modelled as 100% passthrough for all levels pending primary source confirmation; this is a conservative over-estimate for the 2026-2028 period.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Model the post-2026 under-classification apprenticeship from a D271 primary source.

!!! warning "occhiali-occhialeria-industria/apprentice_seniority · seniority · impact unknown · open"
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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-12-04 | [↗](https://italpaghe.ilccnl.it/ccnl/occhiali---industria/occhiali---industria/tabelleretributive) |
| — | — | 2026-01-30 | [↗](https://www.cisl.it/ccnl-occhiali-sindacati-sottoscritta-ipotesi-accordo-per-rinnovo-contratto-204e-laumento-del-complessivo-triennio-2026-2028/) |

??? note "Coverage notes"
    CCNL signed 04/12/2023 valid 01/01/2023-31/12/2025; renewed 30/01/2026 valid 01/01/2026-31/12/2028 (ANFAO+Filctem-CGIL+Femca-CISL+UilTEC-UIL).
    
    CONGLOBATED (since 01/01/2009): contingenza and EDR are inglobated into the tabular minimum. Single base_salary column per level; no separate contingenza allowance.
    
    Level Q (Quadro): indennita di funzione +82.63 EUR/month on top of the tabular minimum (all tranches). Modelled as INDENNITA_FUNZIONE fixed allowance, months_per_year=13.
    
    HOURLY DIVISOR: 173 (standard 40h/week). Shift workers on 6x6 turns use divisor 156; engine models the 173 case uniformly.
    
    SENIORITY: 5 biennali (24-month) scatti. Per-level amounts (EUR): 1=6.84, 2=7.36, 3=3S=7.80, 4=4S=8.26, 5=5S=9.76, 6=Q=11.65.
    
    LEVEL 1 sub-level: the CCNL provides automatic advancement from entry sub-level (L1 ingresso) to L1 standard after 6 months. The file models only the post-advance minimum throughout, which is the relevant value for permanent workers and for workers beyond their 6th month. The entry sub-level undervaluation during the first 6 months is a deliberate structural simplification.
    
    TRANCHES 01/10/2026 through 01/11/2028: L4 reference increments confirmed from primary source (CISL communique CCNL occhialeria 30/01/2026: +30, +50, +45, +20 EUR at L4). All-level amounts derived via the parametric ratio matrix from confirmed 01/03/2026 per-level deltas. The CCNL occhialeria uses a declared parametric system; parametric derivation is contractually consistent.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/occhiali-occhialeria-industria.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/occhiali-occhialeria-industria.py"
```
