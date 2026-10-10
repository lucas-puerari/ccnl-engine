# CCNL Marittimi — Industria Armatoriale (CONFITARMA)

| | |
|---|---|
| **CNEL code** | `I391` |
| **Sector** | navigazione marittima — personale di terra |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~15k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🟢 Verified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CONFITARMA
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
| **Last renewal** | — |
| **Last verified** | — |
| **Latest salary tranche** | 2026-07-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `VIIQ` | Livello VII Q — Quadri: VII minimo + INDENNITA_FUNZIONE EUR 225.00 (Art. 18 quinquies) | € 2,800.07 | 2026-07-01 |
| `VII` | Livello VII — Lavoratori con responsabilita direttive di alto livello | € 2,800.07 | 2026-07-01 |
| `VI` | Livello VI — Lavoratori con elevata autonomia e responsabilita gestionale | € 2,429.76 | 2026-07-01 |
| `V` | Livello V — Lavoratori altamente specializzati con coordinamento | € 2,108.93 | 2026-07-01 |
| `IV` | Livello IV — Lavoratori con qualifiche tecniche e responsabilita operative | € 1,989.32 | 2026-07-01 |
| `III` | Livello III — Lavoratori specializzati con autonomia operativa | € 1,755.00 | 2026-07-01 |
| `II` | Livello II — Lavoratori qualificati con mansioni esecutive | € 1,591.25 | 2026-07-01 |
| `I` | Livello I — Lavoratori addetti a mansioni di semplice esecuzione | € 1,509.42 | 2026-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `I` | € 23.74 |
| `II` | € 24.41 |
| `III` | € 25.76 |
| `IV` | € 29.35 |
| `V` | € 30.47 |
| `VI` | € 34.39 |
| `VII` | € 36.07 |
| `VIIQ` | € 36.07 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `III`, `IV`, `V`, `VI`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "marittimi-industria-armatoriale/apprentice_seniority · seniority · impact unknown · open"
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

### Without monetary impact

!!! note ""
    PRE-2024 HISTORY: prior CCNL signed 16/12/2020. Values before 01/07/2024 not modelled. From the 2020 contract PDF (usclac.it): terra salary tables were in Allegato 2 (tabelle retributive per il personale di terra, 2021-2023 tranches). Sezione 15 (uffici e terminals) specifically references Allegato 9 "in formato elettronico" — a separate electronic file not embedded in the scanned PDF. Neither Allegato 2 (scanned, image-only) nor Allegato 9 (separate file) is machine-readable. Engine history starts at 01/07/2024.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-07-11 | [↗](https://www.filtcgil.it/images/Contratti/Mare/15_-_SEZIONE_PERSONALE_DI_TERRA.pdf) |

??? note "Coverage notes"
    CCNL 2024-2026 (CONFITARMA/FILT-CGIL/FIT-CISL/UILTRASPORTI), signed 11/07/2024, valid 01/07/2024-31/12/2026. Personale di terra (shore-based staff), Sezione 15 — Allegati 1 and 1bis.
    
    SPLIT model: minimo contrattuale (base_salary) + EAR Elemento Aggiuntivo della Retribuzione (per-level, omnicomprensivo) modelled as fixed_allowance. 3 tranches: 01/07/2024 (40%), 01/07/2025 (30%), 01/07/2026 (30%).
    
    VIIQ (Quadri): VII minimo + INDENNITA_FUNZIONE EUR 225.00/month fixed (since June 2007, not indexed). Included in TFR, 13th and 14th month, festivity. NOT included in overtime base.
    
    HOURLY DIVISOR: 173 (Art. 10 para 8). Daily divisor: 26. Verified on 3 levels: L1=1509.42/173=8.72, LIV=1989.32/173=11.50, LVII=2800.07/173=16.18.
    
    ADDITIONAL MONTHS: 14 — tredicesima (Christmas) and quattordicesima (Easter/summer). Art. 17: base = minimo + superminimo + scatti + contributo mensa + indennita funzione.
    
    SENIORITY: 24-month cadence (biennale), max 5 for workers hired from 1989 onwards. Per-level EUR from Allegato 1: I=23.74, II=24.41, III=25.76, IV=29.35, V=30.47, VI=34.39, VII=36.07.
    
    APPRENTICESHIP: professionalizzante, eligible levels III-VI only. Months 1-12: 70% of minimo; months 13-36: 80% of minimo. Minimum 6 months, maximum 36 months.
    
    SENIORITY MAX: CCNL provides 10 max increments for workers hired before 31/12/1988; modelled as max=5 (post-1988 hires, the prevailing case for the active workforce — no one hired before 1988 is still accumulating scatti). Structural engine limitation for the pre-1988 grandfathered cohort.
    
    SUPERMINIMO LIVELLO: Art. 18 provides additional EUR 7/month for L4 workers after 8 years in level, and EUR 7-11/month for L2-L3 workers under specific conditions. Individual-level amounts tied to personal history — not modellable in a standardised payroll engine (no per-worker tenure field). Out_of_scope structural limitation.
    
    EAR FOR VIIQ: Allegato 1bis lists EAR only for VII (not VIIQ separately). VIIQ workers receive the same EAR as VII; the distinguishing element is INDENNITA_FUNZIONE (additional allowance for quadri). Structural design: VIIQ base = VII base, VIIQ fixed_allowances includes INDENNITA_FUNZIONE.
    
    UNA TANTUM: backpay EUR 200 paid Jul 2024 + EUR 180 paid Jan 2025, uniform all levels. Lump-sum, not recurring. Out_of_scope per engine design (una tantum payments are not included in periodic payroll computation).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/marittimi-industria-armatoriale.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/marittimi-industria-armatoriale.py"
```
