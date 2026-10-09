# CCNL per i lavoratori addetti all'industria orafa, argentiera e della gioielleria (Federorafi)

| | |
|---|---|
| **CNEL code** | `C021` |
| **Sector** | industria |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~18k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federorafi
    - Fim-Cisl
    - Fiom-Cgil
    - Uilm-Uil

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
| **Latest salary tranche** | 2025-06-01 |

### Semplificazioni note

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `7Q` | Level 7Q — top-level quadri | € 2,405.58 | 2025-06-01 |
| `7` | Level 7 — quadri with significant managerial functions | € 2,405.58 | 2025-06-01 |
| `6` | Level 6 — employees with managerial functions or specialist technicians | € 2,212.40 | 2025-06-01 |
| `5S` | Level 5 Superior — workers with qualified executive autonomy | € 2,058.07 | 2025-06-01 |
| `5` | Level 5 — highly specialised workers and white-collar employees | € 1,928.22 | 2025-06-01 |
| `4` | Level 4 — specialist workers and qualified employees | € 1,804.87 | 2025-06-01 |
| `3` | Level 3 — skilled workers and employees | € 1,734.59 | 2025-06-01 |
| `2` | Level 2 — general workers and clerical employees | € 1,574.39 | 2025-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `2` | € 21.59 |
| `3` | € 25.05 |
| `4` | € 26.75 |
| `5` | € 29.64 |
| `5S` | € 32.43 |
| `6` | € 36.41 |
| `7` | € 40.96 |
| `7Q` | € 40.96 |

## Apprenticeship

**professionalizzante_standard** (type: `percentage`)  
Destination levels: `2`, `3`, `4`, `5`, `5S`, `6`, `7`, `7Q`  
percentage: 0.95

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "orafi-argentieri-industria-federorafi/apprentice_seniority · seniority · impact unknown · open"
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
| — | — | 2021-12-23 | [↗](https://www.uilmnazionale.it/wp-content/uploads/2022/01/20211223-CCNL-Orafi-ipotesi-di-rinnovo-apprendistato-firmato.pdf) |
| — | — | 2017-05-18 | [↗](https://www.fim-cisl.it/wp-content/uploads/2021/03/CCNL-orafi-argentieri-18-5-2017.pdf) |
| — | — | — | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=51) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (table minimum inclusive of contingenza and EDR). Source: CCNL 2021 PDF (UILM, signed 23/12/2021), pay tables pp. 4-5. Three tranches from primary source (Jun 2022, Jun 2023, Dec 2024); fourth tranche (Jun 2025) from kitech.it (secondary).
    
    LEVEL 1a REMOVED from 1 June 2022. Art. 4 of the 2021 renewal: workers at level 1a are reclassified to level 2a. The minimum active level post-June 2022 is level 2 (formerly 2a, €1363.86/month). Source: CCNL 2021 PDF Art. 4.
    
    HOURLY DIVISOR 173: confirmed by three independent primary sources — (1) CCNL 2021 PDF Annex 9 apprenticeship ('divisore 173'); (2) CCNL 2017 PDF Art. parental leave ('un centosettantreesimo 1/173'); (3) back-calculation on level 7a tables: 2083.89 / 173 = 12.05 EUR/h.
    
    ADDITIONAL MONTHS: 13 (tredicesima). Source: CCNL 2021 PDF, Annex 9 Art. 7 which refers to the CCNL provisions on the tredicesima.
    
    SENIORITY INCREMENTS: primary source — CCNL 2017 PDF (draft agreement 18/05/2017), General Provisions Section Three 'Aumenti Periodici di Anzianità', 'Valori mensili in vigore dal 1° gennaio 2002'. Confirmed: biennial cadence (24 months), maximum 5 bienniums per category. The 2021 renewal did not modify the increment amounts (not mentioned in the renewal economic clauses). Level Superior (5S) increment = 32.43 EUR confirmed from primary source — value 13.43 on secondary aggregators is incorrect. 7Q increment = 40.96 assumed equal to 7a (no explicit distinction in primary source).
    
    APPRENTICESHIP: three-period percentage (85%/90%/95%), standard duration 36 months. Primary source: CCNL 2021 PDF Annex 9 'Apprendistato professionalizzante'. Art. 4 Annex 9: 85% (months 1-12), 90% (months 13-24), 95% (months 25-36). Divisor 173 confirmed in the same Annex. The 36 months are stated as maximum duration; shorter individual contracts would pro-rate the bands — modelled as a fixed standard track (full 36 months).
    
    ULTRA-ACTIVITY: the 2026 renewal (signed 10/02/2026) has economic effects from 01/10/2026. The 2021 contract governs economically until 30/09/2026. The 2002 increments (from CCNL 2017 PDF) remain operative throughout the modelled period as neither the 2021 nor the 2026 renewal modified them.
    
    JUNE 2025 TRANCHE: values confirmed by two independent secondary sources — kitech.it (category 51) and ilccnl.it (tabelle retributive page, 2025-06-01 data). Both show identical amounts: 2=1574.39, 3=1734.59, 4=1804.87, 5=1928.22, 5S=2058.07, 6=2212.40, 7=2405.58, 7Q=2405.58. 10.54% increase consistent with IPCA+TEM mechanism in Art. 3 CCNL 2021. Cross-confirmed by FIOM-CGIL announcement (fiom-cgil.it, Jun 2025) citing the same mechanism.
    
    FUNCTION ALLOWANCE levels 7 and 7Q: Level 7=59.39 EUR/month, 7Q=114.00 EUR/month. Confirmed stable since 2017 by studiocerbone.com (tabella retributiva page, data from June 2017 onwards) and kitech.it. The 2021 renewal did not modify these allowances (not mentioned in the economic clauses). CCNL 2021 PDF Art. 4 and Annex 9 confirm the 7Q structure but do not re-state the allowance amounts (unchanged since prior contract).
    
    MINIMUM 7Q equals 7a for all tranches. The CCNL does not publish a separate tabular minimum for the 7Q (Quadri) level: quadri receive the same tabular minimum as 7a workers plus the INDENNITA_FUNZIONE_QUADRI allowance (114.00 EUR/month). This two-part structure (base=7a + separate allowance) is the standard model for quadri levels in Italian industrial CCNLs and is consistent with Art. 44 CCNL 2021 provisions on quadri.
    
    INPS: industry sector rates from 2026-industria.json (existing file reused). Employee 9.19%; employer: ≤15 employees 30.13%, 16-50 employees 30.20%, >50 employees 30.50%.
    
    COMETA: supplementary pension fund (Art. 44 CCNL 2021 PDF). Employer 2.00% (from Dec 2024), employee 1.20%. Not modelled in the engine (Layer 3, out of scope).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/orafi-argentieri-industria-federorafi.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/orafi-argentieri-industria-federorafi.py"
```
