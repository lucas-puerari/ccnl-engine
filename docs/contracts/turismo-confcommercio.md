# CCNL Turismo, Pubblici Esercizi e Ristorazione (Confcommercio)

| | |
|---|---|
| **CNEL code** | `H052` |
| **Sector** | turismo |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~300k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federalberghi
    - FIPE-Confcommercio
    - Federviaggio
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTuCS

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
| **Latest salary tranche** | 2027-11-01 |

### Semplificazioni note

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QA` | Grade QA — senior manager with maximum managerial responsibility | € 2,495.22 | 2027-11-01 |
| `QB` | Grade QB — senior manager with high managerial professionalism | € 2,310.11 | 2027-11-01 |
| `1` | Grade 1 — management function / maître / head receptionist | € 2,152.32 | 2027-11-01 |
| `2` | Grade 2 — junior management function / chef de rang / deputy manager | € 1,967.20 | 2027-11-01 |
| `3` | Grade 3 — senior technician / section chef / senior front-office | € 1,855.32 | 2027-11-01 |
| `4` | Grade 4 — process technician / shift leader / receptionist | € 1,750.69 | 2027-11-01 |
| `5` | Grade 5 — specialist operator (waiter, cook, receptionist) | € 1,641.85 | 2027-11-01 |
| `6S` | Grade 6 super — qualified operator (room attendant, basic bar staff) | € 1,578.72 | 2027-11-01 |
| `6` | Grade 6 — basic operator (dishwasher, porter, commis) | € 1,556.35 | 2027-11-01 |
| `7` | Grade 7 — assigned to general tasks, cleaning and support operations | € 1,458.42 | 2027-11-01 |

## Seniority increments

**Cadence:** every 48 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `QA` | € 40.80 |
| `QB` | € 39.25 |
| `1` | € 37.70 |
| `2` | € 36.15 |
| `3` | € 34.86 |
| `4` | € 33.05 |
| `5` | € 32.54 |
| `6S` | € 31.25 |
| `6` | € 30.99 |
| `7` | € 30.47 |

## Apprenticeship

**professionalizzante_36** (type: `percentage`)  
Destination levels: `5`, `4`, `3`, `2`, `6S`  
percentage: 1.00

**professionalizzante_24** (type: `percentage`)  
Destination levels: `6`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "turismo-confcommercio/apprentice_seniority · seniority · impact unknown · open"
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
| — | — | 2024-06-05 | [↗](https://www.lexplain.it/tabelle-retributive-ccnl-alberghi-turismo-confcommercio-aumenti-stipendio-2024-2027/) |
| — | — | — | [↗](https://www.lexplain.it/scatti-di-anzianita-ccnl-turismo-ristorazione-e-pubblici-esercizi/) |

??? note "Coverage notes"
    SUB-SECTOR: salary tables from the hotels/tourism renewal signed on 5 June 2024 (CCNL H052 hotels special section). CCNL H052 also covers the public establishments/FIPE sub-sector (renewal March 2025, slightly different tables) not modelled in this file.
    
    CONGLOBATED MINIMUMS: the base_salary values are the monthly conglobated tabular minimums (basic pay + contingency included), as published by lexplain.it/tabelle-retributive-ccnl-alberghi-turismo-confcommercio-aumenti-stipendio-2024-2027. fixed_allowances is empty for all levels. Verification: level 7 November 2027 = 1458.42 / 172 = 8.48 EUR/h (matches published hourly table).
    
    QA/QB FUNCTION ALLOWANCE: some sources (public establishments) show a separate function allowance (QA=EUR 75, QB=EUR 70). For the hotels sub-sector, the values in the conglobated table appear to already include this component. If checks against actual payslips show a discrepancy, add fixed_allowances QA=EUR 75 and QB=EUR 70.
    
    TRANCHES: July 2024, June 2025, May 2026, April 2027, November 2027. No prior tranches modelled (lower bound: 2024-07-01).
    
    SENIORITY INCREMENTS: 6 four-yearly increments (every 48 months). Amounts from lexplain.it/scatti-di-anzianita-ccnl-turismo-ristorazione-e-pubblici-esercizi. The increments are paid over 14 monthly instalments (including the 13th and 14th) — the gross_annual component is already captured by the additional_months=14 multiplier in the engine.
    
    APPRENTICESHIP percentage (2024 renewal): 80% months 1-12, 85% months 13-24, 90% months 25-36 (source: albergoatenericcione.it, confirmed by research on the 2024 renewal). Duration 36 months for grades 2-5 and 6S (track 'professionalizzante_36'), 24 months for grade 6 (track 'professionalizzante_24'); beyond the contractual duration the worker is fully qualified at 100%. Grade 7, grade 1, and Quadri are not destinations. The under-classification (2 levels below / 1 level below) applied to the previous CCNL.
    
    MONTHLY PAYMENTS: 14 (thirteenth in June, fourteenth in December). Confirmed by CCNL and by the note 'amounts paid over 14 monthly instalments' for seniority increments.
    
    HOURLY DIVISOR: 172 hours/month (40 h/week × 52/12). Verified by back-calculation: 1458.42 / 172 = 8.478 ≈ 8.48 EUR/h (level 7, November 2027 — matches lexplain hourly table).
    
    INPS: uses 2026-terziario.json (same tax_sector as commercio-confcommercio).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/turismo-confcommercio.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/turismo-confcommercio.py"
```
