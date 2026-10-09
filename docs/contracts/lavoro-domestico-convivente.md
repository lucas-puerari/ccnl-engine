# CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (conviventi)

| | |
|---|---|
| **CNEL code** | `H501` |
| **Sector** | lavoro domestico |
| **Tax sector** | `lavoro-domestico` |
| **Last renewal** | — |
| **Workers (est.)** | ~900k |
| **Ruleset version** | `2026.3` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - DOMINA — Associazione Nazionale Famiglie Datori di Lavoro Domestico
    - FIDALDO — Federazione Italiana Datori di Lavoro Domestico
    - ASSINDATCOLF — Associazione Nazionale dei Datori di Lavoro Domestico
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL
    - FEDERCOLF

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
| **Limits of this contract** | base_salary, inps_employee, inps_employer, seniority |

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
| **Latest salary tranche** | 2026-01-01 |

### Semplificazioni note

6 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `DS` | Level DS — senior caregiver / household manager with seniority | € 1,474.73 | 2026-01-01 |
| `D` | Level D — senior caregiver / household manager | € 1,404.51 | 2026-01-01 |
| `CS` | Level CS — specialised domestic worker with seniority | € 1,193.84 | 2026-01-01 |
| `C` | Level C — specialised domestic worker / assistant caregiver (badante) | € 1,123.63 | 2026-01-01 |
| `BS` | Level BS — qualified domestic worker with seniority | € 1,053.39 | 2026-01-01 |
| `B` | Level B — qualified domestic worker (colf qualificata) | € 983.16 | 2026-01-01 |
| `AS` | Level AS — domestic worker with seniority qualification | € 958.55 | 2026-01-01 |
| `A` | Level A — entry-level domestic worker (colf generica) | € 908.10 | 2026-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 7 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 36.32 |
| `AS` | € 38.34 |
| `B` | € 39.33 |
| `BS` | € 42.14 |
| `C` | € 44.95 |
| `CS` | € 47.75 |
| `D` | € 56.18 |
| `DS` | € 58.99 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "lavoro-domestico-convivente/tranches_from_2027 · base_salary · impact yes · open"
    SINGLE PERIOD 2026-01-01. Pre-2026 tranches out of scope. Post-2026 CCNL 2025-2028 tranches not yet modelled: +30 on BS convivente from Jan 2027, +15 from Jan 2028, +15 from Sep 2028 (other levels proportional — exact amounts require official ASSINDATCOLF/DOMINA table for those periods).

    **Applies when:** `base_salary` applies; from 2027-01-01.

    **Remediation:** Add the 2027 and 2028 tranches from the official ASSINDATCOLF/DOMINA tables.

!!! warning "lavoro-domestico-convivente/seniority_frozen_at_2026 · seniority · impact unknown · open"
    Seniority amounts frozen at 2026 base. Future ISTAT adjustments will raise base_salary but amounts_by_level will need manual update.

    **Applies when:** `seniority` applies; from 2027-01-01.

    **Remediation:** Update the seniority amounts with each ISTAT adjustment of the minimum tables.

!!! warning "lavoro-domestico-convivente/part_time_scaling · base_salary · impact unknown · open"
    REDUCED HOURS UNDER ART. 14 C. 1: a convivente may agree fewer than 54 weekly hours (art. 14 c. 1: 'con un massimo di [...] 54 ore settimanali'). The CCNL gives Tabella A as monthly values and no rule to proportion them to the agreed hours; the engine scales the pay linearly on the full time the employment states. The art. 14 c. 2 regime (levels C, B, B super up to 30 hours, Tabella B) is the separate file lavoro-domestico-convivente-orario-ridotto.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source how the Tabella A minimum of a convivente with fewer than 54 agreed weekly hours is computed and model it, then remove this note.

!!! warning "lavoro-domestico-convivente/hourly_inps_bracket_unvalidated · inps_employer · impact unknown · open"
    Dividing TABELLA A monthly base by hourly_divisor 234 yields the cash-only rate: the INPS hourly bracket for weekly_hours <= 24 is selected on it, without the board and lodging the INPS retribuzione oraria effettiva counts. The hourly-wage INPS bracket lookup has not been validated for this file; the wage-bracket path is not exercised by the golden cases shipped with this file.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Validate the hourly INPS bracket lookup for weekly hours up to 24 against the INPS domestic table.

!!! warning "lavoro-domestico-convivente/board_lodging_substitute · base_salary · impact unknown · open"
    The cash indennita sostitutiva of board and lodging is not paid for the days the convivente does not take them: ferie (Art. 17 c. 7), sospensioni extraferiali (Art. 18 c. 1), congedo matrimoniale (Art. 24 c. 2), malattia and infortunio outside hospital (Art. 27 c. 9, Art. 29 c. 7). The request carries no fact on whether board and lodging were taken, so the engine pays none.

    **Applies when:** `base_salary` applies; run kind in regular, termination.

    **Remediation:** Add a fact for the days without board and lodging and pay the Tabella F value for them.

