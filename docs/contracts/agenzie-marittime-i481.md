# CCNL Agenzie Marittime Raccomandatarie, Agenzie Aeree e Mediatori Marittimi

| | |
|---|---|
| **CNEL code** | `I481` |
| **Sector** | Agenzie marittime e aeree |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-09-13 |
| **Workers (est.)** | ~5k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - FEDERAGENTI
    - FILT-CGIL
    - FIT-CISL
    - UILTRASPORTI

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
| **Last renewal** | 2024-09-13 |
| **Last verified** | — |
| **Latest salary tranche** | 2026-09-01 |

### Semplificazioni note

4 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `7` | Livello 7 (Quadro) | € 2,481.46 | 2026-09-01 |
| `6` | Livello 6 | € 2,370.23 | 2026-09-01 |
| `5` | Livello 5 | € 2,305.38 | 2026-09-01 |
| `4` | Livello 4 | € 2,177.70 | 2026-09-01 |
| `3` | Livello 3 | € 1,921.32 | 2026-09-01 |
| `2` | Livello 2 | € 1,841.02 | 2026-09-01 |
| `1` | Livello 1 (operaio comune) | € 1,601.09 | 2026-09-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 0.00 |
| `2` | € 26.50 |
| `3` | € 27.75 |
| `4` | € 28.75 |
| `5` | € 32.00 |
| `6` | € 32.50 |
| `7` | € 33.00 |

## Apprenticeship

**professionalizzante - dest livello 3** (type: `under_classification`)  
Destination levels: `3`  
under-level: `1`

**professionalizzante - dest livelli 4-5** (type: `under_classification`)  
Destination levels: `4`, `5`  
under-level: `1`

**professionalizzante - dest livello 6** (type: `under_classification`)  
Destination levels: `6`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "agenzie-marittime-i481/level_1_seniority_zero · seniority · impact unknown · open"
    SIMPLIFICATION: Level 1 seniority amount = 0.00. Art. 23 table (primary source) lists levels 2-7 only; level 1 is absent. Interpreted as no entitlement. Verify against consolidated CCNL text.

    **Applies when:** `seniority` applies; level in 1.

    **Remediation:** Verify against the consolidated CCNL text whether level 1 accrues seniority increments.

!!! warning "agenzie-marittime-i481/function_allowance_on_fourteenth · base_salary · impact unknown · open"
    SIMPLIFICATION: Whether indennita' di funzione rides the quattordicesima is unconfirmed. Modeled as a standard fixed_allowance (paid 14 mensilita'). If Art. 5 excludes it from the quattordicesima calculation, the annual figure is overstated by ~51.65 EUR/year.

    **Applies when:** `base_salary` applies; level in 7; run kind in fourteenth.

    **Remediation:** Confirm from Art. 5 whether the indennita di funzione is paid in the quattordicesima.

!!! warning "agenzie-marittime-i481/apprentice_seniority · seniority · impact unknown · open"
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

### Without monetary impact

!!! note ""
    SIMPLIFICATION: 2021-2023 previgente salary values not modeled (not publicly available). Modeling starts from the 2024 renewal first tranche (01/09/2024).

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2021-07-30 | [↗](https://www.filtcgil.it/images/Contratti/Mobilit%C3%A0/ccnl-agenziemarittime21-23.pdf) |
| — | — | 2024-09-13 | [↗](https://www.zhrexpert.it/ccnl/i481-agenzie-marittime.html) |

??? note "Coverage notes"
    Salary model: conglobated (Art. 21: 'paga base, contingenza ed EDR'). Source: 2021 CCNL primary text (FILT-CGIL PDF, signed 30/07/2021).
    
    Hourly divisor 168 confirmed from Art. 20 primary source: 'La paga oraria si ottiene dividendo la retribuzione mensile per 168'. Cross-check: L4 Sep-2026 = 2177.70 / 168 = 12.96 EUR/h (matches lavoro-economia.it hourly rate).
    
    Additional months: 14. Art. 24 (tredicesima) and Art. 25 (quattordicesima) of the 2021 CCNL primary source.
    
    Seniority: 8 biennali (Art. 23, 2021 CCNL primary source). Amounts from Art. 23 table dated 01/04/2004: L7=33.00, L6=32.50, L5=32.00, L4=28.75, L3=27.75, L2=26.50. Level 1 not listed in Art. 23 table: modeled as 0.00.
    
    Apprenticeship: under-classification, Art. 8 of 2021 CCNL (D.Lgs. 81/2015). Destination levels 3-6 only. Three tracks: dest=3 (24 months), dest=4-5 (30 months), dest=6 (36 months). Source: Art. 8, 2021 CCNL primary text.
    
    Indennita' per i Quadri (level 7): 51.65 EUR/month. Source: Art. 5 of the 2021 CCNL primary text (FILT-CGIL PDF): 'A far data dal 1 gennaio 1992, tale indennita' viene elevata a Euro 51,65 lorde mensili.' Modeled as fixed_allowance FUNZIONE, level 7 only.
    
    Salary table (4 tranches): 01/09/2024, 01/09/2025, 01/01/2026, 01/09/2026 from 2024 renewal (signed 13/09/2024). Source: zhrexpert.it (proxy); all cells confirmed consistent with primary-source cross-checks (L4 Sep-2026: 2177.70 / 168 = 12.96 matches hourly rate). Best-attested cell: L4 at 01/01/2026 = 2137.70 (two independent proxy sources agree exactly).
    
    Headcount: approx. 5,000 workers (small sector, CNEL archive I481). Employers: FEDERAGENTI members (maritime agencies, shipping agents, air agencies).
    
    Indennita' per i Quadri amount 51.65 EUR confirmed from Art. 5, 2021 CCNL primary text. Amount unchanged since 01/01/1992 per contract text.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/agenzie-marittime-i481.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/agenzie-marittime-i481.py"
```
