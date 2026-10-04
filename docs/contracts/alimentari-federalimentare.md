# CCNL per i lavoratori dell'industria alimentare (Federalimentare)

| | |
|---|---|
| **CNEL code** | `E012` |
| **Sector** | industria |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~145k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federalimentare
    - FLAI-CGIL
    - FAI-CISL
    - UILA-UIL

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
| **Latest salary tranche** | 2027-01-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1S` | 1S level — senior managers and executives (under L. 190/1985 for workers classified as Quadri) | € 2,836.32 | 2027-01-01 |
| `1` | 1st level — managers with significant managerial and directional responsibilities | € 2,466.34 | 2027-01-01 |
| `2` | 2nd level — intermediate managers and workers with coordination responsibilities | € 2,034.77 | 2027-01-01 |
| `3A` | 3A level — specialist workers with significant operational responsibilities | € 1,788.12 | 2027-01-01 |
| `3` | 3rd level — specialist workers with operational autonomy | € 1,603.17 | 2027-01-01 |
| `4` | 4th level — qualified workers with specific tasks and limited responsibilities | € 1,479.82 | 2027-01-01 |
| `5` | 5th level — qualified workers with simple executive tasks | € 1,356.52 | 2027-01-01 |
| `6` | 6th level — entry-level workers, simple operations | € 1,233.20 | 2027-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1S` | € 51.42 |
| `1` | € 44.71 |
| `2` | € 36.89 |
| `3A` | € 32.42 |
| `3` | € 29.06 |
| `4` | € 26.83 |
| `5` | € 24.59 |
| `6` | € 22.35 |

## Apprenticeship

**professionalizzante_36** (type: `under_classification`)  
Destination levels: `4`, `3`, `3A`, `2`, `1`

**professionalizzante_24** (type: `under_classification`)  
Destination levels: `5`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "alimentari-federalimentare/apprenticeship_period_boundaries · base_salary · impact unknown · open"
    APPRENTICESHIP under_classification (Art. 21 CCNL, renewal 01/03/2024; period structure from afi-ipl.org): 36-month track for destinations 4, 3, 3A, 2, 1 (0-10 months two levels below, 10-22 one level below, then destination); 24-month track for destination 5 (0-10 months at level 6, then level 5). Level 6 and 1S are not apprenticeship destinations. The 10/22-month boundaries are as reported by the source; the contract text refers to 'first/second/third period'.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Confirm the 10 and 22 month period boundaries against the Art. 21 contract text.

!!! warning "alimentari-federalimentare/apprentice_seniority · seniority · impact unknown · open"
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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-03-01 | [↗](https://flaiveneto.it/rinnovato-il-ccnl-industria-alimentare/) |
| — | — | — | [↗](https://www.direzionelavoro.it/wp-content/uploads/2023/10/Alimentari-industria-CNEL-E012.pdf) |
| — | — | — | [↗](https://sindacato.it/ccnl-alimentari-industria/) |
| — | — | — | [↗](https://www.kitech.it/tabelle-retributive-alimentari-industria) |
| — | — | — | [↗](https://www.afi-ipl.org/agenda-apprendisti/industria-alimentare/) |

??? note "Coverage notes"
    SALARY MODEL: split (base pay/TEM + contingency allowance + EDR + IAR as separate allowances). TEM varies by level and tranche; contingency frozen from 31/07/1992 (Government-social partners Protocol); EDR fixed at 10.33 EUR for all levels (Agreement 31/07/1992). IAR (Additional Pay Increment) remains a separate component of the TEC — not absorbed into TEM (confirmed by FLAI Veneto: 'the CCNL renews and redefines the TEC as the sum of TEM and IAR'). TEM source: sindacato.it (2024 salary tables). IAR source: flaiveneto.it.
    
    IAR tranche September 2027: the CCNL sets +11 EUR at level 4; per-level amounts derived by proportional scaling using the same ratio as the Dec-2023 IAR amounts to level 4. Math verified 2026-09-09: L6 delta=9.17 (11×5/6=9.167 ✓), L5=10.08 (11×11/12=10.083 ✓), L3=11.92 (11×13/12=11.917 ✓), L1=18.33 (11×5/3=18.333 ✓), L1S=21.08 (11×23/12=21.083 ✓). All deltas match rounded to cent. Dec-2023 base IAR amounts are published (FLAI Veneto); Sept-2027 per-level table not independently published but mathematically implied by the parametric IAR structure.
    
    CONTINGENCY ALLOWANCE: amounts from lexplain.it and kitech.it — confirmed by two independent sources. Values identical to the previous contracts (frozen since 1993). 1S=545.72, 1=538.70, 2=530.51, 3A=525.83, 3=522.32, 4=519.99, 5=517.65, 6=515.31.
    
    FUNCTION ALLOWANCE 1S: 100 EUR/month for level-1S workers classified as Quadri (L. 190/1985), modelled as an allowance with role 'quadro' (compute(..., roles={'quadro'})).
    
    ADDITIONAL MONTHS: 14 (thirteenth + fourteenth month payment). Source: FLAI Veneto, confirmed by lexplain.it.
    
    SENIORITY: biennial cadence (24 months), maximum 5 increments. Post-2024-renewal amounts from FLAI Veneto (renewal 01/03/2024). valid_from 2023-12-01 assumed equal to the first TEM tranche; sources do not explicitly confirm the effective date of increments (alternative: 2024-03-01, signing date).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/alimentari-federalimentare.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/alimentari-federalimentare.py"
```
