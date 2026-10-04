# CCNL Noleggio Autobus con Conducente (ANAV)

| | |
|---|---|
| **CNEL code** | `IC36` |
| **Sector** | Trasporti - Noleggio autobus con conducente |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-05-23 |
| **Workers (est.)** | ~5422 |
| **Ruleset version** | `1.0.0` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANAV
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
| **Limits of this contract** | base_salary, seniority, una_tantum |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2025-05-23 |
| **Last verified** | — |
| **Latest salary tranche** | 2026-08-01 |

### Semplificazioni note

6 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q1` | Livello Q1 (quadro) | € 1,831.31 | 2026-08-01 |
| `Q2` | Livello Q2 (quadro) | € 1,831.31 | 2026-08-01 |
| `A1` | Livello A1 | € 1,831.31 | 2026-08-01 |
| `A2` | Livello A2 | € 1,721.42 | 2026-08-01 |
| `B1` | Livello B1 | € 1,556.61 | 2026-08-01 |
| `B2` | Livello B2 | € 1,483.35 | 2026-08-01 |
| `B3` | Livello B3 | € 1,419.26 | 2026-08-01 |
| `C1` | Livello C1 | € 1,391.79 | 2026-08-01 |
| `C2` | Livello C2 | € 1,226.97 | 2026-08-01 |
| `C3` | Livello C3 | € 1,144.55 | 2026-08-01 |
| `C4` | Livello C4 | € 915.65 | 2026-08-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 9 increments

| Level | Increment (monthly) |
|---|---:|
| `Q1` | € 33.10 |
| `Q2` | € 33.10 |
| `A1` | € 33.10 |
| `A2` | € 32.19 |
| `B1` | € 30.36 |
| `B2` | € 29.57 |
| `B3` | € 29.39 |
| `C1` | € 29.23 |
| `C2` | € 27.17 |
| `C3` | € 26.61 |
| `C4` | € 25.35 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `Q1`, `Q2`, `A1`, `A2`, `B1`, `B2`, `B3`, `C1`, `C2`, `C3`, `C4`  
percentage: 0.95

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "noleggio-autobus-conducente-anav/t0_table_back_calculated · base_salary · impact unknown · open"
    SIMPLIFICATION: T0 salary table (valid_from 2024-01-01, valid_until 2025-06-30) back-calculated from T1 minus riparametrated increment. Pre-2025-07-01 values are derived, not sourced from an official table. Results for dates before 2025-07-01 should not be relied upon.

    **Applies when:** `base_salary` applies; before 2025-07-01.

    **Remediation:** Source the pre-July 2025 salary table from an official ANAV table.

!!! warning "noleggio-autobus-conducente-anav/seniority_from_ic35 · seniority · impact unknown · open"
    SIMPLIFICATION: Seniority amounts (cadence_months=24, max 9 tranches) taken from kitech.it tables for IC36, which show identical values to IC35 (ANIASA). Cross-contract borrowing — verify against official ANAV CCNL text.

    **Applies when:** `seniority` applies.

    **Remediation:** Verify the seniority amounts against the official ANAV CCNL text.

!!! warning "noleggio-autobus-conducente-anav/una_tantum_2025_2026 · una_tantum · impact yes · open"
    SIMPLIFICATION: Una-tantum payment of 600 EUR at C2 (split June 2025 + Jan 2026) covering Jan-May 2025 gap is excluded: one-off, not a recurring salary element.

    **Applies when:** `una_tantum` applies.

    **Remediation:** Pay the 600 EUR una tantum outside the engine or model it as an event.

!!! warning "noleggio-autobus-conducente-anav/salary_tables_from_proxy · base_salary · impact unknown · open"
    SIMPLIFICATION: salary tables sourced from kitech.it (dati proxy, verificare con testo ufficiale ANAV). No official CNEL PDF or ANAV archive source was found during research.

    **Applies when:** `base_salary` applies.

    **Remediation:** Verify the salary tables against the official ANAV CCNL text.

!!! warning "noleggio-autobus-conducente-anav/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

### Without monetary impact

!!! note ""
    SIMPLIFICATION: Overtime bands not modeled (no standard rates found in public sources; article-specific complexity).

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-05-23 | [↗](https://www.redigo.info/2025/05/27/ccnl-noleggio-autobus-con-conducente-laccordo-di-rinnovo-2024-2026/) |
| — | — | 2025-05-23 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=548) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = retribuzione tabellare; fixed_allowances per level: CONTINGENZA (frozen) + EDR (10.33, frozen since Protocollo 1992) + EDR_RINNOVO (new EDR from 2025-07-01, per level, 14 mensilita) + INDENNITA_FUNZIONE (Q1=67.00, Q2=51.00 only).
    
    SALARY TABLE: 2024-2026 contract signed 23/05/2025, validity 01/01/2024-31/12/2026. Two salary tranches: T1 from 01/07/2025 (+60 EUR at C2, riparametrate), T2 from 01/08/2026 (+100 EUR at C2, riparametrate). New EDR (EDR_RINNOVO) introduced from 01/07/2025: 40.00 EUR at C2, riparametrate per level, paid for 14 mensilita.
    
    HOURLY DIVISOR: 173, consistent with 40h/week x 52/12 = 173.33 convention; ADDITIONAL MONTHS: 14 (tredicesima + quattordicesima).
    
    TAX SECTOR: terziario (same classification as IC35 autorimesse; bus rental companies fall under ATECO division 49 which uses terziario INPS rates).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/noleggio-autobus-conducente-anav.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/noleggio-autobus-conducente-anav.py"
```
