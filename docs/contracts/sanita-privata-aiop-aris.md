# CCNL Case di Cura Private - Personale Non Medico (AIOP/ARIS)

| | |
|---|---|
| **CNEL code** | `T011` |
| **Sector** | Sanità privata |
| **Tax sector** | `terziario` |
| **Last renewal** | 2020-10-08 |
| **Workers (est.)** | ~150k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - AIOP
    - ARIS
    - FILCAMS CGIL
    - FP CGIL
    - FISASCAT CISL
    - CISL FP
    - UILTuCS
    - UILFPL
    - FIALS
    - CISAL SANITÀ

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
| **Last renewal** | 2020-10-08 |
| **Last verified** | — |
| **Latest salary tranche** | 2020-07-01 |

### Semplificazioni note

Nessuna semplificazione documentata.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `E2` | Categoria E — progressione orizzontale 2 | € 3,554.39 | 2020-07-01 |
| `E1` | Categoria E — progressione orizzontale 1 | € 2,936.33 | 2020-07-01 |
| `DS4` | Categoria DS — progressione orizzontale 4 | € 2,418.05 | 2020-07-01 |
| `E` | Categoria E — quadro / specialista | € 2,410.22 | 2020-07-01 |
| `DS3` | Categoria DS — progressione orizzontale 3 | € 2,345.38 | 2020-07-01 |
| `DS2` | Categoria DS — progressione orizzontale 2 | € 2,261.56 | 2020-07-01 |
| `D4` | Categoria D — progressione orizzontale 4 | € 2,209.98 | 2020-07-01 |
| `DS1` | Categoria DS — progressione orizzontale 1 | € 2,180.26 | 2020-07-01 |
| `D3` | Categoria D — progressione orizzontale 3 | € 2,147.12 | 2020-07-01 |
| `DS` | Categoria DS — coordinatore | € 2,101.08 | 2020-07-01 |
| `D2` | Categoria D — progressione orizzontale 2 | € 2,084.77 | 2020-07-01 |
| `C4` | Categoria C — progressione orizzontale 4 | € 2,076.38 | 2020-07-01 |
| `D1` | Categoria D — progressione orizzontale 1 | € 2,022.94 | 2020-07-01 |
| `C3` | Categoria C — progressione orizzontale 3 | € 1,984.10 | 2020-07-01 |
| `D` | Categoria D — professionista sanitario | € 1,953.87 | 2020-07-01 |
| `C2` | Categoria C — progressione orizzontale 2 | € 1,921.25 | 2020-07-01 |
| `C1` | Categoria C — progressione orizzontale 1 | € 1,857.14 | 2020-07-01 |
| `C` | Categoria C — operatore qualificato | € 1,803.61 | 2020-07-01 |
| `B4` | Categoria B — progressione orizzontale 4 | € 1,733.54 | 2020-07-01 |
| `B3` | Categoria B — progressione orizzontale 3 | € 1,697.76 | 2020-07-01 |
| `B2` | Categoria B — progressione orizzontale 2 | € 1,669.36 | 2020-07-01 |
| `B1` | Categoria B — progressione orizzontale 1 | € 1,624.54 | 2020-07-01 |
| `A4` | Categoria A — progressione orizzontale 4 | € 1,592.19 | 2020-07-01 |
| `B` | Categoria B — operatore tecnico-pratico | € 1,579.86 | 2020-07-01 |
| `A3` | Categoria A — progressione orizzontale 3 | € 1,566.67 | 2020-07-01 |
| `A2` | Categoria A — progressione orizzontale 2 | € 1,544.35 | 2020-07-01 |
| `A1` | Categoria A — progressione orizzontale 1 | € 1,506.44 | 2020-07-01 |
| `A` | Categoria A — ausiliario generico | € 1,467.45 | 2020-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**Apprendistato professionalizzante 36 mesi** (type: `percentage`)  
Destination levels: `A`, `B`, `C`, `D`  
percentage: 0.90

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

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
| — | — | 2020-10-08 | [↗](https://www.fondazionerimed.eu/wp-content/uploads/2023/12/CCNL-CASE-DI-CURA-PRIVATE-08.10.2020.pdf) |
| — | — | — | [↗](https://www.contratticcnl.it/ccnl/t011/) |

??? note "Coverage notes"
    CCNL signed 2020-10-08; nominally covers 2016-2018 (Art. 4). Applied in ultrattività from 2019 onwards. Salary tables (Tabella 1) effective 2020-07-01 per Art. 51. No renewal signed as of 2026-09-09. Confirmed 2026-09-09: preintesa June 2020 is the last event; all 2023-2025 bridge agreements found refer to the separate AIOP RSA contract (different CNEL code). The AIOP-ARIS ospedaliero (T011) T011 remains in pure ultrattività.
    
    Salary values are conglobated: EADR incorporated into tabellare from 2020-07-01 per Art. 55. Back-calculation: A 1467.45×13=19076.85 ✓; C4 2076.38×13=26992.94 ✓; DS4 2418.05×13=31434.65 ✓.
    
    28 levels (A, A1–A4, B, B1–B4, C, C1–C4, D, D1–D4, DS, DS1–DS4, E, E1, E2). Order assigned by 2020-07-01 salary because professional families A/B/C/D/DS/E have overlapping salary ranges — categories are not a single hierarchy. A4 (order 6) is paid above B (order 5) per Tabella 1. Horizontal progressions within each category are modelled as static levels per Art. 48; the engine does not auto-advance a worker's level after the contractual service threshold.
    
    Retribuzione individuale di anzianità frozen at 1993-12-31 per Art. 56 (no new seniority accruals). Modelled as seniority_increments.maximum_count=0.
    
    CCNL covers ospedalieri, IRCCS, riabilitazione (AIOP/ARIS members). Does not apply to RSA governed by separate AIOP RSA or Uneba agreements.
    
    hourly_divisor=156 (Art. 58: paga giornaliera=monthly/26, oraria=giornaliera/6 for 36h/week). Levels D4, DS4, E, E1, E2 work 38h/week per Art. 18 (oraria=giornaliera/6.33, exact divisor≈164.6), modelled as 156 uniformly.
    
    Apprenticeship (Art. 23 §14, Art. 23 §2): destination levels are the four category entry positions A, B, C, D only. Horizontal-progression steps (A1-A4, B1-B4, C1-C4, D1-D4) are not apprenticeship destinations. DS and E categories excluded per Art. 23 §2. OSS and Albo-registered health professions excluded per Art. 23 §2 but per-qualification restriction not modellable at level granularity.
    
    INPS: terziario sector confirmed. Kitech.it (table "TERZIARIO attività VARIE", kitech.it/Contributi-previdenziali.aspx?p=4_143) lists operai/impiegati at 9.19% employee contribution and 28.98% employer (≤50 dipendenti) / 29.58% (>50) — matching 2026-terziario.json exactly. Private healthcare (AIOP/ARIS) is classified under terziario standard rates; no healthcare-specific INPS regime applies. INPS Circolare n. 6/2026 confirms 9.19% employee rate for private sector workers.
    
    CCNL applied in ultrattività; Decreto Lavoro 2026 introduced a statutory 30% IPCA auto-adjustment if no renewal within 12 months of expiry. If triggered, legally applicable 2026 minimums may exceed the 2020 Tabella 1 values modelled here. Engine models contractual tables only.
    
    CNEL code T011 verified at https://www.contratticcnl.it/ccnl/t011/ (146585 employees, ARIS/AIOP, ATECO 86).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/sanita-privata-aiop-aris.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/sanita-privata-aiop-aris.py"
```