!!! warning "lavoro-domestico-convivente/extra_month_hours · inps_employee · impact unknown · open"
    INPS and Cas.Sa.Colf are charged on the contributable hours the run states, a tredicesima run too. No bundled source says whether the tredicesima carries contributable hours of its own, and a competence year gives it the hours of its default facts, those of a regular month.

    **Applies when:** `inps_employee` applies; run kind in thirteenth.

    **Remediation:** Source from the INPS rules whether the tredicesima carries contributable hours and set them for extra-month runs.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days. INPS computes it on its own daily base (retribuzione media globale giornaliera of the month before) and on calendar days. The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the INPS indemnity on the INPS daily base and calendar days of the INPS rules, with the pay of the month before, then resolve this limitation.

!!! warning "sickness_cumulation_window · sickness · impact unknown · open"
    The CCNL tier and the comporto are counted on the days of one episode and the relapses it continues. A CCNL that sums the sickness of separate episodes over a window (a calendar year, the last three years) can reach a lower tier or the end of the comporto earlier than the engine shows. The run is affected when an earlier episode outside the relapse chain is recorded.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Add the cumulation window of each CCNL to its sickness rule, with the source, and count the tier and the comporto over it.

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax or INPS ruleset marked provisional: the sources of its year are not published yet (INPS circular on the massimale, minimale and rates of the year; regional and municipal surtax resolutions; budget law of the year), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; the indexed amounts (INPS massimale and minimale) do not, and any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-01-01 | [↗](https://associazionedomina.it/wp-content/uploads/2026/02/TABELLA-minimi-retributivi-2026.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobated retribuzione globale (TABELLA A — Lavoratori Conviventi, Art. 14 Co.1 lett. a CCNL). Values confirmed from official Domina salary table PDF (TABELLA-minimi-retributivi-2026.pdf, effective 01/01/2026, ISTAT +1.00%). Source is signatory employer association — primary source.
    
    TAX SECTOR: lavoro-domestico (TaxSector.LAVORO_DOMESTICO). Flat per-hour INPS contributions from INPS Circ. 9/2026. A household employer is not a withholding agent: it is not among the sostituti d'imposta of art. 23 c. 1 D.P.R. 600/1973 (art. 33 c. 1 D.Lgs. 33/2025 from 2027), so the engine withholds no IRPEF or surtax and pays no trattamento integrativo, ulteriore detrazione or somma esente.
    
    HOURLY DIVISOR: 234 = 54 x 52 / 12: 54 h/week contractual maximum for conviventi (Art. 14 c. 1 lett. a CCNL 28/10/2025) and monthly pay = hourly pay x weekly hours x 52 / 12 (chiarimento a verbale 1). Convivente and non-convivente are independent pay scales (different tables, different hourly divisors).
    
    ADDITIONAL MONTHS: 13 (tredicesima mensilita, Art. 39 CCNL 28/10/2025). No quattordicesima for domestic workers.
    
    SENIORITY: biennale (24 months), maximum 7 scatti. Per-level euro amounts = 4% × 2026 base (confirmed: kitech.it amounts match Domina base × 4% exactly at every level). Amounts frozen at 2026 base — will not automatically recompute at future ISTAT tranches.
    
    APPRENTICESHIP: none. Domestic workers are excluded from D.lgs. 81/2015 Art. 47 apprenticeship provisions.
    
    D/DS INDENNITÀ DI FUNZIONE: 207.69 EUR/month (Art. 34 CCNL) for levels D and DS only. Modelled as fixed_allowance (no role restriction — applies to all workers at those levels). Confirmed from Domina official table.
    
    CNEL code H501 confirmed: lavoro-economia.it explicitly lists 'CCNL Lavoro Domestico (Colf e Badanti) [Cnel: H501]'. Also confirmed via kitech.it. CNEL archive verification not attempted (had returned 404 previously).
    
    Livello Unico (811.09) is a special sub-under-18 level excluded from this model — single-source, limited coverage.
    
    BOARD AND LODGING: every level carries the allowance vitto_alloggio, the valore convenzionale of board and lodging provided in kind (Art. 36 c. 3, Tabella F 2026: 2,33 + 2,33 + 2,00 per day, x 30 = 199,80 per month). A regular run pays no cash for it and counts it in the TFR base (Art. 41 c. 1); the tredicesima pays it in cash (Art. 39 c. 1, chiarimento a verbale 5). It is not reduced for reduced hours (Art. 14 c. 2: intera retribuzione in natura).
    
    CAS.SA.COLF: contributi di assistenza contrattuale of Art. 54 c. 2, 0,06 EUR per paid hour, 0,02 withheld from the worker and 0,04 paid by the employer, charged on the contributable hours of the run.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/lavoro-domestico-convivente.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/lavoro-domestico-convivente.py"
```
