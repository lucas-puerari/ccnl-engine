# CCNL CED, ICT, Professioni Digitali e STP (Assoced-UGL)

| | |
|---|---|
| **CNEL code** | `H601` |
| **Sector** | Terziario |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-07-28 |
| **Workers (est.)** | ~22k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Assoced
    - LAIT
    - Confterziario
    - UGL Terziario

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
| **Limits of this contract** | base_salary, inps_employer |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2025-07-28 |
| **Last verified** | — |
| **Latest salary tranche** | 2028-01-01 |

### Semplificazioni note

1 semplificazione documentata. 2 feature mancanti.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QDIR` | Quadri di Direzione | € 3,186.49 | 2028-01-01 |
| `Q` | Quadri | € 2,895.91 | 2028-01-01 |
| `1` | 1° livello | € 2,486.32 | 2028-01-01 |
| `2` | 2° livello | € 2,225.94 | 2028-01-01 |
| `3S` | 3° livello Super | € 2,134.17 | 2028-01-01 |
| `3` | 3° livello | € 1,997.93 | 2028-01-01 |
| `4` | 4° livello | € 1,859.01 | 2028-01-01 |
| `5` | 5° livello | € 1,769.98 | 2028-01-01 |
| `6` | 6° livello | € 1,494.74 | 2028-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**professionalizzante_36** (type: `under_classification`)  
Destination levels: `2`, `3S`, `3`, `4`  
under-level: `1`

**professionalizzante_24** (type: `under_classification`)  
Destination levels: `5`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "ced-assoced/terziario_inps_rates_unverified · inps_employer · impact unknown · open"
    INPS terziario rates reused from 2026-terziario.json (same sector as H016). Verify against annual INPS circular for exact H601 sub-sector rate.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Verify the H601 sub-sector INPS rate against the annual INPS circular.

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
| — | — | 2022-03-09 | [↗](https://www.fondoeasi.it/fondo-easi/ccnl-ced-ced-ict-professioni-digitali-e-stp/stesura-ccnl-ced-09-marzo-2022.pdf) |
| — | — | 2025-07-28 | [↗](https://www.redigo.info/ccnl-ced-ict-professioni-digitali-stp) |
| — | — | 2025-07-28 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=62) |

??? note "Coverage notes"
    Salary model: paga base nazionale conglobata (Art. 172, 2022 stesura). Single TimeSeries per level, no separate contingenza or EDR.
    
    Unified classification covers CED, ICT, Professioni Digitali and STP workers (Art. 172 + Tabella A, one scale). No separate STP salary table exists in the 2022 stesura or 2025 renewal.
    
    Divisore convenzionale 173 h/month (Art. 171) and 26 d/month (Art. 170). Source: 2022 stesura fondoeasi.it.
    
    Mensilita supplementari: tredicesima (Art. 175) and quattordicesima (Art. 176). additional_months = 14.
    
    Indennita di funzione (Tabella A note, 2025 renewal): QDIR 287/296/306 EUR, Q 250/258/266 EUR per 14 mensilita. Tranche dates: 01/09/2025, 01/09/2026, 01/09/2027, distinct from base salary tranches.
    
    Scatti di anzianita (Art. 166, 2022 stesura): abrogated from 01/01/2019. Grandfathered for personale in forza al 31-12-2018 only. New hires (post-2018): maximum_count=0. Per-level 2009 amounts: QDIR=52, Q=47, L1=44, L2=40, L3S=36, L3=33, L4=30, L5=27, L6=24 (frozen, not updated since 2009 across 2022 and 2025 renewals).
    
    Apprenticeship (Art. 23-24, 2022 stesura, ccnlced.it allegato): under_classification. First half 2 levels below, second half 1 level below. Level 5 exception: stays at Level 6 throughout 24-month track. Destination L2 duration 36 months (studiocerbone.com: 240 h/36 months for 2° livello). Source ccnlced.it showed '6 months' for L2 — treated as parsing artifact; 36 months adopted from studiocerbone.com.
    
    Salary tranches: 01/09/2025 (source-confirmed, redigo.info and kitech.it), 01/06/2026 (source-confirmed, both sources agree), 01/03/2027 (redigo.info only, single-source), 01/01/2028 (redigo.info only, single-source).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/ced-assoced.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/ced-assoced.py"
```
