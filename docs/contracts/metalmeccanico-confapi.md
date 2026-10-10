# CCNL Metalmeccanici Piccola Industria (Unionmeccanica-Confapi)

| | |
|---|---|
| **CNEL code** | `C018` |
| **Sector** | metalmeccanico |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~350k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Unionmeccanica-Confapi
    - FIM-CISL
    - FIOM-CGIL
    - UILM-UIL

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
| **Limits of this contract** | base_salary, pension_fund_contribution, seniority |

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
| **Latest salary tranche** | 2026-06-01 |

### Semplificazioni note

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `9` | Level 9 — highly qualified quadro | € 3,124.30 | 2026-06-01 |
| `8` | Level 8 — highly specialised technician, quadro | € 2,809.37 | 2026-06-01 |
| `7` | Level 7 — high technical or managerial expertise | € 2,583.36 | 2026-06-01 |
| `6` | Level 6 — specialist technician, department head, senior technical employee | € 2,407.97 | 2026-06-01 |
| `5` | Level 5 — specialist worker 2nd category, senior white-collar employee (CCNL reference level) | € 2,245.87 | 2026-06-01 |
| `4` | Level 4 — specialist worker 1st category, white-collar employee | € 2,096.58 | 2026-06-01 |
| `3` | Level 3 — skilled worker, clerical employee | € 2,009.48 | 2026-06-01 |
| `2` | Level 2 — standardised operations, simple executive duties | € 1,811.11 | 2026-06-01 |
| `1` | Level 1 — auxiliary duties, simple and repetitive operations | € 1,639.96 | 2026-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 18.49 |
| `2` | € 21.59 |
| `3` | € 25.05 |
| `4` | € 26.75 |
| `5` | € 29.64 |
| `6` | € 32.43 |
| `7` | € 36.41 |
| `8` | € 40.95 |
| `9` | € 45.96 |

## Apprenticeship

**professionalizzante** (type: `under_classification`)  
Destination levels: `3`, `4`, `5`, `6`, `7`, `8`, `9`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "metalmeccanico-confapi/apprenticeship_36_months_assumed · base_salary · impact unknown · open"
    APPRENTICESHIP under-classification (Art. 10 consolidated CCNL text 26/05/2021): graded two levels below destination in the 1st period (0-12 months), one level below in the 2nd (12-24), at destination from the 25th month; 'professionalizzante' track for destinations from level 3 to level 9 (36-month duration assumed for all destinations).

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Source the apprenticeship duration per destination level from Art. 10.

!!! warning "metalmeccanico-confapi/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "metalmeccanico-confapi/fondapi_base_elements · pension_fund_contribution · impact yes · open"
    The Fondapi base ('retribuzione Fondapi' or 'elemento retributivo nazionale') counts the EDR, the indennita di funzione of the quadri and the elemento retributivo of the 8th and 9th categories besides the minimum; the bundle pay of this CCNL does not hold them, so the fund contributions of an enrolled worker are computed on the minimum alone and understated.

    **Applies when:** `pension_fund_contribution` applies.

    **Remediation:** Model the EDR, the indennita di funzione of the quadri and the elemento retributivo of the 8th and 9th categories in the pay of the CCNL and add them to the Fondapi base, then remove this note.

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

!!! warning "tfr_compensation_apprentice_guarantee_fund · inps_employer · impact yes · open"
    An apprentice whose TFR goes to a pension fund or to the Fondo Tesoreria takes the 0.28-point relief of D.L. 203/2005 art. 8, but not the exemption from the 0.20% Fondo di garanzia contribution of D.Lgs. 252/2005 art. 10 c. 2: no source found says whether the apprentice rate (10% of L. 296/2006 art. 1 c. 773 plus NASpI and the integration funds) holds a Fondo di garanzia share to exempt. The employer contributions of the run may be overstated by 0.20% of the INPS base.

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Find an INPS source on the Fondo di garanzia share of the apprentice rate, then exempt it with the other workers or record that none is due.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-06-01 | [↗](https://www.studiotuscano.it/news/nuovi-minimi-retributivi-per-il-ccnl-metalmeccanica-piccola-industria-confapi) |
| — | — | 2025-06-01 | [↗](https://www.studiomorettistp.it/aumento-retribuzione-tabellare-ccnl-metalmeccanici-piccola-industria-confapi-cnel-c018_n97.php) |
| — | — | 2026-06-01 | [↗](https://leggeinchiaro.it/ccnl-metalmeccanica-confapi-pmi-tabelle-retributive/) |
| — | — | — | [↗](https://www.lexplain.it/scatti-di-anzianita-ccnl-metalmeccanici-pmi-confapi/) |

??? note "Coverage notes"
    CONSOLIDATED MINIMUMS: the values in base_salary are the Confapi PMI 'consolidated table minimums', which incorporate base pay, contingenza, and terzo elemento into a single figure (ilccnl.it shows contingenza=0 and terzo elemento=0). fixed_allowances is empty for all levels.
    
    MODELLED TRANCHES: June 2024 (source: studiotuscano.it — Confapi June 2024 tables), June 2025 (source: studiomorettistp.it — FIM-CISL minutes 19/06/2025), September 2025 (derived by re-parametrisation, see note below), June 2026 (source: leggeinchiaro.it, Unionmeccanica tables).
    
    SEPTEMBER 2025 TRANCHE — RE-PARAMETRISATION: the agreement of 24 July 2025 provides +22.10 € at level 5 from 1 September 2025. The values for the other levels are calculated using the deterministic formula set out in the CCNL ('re-parametrisation of the other contractual levels'): level_increase = round(22.10 × (level_min_jun25 / 2173.76), 2). The same formula is verified against the June 2025 tranches (results matching to the cent with the FIM-CISL minutes). Verify the official table from Unionmeccanica or FIM-CISL for confirmation; possible deviation of ±0.01 € on some levels due to rounding.
    
    PRE-JUNE 2024 TRANCHES (CCNL in force since 26 May 2021) are outside the modelled window.
    
    SENIORITY INCREMENTS: amounts verified against Art. 41 of the CCNL consolidated text 26/05/2021 (source: www.htdi.it/CCNL%20Consolidato%20del%2026-05-2021.pdf). Full table: 1a=18.49 2a=21.59 3a=25.05 4a=26.75 5a=29.64 6a=32.43 7a=36.41 8a=40.95 9a=45.96 (in force from 1 January 2001). 24-month cadence, maximum 5 increments.
    
    HOURLY DIVISOR: 173 hours/month (40 h/week × 52/12, industry standard — confirmed by Art. 10 CCNL for calculation of apprentice hourly pay).
    
    MONTHLY PAYMENTS: 13 (thirteenth month). The fourteenth month is not provided for in the Confapi PMI CCNL.
    
    INPS: uses 2026-industria.json. Standard industry rates; verify whether Confapi PMI provides differentiated contributions compared to Federmeccanica for CIG/FIS.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/metalmeccanico-confapi.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/metalmeccanico-confapi.py"
```
