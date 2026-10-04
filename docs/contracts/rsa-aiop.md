# CCNL RSA e Strutture Residenziali Socio-Assistenziali (AIOP)

| | |
|---|---|
| **CNEL code** | `T091` |
| **Sector** | residenze sanitarie assistenziali — personale non medico |
| **Tax sector** | `terziario` |
| **Last renewal** | 2012-03-22 |
| **Workers (est.)** | ~17k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - AIOP
    - FP-CGIL
    - CISL-FP
    - UIL-FPL
    - UGL Sanità
    - FISMIC-CONFSAL
    - FIALS

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
| **Last renewal** | 2012-03-22 |
| **Last verified** | — |
| **Latest salary tranche** | 2023-10-01 |

### Semplificazioni note

Nessuna semplificazione documentata.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `H` | Livello H | € 3,294.68 | 2023-10-01 |
| `G` | Livello G | € 2,749.49 | 2023-10-01 |
| `F` | Livello F | € 2,095.50 | 2023-10-01 |
| `E3` | Livello E3 | € 1,806.00 | 2023-10-01 |
| `E2` | Livello E2 | € 1,746.00 | 2023-10-01 |
| `E1` | Livello E1 | € 1,550.56 | 2023-10-01 |
| `D3` | Livello D3 | € 1,496.06 | 2023-10-01 |
| `D2` | Livello D2 | € 1,463.33 | 2023-10-01 |
| `D1` | Livello D1 | € 1,419.80 | 2023-10-01 |
| `C` | Livello C | € 1,419.80 | 2023-10-01 |
| `B` | Livello B | € 1,311.68 | 2023-10-01 |
| `A` | Livello A | € 1,223.57 | 2023-10-01 |

## Seniority increments

**Cadence:** every 60 months  
**Maximum:** 1 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 40.00 |
| `B` | € 40.00 |
| `C` | € 40.00 |
| `D1` | € 40.00 |
| `D2` | € 40.00 |
| `D3` | € 40.00 |
| `E1` | € 40.00 |
| `E2` | € 40.00 |
| `E3` | € 40.00 |
| `F` | € 0.00 |
| `G` | € 0.00 |
| `H` | € 0.00 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `A`, `B`, `C`, `D1`, `D2`, `D3`, `E1`, `E2`, `E3`, `F`  
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
| — | — | 2012-03-22 | [↗](https://acopnazionale.it/wp-content/uploads/2022/03/ccnl-rsa-aiop-2012.pdf) |
| — | — | 2023-10-03 | [↗](https://www.frgeditore.it/images/cop/pdf/titolo-6/ccnl/rsa/63_accordo_3-10-2023_aiop.pdf) |

??? note "Coverage notes"
    CCNL T091 — AIOP RSA. Conglobated. 12 levels: A-B-C-D1-D2-D3-E1-E2-E3-F-G-H. Divisor 165, 13 months. Original 2012 contract, updated by accordo ponte Oct 2023.
    
    Accordo ponte (Oct 2023) expired June 2024. Contract applied in ultrattività pending renewal. Oct 2023 table modeled as current (valid_until null).
    
    Seniority: CCNL RSA-AIOP provides a flat EUR 40/month after 5 years of service (levels A-E3 only; F/G/H excluded). Modelled as cadence_months=60, maximum_count=1 — correct for new hires (single increment at month 60). Oct 2023 'premio di anzianita' (EUR 40 one-time for 10+ year workers) is a one-time payment, out_of_scope.
    
    Apprenticeship: CCNL RSA-AIOP specifies sotto-inquadramento up to 2 levels below destination (levels A-F eligible, 36 months). Engine schema requires a static pay_level_code; cannot express dynamic under-classification tracks; modelled as 100% passthrough (correct for permanent workers, overstates pay for apprentices). Structural engine limitation.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/rsa-aiop.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/rsa-aiop.py"
```
