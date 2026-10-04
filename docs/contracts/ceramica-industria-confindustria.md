# CCNL Ceramica Industria (Confindustria-Assopiastrelle)

| | |
|---|---|
| **CNEL code** | `B122` |
| **Sector** | ceramica |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~23k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Confindustria Ceramica
    - FILCTEM-CGIL
    - FEMCA-CISL
    - UILTEC-UIL

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
| **Latest salary tranche** | 2027-06-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A` | Level A — quadri and workers with maximum autonomy and managerial responsibility | € 2,793.96 | 2027-06-01 |
| `B1` | Level B1 — workers with high professional skill or specialisation and full IPO | € 2,515.17 | 2027-06-01 |
| `B2` | Level B2 — workers with high professional skill or specialisation, without IPO | € 2,515.17 | 2027-06-01 |
| `C1` | Level C1 — workers with basic technical or managerial responsibility and full IPO | € 2,194.75 | 2027-06-01 |
| `C2` | Level C2 — workers with basic technical or managerial responsibility and reduced IPO | € 2,194.75 | 2027-06-01 |
| `C3` | Level C3 — workers with basic technical or managerial responsibility, without IPO | € 2,194.75 | 2027-06-01 |
| `D1` | Level D1 — workers with medium-complexity operative functions and full IPO | € 1,972.36 | 2027-06-01 |
| `D2` | Level D2 — workers with medium-complexity operative functions and reduced IPO | € 1,972.36 | 2027-06-01 |
| `D3` | Level D3 — workers with medium-complexity operative functions, without IPO | € 1,972.36 | 2027-06-01 |
| `E1` | Level E1 — workers with executive duties and position IPO allowance (CCNL IPO art.) | € 1,783.43 | 2027-06-01 |
| `E2` | Level E2 — workers with executive duties, standardised operative tasks | € 1,783.43 | 2027-06-01 |
| `F` | Level F — entry-level workers performing basic operations | € 1,666.45 | 2027-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 19.63 |
| `B1` | € 17.56 |
| `B2` | € 17.56 |
| `C1` | € 12.91 |
| `C2` | € 12.91 |
| `C3` | € 12.91 |
| `D1` | € 12.14 |
| `D2` | € 12.14 |
| `D3` | € 12.14 |
| `E1` | € 8.78 |
| `E2` | € 8.78 |
| `F` | € 7.75 |

## Apprenticeship

**qualificazione_professionale** (type: `percentage`)  
Destination levels: `A`, `B1`, `B2`, `C1`, `C2`, `C3`, `D1`, `D2`, `D3`, `E1`, `E2`, `F`  
percentage: 0.95

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "ceramica-industria-confindustria/apprentice_seniority_amount · seniority · impact unknown · open"
    APPRENTICE INCREMENT: apprentice_amount=null. No confirmation from any accessible primary source for B122 industria. The EUR 6 value is confirmed only for CCNL Ceramica Artigianato (V751), not B122. Italian CCNLs frequently exclude apprentices from seniority accrual during the training period (D.Lgs 81/2015 Art. 47), so null may be the correct answer rather than a gap. Verification requires full CCNL text (Arts. 80-82 of the July 2024 rinnovo), which is not publicly machine-readable.

    **Applies when:** `seniority` applies; contract type in apprentice.

    **Remediation:** Verify Arts. 80-82 of the July 2024 rinnovo for the apprentice seniority amount.

!!! warning "ceramica-industria-confindustria/apprentice_seniority · seniority · impact unknown · open"
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
| — | — | 2024-07-22 | [↗](https://www.filctemcgil.it/images/download/CONTRATTI/ceramica_piastrelle/240722_CERAMICHE_RINNOVO_1LUGLIO2023_30GIUGNO2027_TABELLE.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobated tabular minimum (single base pay absorbing contingency and EDR) + IPO (Organisational Position Allowance) as a separate fixed_allowance for the levels that receive it. Source: official FILCTEM-CGIL tables (PDF signed 22/07/2024, PIASTRELLE sub-sector). REFRACTORY MATERIALS has tables identical to PIASTRELLE.
    
    HOURLY_DIVISOR: 173 hours/month (40h weeks × 52/12 = 173.33 rounded). Verified on lavoro-economia.it for CCNL B122.
    
    SENIORITY: 5 biennial increments (cadence 24 months, maximum 5). Amounts from kitech.it (B122, primary levels). Amounts for B2, C2, C3, D2, D3, E2 confirmed equal to B1, C1, D1, E1 respectively: kitech.it (B122, 2026-07-01) shows B1=B2=17.56, C1=C2=C3=12.91, D1=D2=D3=12.14, E1=E2=8.78 EUR. All sub-levels within a grade share the same scatto amount per CCNL B122 category rule (same tabular minimum, standard practice for CCNL ceramica); not confirmed from a primary source.
    
    APPRENTICESHIP: 95% of destination level (base + IPO) for full contract duration. Confirmed by ISFOL official monitoring report (old.isfol.it, citing the ceramica apprendistato agreement of 17/07/2012): 'La retribuzione dell’apprendista per tutta la durata del contratto formativo di qualificazione è fissata nella misura del 95% del livello salariale (minimo di categoria più indennità di posizione)'. The 22/07/2024 renewal modifies Arts. 75 and 80-82 but independent sources confirm no change to apprenticeship structure. Maximum legal duration per D.Lgs 81/2015 Art. 44.
    
    SUB-SECTORS: CCNL B122 covers Tiles (porcelain and stoneware), Refractory Materials, Sanitary Ceramics and Tableware, and Artistic and Traditional Ceramics. This file models the PIASTRELLE sub-sector (and REFRATTARI, which has identical tables). Sanitary Ceramics has a different pay structure (significantly higher IPO) and is not modelled here.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/ceramica-industria-confindustria.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/ceramica-industria-confindustria.py"
```
