# CCNL Edilizia e Affini Artigianato

| | |
|---|---|
| **CNEL code** | `F015` |
| **Sector** | edilizia |
| **Tax sector** | `artigianato` |
| **Last renewal** | — |
| **Workers (est.)** | ~350k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CNA Costruzioni
    - ANAEPA-Confartigianato
    - FIAE-Casartigiani
    - Feneal-UIL
    - Filca-CISL
    - Fillea-CGIL

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
| **Limits of this contract** | bilateral_funds, pension_fund_contribution, seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | 2026-09-18 |

### Freschezza

| | |
|---|---|
| **Last renewal** | — |
| **Last verified** | 2026-09-18 |
| **Latest salary tranche** | 2028-01-01 |

### Semplificazioni note

4 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `7Q` | Quadro — manager with statutory Quadro status (Art. 2095 c.c., L. 190/1985) | € 2,358.36 | 2028-01-01 |
| `7` | Senior executive employee / site manager — site manager / senior technical staff | € 2,358.36 | 2028-01-01 |
| `6` | Technical employee / worker with supervisory duties — technical staff or team leader | € 2,097.48 | 2028-01-01 |
| `5` | Highly specialised worker — highly specialized worker | € 1,748.04 | 2028-01-01 |
| `4` | Specialised worker — specialized construction worker | € 1,628.40 | 2028-01-01 |
| `3` | First-category worker — skilled worker | € 1,515.12 | 2028-01-01 |
| `2` | Second-category worker — semi-skilled worker | € 1,358.35 | 2028-01-01 |
| `1` | Common worker — unskilled construction worker | € 1,165.30 | 2028-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 0.00 |
| `2` | € 9.86 |
| `3` | € 10.78 |
| `4` | € 11.54 |
| `5` | € 12.55 |
| `6` | € 15.92 |
| `7` | € 16.73 |
| `7Q` | € 16.73 |

## Apprenticeship

**standard_gruppo_4** (type: `percentage`)  
Destination levels: `4`  
percentage: 1.00

**standard_gruppi_1_3** (type: `percentage`)  
Destination levels: `3`, `4`, `5`  
percentage: 1.00

**specialistico_1sp** (type: `percentage`)  
Destination levels: `4`, `5`  
percentage: 1.00

**specialistico_2sp** (type: `percentage`)  
Destination levels: `3`, `4`  
percentage: 1.00

**specialistico_3sp** (type: `percentage`)  
Destination levels: `3`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "edilizia-artigianato-cna/seniority_cadence_unconfirmed · seniority · impact unknown · open"
    Seniority increment cadence (24 months) and maximum count (5) taken from general CCNL Edilizia Artigianato provisions; F015-specific text not independently confirmed. Level 1 scatto = EUR 0.00 as published in kitech.it.

    **Applies when:** `seniority` applies.

    **Remediation:** Confirm the 24-month cadence, the 5-scatti maximum and the level 1 amount against the F015 text.

!!! warning "edilizia-artigianato-cna/cassa_edile_accruals_missing · bilateral_funds · impact yes · open"
    For blue-collar workers in construction the Cassa Edile / EPR bilateral system provides additional accrual benefits (annual leave, Christmas bonus, seniority) that are separate from INPS seniority increments. These are not modelled; only the tabular seniority increments are implemented.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Pass the Cassa Edile contributions as a bilateral fund event, or model the Cassa Edile system.

!!! warning "edilizia-artigianato-cna/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "edilizia-artigianato-cna/contractual_fund_uncovered · pension_fund_contribution · impact yes · open"
    The Prevedi table has no row for some levels of the bundle (a quadro level, or an operaio at a level the hourly table lacks): such a worker owes a contractual contribution the engine does not compute, and the run has the incomplete issue contractual_fund_not_computed.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Source the Prevedi amount of the levels without a row and add it, then remove this note.

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
| — | — | 2025-05-20 | [↗](https://www.ediltecnico.it/ccnl-edilizia-artigianato-novita-su-campo-di-applicazione-classificazione-personale-e-apprendistato/) |
| — | — | 2025-05-20 | [↗](https://www.ilccnl.it/ccnl-edilizia-artigianato/) |
| — | — | 2026-01-01 | [↗](https://www.kitech.it/ccnl/edilizia-artigianato) |
| — | — | 2023-07-01 | [↗](https://lexplain.it/ccnl-edilizia-artigianato-tabelle-retributive/) |

??? note "Coverage notes"
    Split salary model: paga base (TimeSeries, 4 tranches May 2025/Jan 2026/Jan 2027/Jan 2028) + contingenza (frozen since July 1992 Protocol) + EDR (frozen EUR 10.33 since 1992).
    
    Paga base May 2025 and Jan 2026 verified directly against published salary tables (ilccnl.it, kitech.it). Jan 2026 cross-checked across all 8 levels.
    
    Jan 2027 and Jan 2028 paga base values confirmed from CCNL F015 renewal text (signed 2025-05-20): 4 tranches totalling +178 EUR at parametro 100 — May 2025 +75, Jan 2026 +35, Jan 2027 +35, Jan 2028 +33 (all at parametro 100 / L1). Parametro coefficients (L1=100, L2=115, L3=130, L4=139, L5=150, L6=180, L7=L7Q=205) applied proportionally; all 8 levels for all 4 periods cross-checked against Jan 2026 published figures (ilccnl.it, kitech.it); max deviation < 0.01 EUR. Source: confartigianatomarcatrevigiana.it citing F015 renewal.
    
    Level 7Q has the same paga base as level 7, plus a fixed indennita di funzione of EUR 140.00/month (F015 Art. on Quadri, L. 190/1985). Modelled at order 8 (above level 7 order 7).
    
    Apprenticeship standard professionalizzante Group 4 (Art. 7, Allegato D, renewal May 2025): 36 months / 6 semesters, destination level 4, 74/76/79/86/91/96% per semester, track 'standard_gruppo_4'. Source: ediltecnico.it citing F015 Allegato D.
    
    INPS contribution rates from 2026-artigianato.json (artigianato sector). No Cassa Edile contribution substitution modelled in the INPS rate; employer Cassa Edile contributions are additional and are out of scope.
    
    Layer 3 (overtime, Cassa Edile contributions, holiday/night premiums, accruals managed bilaterally) is out of scope.
    
    Apprenticeship specialistico tracks (Allegato D, verbale 05/09/2023, Art. 9): 1 Sp (54m, livelli 4-5): 0-12=78%, 12-24=80%, 24-36=86%, 36-42=91%, 42-54=96%. 3 Sp (42m, livello 3): 0-12=78%, 12-24=80%, 24-36=86%, 36-42=91%. SIMPLIFICATION: 2 Sp (45m, livelli 3-4): last 8th sem.=3m (not 6m) to reach 45m (the exact boundary of the last period is not published in textual form by any secondary source; total duration of 45m is confirmed). Source: studiodalmaschio.it; fareapprendistato.it; cdltorino.it.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/edilizia-artigianato-cna.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/edilizia-artigianato-cna.py"
```
