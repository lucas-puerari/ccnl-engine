# CCNL per i dipendenti degli studi e delle attività professionali (Confprofessioni)

| | |
|---|---|
| **CNEL code** | `H442` |
| **Sector** | terziario |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~350k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Confprofessioni
    - Filcams-CGIL
    - Fisascat-CISL
    - Uiltucs-UIL

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
| **Latest salary tranche** | 2026-12-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Manager (Quadro) — staff with managerial functions (Art. 2095 c.c., L. 190/1985) | € 2,436.76 | 2026-12-01 |
| `1` | 1st Level — staff with directive functions or highly specialised technical role | € 2,156.38 | 2026-12-01 |
| `2` | 2nd Level — senior concept-grade staff / highly specialised technicians | € 1,878.26 | 2026-12-01 |
| `3S` | 3rd Level Super — senior concept-grade staff with specialised expertise | € 1,742.20 | 2026-12-01 |
| `3` | 3rd Level — concept-grade staff with technical or administrative expertise | € 1,726.37 | 2026-12-01 |
| `4S` | 4th Level Super — qualified staff with higher-grade duties | € 1,674.10 | 2026-12-01 |
| `4` | 4th Level — qualified clerical staff | € 1,614.12 | 2026-12-01 |
| `5` | 5th Level — clerical staff performing routine tasks | € 1,502.19 | 2026-12-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 30.00 |
| `1` | € 26.00 |
| `2` | € 23.00 |
| `3S` | € 22.00 |
| `3` | € 22.00 |
| `4S` | € 20.00 |
| `4` | € 20.00 |
| `5` | € 20.00 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `4`, `4S`, `3`, `3S`, `2`, `1`  
percentage: 0.93

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "studi-professionali-confprofessioni/uniform_apprenticeship_percentages · base_salary · impact unknown · open"
    APPRENTICESHIP percentage (Allegato B Table 3 CCNL 2024): 70% months 1-12, 85% months 13-24, 93% from month 25, applied to all eligible destinations (4, 4S, 3, 3S, 2, 1); level V is excluded from professional apprenticeship (Art. 30B) and Quadri are not a destination. The same percentage table is assumed for all destination levels.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Confirm that Allegato B Table 3 applies to every destination level.

!!! warning "studi-professionali-confprofessioni/apprentice_seniority · seniority · impact unknown · open"
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
    The run reads a tax ruleset marked provisional: the sources of its year are not published yet (budget law of the year; regional and municipal surtax resolutions), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

!!! warning "provisional_inps_ruleset · inps_employer · impact unknown · open"
    The run reads an INPS ruleset marked provisional: the INPS circulars of its year are not published yet, so the rates, the massimale and the minimale (and the hourly contributions of domestic work) are those of the year before, carried over. The indexed amounts change every January: the carried-over values understate them.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional INPS ruleset of the year with the values of the INPS circulars of the year, drop its provisional flag, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-02-16 | [↗](https://confprofessioni.eu/wp-content/uploads/2025/11/CCNL-Studi-2024-integrale-definitivo.pdf) |
| — | — | 2024-02-16 | [↗](https://www.confprofessioni.eu/wp-content/uploads/2026/07/00274046_CCNL_Studi_Professionali_2026.04.10_completo.pdf) |

??? note "Coverage notes"
    CONGLOBATED MINIMUMS: the minimum tabellare includes contingenza (up to 01/05/1992) and EDR (Interconfederal Agreement 31/07/1992), merged under CCNL 10/12/1992 and reaffirmed by Art. 138 CCNL 2024. fixed_allowances is empty for all levels.
    
    HOURLY DIVISOR: 170. Primary source: Art. 45 and Art. 137 CCNL 2024 ('divisore convenzionale orario fissato in 170').
    
    TRANCHES: four tranches — 01/03/2024, 01/10/2024, 01/10/2025, 01/12/2026. Source: Art. 139-140 and salary tables CCNL 2024 (confprofessioni.eu, complete version April 2026).
    
    ADDITIONAL MONTHS: 14 (tredicesima Art. 142 + quattordicesima Art. 143 CCNL 2024).
    
    SENIORITY INCREMENTS: triennial (36-month cadence), max 8 increments. Fixed amounts per Art. 134 CCNL 2024 in force from 01/10/2011: Q=30, 1=26, 2=23, 3S=22, 3=22, 4S=20, 4=20, 5=20.
    
    ENAC (Art. 141 CCNL 2024): EUR 42.35 (level 1), EUR 102.53 (level 2), EUR 110.40 (level 3S) per month, payable only to workers already classified under the Confedertecnica CCNL as of 01/07/2004; modelled as an allowance with role 'confedertecnica_pre_2004' (compute(..., roles={'confedertecnica_pre_2004'})).
    
    INPS: uses 2026-terziario.json (TaxSector.TERZIARIO). File already present — no changes to the tax file.
    
    CNEL code H442: confirmed from the CNEL archive 'Studi Professionali — Confprofessioni'. Workers covered: 317,554 (UNIEMENS 2022).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/studi-professionali-confprofessioni.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/studi-professionali-confprofessioni.py"
```
