# CCNL Dipendenti delle Farmacie Municipalizzate (ASSOFARM)

| | |
|---|---|
| **CNEL code** | `H124` |
| **Sector** | Farmacie municipalizzate e partecipate da enti locali |
| **Tax sector** | `terziario` |
| **Last renewal** | 2022-07-07 |
| **Workers (est.)** | ~6k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ASSOFARM
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTuCS

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
| **Limits of this contract** | inps_employer, seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2022-07-07 |
| **Last verified** | — |
| **Latest salary tranche** | 2024-07-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1Q` | 1o livello Q - Direttore responsabile e area manager | € 2,456.91 | 2024-07-01 |
| `1S` | 1o livello super - Direttore responsabile con funzioni direttive | € 2,372.46 | 2024-07-01 |
| `1C` | 1o livello C - Farmacista collaboratore con funzioni speciali | € 2,266.37 | 2024-07-01 |
| `1_12` | 1o livello + 12 anni - Farmacista collaboratore con 12+ anni di servizio | € 2,109.97 | 2024-07-01 |
| `1_2` | 1o livello + 2 anni - Farmacista collaboratore con 24+ mesi di servizio | € 2,109.97 | 2024-07-01 |
| `1` | 1o livello - Farmacista collaboratore | € 2,109.97 | 2024-07-01 |
| `2` | 2o livello - Lavoratori con funzioni di coordinamento o tecnico-specialistiche | € 1,872.16 | 2024-07-01 |
| `3` | 3o livello - Lavoratori con conoscenze tecnico-pratiche qualificate | € 1,777.29 | 2024-07-01 |
| `4` | 4o livello - Lavoratori con compiti esecutivi e conoscenze tecnico-pratiche | € 1,652.61 | 2024-07-01 |
| `5` | 5o livello - Lavoratori qualificati con normali conoscenze operative | € 1,522.17 | 2024-07-01 |
| `6` | 6o livello - Lavoratori con mansioni di pulizia e operazioni semplici | € 1,421.48 | 2024-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 15 increments

| Level | Increment (monthly) |
|---|---:|
| `1Q` | € 26.50 |
| `1S` | € 25.82 |
| `1C` | € 25.31 |
| `1_12` | € 25.31 |
| `1_2` | € 25.31 |
| `1` | € 25.31 |
| `2` | € 23.24 |
| `3` | € 22.72 |
| `4` | € 20.66 |
| `5` | € 20.14 |
| `6` | € 19.63 |

## Apprenticeship

**farmacista_collaboratore** (type: `under_classification`)  
Destination levels: `1`

**professionalizzante** (type: `under_classification`)  
Destination levels: `4`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "farmacie-municipalizzate-assofarm/terziario_rates_proxy · inps_employer · impact unknown · open"
    INPS RATES. Terziario proxy used. ASSOFARM entities operate as aziende speciali or società di gestione farmacia (private-law entities under municipal control); the contract is registered CNEL H124 and negotiated by UGL Terziario — standard private-sector INPS regime (terziario) is the expected classification. Note: CCNL text references "INPS Gestione ex INPDAP" in benefit provisions, suggesting legacy workers transferred from public-sector management may retain the ex-INPDAP pension regime — contribution rates for those workers differ. No sector-specific INPS circular identified; kitech.it does not list a dedicated contribution table for farmacie municipalizzate. Simplification retained.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Verify the INPS classification against a sector circular, including ex-INPDAP legacy workers.

!!! warning "farmacie-municipalizzate-assofarm/apprentice_seniority · seniority · impact unknown · open"
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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2022-07-07 | [↗](https://www.assofarm.it/wp-content/uploads/2024/12/CCNL2022.2024.signedcorrect.pdf) |

??? note "Coverage notes"
    Salary model: conglobated. Allegato B shows unified retribuzione di base with no separate contingenza or EDR columns. Back-calculation: L1=2109.97/173=12.20 EUR/h, L3=1777.29/173=10.27 EUR/h, L6=1421.48/173=8.22 EUR/h (all consistent with divisor 173).
    
    Hourly divisor 173: Art. 18 explicit: 'La quota oraria di retribuzione si ottiene dividendo la retribuzione mensile per 173'.
    
    Additional months: 14. Art. 20 explicit: quattordicesima (luglio) + tredicesima (dicembre).
    
    IQ (Indennita Quadri): Allegato C, effective 01/07/2022. Levels 1Q=160, 1S=150, 1C=145 EUR/month.
    
    IS (Indennita Speciale): Art. 19bis + Allegato A. Level 1+12anni=130, Level 1+2anni=100 EUR/month. Unchanged in 2022 renewal (Allegato C covers only IQ increments; Art. 19bis refers to Tabella A 2015 values).
    
    Seniority: 15 scatti biennali per Allegato E, decorrenza 1 gennaio 2014.
    
    Apprenticeship: Allegato F, under-classification. Farmacista collaboratore stays at Primo livello for all 36 months (levels_below=0). Non-pharmacist roles (Coadiutore, Capo settore, Addetto amministrativo): months 1-12 at Sesto, months 13-36 at Quinto, exit Quarto.
    
    Contract valid 07/07/2022-31/12/2024, ultrattivo since 01/01/2025 (no successor deposited at CNEL as of 2026-09-05). Third tranche (01/07/2024) modelled open-ended.
    
    Headcount: 6,389 workers, 335 employers (ASSOFARM primary source).
    
    Levels 1_12 and 1_2 (Farmacista Collaboratore with 12+ or 2+ years continuous service) are automatic time-in-grade progressions under Art. 19bis. Engine cannot model auto-advancement; implemented as static level codes distinguishable by IS allowance amount (1_12=130, 1_2=100 EUR/month). Structural engine limitation — correct payroll calculation requires knowing the worker's actual time-in-grade.
    
    Function and Tech-Prof allowances shown in kitech for L2/L3/quadri sub-levels are EXCLUDED. They appear in no allegato of the signed CCNL; Art. 17 defines retribuzione di base as Tabelle A+B only. Verification: 1Q base+IQ=2456.91+160=2616.91 vs kitech 2758.68; delta 141.77 = sum of the two extra kitech lines — confirming they are historical/personal elements outside the contractual minimum. Exclusion is correct.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/farmacie-municipalizzate-assofarm.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/farmacie-municipalizzate-assofarm.py"
```
