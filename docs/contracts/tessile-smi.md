# CCNL per i lavoratori dell'industria tessile, abbigliamento, moda (SMI)

| | |
|---|---|
| **CNEL code** | `D014` |
| **Sector** | industria |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~160k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - SMI
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
| **Latest salary tranche** | 2027-01-01 |

### Semplificazioni note

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `8` | Grade 8 — department head/supervisor with managerial functions | € 2,518.68 | 2027-01-01 |
| `7` | Grade 7 — managers with managerial responsibility | € 2,376.10 | 2027-01-01 |
| `6` | Grade 6 — managers and technicians with area responsibility | € 2,229.13 | 2027-01-01 |
| `5` | Grade 5 — junior managers and specialist technicians | € 2,088.36 | 2027-01-01 |
| `4` | Grade 4 — highly specialist workers and skilled clerical employees | € 1,986.95 | 2027-01-01 |
| `3S` | Grade 3 super — specialist workers with autonomy and executive clerical employees | € 1,941.98 | 2027-01-01 |
| `3` | Grade 3 — specialist workers and routine clerical employees | € 1,899.25 | 2027-01-01 |
| `2S` | Grade 2 super — qualified workers with executive autonomy | € 1,843.81 | 2027-01-01 |
| `2` | Grade 2 — basic qualified workers | € 1,803.70 | 2027-01-01 |
| `1` | Grade 1 — elementary operations requiring no prior experience | € 1,560.00 | 2027-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 4 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 6.71 |
| `2` | € 7.23 |
| `2S` | € 7.23 |
| `3` | € 7.75 |
| `3S` | € 7.75 |
| `4` | € 8.26 |
| `5` | € 9.81 |
| `6` | € 10.33 |
| `7` | € 11.88 |
| `8` | € 12.91 |

## Apprenticeship

**prof_L6_L8** (type: `under_classification`)  
Destination levels: `6`, `7`, `8`

**prof_L5** (type: `under_classification`)  
Destination levels: `5`

**prof_L4** (type: `under_classification`)  
Destination levels: `4`

**prof_L3S** (type: `under_classification`)  
Destination levels: `3S`

**prof_L3** (type: `under_classification`)  
Destination levels: `3`

**prof_L2S** (type: `under_classification`)  
Destination levels: `2S`

**prof_L2** (type: `under_classification`)  
Destination levels: `2`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "tessile-smi/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

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
| — | — | 2024-11-11 | [↗](https://www.sistemamodaitalia.com/) |
| — | — | — | [↗](https://www.lexplain.it/tabelle-retributive-ccnl-tessile-abbigliamento-smi/) |
| — | — | — | [↗](https://www.kitech.it/tabelle-retributive-tessile-abbigliamento) |

??? note "Coverage notes"
    December 2024 tranche (01/12/2024): per-level values derived proportionally from the +EUR 95 increase at grade 4 (2024 SMI renewal, source filctemcgil.it). Rationale: Dec-2024 increment = 95/152 = 5/8 of the total increase Nov-2024→Jan-2026; verified by exact closure on all levels against Jan-2026 values from kitech.it.
    
    Level 8 function allowance: the total ERN published on lexplain.it (2,316.33) includes the function allowance (EUR 51.65). base_salary = ERN - 51.65 = 2,264.68 (pre-Dec 2024) and 2,457.72 (Jan 2026). Source kitech.it reports minimum and total separately for Level 8. Verification: combined increase (Dec2024+Jan2026) at Level 8 = EUR 193.04, expected proportional = 126.74% × 152.24 = EUR 193.12 (delta < 0.1 EUR). Interpretation confirmed.
    
    VV.PP. (Travelling and Area Salespeople): not modelled. Special category with their own rates (1st cat.: 1,932.91/1,932.91 pre-Dec 2024; 2nd cat.: 1,823.07); excluded due to complexity.
    
    Seniority increments (Art. 46 CCNL): amounts confirmed via ilccnl.it (updated 2024-11-12, day after renewal signing), which lists per-level hourly increment in the salary table: L1=6.71, L2=7.23, L2S=7.23, L3=7.75 EUR — matching lexplain.it values exactly. L4-L8 values (8.26, 9.81, 10.33, 11.88, 12.91 EUR) from lexplain.it Art. 46 table (published 2024-08-26), consistent with the confirmed lower-level pattern. November 2024 renewal announcements do not mention changes to scatti amounts; Art. 46 specifies a fixed amount "non rinnovato in aumento" per renewal. Verified 2026-09-09.
    
    Source for pre-Dec 2024 tables: lexplain.it, retrieved September 2026. Source for Jan 2026 tables: kitech.it, retrieved September 2026. Source for TEM and effective dates: SMI press release (sistemamodaitalia.com), November 2024.
    
    APPRENTICESHIP: sotto-inquadramento. Group A (L4-L8) 36m total: 0-15m = 2 full levels below dest, 15-30m = 1 full level below, 30-36m+ = dest. Note: 'full level' skips S-variants, so levels_below in order arithmetic: L6-L8 → 2/1, L5 → 3/1, L4 → 4/2. Group B (L3/3S) 36m: 0-12m at L1, 12-30m at L2, 30m+ at dest. Group B (L2/2S) 36m: 0-12m at L1, then dest. L1 excluded as destination. Source: CCNL SMI (CNEL D014) + Gruppo24ORE scheda Oct 2023 + MySolution sintesi 2017. SIMPLIFICATION: MySolution notes 3S second period uses L2 pay (not L3).
    
    JANUARY 2027 TRANCHE: +60.96 at L8 basis, proportional to parametri. Values from rinnovo 11/11/2024 (Chapter VI column 'da gennaio 2027'). Source: studiobergonzini.it ipotesi 11/11/2024 PDF.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/tessile-smi.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/tessile-smi.py"
```
