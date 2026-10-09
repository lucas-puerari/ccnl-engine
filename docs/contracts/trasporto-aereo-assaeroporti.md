# CCNL Trasporto Aereo — Gestori Aeroportuali

| | |
|---|---|
| **CNEL code** | `I810` |
| **Sector** | trasporto aereo |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-06-04 |
| **Workers (est.)** | ~40k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Assaeroporti — Associazione Italiana Gestori Aeroporti
    - FILT-CGIL — Federazione Italiana Lavoratori Trasporti
    - FIT-CISL — Federazione Italiana Trasporti
    - Uiltrasporti
    - UGL Trasporto Aereo

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
| **Last renewal** | 2025-06-04 |
| **Last verified** | — |
| **Latest salary tranche** | 2027-07-01 |

### Semplificazioni note

4 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1S` | Livello 1S — Quadri | € 2,174.53 | 2027-07-01 |
| `1` | Livello 1 | € 1,973.18 | 2027-07-01 |
| `2A` | Livello 2A | € 1,804.05 | 2027-07-01 |
| `2B` | Livello 2B | € 1,691.30 | 2027-07-01 |
| `3` | Livello 3 | € 1,570.49 | 2027-07-01 |
| `4` | Livello 4 | € 1,417.47 | 2027-07-01 |
| `5` | Livello 5 | € 1,336.93 | 2027-07-01 |
| `6` | Livello 6 | € 1,256.39 | 2027-07-01 |
| `7` | Livello 7 | € 1,127.53 | 2027-07-01 |
| `8` | Livello 8 | € 1,014.78 | 2027-07-01 |
| `9` | Livello 9 | € 805.38 | 2027-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `1S` | € 37.29 |
| `1` | € 34.45 |
| `2A` | € 32.18 |
| `2B` | € 30.47 |
| `3` | € 29.33 |
| `4` | € 27.42 |
| `5` | € 26.65 |
| `6` | € 25.31 |
| `7` | € 24.22 |
| `8` | € 22.67 |
| `9` | € 0.00 |

## Apprenticeship

**professionalizzante_18m** (type: `percentage`)  
Destination levels: `9`, `8`, `7`, `6`, `5`, `4`, `3`, `2B`, `2A`, `1`  
percentage: 0.90

**professionalizzante_24m** (type: `percentage`)  
Destination levels: `9`, `8`, `7`, `6`, `5`, `4`, `3`, `2B`, `2A`, `1`  
percentage: 0.95

**professionalizzante_36m** (type: `percentage`)  
Destination levels: `9`, `8`, `7`, `6`, `5`, `4`, `3`, `2B`, `2A`, `1`  
percentage: 0.95

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "trasporto-aereo-assaeroporti/level_9_seniority_zero · seniority · impact unknown · open"
    LEVEL 9 SENIORITY. Art. G23 seniority table lists amounts for levels 1S through 8 only. Level 9 is absent. Modelled as 0.00; not confirmed whether intentional exclusion or typographical omission.

    **Applies when:** `seniority` applies; level in 9.

    **Remediation:** Confirm whether level 9 is excluded from Art. G23 seniority increments.

!!! warning "trasporto-aereo-assaeroporti/role_conditional_allowances · base_salary · impact yes · open"
    SUPPLEMENTARY ALLOWANCES. Role-conditional allowances (turno, campo, maneggio denaro, DPI) and the una tantum of EUR 500 (Art. G20, October 2025) are not modelled. All are attendance- or role-conditional or one-time payments.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the role- and attendance-conditional allowances as roles, and the una tantum as a una tantum payment.

!!! warning "trasporto-aereo-assaeroporti/art_g6_reclassification · base_salary · impact unknown · open"
    ART. G6 RECLASSIFICATION. A supplementary agreement of 23 March 2026 reportedly amended Art. G6 (professional classification). The amendment text was not retrieved; its effect on level codes and salary tables for as_of dates from 2026-03-01 onward is unverified. Hourly divisor taken from Art. G28 text; no official hourly-rate column available in the source for back-calculation cross-check.

    **Applies when:** `base_salary` applies; from 2026-03-01.

    **Remediation:** Retrieve the 23 March 2026 agreement and apply its effect on levels and salary tables.

!!! warning "trasporto-aereo-assaeroporti/apprentice_seniority · seniority · impact unknown · open"
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
| — | — | 2025-06-04 | [↗](https://assaeroporti.com/wp-content/uploads/2025/06/CCNL-Parte-Specifica-versione-accessibile.pdf) |
| — | — | 2025-06-04 | [↗](https://assaeroporti.com/ccnl-del-trasporto-aereo/) |

??? note "Coverage notes"
    APPRENTICESHIP TRACKS. Art. G14 §16 defines three professionalising tracks (18m, 24m, 36m) with percentage tables by semester. All three are implemented. Art. G14 does not restrict which track applies per destination level; employers and workers choose the duration per PFI. When calling compute() with Apprentice for any covered level, set Apprentice.track to 'professionalizzante_18m', 'professionalizzante_24m', or 'professionalizzante_36m'. Source: CCNL Parte Specifica Gestori Aeroportuali (assaeroporti.com, 04/06/2025), Art. G14 §16 table.
    
    EDR APPRENTICESHIP EXEMPTION. Art. G14 §16 limits the apprenticeship percentage to 'minimi tabellari in vigore, indennità di contingenza'. EDR (Art. G22) is not listed and is therefore paid at full value for apprentices. Modelled via apprenticeship_pct_relevant=false on all EDR allowances.
    
    SENIORITY CAP: maximum_count=8, as per 2025 rinnovo (signed 04/06/2025, FILT-CGIL comunicato) which recognized the 8th scatto from 01/01/2026 for all workers with ≥16 years seniority. Pre-1993 employees with 16+ years already captured under this rule. Engine has no hire-date input; this is a structural limitation — maximum_count=8 is the correct model for the vast majority of new hires.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/trasporto-aereo-assaeroporti.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/trasporto-aereo-assaeroporti.py"
```
