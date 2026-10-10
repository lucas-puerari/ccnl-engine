# CCNL Autostrade e Trafori Concessionari

| | |
|---|---|
| **CNEL code** | `I192` |
| **Sector** | autostrade e trafori — addetti alle concessionarie autostradali |
| **Tax sector** | `industria` |
| **Last renewal** | 2023-01-01 |
| **Workers (est.)** | ~15k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - AISCAT
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
| **Last renewal** | 2023-01-01 |
| **Last verified** | — |
| **Latest salary tranche** | 2028-01-01 |

### Semplificazioni note

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `AQ` | Livello AQ (Quadro) | € 3,430.84 | 2028-01-01 |
| `A` | Livello A | € 3,430.84 | 2028-01-01 |
| `A1` | Livello A1 | € 3,065.88 | 2028-01-01 |
| `B+` | Livello B Superiore | € 2,803.04 | 2028-01-01 |
| `B` | Livello B | € 2,700.85 | 2028-01-01 |
| `B1+` | Livello B1 Superiore | € 2,569.52 | 2028-01-01 |
| `B1` | Livello B1 | € 2,467.30 | 2028-01-01 |
| `C+` | Livello C Superiore | € 2,262.89 | 2028-01-01 |
| `C` | Livello C | € 2,160.70 | 2028-01-01 |
| `C1` | Livello C1 | € 1,970.92 | 2028-01-01 |
| `D` | Livello D | € 1,459.92 | 2028-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 9 increments

| Level | Increment (monthly) |
|---|---:|
| `D` | € 24.17 |
| `C1` | € 25.49 |
| `C` | € 26.47 |
| `C+` | € 26.47 |
| `B1` | € 28.59 |
| `B1+` | € 28.59 |
| `B` | € 30.68 |
| `B+` | € 30.68 |
| `A1` | € 33.58 |
| `A` | € 36.48 |
| `AQ` | € 36.48 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `D`, `C1`, `C`, `C+`, `B1`, `B1+`, `B`, `B+`, `A1`, `A`, `AQ`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "autostrade-trafori/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "apprenticeship_pct_undeclared_components · base_salary · impact unknown · open"
    A percentage apprenticeship reduces every fixed allowance whose apprenticeship_pct_relevant flag the data leaves at its default, together with the base salary. Whether the CCNL applies the percentage to that allowance (an EDR, a contingenza, a function allowance) was not sourced. The run is affected when such an allowance is in the apprentice's pay.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source, for each CCNL, the elements the apprenticeship percentage applies to and set apprenticeship_pct_relevant on every allowance; the limitation then no longer applies to its runs.

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

!!! warning "tfr_compensation_apprentice_guarantee_fund · inps_employer · impact yes · open"
    An apprentice whose TFR goes to a pension fund or to the Fondo Tesoreria takes the 0.28-point relief of D.L. 203/2005 art. 8, but not the exemption from the 0.20% Fondo di garanzia contribution of D.Lgs. 252/2005 art. 10 c. 2: no source found says whether the apprentice rate (10% of L. 296/2006 art. 1 c. 773 plus NASpI and the integration funds) holds a Fondo di garanzia share to exempt. The employer contributions of the run may be overstated by 0.20% of the INPS base.

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Find an INPS source on the Fondo di garanzia share of the apprentice rate, then exempt it with the other workers or record that none is due.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-01-01 | [↗](https://www.aiscat.it/contratto-collettivo-autostrade-trafori) |

??? note "Coverage notes"
    CCNL I192 — Autostrade e Trafori Concessionari. Split model: paga base (minimo tabellare) + CONTINGENZA (frozen, 14m) + EDR 1991 (13m, EUR 10.33 uniform) + EDR 1997 (frozen, 14m, per-level) + IDR 2021 (14m, 2 tranches). AQ level has additional Indennità di Funzione EUR 72.30/month (14m). Seniority: 9 biennali.
    
    Contract covers two renewal periods: 2023 CCNL (01/01/2023–01/01/2025) and 2026 CCNL (01/08/2026–01/01/2028 open). Gap period 01/01/2025–01/08/2026 modeled at 2023 final-tranche values (inter-contract ultrattività).
    
    INPS: uses 2026-industria.json (TaxSector.INDUSTRIA). Divisor 167 derived from contract sources.
    
    Levels B+, B1+, C+ are parametrically derived as D × param/100 for the 2023 contract tranches (params: B+=192, B1+=176, C+=155). Verified against D values to within rounding. 2026 contract values taken from research agent sources.
    
    IDR 2021: modeled as 0.00 for 01/01/2023–01/08/2023 (element not yet established in first 2023 tranches). Period 1 values from 01/08/2023; period 2 from 01/01/2024 onwards.
    
    Apprenticeship: CCNL provides under-classification 2 levels below (engine schema requires static pay_level_code). Modeled as 100% passthrough.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/autostrade-trafori.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/autostrade-trafori.py"
```
