# CCNL per i lavoratori delle imprese produttrici, distributrici di energia elettrica (Elettricita Futura)

| | |
|---|---|
| **CNEL code** | `K051` |
| **Sector** | industria |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~60k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Elettricita Futura
    - Utilitalia
    - Enel SpA
    - GSE
    - Sogin SpA
    - Terna SpA
    - FILCTEM-CGIL
    - FLAEI-CISL
    - UILTEC-UIL

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
| **Latest salary tranche** | 2027-10-01 |

### Semplificazioni note

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QS` | Senior Quadro | € 4,399.12 | 2027-10-01 |
| `Q` | Quadro | € 3,947.60 | 2027-10-01 |
| `ASS` | Senior Senior Specialist Area | € 3,484.42 | 2027-10-01 |
| `AS` | Senior Specialist Area | € 3,261.27 | 2027-10-01 |
| `A1S` | Area 1 Senior | € 3,124.14 | 2027-10-01 |
| `A1` | Area 1 | € 2,980.96 | 2027-10-01 |
| `BSS` | Area B Senior Senior | € 2,838.72 | 2027-10-01 |
| `BS` | Area B Senior | € 2,717.73 | 2027-10-01 |
| `B1S` | Area B1 Senior | € 2,589.64 | 2027-10-01 |
| `B1` | Area B1 | € 2,473.33 | 2027-10-01 |
| `B2S` | Area B2 Senior | € 2,309.87 | 2027-10-01 |
| `B2` | Area B2 | € 2,149.26 | 2027-10-01 |
| `CS` | Area C Senior | € 1,905.68 | 2027-10-01 |
| `C1` | Area C1 | € 1,724.71 | 2027-10-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `QS` | € 49.01 |
| `Q` | € 46.33 |
| `ASS` | € 43.07 |
| `AS` | € 39.82 |
| `A1S` | € 37.86 |
| `A1` | € 35.74 |
| `BSS` | € 33.72 |
| `BS` | € 31.97 |
| `B1S` | € 30.16 |
| `B1` | € 28.46 |
| `B2S` | € 26.13 |
| `B2` | € 23.81 |
| `CS` | € 20.30 |
| `C1` | € 17.66 |

## Apprenticeship

**gruppo_c** (type: `percentage`)  
Destination levels: `CS`  
percentage: 1.00

**gruppo_b** (type: `percentage`)  
Destination levels: `B1`  
percentage: 1.00

**gruppo_a_bss** (type: `percentage`)  
Destination levels: `BSS`, `A1`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "elettrico-elettricita-futura/apprentice_seniority · seniority · impact unknown · open"
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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-02-11 | [↗](https://www.contratticcnl.it/elettrico/tabelle-retributive/) |
| — | — | 2025-02-11 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=92) |

??? note "Coverage notes"
    Salary model is split. base_salary = paga base (time-series, 4 tranches from the 2025-02-11 renewal); fixed_allowances = EDR (Elemento Distinto della Retribuzione) frozen at EUR 10.33/month since 1988, same for all levels.
    
    hourly_divisor 173.33 as stated by the contract (40h/week statutory base: 40 x 52 / 12). Actual weekly hours are 38 (non-shift) or 40 (shift); the divisor is contractually fixed on the 40h base.
    
    Seniority cadence 24 months (biennale), maximum 5 scatti (10 years of service per contract text). Amounts vary by level (kitech.it, April 2026).
    
    APPRENTICESHIP (Art. 15 CCNL 2025-02-11, apprendistato professionalizzante). Three tracks by qualification group. Gruppo C (dest CS, 36m): yr1=86%, yr2=90%, yr3=96%, then 100%. Gruppo B excl. BSS (dest B1, 36m): same progression. BSS + Gruppo A (dest BSS and A1, 24m): yr1=86%, yr2=96%, then 100%. Source: Art. 15 para.5 table (CCNL full text PDF filctemcgil.it, 2025-02-11). Note: only the four qualification levels explicitly cited in Art.15 (CS, B1, BSS, A1) are modelled; S-suffix variants (B1S, A1S, etc.) are senior-grade levels not addressed in the apprenticeship article.
    
    APR 2027 VALUES: confirmed via parametric derivation. The CCNL elettrici system applies a fixed valore-punto increase each tranche (same absolute amount per parametro per tranche). Apr 2026 and Apr 2027 increments are equal across all 14 levels (ratio=1.000 verified); A1S reference level gets +65.50 EUR matching the search-confirmed '+65 EUR average TEM' for Apr 2027 (fiscoetasse.com, pmi.it). October 2027 values verified against contratticcnl.it (all 14 levels match).
    
    Workers covered: approximately 63,000 in 687 companies (Enel SpA, Terna SpA, GSE, Sogin, Energia Libera and affiliated). Agreement signed 2025-02-11; valid until 2027-12-31.
    
    INPS rates from 2026-industria.json (industria sector, 50 employees tier). IRPEF 2026 brackets applied (L. 199/2025).
    
    contratticcnl.it shows data alignment errors for BSS, BS, B1 in the April 2026 and April 2027 columns; kitech.it April 2026 values used as authoritative for all 14 levels.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/elettrico-elettricita-futura.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/elettrico-elettricita-futura.py"
```
