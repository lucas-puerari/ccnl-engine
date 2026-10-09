# CCNL Trasporto a Fune (Funivie Terrestri ed Aeree) - ANEF

| | |
|---|---|
| **CNEL code** | `I911` |
| **Sector** | Trasporto a fune |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-05-16 |
| **Workers (est.)** | ~15k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANEF
    - FILT-CGIL
    - FIT-CISL
    - UILTRASPORTI
    - SAVT

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
| **Last renewal** | 2025-05-16 |
| **Last verified** | — |
| **Latest salary tranche** | 2028-03-01 |

### Semplificazioni note

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1S` | 1° livello Super (parametro 210) | € 2,410.99 | 2028-03-01 |
| `1` | 1° livello (parametro 195) | € 2,238.88 | 2028-03-01 |
| `2` | 2° livello (parametro 176) | € 2,020.97 | 2028-03-01 |
| `3` | 3° livello (parametro 160) | € 1,836.94 | 2028-03-01 |
| `4` | 4° livello (parametro 145) | € 1,664.59 | 2028-03-01 |
| `5` | 5° livello (parametro 130) | € 1,492.75 | 2028-03-01 |
| `6` | 6° livello (parametro 120) | € 1,377.94 | 2028-03-01 |
| `7` | 7° livello (parametro 100) | € 1,148.35 | 2028-03-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1S` | € 70.00 |
| `1` | € 65.00 |
| `2` | € 60.00 |
| `3` | € 55.00 |
| `4` | € 50.00 |
| `5` | € 45.00 |
| `6` | € 40.00 |
| `7` | € 35.00 |

## Apprenticeship

**professionalizzante** (type: `under_classification`)  
Destination levels: `1`, `2`, `3`, `4`, `5`, `6`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "funivie-anef/apprentice_seniority · seniority · impact unknown · open"
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
| — | — | 2025-05-16 | [↗](https://www.funiviearabba.it/wp-content/uploads/2025/12/Sintesi-CCNL-ANEF.pdf) |

??? note "Coverage notes"
    Salary model: split. base_salary = paga base (Allegato 1). fixed_allowances = contingenza (per-level, Allegato 2). No EDR: ilccnl.it Oct-2025 table shows Terzo Elemento = 0.00; totals confirm base + contingenza only (e.g. 2179.27 + 528.67 = 2707.94).
    
    8 livelli retributivi (parametri 210/195/176/160/145/130/120/100 per Art. 18). Sintesi: '8 categorie professionali e altrettanti livelli retributivi'.
    
    Hourly divisor 173 from Art. 18 of the 2025 CCNL text (confirmed thaler.it and lavoro-economia.it).
    
    Additional months: 14 (tredicesima natalizia + quattordicesima luglio, confirmed thaler.it and lavoro-economia.it).
    
    Seniority from Allegato 3 (new-hire amounts, biennale cadence, max 5 scatti). Double-sourced: ilccnl.it Oct-2025 column confirms 1S=70, 1=65, 2=60, 3=55. Allegato 3.1 (pre-30/04/2016 cohort grandfathered amounts) not modelled.
    
    Tranche dates (Allegato 1): 2025-05-01, 2025-10-01, 2027-03-01, 2028-03-01.
    
    Headcount not verified; no CNEL/ADAPT figure located for I911. INPS-CNEL mapping: I911.
    
    tax_sector=industria: ANEF funivie operators are classified under ATECO H (trasporti) which INPS maps to the industria contribution table. No dedicated 'funivie' or 'trasporto-fune' TaxSector exists in the engine enum; industria is the correct proxy for this transport-infrastructure category.
    
    Indennita di funzione (118.79 EUR/month) for Quadri (L. 190/1985 status within levels 1S and 1) is not modelled. It is a person-status allowance tied to individual Quadro designation — not a livello retributivo. Structural engine limitation: the engine does not support per-person status allowances.
    
    Allegato 3.1 (grandfathered scatti for workers hired before 30/04/2016) not modelled. Only Allegato 3 (standard post-2016 cohort) amounts implemented. Structural scope decision: pre-2016 grandfathered amounts affect a declining cohort; the new-hire case is exact.
    
    Apprenticeship destinations limited to levels 1-6. Level 1S excluded: Quadro status per L. 190/1985 is a person-status designation acquired through individual deed, not a contractually defined apprenticeship destination.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/funivie-anef.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/funivie-anef.py"
```
