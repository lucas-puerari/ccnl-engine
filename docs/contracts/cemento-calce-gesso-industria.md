# CCNL Cemento, Calce e Gesso — Industria (Federbeton)

| | |
|---|---|
| **CNEL code** | `F032` |
| **Sector** | industria del cemento calce e gesso |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~25k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🟢 Verified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federbeton
    - FILLEA-CGIL
    - FILCA-CISL
    - FENEAL-UIL

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
| **Latest salary tranche** | 2027-10-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `AD3` | Area Direttiva 3 — Quadro con responsabilita direttive superiori (Art. 2095 c.c.) | € 2,710.23 | 2027-10-01 |
| `AD2` | Area Direttiva 2 — Lavoratori con funzioni direttive di secondo livello | € 2,426.28 | 2027-10-01 |
| `AD1` | Area Direttiva 1 — Lavoratori con funzioni direttive di primo livello | € 2,219.77 | 2027-10-01 |
| `AC3` | Area Concettuale 3 — Lavoratori con responsabilita di coordinamento complesso | € 2,103.67 | 2027-10-01 |
| `AC2` | Area Concettuale 2 — Lavoratori con elevata autonomia e responsabilita funzionale | € 2,026.26 | 2027-10-01 |
| `AC1` | Area Concettuale 1 — Lavoratori con funzioni di natura concettuale e autonomia decisionale | € 1,922.99 | 2027-10-01 |
| `AS3` | Area Specialistica 3 — Lavoratori altamente specializzati o con funzioni di riferimento | € 1,806.82 | 2027-10-01 |
| `AS2` | Area Specialistica 2 — Lavoratori specializzati con autonomia operativa | € 1,729.41 | 2027-10-01 |
| `AS1` | Area Specialistica 1 — Lavoratori specializzati con competenze tecniche | € 1,664.89 | 2027-10-01 |
| `AQ2` | Area Qualificata 2 — Lavoratori con qualifica professionale specializzata | € 1,561.62 | 2027-10-01 |
| `AQ1` | Area Qualificata 1 — Lavoratori con qualifica professionale di base | € 1,497.04 | 2027-10-01 |
| `AE1` | Area Esecutiva 1 — Lavoratori addetti a mansioni esecutive semplici | € 1,299.90 | 2027-10-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `AE1` | € 7.70 |
| `AQ1` | € 8.30 |
| `AQ2` | € 8.50 |
| `AS1` | € 8.90 |
| `AS2` | € 9.10 |
| `AS3` | € 9.30 |
| `AC1` | € 9.80 |
| `AC2` | € 10.70 |
| `AC3` | € 11.00 |
| `AD1` | € 11.50 |
| `AD2` | € 13.00 |
| `AD3` | € 14.80 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `AQ2`, `AS1`, `AS2`, `AS3`, `AC1`, `AC2`, `AC3`, `AD1`, `AD2`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "cemento-calce-gesso-industria/apprenticeship_full_pay_passthrough · base_salary · impact yes · open"
    APPRENTICESHIP (Art. 25): under_classification model — period 1 at 2 levels below target, period 2 at 1 level below target, period 3 (where applicable) at target level pay. The engine under_classification schema requires a fixed pay_level_code per period for all destination levels; expressing the level-relative structure requires per-destination-level entries with 9 separate apprenticeship objects. Modelled as 100% passthrough for all eligible levels (AQ2 and above); correct for permanent workers.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Model the Art. 25 under-classification periods per destination level.

!!! warning "cemento-calce-gesso-industria/apprentice_seniority · seniority · impact unknown · open"
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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-05-08 | [↗](https://www.fenealuil.it/wp-content/uploads/2026/02/CEMENTO_STAMPA-CCNL_2025-NO-UGL.pdf) |

??? note "Coverage notes"
    CCNL signed 08/05/2025, valid 01/01/2025-31/12/2027 (Federbeton+FILLEA-CGIL+FILCA-CISL+FENEAL-UIL). Source: official PDF 248 pages.
    
    SPLIT model: paga base (Art. 44) + contingenza frozen Nov 1991 (Art. 45) + EDR 10.33 EUR all levels. Three separate components; only paga base changes at each tranche.
    
    PRE-RENEWAL RECOVERY: a +120 EUR recovery (at param 140 reference) was granted in Dec 2024, prior to the May 2025 renewal. The 31/12/2024 column already includes this recovery. Engine models from this base forward.
    
    TRANCHE AMOUNTS (Art. 44): increases proportional to param indices. Reference param=140 (AS3): +60 EUR (01/10/2025), +60 EUR (01/10/2026), +55 EUR (01/10/2027). All-level amounts confirmed from the PDF.
    
    AREA DIRETTIVA 3 (AD3, Quadro): indennita di funzione +41.32 EUR/month (Art. 15). Modelled as INDENNITA_FUNZIONE fixed allowance, months_per_year=13.
    
    AREA ESECUTIVA 1 (AE1): superminimum collettivo di gruppo +7.75 EUR/month treated as paga base for contractual purposes (Art. 44). Added to paga base values in this file.
    
    SENIORITY (Art. 48): 5 biennali (24-month) scatti. Per-level EUR amounts confirmed from Art. 48 of the PDF.
    
    ADDITIONAL MONTHS: 13 (tredicesima only).
    
    HOURLY DIVISOR: 175.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/cemento-calce-gesso-industria.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/cemento-calce-gesso-industria.py"
```
