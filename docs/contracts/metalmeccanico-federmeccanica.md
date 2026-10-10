# CCNL Metalmeccanici e Installatori di Impianti (Federmeccanica-Assistal)

| | |
|---|---|
| **CNEL code** | `C011` |
| **Sector** | metalmeccanico |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~1,7M |
| **Ruleset version** | `2026.3` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🏭 Production |

[← Contracts index](index.md)

??? note "Signatories"
    - Federmeccanica
    - Assistal
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
| **Limits of this contract** | overtime, seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🏭 Production |
| **Confidence** | 🟢 Verified |
| **Last human review** | 2026-10-10 |

### Freschezza

| | |
|---|---|
| **Last renewal** | — |
| **Last verified** | 2026-10-10 |
| **Latest salary tranche** | 2028-06-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A1` | Level 8 — quadro, maximum professional grade | € 3,070.61 | 2028-06-01 |
| `B3` | Level 7 — high technical or managerial expertise | € 2,998.76 | 2028-06-01 |
| `B2` | Level 6 — specialist technician, department head, technical employee | € 2,686.08 | 2028-06-01 |
| `B1` | Level 5 Super — highly specialised worker, technician | € 2,503.72 | 2028-06-01 |
| `C3` | Level 5 — specialist worker 2nd category, senior white-collar employee (CCNL reference level) | € 2,335.88 | 2028-06-01 |
| `C2` | Level 4 — specialist worker 1st category, white-collar employee | € 2,181.09 | 2028-06-01 |
| `C1` | Level 3 — skilled worker, clerical employee | € 2,135.89 | 2028-06-01 |
| `D2` | Level 2 — standardised operations, simple white-collar duties | € 2,090.76 | 2028-06-01 |
| `D1` | Level 1 — auxiliary duties, simple and repetitive operations | € 1,885.37 | 2028-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `D1` | € 21.59 |
| `D2` | € 25.05 |
| `C1` | € 25.05 |
| `C2` | € 26.75 |
| `C3` | € 29.64 |
| `B1` | € 32.43 |
| `B2` | € 36.41 |
| `B3` | € 40.96 |
| `A1` | € 40.96 |

## Apprenticeship

**professionalizzante_36** (type: `percentage`)  
Destination levels: `D2`, `C1`, `C2`, `C3`, `B1`, `B2`, `B3`  
percentage: 1.00

**professionalizzante_30** (type: `percentage`)  
Destination levels: `D2`, `C1`, `C2`, `C3`, `B1`, `B2`, `B3`  
percentage: 1.00

**professionalizzante_24** (type: `percentage`)  
Destination levels: `D2`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "metalmeccanico-federmeccanica/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "metalmeccanico-federmeccanica/overtime_exempt_quota_supplement · overtime · impact yes · open"
    OVERTIME, QUOTE ESENTI: the 2025 ipotesi (p. 35) adds 8% to the overtime hours worked beyond the exempt quota of 40 or 48 hours a year; the engine does not count the overtime hours of the year, so it does not add it.

    **Applies when:** `overtime` applies.

    **Remediation:** Count the overtime hours of the year and add 8% past the exempt quota, or pass the multiplier on the overtime event.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days. INPS computes it on its own daily base (retribuzione media globale giornaliera of the month before) and on calendar days. The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the INPS indemnity on the INPS daily base and calendar days of the INPS rules, with the pay of the month before, then resolve this limitation.

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
| — | — | 2025-11-22 | [↗](https://www.contratticcnl.it/metalmeccanici/tabelle-retributive/) |
| — | — | — | [↗](https://www.lexplain.it/tabelle-retributive-metalmeccanici-industria/) |
| — | — | — | [↗](https://www.lexplain.it/scatti-di-anzianita-contratto-metalmeccanici-industria/) |

??? note "Coverage notes"
    CONSOLIDATED MINIMUMS: the values in base_salary are the 'consolidated table minimums' of the CCNL Federmeccanica-Assistal, which incorporate base pay, contingenza, and EDR into a single figure (Federmeccanica practice since 2001). For this reason fixed_allowances is empty for all levels.
    
    JUNE 2025 TRANCHE: values verified against the agreement of 12 June 2025 (source: studiomorettistp.it and dinunzio.it, which report the official Federmeccanica-Assistal consolidated table minimums). All 9 levels confirmed.
    
    JUNE 2024 AND JUNE 2026 TRANCHES: values verified on contratticcnl.it (updated July 2026) and lexplain.it.
    
    SENIORITY INCREMENTS: the proposal to replace monthly increments with a one-off 'early settlement' was REJECTED by the unions during the CCNL 2025-2028 negotiations (November 2025 agreement). Increments remain recurring monthly additions as provided by Art. 6 of the current CCNL. The model (seniority_count × amount_by_level) is correct. The amounts in amount_by_level are verified on lexplain.it.
    
    APPRENTICESHIP: professionalizzante (accordo integrativo 20/04/2021). Eligible levels: D2, C1, C2, C3, B1, B2, B3 (D1 and A1 excluded). Pay: 85% (first third), 90% (second third), 95% (third third), then classified at destination. Three duration tracks: 36m (standard), 30m (diploma EQF 4-7 consistent with profession), 24m (D2 serial repetitive production only). Source: accordo 20/04/2021 Federmeccanica art. 'Apprendistato professionalizzante', reproduced in MySolution circolare Marini 13/05/2021.
    
    HOURLY DIVISOR: 173 hours/month (40 h/week × 52/12 = 173.33 rounded to 173, Federmeccanica standard).
    
    MONTHLY PAYMENTS: 13 (thirteenth month). The fourteenth month is not provided for in the Federmeccanica CCNL. The performance bonus/variable company element is not modelled (layer 3).
    
    INPS: the employer rates in 2026-industria.json are calculated for verified components (IVS 23.81% + DS 1.61% + CUAF 2.48% + CIGO D.Lgs.148/2015 + FIS/CIGS Circ.INPS 5/2025). Resulting totals: ≤15 employees = 30.13%, 16-50 employees = 30.20%, >50 employees = 30.50%. Does not include INAIL. The CIGS employee share (0.30% for >15 employees) is not yet modelled in employee_rate.
    
    JUN 2021, JUN 2022, JUN 2023 TRANCHES: values retrieved from lexplain.it (metalworking industry pay tables; secondary aggregator source). Cross-check: D1 Jun-2024=1719.67 confirms exact alignment with data already present. Four annual tranches (Jun 2021-2024) based on the IPCA mechanism from the CCNL 05/02/2021.
    
    OVERTIME/NIGHT/HOLIDAY (L3): percentages modelled per Art. 14 CCNL Federmeccanica 2021 (straordinario diurno 15%, lavoro notturno 20%, lavoro festivo 30%). Source: testo contrattuale Art. 14. NOTE: the 2025-11-22 renewal (CCNL 2025-2028) is expected to update these percentages; a dedicated data correction PR will add time-versioned 2025 rates once the official text is available in machine-readable form.
    
    SICKNESS (Sez. Quarta Titolo VI Art. 2): full pay for the first 122/153/214 days of the treatment chain and 80% after, by seniority band (up to 3 years, 3 to 6, over 6); comporto breve of 183/274/365 days over the sickness of the three years that end on the day; the chain restarts after 61 days of work; the first 3 days of the fourth short absence (at most 5 days) of a calendar year are paid 66%, of the fifth and later 50%. The history before the imported episodes, the seniority and the exemption of a short absence are facts: when they could change a sick day the run has a missing_fact blocker.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/metalmeccanico-federmeccanica.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/metalmeccanico-federmeccanica.py"
```
