# CCNL Scuole Private Laiche (ANINSEI-Assoscuola)

| | |
|---|---|
| **CNEL code** | `T231` |
| **Sector** | istruzione privata laica |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~25k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANINSEI
    - Assoscuola
    - UIL Scuola RUA
    - CONFSAL-SNALS
    - ANIEF

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
| **Limits of this contract** | — |

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

Nessuna semplificazione documentata.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `VIII_B` | Livello VIII B — quadro superiore con massima responsabilita gestionale | € 1,819.62 | 2027-01-01 |
| `VIII_A` | Livello VIII A — quadro superiore, direttore o responsabile di sede | € 1,725.56 | 2027-01-01 |
| `VII` | Livello VII — quadro intermedio, responsabile di plesso o coordinatore | € 1,646.17 | 2027-01-01 |
| `VI` | Livello VI — docente coordinatore o tecnico senior con responsabilita | € 1,619.64 | 2027-01-01 |
| `V` | Livello V — docente o impiegato di concetto con autonomia operativa | € 1,619.64 | 2027-01-01 |
| `IV` | Livello IV — impiegato o tecnico di concetto | € 1,519.52 | 2027-01-01 |
| `III` | Livello III — operatore specializzato, mansioni tecnico-pratiche | € 1,446.24 | 2027-01-01 |
| `II` | Livello II — operatore qualificato, mansioni esecutive di supporto | € 1,379.61 | 2027-01-01 |
| `I` | Livello I — personale ausiliario e operatore generico | € 1,347.46 | 2027-01-01 |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

| Level | Increment (monthly) |
|---|---:|
| `I` | € 0.00 |
| `II` | € 0.00 |
| `III` | € 0.00 |
| `IV` | € 0.00 |
| `V` | € 0.00 |
| `VI` | € 0.00 |
| `VII` | € 0.00 |
| `VIII_A` | € 0.00 |
| `VIII_B` | € 0.00 |

## Apprenticeship

**professionalizzante_36** (type: `percentage`)  
Destination levels: `I`, `II`, `III`, `IV`, `V`, `VI`, `VII`, `VIII_A`, `VIII_B`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "apprentice_seniority_simplified · seniority · impact unknown · open"
    Apprentices accrue only the CCNL apprentice-specific seniority increment (zero when the CCNL declares none); the increments of the level start after qualification. The run is affected when the apprentice has matured increments and the level amount differs from the apprentice amount.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source, for each CCNL, whether apprentices accrue the level increments or an amount of their own, model it, then resolve this limitation.

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
| — | — | 2024-06-15 | [↗](https://foe.it/files/2024/07/CCNL-ANINSEI_2024-2027cd.pdf) |

??? note "Coverage notes"
    RENEWAL: CCNL signed 2024-06-15 by ANINSEI and Assoscuola with UIL Scuola RUA, CONFSAL-SNALS and ANIEF. Validity 01/01/2024-31/12/2027. Economic effects from 01/01/2025.
    
    CONGLOBATED MINIMUMS (Art. 23): contingenza maturata al 30/11/1991 comprensiva dell'EDR e' inglobata nella retribuzione tabellare (Art. 22). Values are fully conglobated — no separate contingenza or EDR column.
    
    SALARY TABLE (Art. 22): four tranches. Carry-over base from old CCNL 2021-2023 dal 01/09/2023 applies from 2024-06-15 to 2024-12-31. All four tranches read directly from Art. 22 table in PDF (pdftotext -layout, pages 51-53).
    
    HOURLY DIVISOR (Art. 27): 165 h/month for 38h/week full-time. The contract table lists divisors for reduced weekly hours (36h=156, 34h=147, 32h=139, 24h=104, 21h=91, 18h=78); each is 165 scaled by hours/38, matching part_time_pct equivalents. hourly_divisor=165 is exact — no simplification.
    
    ADDITIONAL MONTHS (Art. 21): 13 (tredicesima only, paid by 16 December).
    
    SENIORITY (Art. 24): salario di anzianita frozen as of 2025-01-01, milestone-based (hire-date brackets). Workers with 2+ years continuous service at 01/01/2025 receive 20 EUR/month; pre-2002 hires up to 90 EUR/month (grandfathered). New hires after ~2023-01-01 receive nothing. maximum_count=0 correctly models new-hire case (zero seniority). The engine cadence model cannot express hire-date milestones: long-tenure workers are understated. Structural engine limitation — no data gap.
    
    APPRENTICESHIP (Art. 9.7): percentages 85/90/100% over 36 months confirmed from Art. 9.7 of ANINSEI CCNL 2024-2027 PDF. Destination level list not specified in available pages; all nine levels modelled as destinations (conservative assumption — no restriction applied). This may overstate eligible levels but never understates payroll cost.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/scuole-private-laiche-aninsei.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/scuole-private-laiche-aninsei.py"
```
